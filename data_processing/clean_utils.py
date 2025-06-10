"""
EMC知识图谱数据清理工具
为实体消歧提供高质量的输入数据
"""

import re
import string
from typing import List, Dict, Tuple, Optional, Set
import unicodedata
import logging

logger = logging.getLogger(__name__)

class EMCDataCleaner:
    """
    EMC领域专用的数据清理器
    
    这个类专门处理EMC文档中常见的文本问题，比如：
    - 标准编号的格式标准化
    - 技术术语的统一化  
    - 特殊符号和编码问题的处理
    """
    
    def __init__(self):
        """初始化清理器，设置EMC领域特定的清理规则"""
        # EMC标准格式的正则表达式
        self.standard_patterns = {
            'iec': re.compile(r'IEC\s*(\d+[-/]\d+(?:[-/]\d+)*)', re.IGNORECASE),
            'cispr': re.compile(r'CISPR\s*(\d+)', re.IGNORECASE),
            'fcc': re.compile(r'FCC\s*(Part\s*\d+|CFR\s*\d+)', re.IGNORECASE),
            'en': re.compile(r'EN\s*(\d+(?:[-/]\d+)*)', re.IGNORECASE),
            'iso': re.compile(r'ISO\s*(\d+(?:[-/]\d+)*)', re.IGNORECASE)
        }
        
        # EMC术语标准化映射
        self.term_normalizations = {
            # 频率单位标准化
            'mhz': 'MHz', 'MHZ': 'MHz', 'Mhz': 'MHz',
            'ghz': 'GHz', 'GHZ': 'GHz', 'Ghz': 'GHz',
            'khz': 'kHz', 'KHZ': 'kHz', 'Khz': 'kHz',
            'hz': 'Hz', 'HZ': 'Hz',
            
            # 电磁现象标准化
            'emi': 'EMI', 'EMi': 'EMI', 'eMI': 'EMI',
            'emc': 'EMC', 'EMc': 'EMC', 'eMC': 'EMC',
            'esd': 'ESD', 'ESd': 'ESD', 'eSD': 'ESD',
            'eft': 'EFT', 'EFt': 'EFT', 'eFT': 'EFT',
            
            # 测试术语标准化
            'radiated emission': 'Radiated Emission',
            'conducted emission': 'Conducted Emission',
            'radiated immunity': 'Radiated Immunity',
            'conducted immunity': 'Conducted Immunity'
        }
        
        # 需要移除的噪声字符
        self.noise_chars = set('•○●◦‣⁃')
        
    def clean_entity_text(self, text: str) -> str:
        """
        清理单个实体文本
        
        这是实体文本清理的核心方法，它会：
        1. 处理编码问题和特殊字符
        2. 标准化EMC专业术语
        3. 修正格式问题
        
        Args:
            text: 原始实体文本
            
        Returns:
            清理后的实体文本
        """
        if not text or not isinstance(text, str):
            return ""
        
        # 第一步：Unicode标准化和基础清理
        cleaned = self._normalize_unicode(text)
        
        # 第二步：移除噪声字符
        cleaned = self._remove_noise_characters(cleaned)
        
        # 第三步：标准化EMC术语
        cleaned = self._normalize_emc_terms(cleaned)
        
        # 第四步：标准化技术编号
        cleaned = self._normalize_standards(cleaned)
        
        # 第五步：最终格式化
        cleaned = self._final_formatting(cleaned)
        
        return cleaned.strip()
    
    def clean_context_text(self, context: str) -> str:
        """
        清理上下文文本
        
        上下文文本的清理相对宽松，主要目的是：
        1. 保持语义完整性
        2. 移除明显的噪声
        3. 标准化关键术语
        """
        if not context or not isinstance(context, str):
            return ""
        
        # 基础清理
        cleaned = self._normalize_unicode(context)
        cleaned = self._remove_noise_characters(cleaned)
        
        # 轻度术语标准化（保持上下文的自然性）
        for term, normalized in self.term_normalizations.items():
            # 使用词边界匹配，避免过度替换
            pattern = r'\b' + re.escape(term) + r'\b'
            cleaned = re.sub(pattern, normalized, cleaned, flags=re.IGNORECASE)
        
        # 清理多余空白
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned.strip()
    
    def batch_clean_entities(self, 
                           entities: List[str], 
                           contexts: Optional[List[str]] = None) -> Tuple[List[str], List[str]]:
        """
        批量清理实体和上下文
        
        这个方法优化了批处理性能，适合处理大量数据。
        
        Args:
            entities: 实体文本列表
            contexts: 上下文文本列表（可选）
            
        Returns:
            (清理后的实体列表, 清理后的上下文列表)
        """
        logger.info(f"开始批量清理 {len(entities)} 个实体")
        
        # 清理实体
        cleaned_entities = [self.clean_entity_text(entity) for entity in entities]
        
        # 清理上下文
        if contexts:
            cleaned_contexts = [self.clean_context_text(ctx) for ctx in contexts]
        else:
            cleaned_contexts = [""] * len(entities)
        
        # 过滤空实体
        valid_pairs = [
            (entity, context) 
            for entity, context in zip(cleaned_entities, cleaned_contexts)
            if entity.strip()
        ]
        
        if len(valid_pairs) != len(entities):
            logger.warning(f"过滤掉 {len(entities) - len(valid_pairs)} 个空实体")
        
        final_entities, final_contexts = zip(*valid_pairs) if valid_pairs else ([], [])
        
        logger.info(f"批量清理完成，有效实体: {len(final_entities)}")
        return list(final_entities), list(final_contexts)
    
    def _normalize_unicode(self, text: str) -> str:
        """Unicode标准化和编码修复"""
        # NFKD标准化 - 将复合字符分解
        normalized = unicodedata.normalize('NFKD', text)
        
        # 移除控制字符但保留换行和制表符
        cleaned = ''.join(
            char for char in normalized 
            if unicodedata.category(char)[0] != 'C' or char in '\n\t'
        )
        
        return cleaned
    
    def _remove_noise_characters(self, text: str) -> str:
        """移除噪声字符"""
        # 移除预定义的噪声字符
        for char in self.noise_chars:
            text = text.replace(char, '')
        
        # 移除多余的标点符号
        text = re.sub(r'[^\w\s\-/().,:]', ' ', text)
        
        return text
    
    def _normalize_emc_terms(self, text: str) -> str:
        """标准化EMC术语"""
        result = text
        for term, normalized in self.term_normalizations.items():
            # 精确匹配，区分大小写
            if term in result:
                result = result.replace(term, normalized)
        
        return result
    
    def _normalize_standards(self, text: str) -> str:
        """标准化技术标准编号"""
        result = text
        
        for standard_type, pattern in self.standard_patterns.items():
            matches = pattern.findall(result)
            for match in matches:
                # 重新构造标准化的标准编号
                if standard_type == 'iec':
                    normalized = f"IEC {match}"
                elif standard_type == 'cispr':
                    normalized = f"CISPR {match}"
                elif standard_type == 'fcc':
                    normalized = f"FCC {match}"
                elif standard_type == 'en':
                    normalized = f"EN {match}"
                elif standard_type == 'iso':
                    normalized = f"ISO {match}"
                
                # 替换原始匹配
                original_match = pattern.search(result)
                if original_match:
                    result = result.replace(original_match.group(0), normalized)
        
        return result
    
    def _final_formatting(self, text: str) -> str:
        """最终格式化处理"""
        # 标准化空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除首尾空白
        text = text.strip()
        
        # 确保适当的大小写（对于缩写词）
        words = text.split()
        formatted_words = []
        
        for word in words:
            # 如果是已知的缩写词，保持大写
            if word.upper() in ['EMC', 'EMI', 'ESD', 'EFT', 'IEC', 'CISPR', 'FCC', 'EN', 'ISO']:
                formatted_words.append(word.upper())
            else:
                formatted_words.append(word)
        
        return ' '.join(formatted_words)

