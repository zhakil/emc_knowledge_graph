"""
增强的EMC实体提取器
这个类扩展了原有的实体提取器，添加了KAG的知识提取能力
"""

import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from .entity_extractor import EMCEntityExtractor
from ..integrations.kag_adapter import create_emc_kag_adapter, EMCKAGAdapter
from ..ai_integration.deepseek_service import DeepSeekEMCService


class EnhancedEMCEntityExtractor(EMCEntityExtractor):
    """
    增强的EMC实体提取器
    这个类扩展了现有的实体提取器，添加了KAG的知识提取能力
    """
    
    def __init__(self, deepseek_service: Optional[Any] = None, kag_config_path: Optional[str] = None):
        # 初始化基础实体提取器
        super().__init__(deepseek_service)
        
        self.logger = logging.getLogger(__name__)
        
        # 初始化KAG适配器
        try:
            self.kag_adapter = create_emc_kag_adapter(kag_config_path)
            self.kag_available = self.kag_adapter.is_kag_available()
            
            if self.kag_available:
                self.logger.info("KAG适配器初始化成功")
            else:
                self.logger.warning("KAG不可用，将使用原有的提取方法")
                
        except Exception as e:
            self.logger.error(f"KAG适配器初始化失败: {e}")
            self.kag_adapter = None
            self.kag_available = False
    
    async def extract_from_file(
        self, 
        file_path: str, 
        file_type: Optional[str] = None,
        use_kag: bool = True,
        use_ai: bool = True,
        use_rules: bool = True
    ) -> Dict[str, Any]:
        """
        从文件中提取实体和关系
        这是新增的方法，支持多种文件格式
        """
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 确定文件类型
        if file_type is None:
            file_type = file_path_obj.suffix.lower().lstrip('.')
        
        self.logger.info(f"开始处理文件: {file_path} (类型: {file_type})")
        
        result = {
            "file_path": file_path,
            "file_type": file_type,
            "entities": [],
            "relationships": [],
            "chunks": [],
            "metadata": {
                "success": False,
                "extraction_methods": [],
                "total_entities": 0,
                "total_relationships": 0
            }
        }
        
        # 1. 尝试使用KAG进行文件级提取（针对PDF等复杂文档）
        if use_kag and self.kag_available and file_type == 'pdf':
            try:
                kag_result = await self.kag_adapter.extract_from_emc_pdf(
                    pdf_path=file_path,
                    use_kag=True,
                    fallback_to_deepseek=True
                )
                
                if kag_result["metadata"]["success"]:
                    result["entities"].extend(kag_result["entities"])
                    result["relationships"].extend(kag_result["relationships"])
                    result["chunks"] = kag_result["chunks"]
                    result["metadata"]["extraction_methods"].append(
                        kag_result["metadata"]["extraction_method"]
                    )
                    
                    self.logger.info(f"KAG提取成功: {len(kag_result['entities'])} 实体, {len(kag_result['relationships'])} 关系")
                
            except Exception as e:
                self.logger.error(f"KAG文件提取失败: {e}")
        
        # 2. 如果KAG没有成功或不适用，回退到文本级提取
        if not result["entities"] or use_ai or use_rules:
            try:
                # 提取文本内容
                text_content = await self._extract_text_from_file(file_path, file_type)
                
                if text_content:
                    # 使用原有的文本提取方法
                    text_entities = await self.extract_entities(
                        text_content=text_content,
                        document_id=file_path,
                        use_ai=use_ai,
                        use_rules=use_rules
                    )
                    
                    # 转换格式以保持一致性
                    converted_entities = self._convert_legacy_entities(text_entities)
                    result["entities"].extend(converted_entities)
                    
                    if not result["chunks"]:
                        result["chunks"] = [text_content]
                    
                    methods = []
                    if use_ai and self.deepseek_service:
                        methods.append("DeepSeek_Legacy")
                    if use_rules:
                        methods.append("Rules")
                    
                    result["metadata"]["extraction_methods"].extend(methods)
                    
                    self.logger.info(f"文本提取成功: {len(converted_entities)} 实体")
                
            except Exception as e:
                self.logger.error(f"文本提取失败: {e}")
        
        # 3. 统计和元数据
        result["metadata"]["total_entities"] = len(result["entities"])
        result["metadata"]["total_relationships"] = len(result["relationships"])
        result["metadata"]["success"] = result["metadata"]["total_entities"] > 0
        
        # 4. 去重处理
        result["entities"] = self._deduplicate_entities(result["entities"])
        result["relationships"] = self._deduplicate_relationships(result["relationships"])
        
        self.logger.info(
            f"文件处理完成: {result['metadata']['total_entities']} 实体, "
            f"{result['metadata']['total_relationships']} 关系, "
            f"方法: {result['metadata']['extraction_methods']}"
        )
        
        return result
    
    async def _extract_text_from_file(self, file_path: str, file_type: str) -> str:
        """从不同类型的文件中提取文本"""
        text_content = ""
        
        try:
            if file_type == 'pdf':
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
            
            elif file_type in ['txt', 'md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
            
            elif file_type in ['docx']:
                try:
                    from docx import Document
                    doc = Document(file_path)
                    for paragraph in doc.paragraphs:
                        text_content += paragraph.text + "\n"
                except ImportError:
                    self.logger.warning("python-docx未安装，无法处理DOCX文件")
            
            elif file_type in ['html', 'htm']:
                try:
                    from bs4 import BeautifulSoup
                    with open(file_path, 'r', encoding='utf-8') as f:
                        soup = BeautifulSoup(f.read(), 'html.parser')
                        text_content = soup.get_text()
                except ImportError:
                    self.logger.warning("beautifulsoup4未安装，无法处理HTML文件")
            
            else:
                self.logger.warning(f"不支持的文件类型: {file_type}")
        
        except Exception as e:
            self.logger.error(f"文本提取失败: {e}")
        
        return text_content.strip()
    
    def _convert_legacy_entities(self, legacy_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """将原有格式的实体转换为新格式"""
        converted_entities = []
        
        for entity in legacy_entities:
            try:
                entity_data = entity.get("data", {})
                converted_entity = {
                    "id": f"legacy_{len(converted_entities)}",
                    "name": entity_data.get("name", "Unknown"),
                    "type": entity.get("label", "Unknown"),
                    "properties": entity_data.get("properties", {}),
                    "confidence": 0.8,  # 原有方法的默认置信度
                    "extraction_method": "Legacy"
                }
                
                # 添加特定类型的属性
                for key, value in entity_data.items():
                    if key not in ["name", "properties"]:
                        converted_entity["properties"][key] = value
                
                converted_entities.append(converted_entity)
                
            except Exception as e:
                self.logger.warning(f"转换实体失败: {e}")
        
        return converted_entities
    
    def _deduplicate_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """实体去重"""
        seen = set()
        deduplicated = []
        
        for entity in entities:
            # 使用名称和类型作为唯一标识
            key = (entity.get("name", "").lower(), entity.get("type", ""))
            
            if key not in seen:
                seen.add(key)
                deduplicated.append(entity)
            else:
                # 如果重复，保留置信度更高的
                existing_idx = next(
                    i for i, e in enumerate(deduplicated) 
                    if (e.get("name", "").lower(), e.get("type", "")) == key
                )
                
                if entity.get("confidence", 0) > deduplicated[existing_idx].get("confidence", 0):
                    deduplicated[existing_idx] = entity
        
        return deduplicated
    
    def _deduplicate_relationships(self, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """关系去重"""
        seen = set()
        deduplicated = []
        
        for relationship in relationships:
            # 使用源、目标和类型作为唯一标识
            key = (
                relationship.get("source", "").lower(),
                relationship.get("target", "").lower(),
                relationship.get("type", "")
            )
            
            if key not in seen:
                seen.add(key)
                deduplicated.append(relationship)
        
        return deduplicated
    
    async def batch_extract_from_files(
        self, 
        file_paths: List[str],
        use_kag: bool = True,
        use_ai: bool = True,
        use_rules: bool = True,
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """
        批量处理多个文件
        """
        import asyncio
        
        # 限制并发数量
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_single_file(file_path: str) -> Dict[str, Any]:
            async with semaphore:
                try:
                    return await self.extract_from_file(
                        file_path=file_path,
                        use_kag=use_kag,
                        use_ai=use_ai,
                        use_rules=use_rules
                    )
                except Exception as e:
                    self.logger.error(f"处理文件失败 {file_path}: {e}")
                    return {
                        "file_path": file_path,
                        "entities": [],
                        "relationships": [],
                        "metadata": {"success": False, "error": str(e)}
                    }
        
        # 并发处理所有文件
        tasks = [process_single_file(file_path) for file_path in file_paths]
        results = await asyncio.gather(*tasks)
        
        # 统计信息
        total_entities = sum(len(result["entities"]) for result in results)
        total_relationships = sum(len(result["relationships"]) for result in results)
        successful_files = sum(1 for result in results if result["metadata"]["success"])
        
        self.logger.info(
            f"批量处理完成: {successful_files}/{len(file_paths)} 文件成功, "
            f"总计 {total_entities} 实体, {total_relationships} 关系"
        )
        
        return results
    
    async def extract_entities_enhanced(
        self,
        text_content: str,
        document_id: Optional[str] = None,
        use_kag: bool = False,  # 对于纯文本，KAG优势不明显
        use_ai: bool = True,
        use_rules: bool = True
    ) -> List[Dict[str, Any]]:
        """
        增强的文本实体提取方法
        保持向后兼容性的同时添加新功能
        """
        # 调用原有方法
        legacy_entities = await self.extract_entities(
            text_content=text_content,
            document_id=document_id,
            use_ai=use_ai,
            use_rules=use_rules
        )
        
        # 转换为新格式
        enhanced_entities = self._convert_legacy_entities(legacy_entities)
        
        return enhanced_entities
    
    async def health_check(self) -> Dict[str, Any]:
        """系统健康检查"""
        status = {
            "legacy_extractor": True,
            "deepseek_service": self.deepseek_service is not None,
            "kag_adapter": self.kag_available,
            "supported_formats": ["txt", "pdf", "docx", "html", "md"]
        }
        
        if self.kag_adapter:
            kag_status = await self.kag_adapter.health_check()
            status["kag_details"] = kag_status
        
        return status


# 工厂函数
def create_enhanced_entity_extractor(
    deepseek_service: Optional[Any] = None,
    kag_config_path: Optional[str] = None
) -> EnhancedEMCEntityExtractor:
    """创建增强实体提取器实例"""
    return EnhancedEMCEntityExtractor(
        deepseek_service=deepseek_service,
        kag_config_path=kag_config_path
    )


# 使用示例
if __name__ == "__main__":
    import asyncio
    import os
    
    async def test_enhanced_extractor():
        # 创建增强提取器
        extractor = create_enhanced_entity_extractor()
        
        # 健康检查
        health = await extractor.health_check()
        print("系统健康状态:")
        print(json.dumps(health, indent=2, ensure_ascii=False))
        
        # 测试文本提取
        sample_text = """
        本设备按照IEC 61000-4-2标准进行静电放电测试。
        测试频率范围为30MHz至1GHz。设备型号为EMC-TEST-001。
        """
        
        print("\n=== 文本提取测试 ===")
        entities = await extractor.extract_entities_enhanced(sample_text)
        for entity in entities:
            print(f"实体: {entity['name']} (类型: {entity['type']}, 方法: {entity['extraction_method']})")
        
        # 如果有PDF文件，测试文件提取
        # test_pdf = "test_emc_document.pdf"
        # if os.path.exists(test_pdf):
        #     print(f"\n=== PDF文件提取测试: {test_pdf} ===")
        #     result = await extractor.extract_from_file(test_pdf)
        #     print(f"提取结果: {result['metadata']}")
    
    # 运行测试
    asyncio.run(test_enhanced_extractor())