"""
DeepSeek实体关系提取器使用示例
展示各种使用场景和Temperature配置
"""

import asyncio
import json
import os
from deepseek_entity_relation_extractor import (
    DeepSeekEntityRelationExtractor,
    ExtractionConfig, 
    ExtractionTask,
    ExtractionGoal,
    TemperatureAdvisor,
    create_extraction_service
)


# 示例EMC文本数据
SAMPLE_TEXTS = {
    "standard_analysis": """
    IEC 61000-4-3:2020标准规定了射频电磁场抗扰度测试方法。
    测试频率范围为80MHz到6GHz，场强等级分为1V/m、3V/m、10V/m和30V/m。
    测试设备包括信号发生器、功率放大器、定向耦合器和辐射天线。
    被测设备应放置在测试台上，距离辐射天线3米。
    """,
    
    "equipment_test": """
    对智能手机进行传导发射测试，使用R&S FSW信号与频谱分析仪。
    测试频率为150kHz至30MHz，使用人工电源网络LISN进行信号耦合。
    测量结果显示在1MHz处峰值为45dBμV，符合EN 55032 Class B限值要求。
    使用双锥天线和对数周期天线覆盖不同频段的辐射发射测试。
    """,
    
    "compliance_report": """
    产品型号XYZ-123通过了FCC Part 15 Subpart B的认证测试。
    传导发射测试在30MHz以下频段全部符合Class A设备限值。
    辐射发射测试使用3米法半电波暗室，天线高度1米至4米扫描。
    EUT工作在最大功率状态，连接典型电缆进行最坏情况测试。
    """,
    
    "technical_specification": """
    EMI滤波器采用π型拓扑结构，包含差模电感2.2mH和共模扼流圈4.7mH。
    X电容使用0.1μF/275VAC规格，Y电容采用2.2nF/250VAC安全电容。
    滤波器插入损耗在150kHz处大于40dB，在30MHz处达到60dB。
    外壳采用铁氧体磁性材料，提供额外的高频抑制效果。
    """
}


async def demonstrate_temperature_recommendations():
    """演示Temperature推荐系统"""
    print("=== Temperature推荐系统演示 ===\n")
    
    advisor = TemperatureAdvisor()
    
    # 显示所有推荐配置
    print("所有可用的Temperature推荐配置:")
    recommendations = advisor.get_all_recommendations()
    
    for rec in recommendations:
        print(f"\n任务: {rec.task.value}")
        print(f"目标: {rec.goal.value}")
        print(f"推荐Temperature: {rec.recommended_temp}")
        print(f"范围: {rec.min_temp} - {rec.max_temp}")
        print(f"说明: {rec.description}")
        print(f"原因: {rec.reasoning}")
    
    print("\n" + "="*60 + "\n")


async def demonstrate_basic_extraction():
    """演示基础提取功能"""
    print("=== 基础提取功能演示 ===\n")
    
    # 需要设置API密钥
    api_key = os.getenv("DEEPSEEK_API_KEY", "your_api_key_here")
    if api_key == "your_api_key_here":
        print("请设置DEEPSEEK_API_KEY环境变量")
        return
    
    # 创建不同配置的提取器
    extractors = {
        "高精度": create_extraction_service(
            api_key=api_key,
            task=ExtractionTask.COMBINED_EXTRACTION,
            goal=ExtractionGoal.HIGH_PRECISION
        ),
        "平衡": create_extraction_service(
            api_key=api_key,
            task=ExtractionTask.COMBINED_EXTRACTION, 
            goal=ExtractionGoal.BALANCED
        ),
        "创造性": create_extraction_service(
            api_key=api_key,
            task=ExtractionTask.RELATION_EXTRACTION,
            goal=ExtractionGoal.CREATIVE
        )
    }
    
    # 使用标准分析文本进行演示
    text = SAMPLE_TEXTS["standard_analysis"]
    print(f"待分析文本：\n{text}\n")
    
    for name, extractor in extractors.items():
        print(f"--- {name}配置提取结果 ---")
        print(f"Temperature: {extractor.config.temperature}")
        
        try:
            result = await extractor.extract_entities_and_relations(text)
            
            print(f"提取到实体数量: {len(result.entities)}")
            print(f"提取到关系数量: {len(result.relations)}")
            print(f"整体置信度: {result.confidence_scores.get('overall_confidence', 0):.2f}")
            print(f"处理时间: {result.processing_time:.2f}秒")
            
            # 显示前3个实体
            for i, entity in enumerate(result.entities[:3]):
                print(f"  实体{i+1}: {entity['name']} ({entity['type']}) - {entity.get('confidence', 0):.2f}")
            
            print()
            
        except Exception as e:
            print(f"提取失败: {str(e)}\n")
    
    print("="*60 + "\n")


