"""
实体消歧功能集成测试
验证从数据清理到实体链接的完整流程
"""

import unittest
import time
from typing import List, Tuple
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from data_processing.clean_utils import clean_entities_for_disambiguation
from kg_construction.entity_linking import EntityLinker, link_entities_simple

class TestEntityDisambiguationIntegration(unittest.TestCase):
    """
    集成测试类
    
    这个测试类验证实体消歧功能的几个关键方面：
    1. 功能正确性：能否正确识别和消歧实体
    2. 性能要求：处理大量数据的速度
    3. 接口兼容性：保持现有函数接口不变
    """
    
    def setUp(self):
        """测试前的准备工作"""
        self.linker = EntityLinker(similarity_threshold=0.7)
        
        # 准备测试数据集
        self.test_entities, self.test_contexts = self._prepare_test_data()
    
    def _prepare_test_data(self) -> Tuple[List[str], List[str]]:
        """
        准备测试数据
        
        这些数据模拟了EMC文档中常见的实体消歧挑战：
        - 同名但不同含义的实体
        - 格式不统一的相同实体  
        - 缩写和全称的混用
        """
        entities = [
            # 相同标准的不同表示方式
            "IEC 61000-4-2", "iec 61000-4-2", "IEC61000-4-2",
            
            # 设备名称的不同形式
            "Spectrum Analyzer", "spectrum analyzer", "Spectrum analyser",
            
            # EMI Filter的不同表达
            "EMI Filter", "emi filter", "EMI filter",
            
            # 频率描述
            "100 MHz", "100MHz", "100 mhz",
            
            # 不同含义的相同词汇
            "Filter", "filter",  # 可能是EMI滤波器或数字滤波器
            
            # 测试方法
            "ESD Test", "esd test", "Electrostatic Discharge Test"
        ]
        
        contexts = [
            # IEC 61000-4-2相关上下文
            "electrostatic discharge immunity test standard procedure",
            "ESD test requirements according to international standard",
            "immunity testing for electronic equipment ESD protection",
            
            # 频谱分析仪相关上下文
            "RF measurement equipment for emissions testing",
            "radio frequency analyzer for EMC compliance testing", 
            "measuring equipment for radiated emission analysis",
            
            # EMI滤波器相关上下文
            "component for reducing electromagnetic interference",
            "passive filter for EMI suppression in power lines",
            "electromagnetic interference reduction component",
            
            # 频率相关上下文
            "frequency range for EMC testing procedures",
            "operating frequency of wireless communication device",
            "test frequency according to EMC standard requirements",
            
            # 滤波器上下文（不同含义）
            "digital signal processing filter algorithm",  # 数字滤波器
            "analog filter circuit for noise reduction",   # 模拟滤波器
            
            # ESD测试相关上下文
            "electrostatic discharge immunity test procedure",
            "ESD protection testing for electronic devices",
            "immunity testing against electrostatic discharge events"
        ]
        
        return entities, contexts
    
    def test_data_cleaning_functionality(self):
        """测试数据清理功能"""
        print("\n=== 测试数据清理功能 ===")
        
        # 使用包含各种问题的脏数据
        dirty_entities = [
            "iec  61000-4-2",    # 多余空格
            "EMi•Filter",        # 噪声字符
            "  100 mhz  ",       # 首尾空格和大小写
            "esd test"           # 大小写问题
        ]
        
        dirty_contexts = [
            "The  iec  standard   defines  requirements",
            "This•filter•reduces•interference",
            "  frequency  range  for  testing  ",
            "esd  immunity  test  procedure"
        ]
        
        # 执行清理
        clean_entities, clean_contexts = clean_entities_for_disambiguation(
            dirty_entities, dirty_contexts
        )
        
        # 验证清理效果
        self.assertEqual(clean_entities[0], "IEC 61000-4-2")
        self.assertEqual(clean_entities[1], "EMI Filter")
        self.assertEqual(clean_entities[2], "100 MHz")
        self.assertEqual(clean_entities[3], "ESD test")
        
        # 验证上下文也被正确清理
        for context in clean_contexts:
            self.assertNotIn("  ", context)  # 没有多余空格
            self.assertNotIn("•", context)   # 没有噪声字符
        
        print("✓ 数据清理功能测试通过")
    
    def test_entity_disambiguation_accuracy(self):
        """测试实体消歧准确性"""
        print("\n=== 测试实体消歧准确性 ===")
        
        # 先清理数据
        clean_entities, clean_contexts = clean_entities_for_disambiguation(
            self.test_entities, self.test_contexts
        )
        
        # 执行实体链接
        linked_entities = self.linker.link_entities(clean_entities, clean_contexts)
        
        # 验证消歧效果
        self.assertLess(len(linked_entities), len(clean_entities), 
                       "消歧应该减少实体数量")
        
        # 检查特定的消歧效果
        entity_ids = [entity.unique_id for entity in linked_entities]
        unique_ids = set(entity_ids)
        
        # IEC 61000-4-2的不同形式应该被合并
        iec_variants = ["IEC 61000-4-2", "iec 61000-4-2", "IEC61000-4-2"]
        found_iec_entities = [
            entity for entity in linked_entities 
            if any(variant in entity.variants for variant in iec_variants)
        ]
        self.assertGreaterEqual(len(found_iec_entities), 1, 
                               "应该识别出IEC 61000-4-2实体")
        
        print(f"✓ 消歧准确性测试通过 - 原始{len(clean_entities)}个实体消歧为{len(linked_entities)}个唯一实体")
    
    def test_performance_requirements(self):
        """测试性能要求：10,000实体在30秒内完成"""
        print("\n=== 测试性能要求 ===")
        
        # 生成10,000个测试实体（重复使用基础数据）
        base_entities, base_contexts = clean_entities_for_disambiguation(
            self.test_entities, self.test_contexts
        )
        
        # 扩展到10,000个
        multiplier = 10000 // len(base_entities) + 1
        large_entities = (base_entities * multiplier)[:10000]
        large_contexts = (base_contexts * multiplier)[:10000]
        
        print(f"准备测试 {len(large_entities)} 个实体进行消歧性能测试")