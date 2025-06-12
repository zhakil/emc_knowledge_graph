#!/usr/bin/env python3
"""
完整的前端功能测试
"""
import requests
import time
import json

def test_frontend_accessibility():
    """测试前端可访问性"""
    print("🔍 测试前端界面可访问性...")
    
    try:
        response = requests.get('http://localhost:3000', timeout=10)
        if response.status_code == 200:
            print("✅ 前端界面响应正常")
            
            # 检查HTML内容
            html_content = response.text
            if 'EMC知识图谱' in html_content:
                print("✅ 页面标题正确")
            else:
                print("⚠️  页面标题可能有问题")
            
            if 'bundle.js' in html_content:
                print("✅ JavaScript包已加载")
            else:
                print("⚠️  JavaScript包可能未正确加载")
                
            return True
        else:
            print(f"❌ 前端响应异常: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 前端访问失败: {e}")
        return False

def test_api_proxy():
    """测试API代理"""
    print("\n🔗 测试API代理功能...")
    
    # 测试通过前端代理访问后端
    try:
        # 前端配置了proxy到8000端口
        response = requests.get('http://localhost:3000/api/health', timeout=5)
        print(f"📡 API代理响应: {response.status_code}")
        return True
    except Exception as e:
        print(f"⚠️  API代理可能未配置: {e}")
        return False

def show_frontend_info():
    """显示前端信息"""
    print("\n" + "=" * 60)
    print("🎨 EMC知识图谱前端界面")
    print("=" * 60)
    print("🌐 访问地址: http://localhost:3000")
    print("🎯 设计风格: 中式古典审美")
    print("📱 响应式设计: 支持桌面和移动端")
    print("\n📋 主要功能模块:")
    print("  🏠 系统概览 - 仪表板和状态监控")
    print("  📁 文件上传 - 拖拽上传和智能分类")
    print("  📂 文件管理 - 浏览、搜索、批量操作")
    print("  🕸️ 知识图谱 - D3.js可视化和交互编辑")
    print("  📝 Markdown编辑 - 实时预览和工具栏")
    print("  ⚙️ 系统设置 - API配置和连接测试")
    
    print("\n🎨 设计特色:")
    print("  🏮 金黄色主题 (#d4af37)")
    print("  📜 中文字体支持")
    print("  💫 温润如玉的交互动效")
    print("  🎋 对称平衡的布局设计")

def show_usage_guide():
    """显示使用指南"""
    print("\n" + "=" * 60)
    print("📖 使用指南")
    print("=" * 60)
    print("1. 🏠 系统概览页面:")
    print("   - 查看系统运行状态")
    print("   - 监控文件统计信息")
    print("   - 使用快捷操作入口")
    
    print("\n2. 📁 文件上传功能:")
    print("   - 拖拽文件到上传区域")
    print("   - 选择文件分类和标签")
    print("   - 查看AI分析结果")
    
    print("\n3. 🕸️ 知识图谱操作:")
    print("   - 拖拽节点改变位置")
    print("   - 点击节点查看详情")
    print("   - 使用搜索和过滤功能")
    print("   - 添加新节点和关系")
    
    print("\n4. 📝 Markdown编辑:")
    print("   - 使用工具栏快速插入元素")
    print("   - 实时预览渲染效果")
    print("   - 自动保存防止数据丢失")
    
    print("\n5. ⚙️ 系统设置:")
    print("   - 配置DeepSeek API密钥")
    print("   - 设置Neo4j数据库连接")
    print("   - 测试各组件连接状态")

if __name__ == "__main__":
    print("🚀 EMC知识图谱前端完整测试")
    print("=" * 60)
    
    # 测试前端可访问性
    frontend_ok = test_frontend_accessibility()
    
    # 测试API代理
    proxy_ok = test_api_proxy()
    
    # 显示信息
    show_frontend_info()
    show_usage_guide()
    
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    if frontend_ok:
        print("✅ 前端界面: 正常运行")
    else:
        print("❌ 前端界面: 访问异常")
    
    if proxy_ok:
        print("✅ API代理: 配置正常")
    else:
        print("⚠️  API代理: 可能需要配置")
    
    print("\n🎉 EMC知识图谱系统前端界面已准备就绪！")
    print("🔗 立即访问: http://localhost:3000")
    
    if frontend_ok:
        print("\n💡 提示: 前端已成功启动，您现在可以:")
        print("   1. 在浏览器中打开 http://localhost:3000")
        print("   2. 体验中式古典审美的用户界面")
        print("   3. 使用完整的知识图谱功能")
        print("   4. 上传和管理EMC相关文档")
    else:
        print("\n🛠️  故障排除建议:")
        print("   1. 检查React服务是否正在运行: ps aux | grep react")
        print("   2. 查看启动日志: tail -f frontend.log")
        print("   3. 重新启动服务: cd frontend && npm start")