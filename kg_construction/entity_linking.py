"""
EMC知识图谱实体链接模块
集成基于词向量的实体消歧功能
"""

from typing import List, Dict, Tuple, Optional, Any
import logging
from dataclasses import dataclass, field
from pathlib import Path
import sys

# 导入我们刚创建的消歧模块
sys.path.append(str(Path(__file__).parent.parent))
from services.knowledge_graph.entity_disambiguation import EntityDisambiguator, DisambiguatedEntity

logger = logging.getLogger(__name__)

@dataclass
class LinkedEntity:
    """链接后的实体，包含消歧信息"""
    unique_id: str
    canonical_form: str
    entity_type: str
    confidence: float
    variants: List[str] = field(default_factory=list)
    original_mentions: List[Dict[str, Any]] = field(default_factory=list)
    context_features: Optional[Dict[str, Any]] = None

class EntityLinker:
    """
    实体链接器 - 整合实体识别、消歧和标准化
    
    这个类的设计遵循了几个重要的理论原则：
    1. 保持接口稳定性：现有的link_entities方法签名不变
    2. 内部增强：在不破坏外部调用的前提下添加消歧功能
    3. 性能优化：使用批处理和并行计算提高效率
    """
    
    def __init__(self, 
                 spacy_model: str = "en_core_web_sm",
                 vector_model_path: Optional[str] = None,
                 similarity_threshold: float = 0.7):
        """
        初始化实体链接器
        
        参数说明：
        - spacy_model: spaCy模型名称，用于基础NLP处理
        - vector_model_path: 预训练词向量路径，可选
        - similarity_threshold: 实体相似度阈值，控制消歧的严格程度
        """
        self.disambiguator = EntityDisambiguator(
            model_path=vector_model_path,
            spacy_model=spacy_model
        )
        self.disambiguator.similarity_threshold = similarity_threshold
        
        # 缓存已处理的实体，提高重复处理效率
        self._entity_cache: Dict[str, LinkedEntity] = {}
        
        logger.info(f"EntityLinker initialized with model: {spacy_model}")
    
    def link_entities(self, 
                     entities: List[str], 
                     contexts: Optional[List[str]] = None,
                     entity_types: Optional[List[str]] = None) -> List[LinkedEntity]:
        """
        主要的实体链接方法 - 保持原有接口签名
        
        这个方法是整个实体链接流程的入口点。它接收原始实体列表，
        返回经过消歧和标准化的实体对象。
        
        Args:
            entities: 原始实体文本列表
            contexts: 每个实体的上下文文本（可选）
            entity_types: 实体类型标注（可选）
            
        Returns:
            链接和消歧后的实体列表
        """
        if not entities:
            return []
        
        # 准备上下文信息 - 如果没有提供上下文，使用空字符串
        if contexts is None:
            contexts = [""] * len(entities)
        elif len(contexts) != len(entities):
            logger.warning(f"Context length ({len(contexts)}) != entity length ({len(entities)})")
            contexts = contexts[:len(entities)] + [""] * (len(entities) - len(contexts))
        
        # 准备实体类型信息
        if entity_types is None:
            entity_types = ["UNKNOWN"] * len(entities)
        elif len(entity_types) != len(entities):
            entity_types = entity_types[:len(entities)] + ["UNKNOWN"] * (len(entities) - len(entity_types))
        
        logger.info(f"Starting entity linking for {len(entities)} entities")
        
        # 第一步：执行实体消歧
        entity_context_pairs = [(entity, context) for entity, context in zip(entities, contexts)]
        disambiguated_entities = self.disambiguator.disambiguate_entities(entity_context_pairs)
        
        # 第二步：将消歧结果转换为LinkedEntity对象
        linked_entities = self._convert_to_linked_entities(
            disambiguated_entities, entities, contexts, entity_types
        )
        
        # 第三步：更新缓存
        self._update_cache(linked_entities)
        
        logger.info(f"Entity linking completed. {len(linked_entities)} unique entities identified")
        return linked_entities
    
    def _convert_to_linked_entities(self, 
                                   disambiguated: List[DisambiguatedEntity],
                                   original_entities: List[str],
                                   contexts: List[str],
                                   entity_types: List[str]) -> List[LinkedEntity]:
        """
        将消歧结果转换为LinkedEntity对象
        
        这个转换过程很重要，因为它建立了原始实体提及和
        消歧后标准实体之间的映射关系。
        """
        linked_entities = []
        
        for disambig_entity in disambiguated:
            # 收集原始提及信息
            original_mentions = []
            for idx in disambig_entity.original_indices:
                if idx < len(original_entities):
                    mention = {
                        "text": original_entities[idx],
                        "context": contexts[idx],
                        "type": entity_types[idx],
                        "position": idx
                    }
                    original_mentions.append(mention)
            
            # 确定实体类型 - 使用最常见的类型
            type_counts = {}
            for mention in original_mentions:
                entity_type = mention["type"]
                type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
            
            primary_type = max(type_counts.keys(), key=lambda k: type_counts[k]) if type_counts else "UNKNOWN"
            
            # 创建LinkedEntity对象
            linked_entity = LinkedEntity(
                unique_id=disambig_entity.unique_id,
                canonical_form=disambig_entity.canonical_form,
                entity_type=primary_type,
                confidence=disambig_entity.confidence,
                variants=disambig_entity.variants,
                original_mentions=original_mentions
            )
            
            linked_entities.append(linked_entity)
        
        return linked_entities
    
    def _update_cache(self, linked_entities: List[LinkedEntity]):
        """更新实体缓存，提高后续处理效率"""
        for entity in linked_entities:
            # 为每个变体和规范形式都建立缓存条目
            cache_key = entity.canonical_form.lower().strip()
            self._entity_cache[cache_key] = entity
            
            for variant in entity.variants:
                variant_key = variant.lower().strip()
                self._entity_cache[variant_key] = entity
    
    def get_entity_by_text(self, text: str) -> Optional[LinkedEntity]:
        """
        根据文本查找已链接的实体
        
        这是一个便利方法，允许快速查找之前处理过的实体。
        """
        cache_key = text.lower().strip()
        return self._entity_cache.get(cache_key)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取链接器的统计信息
        
        这对于监控和调试实体链接的性能很有用。
        """
        unique_entities = len(set(entity.unique_id for entity in self._entity_cache.values()))
        
        return {
            "cached_entities": len(self._entity_cache),
            "unique_entities": unique_entities,
            "disambiguation_threshold": self.disambiguator.similarity_threshold,
            "spacy_model": self.disambiguator.nlp.meta.get("name", "unknown")
        }

# 为了保持向后兼容性，提供一个简化的函数接口
def link_entities_simple(entities: List[str], 
                        contexts: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    简化的实体链接函数，返回字典格式结果
    
    这个函数保持了最简单的接口，适合那些不需要完整
    LinkedEntity对象功能的场景。
    """
    linker = EntityLinker()
    linked = linker.link_entities(entities, contexts)
    
    # 转换为字典格式
    result = []
    for entity in linked:
        entity_dict = {
            "unique_id": entity.unique_id,
            "canonical_form": entity.canonical_form,
            "entity_type": entity.entity_type,
            "confidence": entity.confidence,
            "variants": entity.variants,
            "mention_count": len(entity.original_mentions)
        }
        result.append(entity_dict)
    
    return result

