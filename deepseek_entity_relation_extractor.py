"""
DeepSeek实体关系提取器
支持自定义Temperature和智能Temperature建议系统
专门优化用于EMC知识图谱的实体和关系提取
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
from openai import AsyncOpenAI


class ExtractionTask(Enum):
    """提取任务类型"""
    ENTITY_EXTRACTION = "entity_extraction"
    RELATION_EXTRACTION = "relation_extraction"
    COMBINED_EXTRACTION = "combined_extraction"
    ONTOLOGY_ALIGNMENT = "ontology_alignment"
    ENTITY_DISAMBIGUATION = "entity_disambiguation"


class ExtractionGoal(Enum):
    """提取目标"""
    HIGH_PRECISION = "high_precision"      # 高精度，低召回率
    HIGH_RECALL = "high_recall"            # 高召回率，可能包含噪声
    BALANCED = "balanced"                  # 平衡精度和召回率
    CREATIVE = "creative"                  # 创造性提取，发现新关系
    CONSERVATIVE = "conservative"          # 保守提取，只提取明确的关系


@dataclass
class TemperatureRecommendation:
    """Temperature推荐配置"""
    task: ExtractionTask
    goal: ExtractionGoal
    recommended_temp: float
    min_temp: float
    max_temp: float
    description: str
    reasoning: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task": self.task.value,
            "goal": self.goal.value,
            "recommended_temperature": self.recommended_temp,
            "temperature_range": {
                "min": self.min_temp,
                "max": self.max_temp
            },
            "description": self.description,
            "reasoning": self.reasoning
        }


@dataclass
class ExtractionConfig:
    """提取配置"""
    api_key: str
    base_url: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-chat"
    temperature: float = 0.3
    max_tokens: int = 4000
    top_p: float = 0.9
    task: ExtractionTask = ExtractionTask.COMBINED_EXTRACTION
    goal: ExtractionGoal = ExtractionGoal.BALANCED
    custom_entities: Optional[List[str]] = None
    custom_relations: Optional[List[str]] = None
    domain_context: str = "EMC"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExtractionResult:
    """提取结果"""
    entities: List[Dict[str, Any]]
    relations: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    metadata: Dict[str, Any]
    processing_time: float
    token_usage: Dict[str, int]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TemperatureAdvisor:
    """Temperature建议系统"""
    
    def __init__(self):
        self.recommendations = self._build_recommendation_matrix()
    
    def _build_recommendation_matrix(self) -> Dict[Tuple[ExtractionTask, ExtractionGoal], TemperatureRecommendation]:
        """构建推荐矩阵"""
        matrix = {}
        
        # 实体提取任务
        matrix[(ExtractionTask.ENTITY_EXTRACTION, ExtractionGoal.HIGH_PRECISION)] = TemperatureRecommendation(
            task=ExtractionTask.ENTITY_EXTRACTION,
            goal=ExtractionGoal.HIGH_PRECISION,
            recommended_temp=0.1,
            min_temp=0.0,
            max_temp=0.2,
            description="高精度实体提取",
            reasoning="使用极低temperature确保提取的实体准确性，避免虚假实体"
        )
        
        matrix[(ExtractionTask.ENTITY_EXTRACTION, ExtractionGoal.HIGH_RECALL)] = TemperatureRecommendation(
            task=ExtractionTask.ENTITY_EXTRACTION,
            goal=ExtractionGoal.HIGH_RECALL,
            recommended_temp=0.5,
            min_temp=0.4,
            max_temp=0.7,
            description="高召回率实体提取",
            reasoning="使用中等temperature发现更多潜在实体，包括模糊或隐含的实体"
        )
        
        matrix[(ExtractionTask.ENTITY_EXTRACTION, ExtractionGoal.BALANCED)] = TemperatureRecommendation(
            task=ExtractionTask.ENTITY_EXTRACTION,
            goal=ExtractionGoal.BALANCED,
            recommended_temp=0.2,
            min_temp=0.1,
            max_temp=0.4,
            description="平衡实体提取",
            reasoning="平衡精度和召回率，适合大多数EMC实体提取场景"
        )
        
        # 关系提取任务
        matrix[(ExtractionTask.RELATION_EXTRACTION, ExtractionGoal.HIGH_PRECISION)] = TemperatureRecommendation(
            task=ExtractionTask.RELATION_EXTRACTION,
            goal=ExtractionGoal.HIGH_PRECISION,
            recommended_temp=0.05,
            min_temp=0.0,
            max_temp=0.15,
            description="高精度关系提取",
            reasoning="关系提取比实体提取更需要精确性，使用最低temperature"
        )
        
        matrix[(ExtractionTask.RELATION_EXTRACTION, ExtractionGoal.CREATIVE)] = TemperatureRecommendation(
            task=ExtractionTask.RELATION_EXTRACTION,
            goal=ExtractionGoal.CREATIVE,
            recommended_temp=0.8,
            min_temp=0.6,
            max_temp=1.0,
            description="创造性关系发现",
            reasoning="高temperature帮助发现非显式的、推理性的关系"
        )
        
        matrix[(ExtractionTask.RELATION_EXTRACTION, ExtractionGoal.BALANCED)] = TemperatureRecommendation(
            task=ExtractionTask.RELATION_EXTRACTION,
            goal=ExtractionGoal.BALANCED,
            recommended_temp=0.3,
            min_temp=0.2,
            max_temp=0.5,
            description="平衡关系提取",
            reasoning="在准确性和发现能力之间取平衡"
        )
        
        # 组合提取任务
        matrix[(ExtractionTask.COMBINED_EXTRACTION, ExtractionGoal.BALANCED)] = TemperatureRecommendation(
            task=ExtractionTask.COMBINED_EXTRACTION,
            goal=ExtractionGoal.BALANCED,
            recommended_temp=0.25,
            min_temp=0.15,
            max_temp=0.4,
            description="组合提取平衡模式",
            reasoning="同时提取实体和关系时的最佳平衡点"
        )
        
        matrix[(ExtractionTask.COMBINED_EXTRACTION, ExtractionGoal.CONSERVATIVE)] = TemperatureRecommendation(
            task=ExtractionTask.COMBINED_EXTRACTION,
            goal=ExtractionGoal.CONSERVATIVE,
            recommended_temp=0.1,
            min_temp=0.0,
            max_temp=0.2,
            description="保守组合提取",
            reasoning="只提取高置信度的实体和关系"
        )
        
        # 本体对齐任务
        matrix[(ExtractionTask.ONTOLOGY_ALIGNMENT, ExtractionGoal.HIGH_PRECISION)] = TemperatureRecommendation(
            task=ExtractionTask.ONTOLOGY_ALIGNMENT,
            goal=ExtractionGoal.HIGH_PRECISION,
            recommended_temp=0.15,
            min_temp=0.05,
            max_temp=0.25,
            description="精确本体对齐",
            reasoning="本体对齐需要准确的语义理解，使用较低temperature"
        )
        
        # 实体消歧任务
        matrix[(ExtractionTask.ENTITY_DISAMBIGUATION, ExtractionGoal.HIGH_PRECISION)] = TemperatureRecommendation(
            task=ExtractionTask.ENTITY_DISAMBIGUATION,
            goal=ExtractionGoal.HIGH_PRECISION,
            recommended_temp=0.2,
            min_temp=0.1,
            max_temp=0.3,
            description="精确实体消歧",
            reasoning="实体消歧需要精确的上下文理解"
        )
        
        return matrix
    
    def get_recommendation(self, task: ExtractionTask, goal: ExtractionGoal) -> TemperatureRecommendation:
        """获取温度推荐"""
        key = (task, goal)
        if key in self.recommendations:
            return self.recommendations[key]
        
        # 默认推荐
        return TemperatureRecommendation(
            task=task,
            goal=goal,
            recommended_temp=0.3,
            min_temp=0.1,
            max_temp=0.5,
            description="默认配置",
            reasoning="使用通用的中等temperature配置"
        )
    
    def get_all_recommendations(self) -> List[TemperatureRecommendation]:
        """获取所有推荐配置"""
        return list(self.recommendations.values())
    
    def suggest_optimal_temperature(
        self, 
        task: ExtractionTask, 
        goal: ExtractionGoal,
        text_complexity: str = "medium",  # "low", "medium", "high"
        domain_specificity: str = "high"   # "low", "medium", "high" 
    ) -> float:
        """根据任务和文本特征建议最优temperature"""
        base_rec = self.get_recommendation(task, goal)
        base_temp = base_rec.recommended_temp
        
        # 根据文本复杂度调整
        complexity_adjustment = {
            "low": -0.05,
            "medium": 0.0,
            "high": 0.1
        }
        
        # 根据领域特异性调整
        domain_adjustment = {
            "low": 0.1,    # 通用文本需要更高temperature
            "medium": 0.05,
            "high": 0.0    # 专业文本使用基础temperature
        }
        
        adjusted_temp = base_temp + complexity_adjustment.get(text_complexity, 0) + domain_adjustment.get(domain_specificity, 0)
        
        # 确保在合理范围内
        return max(0.0, min(1.0, adjusted_temp))


class DeepSeekEntityRelationExtractor:
    """DeepSeek实体关系提取器主类"""
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
        self.advisor = TemperatureAdvisor()
        self.logger = logging.getLogger(__name__)
        
        # EMC领域默认实体类型
        self.default_emc_entities = [
            "EMC_Standard", "Test_Equipment", "Test_Method", "Frequency_Range",
            "Emission_Limit", "Immunity_Level", "Product_Category", "Test_Site",
            "Measurement_Uncertainty", "Compliance_Requirement", "Antenna",
            "Filter", "Shielding", "Grounding", "Cable", "Connector"
        ]
        
        # EMC领域默认关系类型
        self.default_emc_relations = [
            "APPLIES_TO", "REQUIRES", "TESTS", "COMPLIES_WITH", "EXCEEDS",
            "USES", "CONNECTS_TO", "SHIELDS", "FILTERS", "GROUNDS",
            "MEASURES", "SPECIFIES", "REFERENCES", "DEPENDS_ON"
        ]
    
    def get_temperature_recommendation(self, task: ExtractionTask, goal: ExtractionGoal) -> TemperatureRecommendation:
        """获取temperature推荐"""
        return self.advisor.get_recommendation(task, goal)
    
    def suggest_optimal_temperature(self, **kwargs) -> float:
        """建议最优temperature"""
        return self.advisor.suggest_optimal_temperature(
            task=self.config.task,
            goal=self.config.goal,
            **kwargs
        )
    
    async def extract_entities_and_relations(
        self, 
        text: str,
        custom_temperature: Optional[float] = None,
        custom_entities: Optional[List[str]] = None,
        custom_relations: Optional[List[str]] = None
    ) -> ExtractionResult:
        """提取实体和关系"""
        start_time = time.time()
        
        # 使用自定义或配置的temperature
        temperature = custom_temperature if custom_temperature is not None else self.config.temperature
        
        # 构建提示词
        prompt = self._build_extraction_prompt(
            text, 
            custom_entities or self.config.custom_entities or self.default_emc_entities,
            custom_relations or self.config.custom_relations or self.default_emc_relations
        )
        
        try:
            # 调用DeepSeek API
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p
            )
            
            # 解析结果
            content = response.choices[0].message.content
            result_data = self._parse_extraction_result(content)
            
            processing_time = time.time() - start_time
            
            return ExtractionResult(
                entities=result_data.get("entities", []),
                relations=result_data.get("relations", []),
                confidence_scores=result_data.get("confidence_scores", {}),
                metadata={
                    "temperature_used": temperature,
                    "task": self.config.task.value,
                    "goal": self.config.goal.value,
                    "text_length": len(text),
                    "prompt_length": len(prompt)
                },
                processing_time=processing_time,
                token_usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )
            
        except Exception as e:
            self.logger.error(f"提取失败: {str(e)}")
            raise
    
    def _build_extraction_prompt(
        self, 
        text: str, 
        entity_types: List[str], 
        relation_types: List[str]
    ) -> str:
        """构建提取提示词"""
        
        entity_descriptions = {
            "EMC_Standard": "EMC标准和规范（如IEC 61000、FCC Part 15等）",
            "Test_Equipment": "测试设备和仪器（如频谱分析仪、信号发生器等）",
            "Test_Method": "测试方法和程序",
            "Frequency_Range": "频率范围和频段",
            "Emission_Limit": "发射限值和阈值",
            "Immunity_Level": "抗扰度等级",
            "Product_Category": "产品类别和设备类型",
            "Test_Site": "测试场地和环境",
            "Antenna": "天线和辐射器",
            "Filter": "滤波器和滤波电路",
            "Shielding": "屏蔽和屏蔽材料",
            "Grounding": "接地和接地系统"
        }
        
        relation_descriptions = {
            "APPLIES_TO": "标准适用于产品或设备",
            "REQUIRES": "需要或要求",
            "TESTS": "测试或检验",
            "COMPLIES_WITH": "符合或遵循",
            "USES": "使用或采用",
            "CONNECTS_TO": "连接到",
            "SHIELDS": "屏蔽或防护",
            "FILTERS": "滤波或过滤",
            "MEASURES": "测量或检测"
        }
        
        # 构建实体类型说明
        entity_desc = "\n".join([
            f"- {etype}: {entity_descriptions.get(etype, '相关实体')}"
            for etype in entity_types
        ])
        
        # 构建关系类型说明
        relation_desc = "\n".join([
            f"- {rtype}: {relation_descriptions.get(rtype, '相关关系')}"
            for rtype in relation_types
        ])
        
        prompt = f"""
