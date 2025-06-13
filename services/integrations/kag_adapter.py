"""
EMC项目的KAG适配器
这个类封装了KAG的复杂性，提供了适合EMC场景的简单接口
"""

import os
import json
import yaml
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

# KAG核心组件导入
try:
    from kag.builder.component.reader.pdf_reader import PDFReader
    from kag.builder.component.extractor.schema_constraint_extractor import SchemaConstraintExtractor
    from kag.solver.main_solver import MainSolver
    from kag.common.conf import KAG_CONFIG
    from kag.builder.component.chunk.chunk_runner import ChunkRunner
    KAG_AVAILABLE = True
except ImportError as e:
    logging.warning(f"KAG components not available: {e}")
    KAG_AVAILABLE = False

from ..ai_integration.deepseek_service import DeepSeekConfig, DeepSeekEMCService
from ..knowledge_graph.emc_ontology import (
    NODE_EMC_STANDARD, NODE_PRODUCT, NODE_COMPONENT, NODE_TEST,
    NODE_TEST_RESULT, NODE_FREQUENCY, NODE_FREQUENCY_RANGE,
    NODE_PHENOMENON, NODE_REGULATION, NODE_MITIGATION_MEASURE,
    NODE_DOCUMENT, NODE_ORGANIZATION, NODE_EQUIPMENT
)


