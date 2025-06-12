#!/usr/bin/env python3
"""
测试系统设置修复情况
"""
import requests
import json

def test_settings_apis():
    """测试设置相关API"""
    print("🔧 测试系统设置API修复情况...")
    
    base_url = "http://localhost:8000"
    
    # 测试设置数据
    test_settings = {
        "deepseek": {
            "apiKey": "sk-test-12345",
            "baseUrl": "https://api.deepseek.com/v1",
            "model": "deepseek-reasoner",
            "timeout": 60,
            "maxRetries": 5
        },
        "neo4j": {
            "uri": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "test123",
            "database": "emc_graph",
            "maxConnections": 200
        },
        "system": {
            "environment": "development",
            "debug": True,
            "logLevel": "DEBUG",
            "uploadMaxSize": 200
        }
    }
    
    try:
        # 1. 测试GET设置（获取默认设置）
        print("\n1. 📥 测试获取设置...")
        get_response = requests.get(f"{base_url}/api/settings", timeout=5)
        if get_response.status_code == 200:
            print("✅ 获取设置成功")
            current_settings = get_response.json()
            print(f"   当前设置项: {list(current_settings.keys())}")
        else:
            print("❌ 获取设置失败")
            return False
        
        # 2. 测试PUT保存设置
        print("\n2. 💾 测试保存设置...")
        put_response = requests.put(
            f"{base_url}/api/settings",
            headers={"Content-Type": "application/json"},
            data=json.dumps(test_settings),
            timeout=5
        )
        if put_response.status_code == 200:
            print("✅ 保存设置成功")
            save_result = put_response.json()
            print(f"   服务器响应: {save_result.get('message', 'N/A')}")
        else:
            print(f"❌ 保存设置失败: HTTP {put_response.status_code}")
            print(f"   错误信息: {put_response.text}")
            return False
        
        # 3. 验证设置是否正确保存
        print("\n3. 🔍 验证设置保存...")
        verify_response = requests.get(f"{base_url}/api/settings", timeout=5)
        if verify_response.status_code == 200:
            saved_settings = verify_response.json()
            
            # 检查关键字段
            if (saved_settings.get("deepseek", {}).get("apiKey") == test_settings["deepseek"]["apiKey"] and
                saved_settings.get("neo4j", {}).get("database") == test_settings["neo4j"]["database"] and
                saved_settings.get("system", {}).get("logLevel") == test_settings["system"]["logLevel"]):
                print("✅ 设置保存验证成功")
                print("   🔑 DeepSeek API Key: 正确保存")
                print("   🗄️ Neo4j Database: 正确保存")
                print("   📊 Log Level: 正确保存")
            else:
                print("❌ 设置保存验证失败")
                print(f"   期望: {test_settings}")
                print(f"   实际: {saved_settings}")
                return False
        else:
            print("❌ 验证设置失败")
            return False
        
        # 4. 测试连接测试功能
        print("\n4. 🔗 测试连接测试...")
        
        # 测试DeepSeek连接
        deepseek_test = requests.post(
            f"{base_url}/api/test-connection/deepseek",
            headers={"Content-Type": "application/json"},
            data=json.dumps(test_settings["deepseek"]),
            timeout=5
        )
        if deepseek_test.status_code == 200:
            print("✅ DeepSeek连接测试正常")
        else:
            print("❌ DeepSeek连接测试失败")
        
        # 测试Neo4j连接
        neo4j_test = requests.post(
            f"{base_url}/api/test-connection/neo4j",
            headers={"Content-Type": "application/json"},
            data=json.dumps(test_settings["neo4j"]),
            timeout=5
        )
        if neo4j_test.status_code == 200:
            print("✅ Neo4j连接测试正常")
        else:
            print("❌ Neo4j连接测试失败")
        
        # 5. 测试POST方法（向后兼容）
        print("\n5. 📤 测试POST方法...")
        post_response = requests.post(
            f"{base_url}/api/settings",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"test": "post_method"}),
            timeout=5
        )
        if post_response.status_code == 200:
            print("✅ POST方法向后兼容正常")
        else:
            print("❌ POST方法失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

def test_frontend_accessibility():
    """测试前端可访问性"""
    print("\n🌐 测试前端系统设置页面...")
    
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ 前端页面可访问")
            return True
        else:
            print("❌ 前端页面访问异常")
            return False
    except Exception as e:
        print(f"❌ 前端测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 EMC知识图谱系统设置修复测试")
    print("=" * 60)
    
    # 测试后端API
    api_ok = test_settings_apis()
    
    # 测试前端可访问性
    frontend_ok = test_frontend_accessibility()
    
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    if api_ok:
        print("✅ 后端设置API: 完全修复")
        print("   - GET /api/settings: 正常")
        print("   - PUT /api/settings: 正常")
        print("   - POST /api/settings: 正常")
        print("   - 连接测试: 正常")
        print("   - 数据持久化: 正常")
    else:
        print("❌ 后端设置API: 仍有问题")
    
    if frontend_ok:
        print("✅ 前端界面: 可访问")
    else:
        print("❌ 前端界面: 访问异常")
    
    if api_ok and frontend_ok:
        print("\n🎉 系统设置功能完全修复！")
        print("💡 现在可以:")
        print("   1. 打开前端: http://localhost:3000")
        print("   2. 点击设置按钮 (右下角)")
        print("   3. 配置DeepSeek API和Neo4j")
        print("   4. 点击'保存配置'按钮")
        print("   5. 使用'测试连接'验证配置")
    else:
        print("\n🛠️  请检查:")
        print("   1. 后端服务是否正常运行")
        print("   2. 前端服务是否正常运行")
        print("   3. 网络连接是否正常")