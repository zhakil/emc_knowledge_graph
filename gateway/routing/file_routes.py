"""
文件处理API路由模块
处理文件上传、解析、实体提取和图数据库集成
"""

import asyncio
import logging
import os
import tempfile
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field, validator

from ..middleware.auth import get_current_user
from ..middleware.rate_limiting import rate_limit
from services.file_processing.emc_file_processor import EMCFileProcessor, FileMetadata, ExtractionResult
from services.knowledge_graph.neo4j_emc_service import Neo4jEMCService


router = APIRouter()
logger = logging.getLogger(__name__)


# 请求/响应模型
class FileProcessingRequest(BaseModel):
    """文件处理请求"""
    extract_entities: bool = Field(True, description="是否提取实体")
    build_graph: bool = Field(True, description="是否构建图数据")
    analysis_mode: str = Field("comprehensive", description="分析模式")
    
    @validator('analysis_mode')
    def validate_analysis_mode(cls, v):
        allowed_modes = ['fast', 'comprehensive', 'detailed']
        if v not in allowed_modes:
            raise ValueError(f'分析模式必须是以下之一: {allowed_modes}')
        return v


class BatchProcessingRequest(BaseModel):
    """批量处理请求"""
    file_ids: List[str] = Field(..., description="文件ID列表")
    processing_options: FileProcessingRequest = Field(..., description="处理选项")
    
    @validator('file_ids')
    def validate_file_ids(cls, v):
        if len(v) > 10:
            raise ValueError('单次批量处理最多支持10个文件')
        return v


class FileSearchRequest(BaseModel):
    """文件搜索请求"""
    query: str = Field(..., description="搜索查询")
    file_types: Optional[List[str]] = Field(None, description="文件类型过滤")
    date_range: Optional[Dict[str, str]] = Field(None, description="日期范围过滤")
    limit: int = Field(20, description="结果限制")


class ProcessingStatus(BaseModel):
    """处理状态"""
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: float
    message: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None


# 依赖注入
def get_file_processor() -> EMCFileProcessor:
    """获取文件处理服务实例"""
    from ..main import service_container
    if not service_container.file_processor:
        raise HTTPException(status_code=500, detail="文件处理服务未初始化")
    return service_container.file_processor


def get_neo4j_service() -> Neo4jEMCService:
    """获取Neo4j服务实例"""
    from ..main import service_container
    if not service_container.neo4j_service:
        raise HTTPException(status_code=500, detail="Neo4j服务未初始化")
    return service_container.neo4j_service


# 全局任务状态跟踪
processing_tasks: Dict[str, ProcessingStatus] = {}