你是一个专业的EMC（电磁兼容性）知识提取专家。请从以下文本中提取实体和关系，并以JSON格式返回结果。

文本内容：
{text}

请识别以下类型的实体：
{entity_desc}

请识别以下类型的关系：
{relation_desc}

要求：
1. 每个实体必须包含：type（类型）、name（名称）、properties（属性字典）、confidence（置信度0-1）
2. 每个关系必须包含：source（源实体名称）、target（目标实体名称）、type（关系类型）、confidence（置信度0-1）
3. 只提取文本中明确存在的实体和关系
4. 属性字典应包含相关的技术参数、规格等信息
5. 置信度应反映提取的确定性程度

请严格按照以下JSON格式返回：
{{
  "entities": [
    {{
      "type": "实体类型",
      "name": "实体名称", 
      "properties": {{"key": "value"}},
      "confidence": 0.95
    }}
  ],
  "relations": [
    {{
      "source": "源实体名称",
      "target": "目标实体名称", 
      "type": "关系类型",
      "confidence": 0.90
    }}
  ],
  "confidence_scores": {{
    "overall_confidence": 0.85,
    "entity_extraction_confidence": 0.88,
    "relation_extraction_confidence": 0.82
  }}
}}
        """
        
        return prompt.strip()
    
    def _parse_extraction_result(self, content: str) -> Dict[str, Any]:
        """解析提取结果"""
        try:
            # 尝试直接解析JSON
            if content.strip().startswith('{'):
                return json.loads(content)
            
            # 尝试提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # 如果无法解析，返回空结果
            self.logger.warning("无法解析提取结果，返回空结果")
            return {
                "entities": [],
                "relations": [],
                "confidence_scores": {
                    "overall_confidence": 0.0,
                    "entity_extraction_confidence": 0.0,
                    "relation_extraction_confidence": 0.0
                }
            }
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析错误: {str(e)}")
            return {
                "entities": [],
                "relations": [],
                "confidence_scores": {
                    "overall_confidence": 0.0,
                    "entity_extraction_confidence": 0.0,
                    "relation_extraction_confidence": 0.0
                }
            }
    
    async def batch_extract(
        self, 
        texts: List[str],
        custom_temperature: Optional[float] = None
    ) -> List[ExtractionResult]:
        """批量提取"""
        tasks = [
            self.extract_entities_and_relations(text, custom_temperature)
            for text in texts
        ]
        
        return await asyncio.gather(*tasks)
    
    async def adaptive_extract(
        self,
        text: str,
        quality_threshold: float = 0.8
    ) -> ExtractionResult:
        """自适应提取 - 根据结果质量动态调整temperature"""
        
        # 首次提取
        result = await self.extract_entities_and_relations(text)
        
        overall_confidence = result.confidence_scores.get("overall_confidence", 0.0)
        
        # 如果质量不够，尝试调整temperature
        if overall_confidence < quality_threshold:
            self.logger.info(f"初始提取质量较低({overall_confidence:.2f})，尝试调整temperature")
            
            # 如果当前temperature较高，降低它以提高精度
            if self.config.temperature > 0.3:
                new_temp = max(0.1, self.config.temperature - 0.2)
                result = await self.extract_entities_and_relations(text, new_temp)
            # 如果当前temperature较低，提高它以增加召回率
            elif self.config.temperature < 0.5:
                new_temp = min(0.8, self.config.temperature + 0.3)
                result = await self.extract_entities_and_relations(text, new_temp)
        
        return result
    
    def analyze_extraction_quality(self, result: ExtractionResult) -> Dict[str, Any]:
        """分析提取质量"""
        entities = result.entities
        relations = result.relations
        
        entity_count = len(entities)
        relation_count = len(relations)
        
        # 计算平均置信度
        entity_confidences = [e.get("confidence", 0.5) for e in entities]
        relation_confidences = [r.get("confidence", 0.5) for r in relations]
        
        avg_entity_confidence = sum(entity_confidences) / len(entity_confidences) if entity_confidences else 0
        avg_relation_confidence = sum(relation_confidences) / len(relation_confidences) if relation_confidences else 0
        
        # 分析实体类型分布
        entity_type_distribution = {}
        for entity in entities:
            etype = entity.get("type", "Unknown")
            entity_type_distribution[etype] = entity_type_distribution.get(etype, 0) + 1
        
        # 分析关系类型分布
        relation_type_distribution = {}
        for relation in relations:
            rtype = relation.get("type", "Unknown")
            relation_type_distribution[rtype] = relation_type_distribution.get(rtype, 0) + 1
        
        return {
            "extraction_summary": {
                "entity_count": entity_count,
                "relation_count": relation_count,
                "avg_entity_confidence": avg_entity_confidence,
                "avg_relation_confidence": avg_relation_confidence,
                "overall_confidence": result.confidence_scores.get("overall_confidence", 0.0)
            },
            "entity_type_distribution": entity_type_distribution,
            "relation_type_distribution": relation_type_distribution,
            "quality_metrics": {
                "entities_per_100_chars": (entity_count / len(result.metadata.get("text_length", 1))) * 100,
                "relations_per_entity": relation_count / entity_count if entity_count > 0 else 0,
                "processing_efficiency": result.token_usage["total_tokens"] / result.processing_time
            }
        }


def create_extraction_service(
    api_key: str,
    task: ExtractionTask = ExtractionTask.COMBINED_EXTRACTION,
    goal: ExtractionGoal = ExtractionGoal.BALANCED,
    custom_temperature: Optional[float] = None
) -> DeepSeekEntityRelationExtractor:
    """创建提取服务实例"""
    
    # 获取推荐的temperature
    advisor = TemperatureAdvisor()
    if custom_temperature is None:
        recommendation = advisor.get_recommendation(task, goal)
        temperature = recommendation.recommended_temp
    else:
        temperature = custom_temperature
    
    config = ExtractionConfig(
        api_key=api_key,
        temperature=temperature,
        task=task,
        goal=goal
    )
    
    return DeepSeekEntityRelationExtractor(config)


# 使用示例
async def example_usage():
    """使用示例"""
    # 创建提取器
    extractor = create_extraction_service(
        api_key="your_deepseek_api_key",
        task=ExtractionTask.COMBINED_EXTRACTION,
        goal=ExtractionGoal.BALANCED
    )
    
    # 获取temperature推荐
    recommendation = extractor.get_temperature_recommendation(
        ExtractionTask.ENTITY_EXTRACTION,
        ExtractionGoal.HIGH_PRECISION
    )
    print(f"推荐配置: {recommendation.to_dict()}")
    
    # 示例文本
    text = """
    根据IEC 61000-4-3标准，对手机进行射频电磁场抗扰度测试。
    测试频率范围为80MHz到1GHz，测试场强为3V/m。
    使用信号发生器和功率放大器产生测试信号，通过双锥天线辐射。
    """
    
    # 执行提取
    result = await extractor.extract_entities_and_relations(text)
    
    # 分析质量
    quality_analysis = extractor.analyze_extraction_quality(result)
    
    print("提取结果:", result.to_dict())
    print("质量分析:", quality_analysis)


if __name__ == "__main__":
    asyncio.run(example_usage())