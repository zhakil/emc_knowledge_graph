#!/usr/bin/env python3
"""
前端访问测试脚本
"""
import requests
import time

def test_frontend_access():
    """测试前端可访问性"""
    print("🌐 测试前端访问...")
    
    try:
        # 尝试访问前端主页
        response = requests.get("http://localhost:3000", timeout=10)
        
        if response.status_code == 200:
            print("✅ 前端主页访问成功")
            print(f"   状态码: {response.status_code}")
            print(f"   内容长度: {len(response.text)} 字符")
            
            # 检查是否包含React应用标识
            if "react" in response.text.lower() or "root" in response.text:
                print("✅ 检测到React应用")
            else:
                print("⚠️  未检测到React应用特征")
                
            return True
        else:
            print(f"❌ 前端访问失败，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectRefused:
        print("❌ 连接被拒绝 - 前端服务可能未启动")
        return False
    except requests.exceptions.Timeout:
        print("❌ 连接超时 - 前端响应缓慢")
        return False
    except Exception as e:
        print(f"❌ 访问失败: {e}")
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n🔧 测试API端点...")
    
    endpoints = [
        "/api/system/status",
        "/api/system/statistics", 
        "/api/files",
        "/api/settings"
    ]
    
    success_count = 0
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - 正常")
                success_count += 1
            else:
                print(f"❌ {endpoint} - 状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - 错误: {e}")
    
    print(f"\nAPI测试结果: {success_count}/{len(endpoints)} 端点正常")
    return success_count == len(endpoints)

if __name__ == "__main__":
    print("🚀 EMC知识图谱 - 前端访问测试")
    print("=" * 50)
    
    # 等待前端完全启动
    print("等待前端启动完成...")
    time.sleep(3)
    
    # 测试前端
    frontend_ok = test_frontend_access()
    
    # 测试API
    api_ok = test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("📋 测试总结")
    print("=" * 50)
    
    if frontend_ok and api_ok:
        print("🎉 所有测试通过！")
        print("✅ 前端: http://localhost:3000 - 可访问")
        print("✅ 后端: http://localhost:8000 - 可访问")
        print("\n💡 解决方案:")
        print("1. 如果浏览器仍然无法访问，请:")
        print("   - 清除浏览器缓存")
        print("   - 尝试无痕模式")
        print("   - 检查防火墙设置")
        print("2. 如果是远程访问，请确保端口转发正确")
    else:
        print("⚠️  部分测试失败")
        if not frontend_ok:
            print("❌ 前端访问失败")
        if not api_ok:
            print("❌ 后端API部分失败")