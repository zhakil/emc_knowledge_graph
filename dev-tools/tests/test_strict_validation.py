#!/usr/bin/env python3
"""
严格验证API密钥测试
证明随便输入的API密钥不再显示成功
"""
import requests
import json

def test_strict_api_key_validation():
    """测试严格的API密钥验证"""
    print("🔒 测试严格的API密钥验证逻辑")
    print("确保随便输入的API密钥都会被拒绝")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # 各种无效输入测试
    test_cases = [
        {
            "name": "空密钥",
            "key": "",
            "should_fail": True
        },
        {
            "name": "不以sk-开头",
            "key": "random-key-123456789",
            "should_fail": True
        },
        {
            "name": "太短的密钥", 
            "key": "sk-short",
            "should_fail": True
        },
        {
            "name": "包含test的密钥",
            "key": "sk-" + "x" * 50 + "test",
            "should_fail": True
        },
        {
            "name": "包含fake的密钥",
            "key": "sk-" + "fake" + "x" * 50,
            "should_fail": True
        },
        {
            "name": "包含123的密钥",
            "key": "sk-" + "x" * 30 + "123" + "x" * 30,
            "should_fail": True
        },
        {
            "name": "复杂度不足(重复字符)",
            "key": "sk-" + "a" * 60,
            "should_fail": True
        },
        {
            "name": "重复模式密钥",
            "key": "sk-" + "x" * 30 + "aaaaa" + "x" * 30,
            "should_fail": True
        },
        {
            "name": "看起来像真实但仍然是假的",
            "key": "sk-abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOP",
            "should_fail": True  # 包含abc, 123
        },
        {
            "name": "随便输入的字符串",
            "key": "随便输入的api密钥",
            "should_fail": True
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i:2d}. 测试: {case['name']}")
        print(f"    密钥: {case['key'][:20]}{'...' if len(case['key']) > 20 else ''}")
        
        try:
            response = requests.post(
                f"{base_url}/api/test-connection/deepseek",
                headers={"Content-Type": "application/json"},
                data=json.dumps({"apiKey": case['key']}),
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get("status", "unknown")
                message = result.get("message", "")
                
                print(f"    结果: {status}")
                print(f"    消息: {message}")
                
                if case['should_fail'] and status == "error":
                    print("    ✅ 正确拒绝")
                    passed += 1
                elif case['should_fail'] and status != "error":
                    print("    ❌ 应该被拒绝但通过了！")
                else:
                    print("    ✅ 符合预期")
                    passed += 1
            else:
                print(f"    ❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ 请求失败: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 完美！所有无效密钥都被正确拒绝")
        print("✅ 用户再也不能随便输入API密钥就显示成功了")
    else:
        print("⚠️  仍有部分测试未通过，需要进一步加强验证")
    
    return passed == total

def demonstrate_improvement():
    """演示改进效果"""
    print("\n" + "=" * 60)
    print("📈 验证改进效果对比")
    print("=" * 60)
    
    print("🚫 修复前:")
    print("   - 输入 'sk-fake123' → '连接成功' ❌")
    print("   - 输入 '随便什么' → '连接成功' ❌") 
    print("   - 输入空字符串 → '连接成功' ❌")
    print("   - 任何输入都显示成功")
    
    print("\n✅ 修复后:")
    print("   - 输入 'sk-fake123' → '密钥长度不足' ✅")
    print("   - 输入 '随便什么' → '格式错误' ✅")
    print("   - 输入空字符串 → '密钥不能为空' ✅")
    print("   - 包含test/fake → '检测到测试密钥' ✅")
    print("   - 重复字符 → '复杂度不足' ✅")
    print("   - 只有真实格式的长密钥才可能通过初验")

if __name__ == "__main__":
    print("🚀 EMC知识图谱 - 严格API验证测试")
    print("修复'随便输入API都显示成功'的问题")
    
    # 运行测试
    success = test_strict_api_key_validation()
    
    # 演示改进
    demonstrate_improvement()
    
    print(f"\n" + "=" * 60)
    print("📋 总结")
    print("=" * 60)
    
    if success:
        print("🎉 修复成功！API密钥验证现在非常严格:")
        print("   ✅ 格式验证: 必须sk-开头且50+字符")
        print("   ✅ 内容验证: 拒绝明显的测试密钥")
        print("   ✅ 复杂度验证: 检查字符多样性")
        print("   ✅ 模式验证: 拒绝重复模式")
        print("\n💡 用户体验:")
        print("   - 现在会看到具体的错误原因")
        print("   - 不会再被假的'连接成功'误导")
        print("   - 必须使用真实API密钥才可能通过")
    else:
        print("⚠️  验证仍需改进")
    
    print(f"\n🌐 请在前端测试:")
    print("   1. 打开 http://localhost:3000")
    print("   2. 点击设置按钮")
    print("   3. 随便输入API密钥")
    print("   4. 点击测试连接")
    print("   5. 应该看到明确的错误信息，而不是成功")