async def demonstrate_custom_temperature():
    """演示自定义Temperature"""
    print("=== 自定义Temperature演示 ===\n")
    
    api_key = os.getenv("DEEPSEEK_API_KEY", "your_api_key_here")
    if api_key == "your_api_key_here":
        print("请设置DEEPSEEK_API_KEY环境变量")
        return
    
    extractor = create_extraction_service(api_key=api_key)
    text = SAMPLE_TEXTS["equipment_test"]
    
    # 测试不同Temperature值
    temperatures = [0.1, 0.3, 0.5, 0.8]
    
    print(f"测试文本：\n{text}\n")
    
    for temp in temperatures:
        print(f"--- Temperature = {temp} ---")
        
        try:
            result = await extractor.extract_entities_and_relations(
                text, 
                custom_temperature=temp
            )
            
            # 分析质量
            quality = extractor.analyze_extraction_quality(result)
            
            print(f"实体数量: {quality['extraction_summary']['entity_count']}")
            print(f"关系数量: {quality['extraction_summary']['relation_count']}")
            print(f"平均实体置信度: {quality['extraction_summary']['avg_entity_confidence']:.2f}")
            print(f"平均关系置信度: {quality['extraction_summary']['avg_relation_confidence']:.2f}")
            print()
            
        except Exception as e:
            print(f"提取失败: {str(e)}\n")
    
    print("="*60 + "\n")


async def demonstrate_adaptive_extraction():
    """演示自适应提取"""
    print("=== 自适应提取演示 ===\n")
    
    api_key = os.getenv("DEEPSEEK_API_KEY", "your_api_key_here")
    if api_key == "your_api_key_here":
        print("请设置DEEPSEEK_API_KEY环境变量")
        return
    
    extractor = create_extraction_service(api_key=api_key)
    
    # 使用技术规格文本（较复杂）
    text = SAMPLE_TEXTS["technical_specification"]
    print(f"测试文本：\n{text}\n")
    
    print("执行自适应提取...")
    
    try:
        result = await extractor.adaptive_extract(text, quality_threshold=0.8)
        
        quality = extractor.analyze_extraction_quality(result)
        
        print("自适应提取结果:")
        print(f"最终Temperature: {result.metadata['temperature_used']}")
        print(f"实体数量: {quality['extraction_summary']['entity_count']}")
        print(f"关系数量: {quality['extraction_summary']['relation_count']}")
        print(f"整体置信度: {quality['extraction_summary']['overall_confidence']:.2f}")
        
        # 显示实体类型分布
        print("\n实体类型分布:")
        for etype, count in quality['entity_type_distribution'].items():
            print(f"  {etype}: {count}")
        
        # 显示关系类型分布  
        print("\n关系类型分布:")
        for rtype, count in quality['relation_type_distribution'].items():
            print(f"  {rtype}: {count}")
            
    except Exception as e:
        print(f"自适应提取失败: {str(e)}")
    
    print("\n" + "="*60 + "\n")


async def demonstrate_batch_processing():
    """演示批量处理"""
    print("=== 批量处理演示 ===\n")
    
    api_key = os.getenv("DEEPSEEK_API_KEY", "your_api_key_here")
    if api_key == "your_api_key_here":
        print("请设置DEEPSEEK_API_KEY环境变量")
        return
    
    extractor = create_extraction_service(
        api_key=api_key,
        goal=ExtractionGoal.BALANCED
    )
    
    # 批量处理所有示例文本
    texts = list(SAMPLE_TEXTS.values())
    print(f"批量处理 {len(texts)} 个文本...")
    
    try:
        results = await extractor.batch_extract(texts, custom_temperature=0.3)
        
        print("批量处理结果汇总:")
        total_entities = sum(len(r.entities) for r in results)
        total_relations = sum(len(r.relations) for r in results)
        avg_confidence = sum(r.confidence_scores.get('overall_confidence', 0) for r in results) / len(results)
        total_time = sum(r.processing_time for r in results)
        
        print(f"总实体数量: {total_entities}")
        print(f"总关系数量: {total_relations}")
        print(f"平均置信度: {avg_confidence:.2f}")
        print(f"总处理时间: {total_time:.2f}秒")
        
        # 显示每个文本的结果
        for i, result in enumerate(results):
            print(f"\n文本{i+1}: {len(result.entities)}个实体, {len(result.relations)}个关系")
            
    except Exception as e:
        print(f"批量处理失败: {str(e)}")
    
    print("\n" + "="*60 + "\n")