class EMCKAGAdapter:
    """
    EMC项目的KAG适配器
    这个类封装了KAG的复杂性，提供了适合EMC场景的简单接口
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        if not KAG_AVAILABLE:
            self.logger.warning("KAG不可用，将使用降级模式")
            self.kag_enabled = False
            return
            
        self.kag_enabled = True
        
        # 加载配置
        self.config = self._load_emc_kag_config(config_path)
        
        # 初始化KAG组件
        try:
            self.pdf_reader = PDFReader(self.config) if self.config else None
            self.extractor = SchemaConstraintExtractor(self.config) if self.config else None
            self.solver = MainSolver(self.config) if self.config else None
            self.chunk_runner = ChunkRunner(self.config) if self.config else None
        except Exception as e:
            self.logger.error(f"KAG组件初始化失败: {e}")
            self.kag_enabled = False
            return
        
        # 加载EMC领域的特定配置
        self.emc_schema = self._load_emc_schema()
        
        # 初始化DeepSeek服务作为后备
        self.deepseek_service = self._init_deepseek_service()
    
    def _load_emc_kag_config(self, config_path: Optional[str]) -> Optional[Any]:
        """
        加载适合EMC项目的KAG配置
        """
        try:
            if config_path is None:
                config_path = os.path.join(
                    os.path.dirname(__file__), 
                    "..", "..", "config", "kag_config.yaml"
                )
            
            if not os.path.exists(config_path):
                self.logger.warning(f"KAG配置文件不存在: {config_path}")
                return None
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f)
            
            # 环境变量替换
            config_dict = self._substitute_env_vars(config_dict)
            
            # 转换为KAG配置对象
            return KAG_CONFIG.from_dict(config_dict)
            
        except Exception as e:
            self.logger.error(f"加载KAG配置失败: {e}")
            return None
    
    def _substitute_env_vars(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """递归替换配置中的环境变量"""
        def substitute_value(value):
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                env_var = value[2:-1]
                return os.getenv(env_var, value)
            elif isinstance(value, dict):
                return {k: substitute_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [substitute_value(item) for item in value]
            else:
                return value
        
        return substitute_value(config_dict)
    
    def _load_emc_schema(self) -> Dict[str, Any]:
        """
        加载EMC领域的知识图谱模式
        """
        return {
            "node_types": [
                NODE_EMC_STANDARD, NODE_EQUIPMENT, NODE_TEST, NODE_PRODUCT,
                NODE_FREQUENCY, NODE_FREQUENCY_RANGE, NODE_TEST_RESULT,
                NODE_DOCUMENT, NODE_ORGANIZATION, NODE_COMPONENT,
                NODE_PHENOMENON, NODE_REGULATION, NODE_MITIGATION_MEASURE
            ],
            "relationship_types": [
                "COMPLIES_WITH", "TESTED_BY", "REQUIRES", "PRODUCES",
                "APPLIES_TO", "RELATED_TO", "DEFINES", "USES"
            ],
            "domain_context": "EMC",
            "language": "zh"
        }
    
    def _init_deepseek_service(self) -> Optional[DeepSeekEMCService]:
        """初始化DeepSeek服务作为后备"""
        try:
            api_key = os.getenv("EMC_DEEPSEEK_API_KEY")
            if not api_key:
                self.logger.warning("DeepSeek API密钥未配置")
                return None
            
            config = DeepSeekConfig(
                api_key=api_key,
                base_url="https://api.deepseek.com/v1",
                model="deepseek-chat",
                max_tokens=4000,
                temperature=0.1
            )
            
            return DeepSeekEMCService(config)
            
        except Exception as e:
            self.logger.error(f"DeepSeek服务初始化失败: {e}")
            return None
    
    async def extract_from_emc_pdf(
        self, 
        pdf_path: str,
        use_kag: bool = True,
        fallback_to_deepseek: bool = True
    ) -> Dict[str, Any]:
        """
        从EMC PDF文档中提取知识
        这个方法将KAG的通用PDF处理能力适配为EMC特定的处理流程
        """
        result = {
            "entities": [],
            "relationships": [],
            "chunks": [],
            "metadata": {
                "source": pdf_path,
                "extraction_method": "unknown",
                "success": False
            }
        }
        
        # 尝试使用KAG进行提取
        if use_kag and self.kag_enabled and self.pdf_reader and self.extractor:
            try:
                kag_result = await self._extract_with_kag(pdf_path)
                if kag_result["metadata"]["success"]:
                    return kag_result
                else:
                    self.logger.warning("KAG提取失败，尝试降级到DeepSeek")
            except Exception as e:
                self.logger.error(f"KAG提取出错: {e}")
        
        # 降级到DeepSeek服务
        if fallback_to_deepseek and self.deepseek_service:
            try:
                return await self._extract_with_deepseek(pdf_path)
            except Exception as e:
                self.logger.error(f"DeepSeek提取失败: {e}")
        
        # 如果都失败了，返回空结果
        self.logger.error(f"所有提取方法都失败了: {pdf_path}")
        return result
    
    async def _extract_with_kag(self, pdf_path: str) -> Dict[str, Any]:
        """使用KAG进行提取"""
        result = {
            "entities": [],
            "relationships": [],
            "chunks": [],
            "metadata": {
                "source": pdf_path,
                "extraction_method": "KAG",
                "success": False
            }
        }
        
        try:
            # 1. 读取PDF内容
            content = self.pdf_reader.read(pdf_path)
            
            # 2. 分块处理
            if self.chunk_runner:
                chunks = self.chunk_runner.run(content)
                result["chunks"] = [chunk.content for chunk in chunks]
            else:
                chunks = [content]  # 如果没有分块器，使用整个文档
                result["chunks"] = [content]
            
            # 3. 使用EMC特定的模式进行知识提取
            all_entities = []
            all_relationships = []
            
            for chunk in chunks:
                extracted_knowledge = self.extractor.extract(
                    chunk, 
                    schema=self.emc_schema,
                    domain_context="EMC"
                )
                
                # 处理提取的实体
                if "entities" in extracted_knowledge:
                    entities = self._process_kag_entities(extracted_knowledge["entities"])
                    all_entities.extend(entities)
                
                # 处理提取的关系
                if "relationships" in extracted_knowledge:
                    relationships = self._process_kag_relationships(extracted_knowledge["relationships"])
                    all_relationships.extend(relationships)
            
            result["entities"] = all_entities
            result["relationships"] = all_relationships
            result["metadata"]["success"] = True
            
            self.logger.info(f"KAG成功提取 {len(all_entities)} 个实体和 {len(all_relationships)} 个关系")
            
        except Exception as e:
            self.logger.error(f"KAG提取过程出错: {e}")
            result["metadata"]["error"] = str(e)
        
        return result
    
    async def _extract_with_deepseek(self, pdf_path: str) -> Dict[str, Any]:
        """使用DeepSeek进行提取"""
        result = {
            "entities": [],
            "relationships": [],
            "chunks": [],
            "metadata": {
                "source": pdf_path,
                "extraction_method": "DeepSeek",
                "success": False
            }
        }
        
        try:
            # 读取PDF内容（简单方式）
            import pdfplumber
            text_content = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text_content += page.extract_text() + "\n"
            
            # 使用DeepSeek提取实体和关系
            deepseek_result = await self.deepseek_service.extract_entities_from_text(
                text_content=text_content
            )
            
            # 解析DeepSeek的JSON响应
            content = deepseek_result.get("content", "")
            try:
                parsed_result = json.loads(content)
                
                # 转换为EMC格式
                result["entities"] = self._convert_deepseek_entities(
                    parsed_result.get("entities", [])
                )
                result["relationships"] = self._convert_deepseek_relationships(
                    parsed_result.get("relationships", [])
                )
                result["chunks"] = [text_content]
                result["metadata"]["success"] = True
                
                self.logger.info(f"DeepSeek成功提取 {len(result['entities'])} 个实体和 {len(result['relationships'])} 个关系")
                
            except json.JSONDecodeError as e:
                self.logger.error(f"DeepSeek响应JSON解析失败: {e}")
                result["metadata"]["error"] = f"JSON解析失败: {e}"
                
        except Exception as e:
            self.logger.error(f"DeepSeek提取过程出错: {e}")
            result["metadata"]["error"] = str(e)
        
        return result
    
    def _process_kag_entities(self, kag_entities: List[Any]) -> List[Dict[str, Any]]:
        """处理KAG提取的实体，转换为EMC格式"""
        processed_entities = []
        
        for entity in kag_entities:
            try:
                processed_entity = {
                    "id": getattr(entity, "id", None) or f"entity_{len(processed_entities)}",
                    "name": getattr(entity, "name", "Unknown"),
                    "type": getattr(entity, "type", "Unknown"),
                    "properties": getattr(entity, "properties", {}),
                    "confidence": getattr(entity, "confidence", 0.8),
                    "extraction_method": "KAG"
                }
                processed_entities.append(processed_entity)
            except Exception as e:
                self.logger.warning(f"处理KAG实体失败: {e}")
        
        return processed_entities
    
    def _process_kag_relationships(self, kag_relationships: List[Any]) -> List[Dict[str, Any]]:
        """处理KAG提取的关系，转换为EMC格式"""
        processed_relationships = []
        
        for relationship in kag_relationships:
            try:
                processed_relationship = {
                    "id": getattr(relationship, "id", None) or f"rel_{len(processed_relationships)}",
                    "source": getattr(relationship, "source", "Unknown"),
                    "target": getattr(relationship, "target", "Unknown"),
                    "type": getattr(relationship, "type", "RELATED_TO"),
                    "properties": getattr(relationship, "properties", {}),
                    "confidence": getattr(relationship, "confidence", 0.8),
                    "extraction_method": "KAG"
                }
                processed_relationships.append(processed_relationship)
            except Exception as e:
                self.logger.warning(f"处理KAG关系失败: {e}")
        
        return processed_relationships
    
    def _convert_deepseek_entities(self, deepseek_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """转换DeepSeek实体为EMC格式"""
        converted_entities = []
        
        for entity in deepseek_entities:
            try:
                converted_entity = {
                    "id": f"deepseek_entity_{len(converted_entities)}",
                    "name": entity.get("name", "Unknown"),
                    "type": entity.get("type", "Unknown"),
                    "properties": entity.get("properties", {}),
                    "confidence": 0.7,  # DeepSeek默认置信度
                    "extraction_method": "DeepSeek"
                }
                converted_entities.append(converted_entity)
            except Exception as e:
                self.logger.warning(f"转换DeepSeek实体失败: {e}")
        
        return converted_entities
    
    def _convert_deepseek_relationships(self, deepseek_relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """转换DeepSeek关系为EMC格式"""
        converted_relationships = []
        
        for relationship in deepseek_relationships:
            try:
                converted_relationship = {
                    "id": f"deepseek_rel_{len(converted_relationships)}",
                    "source": relationship.get("source", "Unknown"),
                    "target": relationship.get("target", "Unknown"),
                    "type": relationship.get("type", "RELATED_TO"),
                    "properties": relationship.get("properties", {}),
                    "confidence": 0.7,  # DeepSeek默认置信度
                    "extraction_method": "DeepSeek"
                }
                converted_relationships.append(converted_relationship)
            except Exception as e:
                self.logger.warning(f"转换DeepSeek关系失败: {e}")
        
        return converted_relationships
    
    async def query_knowledge_graph(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        使用KAG的推理能力查询知识图谱
        """
        if not self.kag_enabled or not self.solver:
            self.logger.warning("KAG推理器不可用")
            return {"result": "KAG推理器不可用", "success": False}
        
        try:
            # 使用KAG的MainSolver进行推理查询
            result = await self.solver.solve(
                query=query,
                context=context or {},
                domain="EMC"
            )
            
            return {
                "result": result,
                "success": True,
                "method": "KAG_Solver"
            }
            
        except Exception as e:
            self.logger.error(f"KAG推理查询失败: {e}")
            return {"result": f"查询失败: {e}", "success": False}
    
    def is_kag_available(self) -> bool:
        """检查KAG是否可用"""
        return self.kag_enabled
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的文件格式"""
        formats = ["pdf"]  # 基础支持
        
        if self.kag_enabled:
            # KAG可能支持更多格式
            formats.extend(["docx", "txt", "html"])
        
        return formats
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        status = {
            "kag_available": self.kag_enabled,
            "deepseek_available": self.deepseek_service is not None,
            "config_loaded": self.config is not None,
            "components": {
                "pdf_reader": self.pdf_reader is not None if self.kag_enabled else False,
                "extractor": self.extractor is not None if self.kag_enabled else False,
                "solver": self.solver is not None if self.kag_enabled else False
            }
        }
        
        return status


# 工厂函数
def create_emc_kag_adapter(config_path: Optional[str] = None) -> EMCKAGAdapter:
    """创建EMC KAG适配器实例"""
    return EMCKAGAdapter(config_path=config_path)


# 使用示例
if __name__ == "__main__":
    import asyncio
    
    async def test_adapter():
        adapter = create_emc_kag_adapter()
        
        # 健康检查
        health = await adapter.health_check()
        print("健康状态:", json.dumps(health, indent=2, ensure_ascii=False))
        
        # 如果有PDF文件，可以测试提取
        # result = await adapter.extract_from_emc_pdf("test.pdf")
        # print("提取结果:", json.dumps(result, indent=2, ensure_ascii=False))
    
    asyncio.run(test_adapter())