# 使用示例和测试
def example_usage():
    """演示实体链接的使用方法"""
    # 创建链接器实例
    linker = EntityLinker(similarity_threshold=0.7)
    
    # 测试数据：包含同名但不同含义的实体
    test_entities = [
        "IEC 61000-4-2",  # EMC标准
        "IEC 61000-4-2",  # 重复的标准名称
        "Spectrum Analyzer", # 测试设备
        "Spectrum analyzer", # 大小写不同的设备名
        "EMI Filter",     # EMC组件
        "EMI filter",     # 重复的组件名
    ]
    
    test_contexts = [
        "electrostatic discharge immunity test standard",
        "ESD test requirements for electronic equipment",
        "RF measurement equipment for emissions testing",
        "radio frequency analyzer for EMC testing",
        "component for reducing electromagnetic interference",
        "passive filter for EMI suppression"
    ]
    
    # 执行实体链接
    results = linker.link_entities(test_entities, test_contexts)
    
    # 输出结果
    print(f"处理了 {len(test_entities)} 个实体，识别出 {len(results)} 个唯一实体")
    for entity in results:
        print(f"\n唯一ID: {entity.unique_id}")
        print(f"标准形式: {entity.canonical_form}")
        print(f"变体: {entity.variants}")
        print(f"提及次数: {len(entity.original_mentions)}")
        print(f"置信度: {entity.confidence:.3f}")

if __name__ == "__main__":
    example_usage()