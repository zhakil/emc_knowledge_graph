#!/usr/bin/env python3
"""
测试Dashboard修复情况
"""
import requests
import time

def test_frontend_dashboard():
    """测试前端Dashboard页面"""
    print("🔍 测试前端Dashboard修复情况...")
    
    try:
        # 测试前端可访问性
        response = requests.get('http://localhost:3000', timeout=10)
        if response.status_code == 200:
            print("✅ 前端页面可访问")
        else:
            print("❌ 前端访问异常")
            return False
    except Exception as e:
        print(f"❌ 前端访问失败: {e}")
        return False
    
    # 测试后端API接口
    try:
        # 测试统计API
        stats_response = requests.get('http://localhost:8000/api/system/statistics', timeout=5)
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print("✅ 统计API正常响应")
            print(f"   - 文件总数: {stats_data.get('totalFiles', 'N/A')}")
            print(f"   - 知识节点: {stats_data.get('totalNodes', 'N/A')}")
            print(f"   - 存储使用: {stats_data.get('storageUsed', 'N/A')}%")
            
            # 验证数据类型
            storage_used = stats_data.get('storageUsed')
            if isinstance(storage_used, (int, float)):
                print("✅ 存储数据类型正确 (数字)")
            else:
                print(f"⚠️  存储数据类型异常: {type(storage_used)}")
        else:
            print("❌ 统计API响应异常")
            return False
            
    except Exception as e:
        print(f"❌ 后端API测试失败: {e}")
        return False
    
    return True

def test_backend_apis():
    """测试所有后端API端点"""
    print("\n🔧 测试后端API端点...")
    
    apis = [
        ('/api/system/status', '系统状态'),
        ('/api/system/statistics', '系统统计'),
        ('/api/system/activities', '系统活动'),
        ('/api/files', '文件管理'),
        ('/api/knowledge-graph/nodes', '知识图谱'),
        ('/api/markdown-files', 'Markdown文件'),
        ('/api/settings', '系统设置')
    ]
    
    success_count = 0
    total_count = len(apis)
    
    for endpoint, name in apis:
        try:
            response = requests.get(f'http://localhost:8000{endpoint}', timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: 正常")
                success_count += 1
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: 连接失败")
    
    print(f"\n📊 API测试结果: {success_count}/{total_count} 个端点正常")
    return success_count == total_count

if __name__ == "__main__":
    print("🚀 EMC知识图谱Dashboard修复测试")
    print("=" * 50)
    
    # 测试Dashboard
    dashboard_ok = test_frontend_dashboard()
    
    # 测试API端点
    apis_ok = test_backend_apis()
    
    print("\n" + "=" * 50)
    print("📋 测试结果汇总")
    print("=" * 50)
    
    if dashboard_ok:
        print("✅ 前端Dashboard: 修复成功")
    else:
        print("❌ 前端Dashboard: 仍有问题")
    
    if apis_ok:
        print("✅ 后端API: 全部正常")
    else:
        print("⚠️  后端API: 部分异常")
    
    if dashboard_ok and apis_ok:
        print("\n🎉 系统完全修复！Dashboard错误已解决")
        print("💡 建议:")
        print("   1. 刷新浏览器页面 (Ctrl+F5)")
        print("   2. 访问 http://localhost:3000")
        print("   3. 检查浏览器控制台是否还有错误")
    else:
        print("\n🛠️  仍需进一步排查问题")
        print("💡 建议:")
        print("   1. 检查浏览器开发者工具")
        print("   2. 查看网络请求状态")
        print("   3. 确认后端服务正常运行")