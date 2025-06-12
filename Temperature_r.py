"""
反馈学习系统的完整实现
展示如何将用户反馈转化为Temperature参数的智能调整
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, NamedTuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from collections import defaultdict, deque
import matplotlib.pyplot as plt

class QueryType(Enum):
    STANDARD_QUERY = "standard"
    TECHNICAL_ANALYSIS = "analysis"
    CREATIVE_DESIGN = "creative"
    TROUBLESHOOTING = "debug"
    EXPLORATION = "explore"

@dataclass
class FeedbackRecord:
    """单次反馈记录"""
    query_text: str
    query_type: QueryType
    temperature_used: float
    user_satisfaction: float  # 0-1之间的满意度分数
    response_quality_metrics: Dict[str, float]  # 响应质量的多维度评估
    timestamp: float
    user_id: str
    context_features: Dict[str, float]  # 上下文特征向量

@dataclass 
class LearningState:
    """学习状态记录"""
    query_type: QueryType
    temperature_estimates: np.ndarray  # Temperature值的概率分布估计
    confidence_scores: np.ndarray      # 对每个Temperature值的置信度
    experience_count: int              # 累积经验次数
    last_update_time: float
    convergence_indicator: float       # 收敛指标

class AdaptiveFeedbackLearner:
    """自适应反馈学习器"""
    
    def __init__(self, 
                 temperature_resolution: int = 100,  # Temperature值的离散化分辨率
                 learning_rate_initial: float = 0.1,
                 learning_rate_decay: float = 0.995,
                 exploration_factor: float = 0.15):
        
        self.temp_resolution = temperature_resolution
        self.learning_rate_initial = learning_rate_initial
        self.learning_rate_decay = learning_rate_decay
        self.exploration_factor = exploration_factor
        
        # 为每种查询类型维护独立的学习状态
        self.learning_states = self._initialize_learning_states()
        
        # 反馈历史记录
        self.feedback_history: List[FeedbackRecord] = []
        self.recent_feedback = defaultdict(lambda: deque(maxlen=50))  # 每种类型保留最近50条
        
        # 学习参数
        self.min_samples_for_update = 5  # 最少需要5个样本才开始学习
        self.confidence_threshold = 0.8  # 高置信度阈值
        
        # 日志配置
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _initialize_learning_states(self) -> Dict[QueryType, LearningState]:
        """初始化各查询类型的学习状态"""
        states = {}
        
        # 从之前校准的基准值开始
        baseline_temperatures = {
            QueryType.STANDARD_QUERY: 0.18,
            QueryType.TECHNICAL_ANALYSIS: 0.52,
            QueryType.CREATIVE_DESIGN: 0.88,
            QueryType.TROUBLESHOOTING: 0.61,
            QueryType.EXPLORATION: 0.79
        }
        
        for query_type in QueryType:
            # 创建Temperature值网格
            temp_grid = np.linspace(0.05, 1.2, self.temp_resolution)
            
            # 初始化概率分布：以基准值为中心的正态分布
            baseline_temp = baseline_temperatures[query_type]
            baseline_idx = np.argmin(np.abs(temp_grid - baseline_temp))
            
            # 创建初始的概率分布（正态分布）
            initial_distribution = np.exp(-0.5 * ((temp_grid - baseline_temp) / 0.1) ** 2)
            initial_distribution /= initial_distribution.sum()  # 归一化
            
            # 初始置信度较低，表示系统还在学习
            initial_confidence = np.full_like(temp_grid, 0.3)
            
            states[query_type] = LearningState(
                query_type=query_type,
                temperature_estimates=initial_distribution,
                confidence_scores=initial_confidence,
                experience_count=0,
                last_update_time=0.0,
                convergence_indicator=0.0
            )
        
        return states
    
    def record_feedback(self, feedback: FeedbackRecord):
        """记录用户反馈"""
        self.feedback_history.append(feedback)
        self.recent_feedback[feedback.query_type].append(feedback)
        
        self.logger.info(f"记录反馈: {feedback.query_type.value}, "
                        f"Temperature: {feedback.temperature_used:.3f}, "
                        f"满意度: {feedback.user_satisfaction:.3f}")
    
    def calculate_learning_rate(self, query_type: QueryType) -> float:
        """计算自适应学习率"""
        state = self.learning_states[query_type]
        
        # 基础学习率随经验次数衰减
        base_rate = self.learning_rate_initial * (self.learning_rate_decay ** state.experience_count)
        
        # 根据收敛状态调整：越收敛，学习率越低
        convergence_adjustment = 1.0 - (state.convergence_indicator * 0.7)
        
        # 根据最近表现调整：如果最近表现不佳，提高学习率
        recent_feedbacks = list(self.recent_feedback[query_type])
        if len(recent_feedbacks) >= 5:
            recent_satisfaction = np.mean([f.user_satisfaction for f in recent_feedbacks[-5:]])
            if recent_satisfaction < 0.6:  # 表现不佳
                performance_boost = 1.5
            elif recent_satisfaction > 0.8:  # 表现良好
                performance_boost = 0.8
            else:
                performance_boost = 1.0
        else:
            performance_boost = 1.0
        
        final_rate = base_rate * convergence_adjustment * performance_boost
        return np.clip(final_rate, 0.01, 0.3)  # 限制在合理范围内
    
    def update_temperature_distribution(self, feedback: FeedbackRecord):
        """使用贝叶斯更新方法更新Temperature分布"""
        query_type = feedback.query_type
        state = self.learning_states[query_type]
        
        # 获取当前分布
        current_dist = state.temperature_estimates.copy()
        temp_grid = np.linspace(0.05, 1.2, self.temp_resolution)
        
        # 找到使用的Temperature在网格中的位置
        temp_idx = np.argmin(np.abs(temp_grid - feedback.temperature_used))
        
        # 计算似然函数：满意度越高，该Temperature的似然越大
        satisfaction = feedback.user_satisfaction
        
        # 创建似然分布：以实际使用的Temperature为中心
        likelihood = np.exp(-0.5 * ((temp_grid - feedback.temperature_used) / 0.05) ** 2)
        
        # 根据满意度调整似然强度
        if satisfaction > 0.7:  # 高满意度
            likelihood_strength = satisfaction * 2.0
        elif satisfaction < 0.4:  # 低满意度，惩罚该Temperature
            likelihood_strength = (1 - satisfaction) * (-1.5)
        else:  # 中等满意度
            likelihood_strength = satisfaction
        
        # 应用贝叶斯更新
        learning_rate = self.calculate_learning_rate(query_type)
        
        if likelihood_strength > 0:
            # 正向更新：增强该Temperature的概率
            update_factor = 1 + learning_rate * likelihood_strength
            current_dist[temp_idx] *= update_factor
        else:
            # 负向更新：降低该Temperature的概率
            update_factor = 1 + learning_rate * likelihood_strength
            current_dist[temp_idx] *= max(0.1, update_factor)  # 避免完全归零
        
        # 归一化分布
        current_dist /= current_dist.sum()
        
        # 更新状态
        state.temperature_estimates = current_dist
        state.experience_count += 1
        state.last_update_time = feedback.timestamp
        
        # 更新收敛指标
        state.convergence_indicator = self._calculate_convergence(current_dist)
        
        self.logger.info(f"更新 {query_type.value} 分布，学习率: {learning_rate:.4f}, "
                        f"收敛度: {state.convergence_indicator:.3f}")
    
    def _calculate_convergence(self, distribution: np.ndarray) -> float:
        """计算分布的收敛程度（熵的倒数归一化）"""
        # 计算熵
        entropy = -np.sum(distribution * np.log(distribution + 1e-10))
        
        # 最大熵（均匀分布）
        max_entropy = np.log(len(distribution))
        
        # 收敛度：1 - 归一化熵
        convergence = 1.0 - (entropy / max_entropy)
        return convergence
    
    def get_optimal_temperature(self, query_type: QueryType, 
                               exploration_mode: bool = False) -> Tuple[float, float]:
        """
        获取最优Temperature值
        
        Returns:
            (optimal_temperature, confidence_score)
        """
        state = self.learning_states[query_type]
        temp_grid = np.linspace(0.05, 1.2, self.temp_resolution)
        
        if exploration_mode and state.experience_count < 20:
            # 探索模式：在高概率区域内随机选择
            probabilities = state.temperature_estimates
            selected_idx = np.random.choice(len(temp_grid), p=probabilities)
            optimal_temp = temp_grid[selected_idx]
            confidence = state.confidence_scores[selected_idx]
        else:
            # 利用模式：选择概率最高的Temperature
            best_idx = np.argmax(state.temperature_estimates)
            optimal_temp = temp_grid[best_idx]
            confidence = state.temperature_estimates[best_idx]
        
        return optimal_temp, confidence
    
    def get_temperature_with_uncertainty(self, query_type: QueryType) -> Dict[str, float]:
        """获取带不确定性信息的Temperature推荐"""
        state = self.learning_states[query_type]
        temp_grid = np.linspace(0.05, 1.2, self.temp_resolution)
        
        # 计算期望值（最优估计）
        expected_temp = np.sum(temp_grid * state.temperature_estimates)
        
        # 计算方差（不确定性）
        variance = np.sum(((temp_grid - expected_temp) ** 2) * state.temperature_estimates)
        std_dev = np.sqrt(variance)
        
        # 计算置信区间
        confidence_level = 0.95
        z_score = 1.96  # 95%置信区间
        conf_interval = (
            expected_temp - z_score * std_dev,
            expected_temp + z_score * std_dev
        )
        
        # 获取最可能值（模式）
        mode_idx = np.argmax(state.temperature_estimates)
        mode_temp = temp_grid[mode_idx]
        
        return {
            'expected_temperature': expected_temp,
            'mode_temperature': mode_temp,
            'uncertainty': std_dev,
            'confidence_interval_lower': conf_interval[0],
            'confidence_interval_upper': conf_interval[1],
            'convergence_score': state.convergence_indicator,
            'experience_count': state.experience_count
        }
    
    def process_feedback_batch(self, feedbacks: List[FeedbackRecord]):
        """批量处理反馈数据"""
        self.logger.info(f"开始批量处理 {len(feedbacks)} 条反馈")
        
        for feedback in feedbacks:
            # 记录反馈
            self.record_feedback(feedback)
            
            # 更新对应类型的Temperature分布
            self.update_temperature_distribution(feedback)
        
        # 批量处理完成后，进行全局优化
        self._global_optimization()
    
    def _global_optimization(self):
        """全局优化：跨查询类型的协调"""
        # 确保不同查询类型的Temperature值保持合理的相对关系
        temp_recommendations = {}
        
        for query_type in QueryType:
            temp_info = self.get_temperature_with_uncertainty(query_type)
            temp_recommendations[query_type] = temp_info['expected_temperature']
        
        # 检查并修正单调性
        expected_order = [
            QueryType.STANDARD_QUERY,
            QueryType.TECHNICAL_ANALYSIS,
            QueryType.TROUBLESHOOTING, 
            QueryType.EXPLORATION,
            QueryType.CREATIVE_DESIGN
        ]
        
        ordered_temps = [temp_recommendations[qt] for qt in expected_order]
        
        # 如果违反单调性，进行温和调整
        for i in range(len(ordered_temps) - 1):
            if ordered_temps[i] > ordered_temps[i + 1]:
                # 违反单调性，进行调整
                avg_temp = (ordered_temps[i] + ordered_temps[i + 1]) / 2
                ordered_temps[i] = avg_temp - 0.02
                ordered_temps[i + 1] = avg_temp + 0.02
                
                self.logger.warning(f"修正单调性违反: {expected_order[i].value} 和 {expected_order[i+1].value}")
        
        # 更新分布（温和调整）
        for i, query_type in enumerate(expected_order):
            target_temp = ordered_temps[i]
            self._adjust_distribution_toward_target(query_type, target_temp, strength=0.1)
    
    def _adjust_distribution_toward_target(self, query_type: QueryType, 
                                         target_temp: float, strength: float):
        """将分布温和地调整向目标Temperature"""
        state = self.learning_states[query_type]
        temp_grid = np.linspace(0.05, 1.2, self.temp_resolution)
        
        # 创建以目标Temperature为中心的调整分布
        adjustment_dist = np.exp(-0.5 * ((temp_grid - target_temp) / 0.08) ** 2)
        adjustment_dist /= adjustment_dist.sum()
        
        # 温和混合
        new_dist = (1 - strength) * state.temperature_estimates + strength * adjustment_dist
        state.temperature_estimates = new_dist
    
    def generate_learning_report(self) -> str:
        """生成学习报告"""
        report = """
