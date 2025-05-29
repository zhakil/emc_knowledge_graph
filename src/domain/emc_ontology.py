"""
EMC领域本体管理器
职责：EMC标准领域的语义知识管理
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
from dataclasses import dataclass
from enum import Enum

from ..core.graph_engine import GraphEngine, Triple

logger = logging.getLogger(__name__)

class EMCEntityType(Enum):
    """EMC实体类型枚举"""
    ORGANIZATION = "organization"
    STANDARD = "standard"
    REGULATION = "regulation"
    TEST_METHOD = "test_method"
    TEST_ENVIRONMENT = "test_environment"
    VEHICLE_TYPE = "vehicle_type"
    FREQUENCY_RANGE = "frequency_range"
    EQUIPMENT = "equipment"

class EMCRelationType(Enum):
    """EMC关系类型枚举"""
    DEVELOPS = "develops"
    INCLUDES = "includes"
    APPLIES_TO = "applies_to"
    USES = "uses"
    REQUIRES = "requires"
    REFERENCES = "references"
    COVERS = "covers"
    EXTENDS = "extends"
    SUPERSEDES = "supersedes"

@dataclass
class EMCEntity:
    """EMC实体标准结构"""
    id: str
    name: str
    entity_type: EMCEntityType
    description: str
    attributes: Dict[str, Any]
    version: str = "1.0"
    confidence: float = 1.0

@dataclass  
class EMCRelation:
    """EMC关系标准结构"""
    subject: str
    predicate: EMCRelationType
    object: str
    weight: float = 1.0
    confidence: float = 1.0
    source: str = "expert_knowledge"

class EMCOntologyManager:
    """
    EMC领域本体管理器
    
    负责EMC标准领域的本体管理，包括：
    - 实体定义和验证
    - 关系语义管理
    - 领域规则推理
    - 知识完整性检查
    """
    
    def __init__(self, schema_path: str = "config/emc_schema.yaml"):
        self.schema_path = Path(schema_path)
        self.schema = self._load_schema()
        self.entities: Dict[str, EMCEntity] = {}
        self.relations: List[EMCRelation] = []
        
        logger.info("EMC本体管理器初始化完成")
    
    def _load_schema(self) -> Dict[str, Any]:
        """加载EMC本体Schema"""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                schema = yaml.safe_load(f)
            logger.info(f"EMC Schema加载完成: {self.schema_path}")
            return schema
        except FileNotFoundError:
            logger.warning(f"Schema文件未找到: {self.schema_path}，使用默认配置")
            return self._get_default_schema()
    
    def _get_default_schema(self) -> Dict[str, Any]:
        """获取默认EMC Schema"""
        return {
            "entities": {
                "Organization": {
                    "required_fields": ["id", "name", "entity_type"],
                    "optional_fields": ["established", "region", "scope"],
                    "validation_rules": {
                        "id": {"pattern": r"^[A-Z]{2,10}$"},
                        "name": {"min_length": 3, "max_length": 100}
                    }
                },
                "Standard": {
                    "required_fields": ["id", "name", "entity_type", "version"],
                    "optional_fields": ["publication_year", "status", "frequency_range"],
                    "validation_rules": {
                        "id": {"pattern": r"^[A-Z]+\d*$"},
                        "version": {"pattern": r"^\d+\.\d+$"}
                    }
                }
            },
            "relations": {
                "develops": {"domain": "Organization", "range": "Standard"},
                "includes": {"domain": "Standard", "range": "TestMethod"},
                "applies_to": {"domain": "Standard", "range": "VehicleType"}
            }
        }
    
    def create_entity(self, entity_data: Dict[str, Any]) -> Optional[EMCEntity]:
        """
        创建EMC实体
        
        Args:
            entity_data: 实体数据字典
            
        Returns:
            创建的EMC实体对象
        """
        try:
            # 验证实体数据
            if not self._validate_entity(entity_data):
                return None
            
            entity = EMCEntity(
                id=entity_data['id'],
                name=entity_data['name'],
                entity_type=EMCEntityType(entity_data['entity_type']),
                description=entity_data.get('description', ''),
                attributes=entity_data.get('attributes', {}),
                version=entity_data.get('version', '1.0'),
                confidence=entity_data.get('confidence', 1.0)
            )
            
            # 存储实体
            self.entities[entity.id] = entity
            logger.debug(f"EMC实体创建成功: {entity.id}")
            
            return entity
            
        except Exception as e:
            logger.error(f"创建EMC实体失败: {e}")
            return None
    
    def create_relation(self, relation_data: Dict[str, Any]) -> Optional[EMCRelation]:
        """
        创建EMC关系
        
        Args:
            relation_data: 关系数据字典
            
        Returns:
            创建的EMC关系对象
        """
        try:
            # 验证关系数据
            if not self._validate_relation(relation_data):
                return None
            
            relation = EMCRelation(
                subject=relation_data['subject'],
                predicate=EMCRelationType(relation_data['predicate']),
                object=relation_data['object'],
                weight=relation_data.get('weight', 1.0),
                confidence=relation_data.get('confidence', 1.0),
                source=relation_data.get('source', 'expert_knowledge')
            )
            
            # 存储关系
            self.relations.append(relation)
            logger.debug(f"EMC关系创建成功: {relation.subject} -> {relation.object}")
            
            return relation
            
        except Exception as e:
            logger.error(f"创建EMC关系失败: {e}")
            return None
    
    def build_knowledge_graph(self, graph_engine: GraphEngine) -> bool:
        """
        构建知识图谱
        
        Args:
            graph_engine: 图引擎实例
            
        Returns:
            构建是否成功
        """
        try:
            # 转换实体为节点
            for entity in self.entities.values():
                graph_engine.graph.add_node(
                    entity.id,
                    name=entity.name,
                    entity_type=entity.entity_type.value,
                    description=entity.description,
                    **entity.attributes
                )
            
            # 转换关系为边  
            triples = []
            for relation in self.relations:
                triple = Triple(
                    subject=relation.subject,
                    predicate=relation.predicate.value,
                    object=relation.object,
                    weight=relation.weight,
                    metadata={
                        'confidence': relation.confidence,
                        'source': relation.source
                    }
                )
                triples.append(triple)
            
            # 批量添加三元组
            success_count = graph_engine.batch_add_triples(triples)
            
            logger.info(f"知识图谱构建完成: {success_count}/{len(triples)} 关系添加成功")
            return success_count == len(triples)
            
        except Exception as e:
            logger.error(f"知识图谱构建失败: {e}")
            return False
    
    def _validate_entity(self, entity_data: Dict[str, Any]) -> bool:
        """验证实体数据"""
        try:
            # 检查必需字段
            required_fields = ["id", "name", "entity_type"]
            for field in required_fields:
                if field not in entity_data:
                    logger.error(f"实体缺少必需字段: {field}")
                    return False
            
            # 验证实体类型
            entity_type = entity_data['entity_type']
            if not any(et.value == entity_type for et in EMCEntityType):
                logger.error(f"无效的实体类型: {entity_type}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"实体验证失败: {e}")
            return False
    
    def _validate_relation(self, relation_data: Dict[str, Any]) -> bool:
        """验证关系数据"""
        try:
            # 检查必需字段
            required_fields = ["subject", "predicate", "object"]
            for field in required_fields:
                if field not in relation_data:
                    logger.error(f"关系缺少必需字段: {field}")
                    return False
            
            # 验证关系类型
            predicate = relation_data['predicate']
            if not any(rt.value == predicate for rt in EMCRelationType):
                logger.error(f"无效的关系类型: {predicate}")
                return False
            
            # 验证实体存在性
            subject = relation_data['subject']
            object_entity = relation_data['object']
            
            if subject not in self.entities:
                logger.warning(f"主体实体不存在: {subject}")
            
            if object_entity not in self.entities:
                logger.warning(f"客体实体不存在: {object_entity}")
            
            return True
            
        except Exception as e:
            logger.error(f"关系验证失败: {e}")
            return False

    def load_emc_knowledge_base(self) -> bool:
        """加载EMC标准知识库"""
        try:
            # 加载EMC标准化组织
            self._load_organizations()
            
            # 加载EMC技术标准
            self._load_standards()
            
            # 加载测试方法
            self._load_test_methods()
            
            # 加载语义关系
            self._load_semantic_relations()
            
            logger.info(f"EMC知识库加载完成: {len(self.entities)} 实体, {len(self.relations)} 关系")
            return True
            
        except Exception as e:
            logger.error(f"EMC知识库加载失败: {e}")
            return False
    
    def _load_organizations(self):
        """加载标准化组织"""
        organizations = [
            {
                "id": "CISPR",
                "name": "CISPR - 国际特别无线电干扰委员会", 
                "entity_type": "organization",
                "description": "制定车辆及其组件发射测量标准的国际组织",
                "attributes": {
                    "full_name": "International Special Committee on Radio Interference",
                    "parent_org": "IEC",
                    "established": 1934,
                    "region": "Global"
                }
            },
            {
                "id": "ISO",
                "name": "ISO - 国际标准化组织",
                "entity_type": "organization", 
                "description": "TC22/SC32/WG3工作组负责制定车辆和组件抗扰度测试标准",
                "attributes": {
                    "full_name": "International Organization for Standardization",
                    "tc_committee": "TC22 - Road vehicles",
                    "region": "Global"
                }
            }
        ]
        
        for org_data in organizations:
            self.create_entity(org_data)
    
    def _load_standards(self):
        """加载技术标准"""
        standards = [
            {
                "id": "CISPR25",
                "name": "CISPR 25 - 车载接收机保护标准",
                "entity_type": "standard",
                "version": "5.0",
                "description": "用于保护车辆、船舶和设备上使用的接收机免受无线电干扰",
                "attributes": {
                    "publication_year": 2021,
                    "frequency_range": "150 kHz - 2.5 GHz",
                    "test_types": ["Conducted emissions", "Radiated emissions"]
                }
            }
        ]
        
        for std_data in standards:
            self.create_entity(std_data)
    
    def _load_test_methods(self):
        """加载测试方法"""
        test_methods = [
            {
                "id": "RadiatedEmissions",
                "name": "辐射发射测试",
                "entity_type": "test_method",
                "description": "测量车辆或组件向空间辐射的电磁能量",
                "attributes": {
                    "measurement_types": ["Broadband", "Narrowband"],
                    "detectors": ["Peak", "Quasi-peak", "Average"]
                }
            }
        ]
        
        for method_data in test_methods:
            self.create_entity(method_data)
    
    def _load_semantic_relations(self):
        """加载语义关系"""
        relations = [
            {
                "subject": "CISPR",
                "predicate": "develops", 
                "object": "CISPR25",
                "weight": 1.0,
                "confidence": 0.98
            }
        ]
        
        for rel_data in relations:
            self.create_relation(rel_data)