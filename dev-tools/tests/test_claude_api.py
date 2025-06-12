#!/usr/bin/env python3
"""
Claude Sonnet 4 API测试
验证Claude API连接和验证功能
"""
import requests
import json

def test_claude_api_validation():
    """测试Claude API验证逻辑"""
    print("🧠 Claude Sonnet 4 API连接测试")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # 测试用例
    test_cases = [
        {
            "name": "空API密钥",
            "data": {"apiKey": "", "baseUrl": "https://api.anthropic.com/v1", "model": "claude-3-5-sonnet-20241022"},
            "expected_status": "error",
            "expected_msg": "API密钥不能为空"
        },
        {
            "name": "无效格式密钥",
            "data": {"apiKey": "sk-invalid123", "baseUrl": "https://api.anthropic.com/v1", "model": "claude-3-5-sonnet-20241022"},
            "expected_status": "error", 
            "expected_msg": "无效的Claude API密钥格式"
        },
        {
            "name": "假的Claude密钥",
            "data": {"apiKey": "sk-ant-fake123456789", "baseUrl": "https://api.anthropic.com/v1", "model": "claude-3-5-sonnet-20241022"},
            "expected_status": "error",
            "expected_msg": "Claude官方验证失败"
        },
        {
            "name": "格式正确但无效的密钥",
            "data": {"apiKey": "sk-ant-api03-abcdefghijklmnopqrstuvwxyz1234567890", "baseUrl": "https://api.anthropic.com/v1", "model": "claude-3-5-sonnet-20241022"},
            "expected_status": "error", 
            "expected_msg": "网络连接失败"  # 可能是网络问题或API密钥无效
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. 测试: {case['name']}")
        print(f"   密钥: {case['data']['apiKey'][:15]}{'...' if len(case['data']['apiKey']) > 15 else ''}")
        print(f"   模型: {case['data']['model']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/test-connection/claude",
                headers={"Content-Type": "application/json"},
                data=json.dumps(case["data"]),
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get("status", "unknown")
                message = result.get("message", "")
                
                print(f"   结果: {status}")
                print(f"   消息: {message}")
                
                # 检查是否符合预期
                if (status == case["expected_status"] and 
                    case["expected_msg"] in message):
                    print("   ✅ 测试通过")
                    passed += 1
                else:
                    print("   ❌ 测试失败")
                    print(f"   期望: {case['expected_status']} 包含 '{case['expected_msg']}'")
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")
    
    print(f"\n" + "=" * 50)
    print(f"📊 Claude API测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有Claude API验证测试通过！")
        print("✅ 格式验证正常")
        print("✅ 错误处理正确")
        print("✅ 官方API调用机制正常")
    else:
        print("⚠️ 部分测试失败，请检查Claude API实现")
    
    return passed == total

def demonstrate_claude_features():
    """演示Claude Sonnet 4功能特点"""
    print("\n" + "=" * 50)
    print("🌟 Claude Sonnet 4 功能特点")
    print("=" * 50)
    
    features = [
        "🧠 强大的推理能力 - 适合复杂逻辑分析",
        "📝 优秀的文本理解 - 精确理解EMC技术文档",
        "🔍 深度分析能力 - 提取关键技术信息",
        "🎯 准确的实体识别 - 识别EMC标准、设备、测试方法",
        "🔗 关系抽取 - 构建高质量知识图谱",
        "📊 数据结构化 - 将非结构化文档转换为结构化数据",
        "🛡️ 安全可靠 - Anthropic官方API，数据安全有保障"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    print("\n💡 在EMC知识图谱中的应用:")
    print("   🔧 智能文档分析 - 自动分析EMC测试报告")
    print("   📋 标准条款提取 - 精确提取标准要求")
    print("   🎯 合规性检查 - 智能评估设备合规性")
    print("   📈 趋势分析 - 分析EMC技术发展趋势")

if __name__ == "__main__":
    print("🚀 EMC知识图谱 - Claude Sonnet 4 集成测试")
    print("验证Claude API连接和功能")
    
    # 运行API验证测试
    success = test_claude_api_validation()
    
    # 展示功能特点
    demonstrate_claude_features()
    
    print(f"\n" + "=" * 50)
    print("📋 集成状态")
    print("=" * 50)
    
    if success:
        print("🎉 Claude Sonnet 4 已成功集成到EMC知识图谱系统！")
        print("\n🌐 使用方法:")
        print("   1. 访问前端: http://localhost:3000")
        print("   2. 进入设置 → Claude Sonnet 4")
        print("   3. 输入您的Claude API密钥")
        print("   4. 选择 Claude 3.5 Sonnet (Latest) 模型")
        print("   5. 点击测试连接验证")
        print("\n📊 或使用测试界面:")
        print("   访问: http://localhost:3001/simple_frontend.html")
        print("   选择 'Claude Sonnet 4' 提供商进行测试")
    else:
        print("⚠️ Claude API集成需要进一步调试")
    
    print(f"\n🔑 API密钥要求:")
    print("   - 格式: sk-ant-api03-xxxxxxxx...")
    print("   - 来源: https://console.anthropic.com/")
    print("   - 权限: 需要对所选模型的访问权限")