===============================================
自适应Temperature学习报告
===============================================

一、学习状态概览
"""
        
        for query_type in QueryType:
            temp_info = self.get_temperature_with_uncertainty(query_type)
            state = self.learning_states[query_type]
            
            report += f"""
{query_type.value.upper()}查询类型：
- 当前最优Temperature: {temp_info['expected_temperature']:.3f}
- 不确定性(标准差): {temp_info['uncertainty']:.3f}
- 95%置信区间: [{temp_info['confidence_interval_lower']:.3f}, {temp_info['confidence_interval_upper']:.3f}]
- 收敛程度: {temp_info['convergence_score']:.1%}
- 学习样本数: {temp_info['experience_count']}
"""
        
        # 添加总体学习质量评估
        total_samples = sum(state.experience_count for state in self.learning_states.values())
        avg_convergence = np.mean([state.convergence_indicator for state in self.learning_states.values()])
        
        report += f"""
二、整体学习质量
- 总学习样本数: {total_samples}
- 平均收敛程度: {avg_convergence:.1%}
- 活跃查询类型: {len([s for s in self.learning_states.values() if s.experience_count > 0])}

三、学习建议
"""
        
        if total_samples < 50:
            report += "- 样本数量较少，建议继续收集用户反馈以提高学习质量\n"
        
        if avg_convergence < 0.3:
            report += "- 系统仍在快速学习中，Temperature推荐可能变化较大\n"
        elif avg_convergence > 0.8:
            report += "- 系统已基本收敛，Temperature推荐相对稳定\n"
        
        return report
    
    def visualize_learning_progress(self):
        """可视化学习进度"""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle('Temperature学习进度可视化', fontsize=16)
        
        temp_grid = np.linspace(0.05, 1.2, self.temp_resolution)
        
        for i, query_type in enumerate(QueryType):
            row = i // 3  
            col = i % 3
            ax = axes[row, col]
            
            state = self.learning_states[query_type]
            
            # 绘制当前分布
            ax.plot(temp_grid, state.temperature_estimates, 
                   linewidth=2, label='学习后分布')
            
            # 绘制最优点
            best_idx = np.argmax(state.temperature_estimates)
            ax.axvline(temp_grid[best_idx], color='red', linestyle='--',
                      label=f'最优值: {temp_grid[best_idx]:.3f}')
            
            # 添加收敛信息
            ax.text(0.05, 0.95, f'收敛度: {state.convergence_indicator:.2f}\n样本数: {state.experience_count}',
                   transform=ax.transAxes, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            ax.set_title(f'{query_type.value}查询')
            ax.set_xlabel('Temperature')
            ax.set_ylabel('概率密度')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        # 隐藏空的子图
        if len(QueryType) < 6:
            axes[1, 2].set_visible(False)
        
        plt.tight_layout()
        plt.show()

# 演示函数
def demonstrate_feedback_learning():
    """演示反馈学习过程"""
    print("开始演示自适应反馈学习系统...")
    
    # 创建学习器
    learner = AdaptiveFeedbackLearner()
    
    # 模拟一系列用户反馈
    import time
    
    sample_feedbacks = [
        # 标准查询的反馈
        FeedbackRecord(
            query_text="EN 55032标准中Class A设备的限值是多少？",
            query_type=QueryType.STANDARD_QUERY,
            temperature_used=0.15,
            user_satisfaction=0.9,  # 高满意度
            response_quality_metrics={"accuracy": 0.95, "completeness": 0.9},
            timestamp=time.time(),
            user_id="user_001",
            context_features={"complexity": 0.2, "specificity": 0.9}
        ),
        # 创意设计的反馈
        FeedbackRecord(
            query_text="如何创新性地设计低EMI开关电源？",
            query_type=QueryType.CREATIVE_DESIGN,
            temperature_used=0.9,
            user_satisfaction=0.85,
            response_quality_metrics={"creativity": 0.9, "practicality": 0.8},
            timestamp=time.time(),
            user_id="user_002",
            context_features={"complexity": 0.8, "creativity_required": 0.9}
        ),
        # 更多反馈...
    ]
    
    # 处理反馈
    learner.process_feedback_batch(sample_feedbacks)
    
    # 生成报告
    report = learner.generate_learning_report()
    print(report)
    
    # 获取Temperature推荐
    for query_type in QueryType:
        temp_info = learner.get_temperature_with_uncertainty(query_type)
        print(f"\n{query_type.value}查询推荐:")
        print(f"  期望Temperature: {temp_info['expected_temperature']:.3f}")
        print(f"  不确定性: ±{temp_info['uncertainty']:.3f}")

if __name__ == "__main__":
    demonstrate_feedback_learning()