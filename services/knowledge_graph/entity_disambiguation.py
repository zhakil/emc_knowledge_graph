"""
EMC知识图谱实体消歧模块
使用词向量相似度进行同名实体消歧
"""

from typing import List, Dict, Tuple, Optional
import hashlib
import time
from dataclasses import dataclass
from gensim.models import Word2Vec, KeyedVectors
import spacy
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class EntityCandidate:
    """实体候选项"""
    text: str
    context: str
    original_index: int
    confidence: float = 0.0

@dataclass
class DisambiguatedEntity:
    """消歧后的实体"""
    unique_id: str
    canonical_form: str
    variants: List[str]
    confidence: float
    original_indices: List[int]

class EntityDisambiguator:
    """基于词向量的实体消歧器"""
    
    def __init__(self, model_path: Optional[str] = None, spacy_model: str = "en_core_web_sm"):
        """
        初始化消歧器
        
        Args:
            model_path: 预训练词向量模型路径（可选）
            spacy_model: spaCy模型名称
        """
        self.nlp = spacy.load(spacy_model)
        self.word_vectors = None
        self.similarity_threshold = 0.7  # 相似度阈值
        
        if model_path:
            self.load_pretrained_vectors(model_path)
    
    def load_pretrained_vectors(self, model_path: str):
        """加载预训练词向量模型"""
        try:
            self.word_vectors = KeyedVectors.load_word2vec_format(model_path, binary=True)
        except Exception as e:
            print(f"Warning: Failed to load pretrained vectors: {e}")
            self.word_vectors = None
    
    def extract_context_features(self, entity: str, context: str) -> np.ndarray:
        """
        提取实体上下文特征向量
        
        Args:
            entity: 实体文本
            context: 上下文文本
            
        Returns:
            特征向量
        """
        # 使用spaCy处理文本
        doc = self.nlp(f"{entity} {context}")
        
        # 收集词向量
        vectors = []
        for token in doc:
            if token.has_vector and not token.is_stop and not token.is_punct:
                vectors.append(token.vector)
        
        if not vectors:
            # 如果没有找到向量，返回零向量
            return np.zeros(self.nlp.vocab.vectors_length)
        
        # 返回平均向量
        return np.mean(vectors, axis=0)
    
    def calculate_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        计算两个向量的余弦相似度
        
        Args:
            vec1, vec2: 特征向量
            
        Returns:
            相似度分数 [0, 1]
        """
        # 处理零向量情况
        norm1, norm2 = np.linalg.norm(vec1), np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # 计算余弦相似度
        similarity = np.dot(vec1, vec2) / (norm1 * norm2)
        return max(0.0, similarity)  # 确保非负
    
    def generate_unique_id(self, canonical_form: str) -> str:
        """
        为消歧后的实体生成唯一ID
        
        Args:
            canonical_form: 规范化实体形式
            
        Returns:
            唯一ID字符串
        """
        # 使用MD5哈希生成ID
        hash_input = canonical_form.lower().strip()
        return f"entity_{hashlib.md5(hash_input.encode()).hexdigest()[:12]}"
    
    def disambiguate_entities(self, entities: List[Tuple[str, str]]) -> List[DisambiguatedEntity]:
        """
        对实体列表进行消歧
        
        Args:
            entities: (实体文本, 上下文) 元组列表
            
        Returns:
            消歧后的实体列表
        """
        start_time = time.time()
        
        # 提取特征向量（并行处理）
        candidates = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_idx = {
                executor.submit(self._process_entity, idx, entity, context): idx
                for idx, (entity, context) in enumerate(entities)
            }
            
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    candidate = future.result()
                    candidates.append(candidate)
                except Exception as e:
                    print(f"Error processing entity {idx}: {e}")
        
        # 按原始索引排序
        candidates.sort(key=lambda x: x.original_index)
        
        # 执行聚类消歧
        disambiguated = self._cluster_entities(candidates)
        
        elapsed = time.time() - start_time
        print(f"Disambiguated {len(entities)} entities in {elapsed:.2f}s")
        
        return disambiguated
    
    def _process_entity(self, idx: int, entity: str, context: str) -> EntityCandidate:
        """处理单个实体（用于并行处理）"""
        return EntityCandidate(
            text=entity,
            context=context,
            original_index=idx
        )
    
    def _cluster_entities(self, candidates: List[EntityCandidate]) -> List[DisambiguatedEntity]:
        """
        使用相似度聚类对实体进行分组
        
        Args:
            candidates: 实体候选列表
            
        Returns:
            聚类后的消歧实体
        """
        # 计算特征向量
        vectors = []
        for candidate in candidates:
            vector = self.extract_context_features(candidate.text, candidate.context)
            vectors.append(vector)
        
        # 简单的层次聚类
        clusters = []
        used = set()
        
        for i, candidate in enumerate(candidates):
            if i in used:
                continue
                
            # 创建新聚类
            cluster_members = [i]
            cluster_texts = [candidate.text]
            cluster_indices = [candidate.original_index]
            
            # 寻找相似实体
            for j, other_candidate in enumerate(candidates[i+1:], i+1):
                if j in used:
                    continue
                    
                similarity = self.calculate_similarity(vectors[i], vectors[j])
                if similarity >= self.similarity_threshold:
                    cluster_members.append(j)
                    cluster_texts.append(other_candidate.text)
                    cluster_indices.append(other_candidate.original_index)
                    used.add(j)
            
            used.add(i)
            
            # 生成消歧实体
            canonical_form = max(cluster_texts, key=len)  # 选择最长的作为规范形式
            unique_id = self.generate_unique_id(canonical_form)
            
            disambiguated = DisambiguatedEntity(
                unique_id=unique_id,
                canonical_form=canonical_form,
                variants=list(set(cluster_texts)),
                confidence=1.0 / len(cluster_members),  # 简单的置信度计算
                original_indices=cluster_indices
            )
            
            clusters.append(disambiguated)
        
        return clusters

# 使用示例
def example_usage():
    """示例用法"""
    disambiguator = EntityDisambiguator()
    
    # 测试数据：同名但不同含义的实体
    test_entities = [
        ("Apple", "technology company smartphone iPhone"),
        ("Apple", "fruit red green nutrition healthy"),
        ("Java", "programming language object oriented"),
        ("Java", "island Indonesia coffee"),
    ]
    
    result = disambiguator.disambiguate_entities(test_entities)
    
    for entity in result:
        print(f"ID: {entity.unique_id}")
        print(f"Canonical: {entity.canonical_form}")
        print(f"Variants: {entity.variants}")
        print(f"Confidence: {entity.confidence:.3f}")
        print("---")

if __name__ == "__main__":
    example_usage()