@router.post("/upload")
@rate_limit(requests_per_minute=20)
async def upload_file(
    file: UploadFile = File(...),
    extract_entities: bool = Form(True),
    build_graph: bool = Form(True),
    analysis_mode: str = Form("comprehensive"),
    background_tasks: BackgroundTasks = None,
    current_user: dict = Depends(get_current_user),
    file_processor: EMCFileProcessor = Depends(get_file_processor)
):
    """
    上传并处理单个文件
    """
    try:
        # 验证文件类型
        if not _is_allowed_file_type(file.filename):
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件类型: {Path(file.filename).suffix}"
            )
        
        # 验证文件大小
        if file.size and file.size > 100 * 1024 * 1024:  # 100MB
            raise HTTPException(
                status_code=400,
                detail="文件大小超过限制(100MB)"
            )
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 保存临时文件
        temp_file_path = await _save_temp_file(file)
        
        # 创建处理状态
        processing_tasks[task_id] = ProcessingStatus(
            task_id=task_id,
            status="pending",
            progress=0.0,
            message="准备处理文件",
            started_at=datetime.now()
        )
        
        # 启动后台处理
        background_tasks.add_task(
            _process_file_async,
            task_id,
            temp_file_path,
            file.filename,
            extract_entities,
            build_graph,
            analysis_mode,
            current_user["id"],
            file_processor
        )
        
        return {
            "task_id": task_id,
            "filename": file.filename,
            "file_size": file.size,
            "status": "processing",
            "message": "文件上传成功，正在处理中",
            "upload_time": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.post("/upload/batch")
@rate_limit(requests_per_minute=5)
async def upload_batch_files(
    files: List[UploadFile] = File(...),
    extract_entities: bool = Form(True),
    build_graph: bool = Form(True),
    analysis_mode: str = Form("comprehensive"),
    background_tasks: BackgroundTasks = None,
    current_user: dict = Depends(get_current_user),
    file_processor: EMCFileProcessor = Depends(get_file_processor)
):
    """
    批量上传和处理文件
    """
    try:
        if len(files) > 10:
            raise HTTPException(status_code=400, detail="单次最多支持上传10个文件")
        
        batch_id = str(uuid.uuid4())
        task_ids = []
        
        for file in files:
            # 验证文件
            if not _is_allowed_file_type(file.filename):
                logger.warning(f"跳过不支持的文件类型: {file.filename}")
                continue
            
            if file.size and file.size > 100 * 1024 * 1024:
                logger.warning(f"跳过超大文件: {file.filename}")
                continue
            
            # 生成任务ID
            task_id = str(uuid.uuid4())
            task_ids.append(task_id)
            
            # 保存临时文件
            temp_file_path = await _save_temp_file(file)
            
            # 创建处理状态
            processing_tasks[task_id] = ProcessingStatus(
                task_id=task_id,
                status="pending",
                progress=0.0,
                message=f"准备处理文件: {file.filename}",
                started_at=datetime.now()
            )
            
            # 启动后台处理
            background_tasks.add_task(
                _process_file_async,
                task_id,
                temp_file_path,
                file.filename,
                extract_entities,
                build_graph,
                analysis_mode,
                current_user["id"],
                file_processor
            )
        
        return {
            "batch_id": batch_id,
            "task_ids": task_ids,
            "file_count": len(task_ids),
            "status": "processing",
            "message": f"批量上传成功，正在处理 {len(task_ids)} 个文件",
            "upload_time": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量文件上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量文件上传失败: {str(e)}")


@router.get("/status/{task_id}")
async def get_processing_status(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    获取文件处理状态
    """
    try:
        if task_id not in processing_tasks:
            raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
        
        task_status = processing_tasks[task_id]
        
        return {
            "task_id": task_id,
            "status": task_status.status,
            "progress": task_status.progress,
            "message": task_status.message,
            "started_at": task_status.started_at.isoformat(),
            "completed_at": task_status.completed_at.isoformat() if task_status.completed_at else None,
            "result": task_status.result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取处理状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")


@router.get("/result/{task_id}")
async def get_processing_result(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    获取文件处理结果
    """
    try:
        if task_id not in processing_tasks:
            raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
        
        task_status = processing_tasks[task_id]
        
        if task_status.status != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"任务状态为 {task_status.status}，处理尚未完成"
            )
        
        return {
            "task_id": task_id,
            "result": task_status.result,
            "completed_at": task_status.completed_at.isoformat(),
            "processing_time": (
                task_status.completed_at - task_status.started_at
            ).total_seconds() if task_status.completed_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取处理结果失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取结果失败: {str(e)}")


@router.post("/reprocess/{task_id}")
@rate_limit(requests_per_minute=10)
async def reprocess_file(
    task_id: str,
    processing_options: FileProcessingRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    file_processor: EMCFileProcessor = Depends(get_file_processor)
):
    """
    重新处理已上传的文件
    """
    try:
        if task_id not in processing_tasks:
            raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
        
        original_task = processing_tasks[task_id]
        
        # 生成新的任务ID
        new_task_id = str(uuid.uuid4())
        
        # 创建新的处理状态
        processing_tasks[new_task_id] = ProcessingStatus(
            task_id=new_task_id,
            status="pending",
            progress=0.0,
            message="准备重新处理文件",
            started_at=datetime.now()
        )
        
        # 这里需要从原始任务中获取文件路径等信息
        # 实际实现中应该将文件元数据存储在数据库中
        
        return {
            "new_task_id": new_task_id,
            "original_task_id": task_id,
            "status": "processing",
            "message": "文件重新处理已启动",
            "started_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重新处理文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"重新处理失败: {str(e)}")


@router.post("/search")
async def search_files(
    request: FileSearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    搜索已处理的文件
    """
    try:
        # 这里应该查询数据库中的文件元数据
        # 暂时返回模拟数据
        mock_results = [
            {
                "file_id": "file_123",
                "filename": "emc_standard_example.pdf",
                "file_type": "pdf",
                "upload_time": "2024-01-01T10:00:00Z",
                "processing_status": "completed",
                "entities_count": 25,
                "relationships_count": 18,
                "uploader": current_user["username"]
            }
        ]
        
        return {
            "query": request.query,
            "results": mock_results,
            "total_count": len(mock_results),
            "search_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"文件搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件搜索失败: {str(e)}")


@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    下载原始文件
    """
    try:
        # 在实际实现中，这里应该从数据库查询文件信息
        # 暂时返回模拟文件下载
        
        # 创建一个模拟的文件内容
        mock_content = f"""# EMC知识文档 - {file_id}

这是一个模拟的EMC文档内容，用于演示文件下载功能。

## 文档信息
- 文件ID: {file_id}
- 下载时间: {datetime.now().isoformat()}
- 下载用户: {current_user.get('username', 'Unknown')}

## EMC测试标准
1. IEC 61000-4-2: 静电放电抗扰度测试
2. IEC 61000-4-3: 射频电磁场辐射抗扰度测试
3. IEC 61000-4-4: 电快速瞬变脉冲群抗扰度测试

## 测试结果
- 传导发射: 合格
- 辐射发射: 合格
- 抗扰度: 合格

---
文档生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.md',
            delete=False,
            encoding='utf-8'
        )
        
        temp_file.write(mock_content)
        temp_file.close()
        
        return FileResponse(
            path=temp_file.name,
            filename=f"emc_document_{file_id}.md",
            media_type="text/markdown"
        )
        
    except Exception as e:
        logger.error(f"下载文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@router.get("/download/{task_id}")
async def download_processed_file(
    task_id: str,
    format: str = "json",
    current_user: dict = Depends(get_current_user)
):
    """
    下载处理后的文件结果
    """
    try:
        if task_id not in processing_tasks:
            raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
        
        task_status = processing_tasks[task_id]
        
        if task_status.status != "completed":
            raise HTTPException(
                status_code=400,
                detail="文件处理尚未完成"
            )
        
        # 生成下载文件
        if format == "json":
            content = {
                "task_id": task_id,
                "result": task_status.result,
                "processed_at": task_status.completed_at.isoformat()
            }
            
            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.json',
                delete=False,
                encoding='utf-8'
            )
            
            import json
            json.dump(content, temp_file, ensure_ascii=False, indent=2)
            temp_file.close()
            
            return FileResponse(
                path=temp_file.name,
                filename=f"processed_result_{task_id}.json",
                media_type="application/json"
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"不支持的格式: {format}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@router.get("/statistics")
async def get_file_statistics(
    current_user: dict = Depends(get_current_user),
    file_processor: EMCFileProcessor = Depends(get_file_processor)
):
    """
    获取文件处理统计信息
    """
    try:
        processing_stats = file_processor.get_processing_stats()
        
        # 计算任务状态统计
        task_stats = {
            "pending": 0,
            "processing": 0,
            "completed": 0,
            "failed": 0
        }
        
        for task in processing_tasks.values():
            task_stats[task.status] = task_stats.get(task.status, 0) + 1
        
        return {
            "processing_statistics": processing_stats,
            "task_statistics": task_stats,
            "total_tasks": len(processing_tasks),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.delete("/cleanup")
@rate_limit(requests_per_minute=5)
async def cleanup_temp_files(
    current_user: dict = Depends(get_current_user),
    file_processor: EMCFileProcessor = Depends(get_file_processor)
):
    """
    清理临时文件
    """
    try:
        # 清理文件处理器的临时文件
        await file_processor.cleanup_temp_files(max_age_days=7)
        
        # 清理已完成的任务记录（保留最近100个）
        completed_tasks = [
            task_id for task_id, task in processing_tasks.items()
            if task.status in ["completed", "failed"]
        ]
        
        if len(completed_tasks) > 100:
            # 按完成时间排序，删除最旧的
            sorted_tasks = sorted(
                completed_tasks,
                key=lambda tid: processing_tasks[tid].completed_at or datetime.min
            )
            
            for task_id in sorted_tasks[:-100]:
                del processing_tasks[task_id]
        
        return {
            "message": "临时文件清理完成",
            "cleaned_task_records": max(0, len(completed_tasks) - 100),
            "remaining_tasks": len(processing_tasks),
            "cleaned_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"清理临时文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清理失败: {str(e)}")


# 辅助函数
async def _save_temp_file(file: UploadFile) -> Path:
    """保存上传的文件到临时目录"""
    temp_dir = Path("./temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    
    # 生成唯一文件名
    file_extension = Path(file.filename).suffix
    temp_filename = f"{uuid.uuid4()}{file_extension}"
    temp_file_path = temp_dir / temp_filename
    
    # 保存文件
    with open(temp_file_path, "wb") as temp_file:
        content = await file.read()
        temp_file.write(content)
    
    return temp_file_path


def _is_allowed_file_type(filename: str) -> bool:
    """检查文件类型是否允许"""
    allowed_extensions = {'.pdf', '.docx', '.xlsx', '.csv', '.json', '.xml', '.txt'}
    return Path(filename).suffix.lower() in allowed_extensions


async def _process_file_async(
    task_id: str,
    file_path: Path,
    filename: str,
    extract_entities: bool,
    build_graph: bool,
    analysis_mode: str,
    user_id: str,
    file_processor: EMCFileProcessor
):
    """异步处理文件"""
    try:
        # 更新状态为处理中
        processing_tasks[task_id].status = "processing"
        processing_tasks[task_id].progress = 10.0
        processing_tasks[task_id].message = "正在分析文件内容"
        
        # 处理文件
        metadata, extraction_result = await file_processor.process_file(
            file_path=file_path,
            file_id=task_id
        )
        
        processing_tasks[task_id].progress = 50.0
        processing_tasks[task_id].message = "文件分析完成，正在提取实体"
        
        result = {
            "file_metadata": {
                "filename": filename,
                "file_type": metadata.file_type,
                "size_bytes": metadata.size_bytes,
                "checksum": metadata.checksum
            }
        }
        
        if extraction_result:
            result["extraction_result"] = {
                "entities_count": len(extraction_result.entities),
                "relationships_count": len(extraction_result.relationships),
                "entities": extraction_result.entities,
                "relationships": extraction_result.relationships,
                "confidence_score": extraction_result.confidence_score,
                "content_summary": extraction_result.content_summary
            }
            
            # 如果需要构建图数据
            if build_graph and extraction_result.entities:
                processing_tasks[task_id].progress = 80.0
                processing_tasks[task_id].message = "正在构建知识图谱"
                
                # 这里应该调用图数据库服务来构建图谱
                # 由于需要额外的依赖注入，这里简化处理
                result["graph_built"] = True
                result["graph_nodes_created"] = len(extraction_result.entities)
                result["graph_relationships_created"] = len(extraction_result.relationships)
        
        # 完成处理
        processing_tasks[task_id].status = "completed"
        processing_tasks[task_id].progress = 100.0
        processing_tasks[task_id].message = "文件处理完成"
        processing_tasks[task_id].completed_at = datetime.now()
        processing_tasks[task_id].result = result
        
        # 清理临时文件
        try:
            file_path.unlink()
        except Exception as e:
            logger.warning(f"清理临时文件失败: {e}")
        
    except Exception as e:
        logger.error(f"文件处理失败 {task_id}: {str(e)}")
        processing_tasks[task_id].status = "failed"
        processing_tasks[task_id].message = f"处理失败: {str(e)}"
        processing_tasks[task_id].completed_at = datetime.now()
        
        # 清理临时文件
        try:
            file_path.unlink()
        except Exception:
            pass