# 便利函数，保持接口兼容性
def clean_entities_for_disambiguation(entities: List[str], 
                                    contexts: Optional[List[str]] = None) -> Tuple[List[str], List[str]]:
    """
    为实体消歧准备清理后的数据
    
    这个函数提供了一个简单的接口，用于将原始提取的实体
    转换为适合消歧处理的标准化格式。
    """
    cleaner = EMCDataCleaner()
    return cleaner.batch_clean_entities(entities, contexts)

# 使用示例
def example_usage():
    """演示数据清理的效果"""
    # 测试数据 - 包含各种需要清理的问题
    dirty_entities = [
        "iec  61000-4-2",  # 格式不规范的标准号
        "EMi Filter",      # 大小写混乱的术语
        "spectrum•analyzer", # 包含噪声字符
        "100 mhz",         # 单位大小写问题
        "  ESD  test  ",   # 多余空白
    ]
    
    dirty_contexts = [
        "The iec 61000-4-2 standard defines  emi test procedures",
        "This emi filter operates at 100mhz frequency range",
        "spectrum•analyzer used for radiated emission measurements",
        "esd immunity testing according to international standards",
        "  conducted  emission   limits   per   fcc  part  15  "
    ]
    
    # 执行清理
    clean_entities, clean_contexts = clean_entities_for_disambiguation(
        dirty_entities, dirty_contexts
    )
    
    # 显示结果
    print("清理结果对比:")
    for i, (orig, clean) in enumerate(zip(dirty_entities, clean_entities)):
        print(f"{i+1}. '{orig}' -> '{clean}'")

if __name__ == "__main__":
    example_usage()