async def demonstrate_temperature_optimization():
    """演示Temperature优化建议"""
    print("=== Temperature优化建议演示 ===\n")
    
    advisor = TemperatureAdvisor()
    
    scenarios = [
        {
            "task": ExtractionTask.ENTITY_EXTRACTION,
            "goal": ExtractionGoal.HIGH_PRECISION,
            "text_complexity": "low",
            "domain_specificity": "high",
            "description": "简单EMC标准文档的精确实体提取"
        },
        {
            "task": ExtractionTask.RELATION_EXTRACTION, 
            "goal": ExtractionGoal.CREATIVE,
            "text_complexity": "high",
            "domain_specificity": "medium",
            "description": "复杂技术文档的创造性关系发现"
        },
        {
            "task": ExtractionTask.COMBINED_EXTRACTION,
            "goal": ExtractionGoal.BALANCED,
            "text_complexity": "medium", 
            "domain_specificity": "high",
            "description": "一般EMC报告的平衡提取"
        }
    ]
    
    for scenario in scenarios:
        print(f"场景: {scenario['description']}")
        print(f"任务: {scenario['task'].value}")
        print(f"目标: {scenario['goal'].value}")
        print(f"文本复杂度: {scenario['text_complexity']}")
        print(f"领域特异性: {scenario['domain_specificity']}")
        
        # 获取基础推荐
        base_rec = advisor.get_recommendation(scenario['task'], scenario['goal'])
        print(f"基础推荐Temperature: {base_rec.recommended_temp}")
        
        # 获取优化建议
        optimal_temp = advisor.suggest_optimal_temperature(
            task=scenario['task'],
            goal=scenario['goal'], 
            text_complexity=scenario['text_complexity'],
            domain_specificity=scenario['domain_specificity']
        )
        print(f"优化后Temperature: {optimal_temp}")
        print(f"调整幅度: {optimal_temp - base_rec.recommended_temp:+.2f}")
        print()
    
    print("="*60 + "\n")


def load_config_example():
    """演示配置文件加载"""
    print("=== 配置文件示例 ===\n")
    
    try:
        with open("deepseek_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        print("成功加载配置文件:")
        print(f"API端点: {config['deepseek_api']['base_url']}")
        print(f"默认模型: {config['deepseek_api']['model']}")
        
        print("\n可用预设配置:")
        for name, preset in config['extraction_presets'].items():
            print(f"  {name}: {preset['description']} (temp={preset['temperature']})")
        
        print(f"\n支持的EMC实体类型数量: {len(config['emc_domain_config']['default_entities'])}")
        print(f"支持的EMC关系类型数量: {len(config['emc_domain_config']['default_relations'])}")
        
    except FileNotFoundError:
        print("配置文件不存在，请确保deepseek_config.json在当前目录")
    except Exception as e:
        print(f"配置文件加载失败: {str(e)}")
    
    print("\n" + "="*60 + "\n")


async def main():
    """主演示函数"""
    print("DeepSeek实体关系提取器 - 完整功能演示\n")
    print("="*80)
    
    # 1. Temperature推荐系统
    await demonstrate_temperature_recommendations()
    
    # 2. 配置文件示例
    load_config_example()
    
    # 3. 基础提取功能（需要API密钥）
    print("注意：以下演示需要有效的DEEPSEEK_API_KEY环境变量")
    print("如果没有API密钥，可以跳过实际API调用部分\n")
    
    # await demonstrate_basic_extraction()
    # await demonstrate_custom_temperature() 
    # await demonstrate_adaptive_extraction()
    # await demonstrate_batch_processing()
    
    # 4. Temperature优化建议
    await demonstrate_temperature_optimization()
    
    print("演示完成！")
    print("\n使用说明:")
    print("1. 设置环境变量: export DEEPSEEK_API_KEY='your_key'")
    print("2. 取消注释上面的演示函数来测试实际API调用")
    print("3. 根据需要修改deepseek_config.json配置文件")
    print("4. 参考示例代码集成到您的项目中")


if __name__ == "__main__":
    asyncio.run(main())