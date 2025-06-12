#!/usr/bin/env python3
"""
检查前端服务状态
"""
import requests
import time
import subprocess

def check_frontend_status():
    """检查前端服务状态"""
    print("🔍 检查EMC知识图谱前端服务状态...")
    print("=" * 50)
    
    # 检查端口是否在监听
    try:
        result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
        if ':3000' in result.stdout:
            print("✅ 端口3000正在监听")
        else:
            print("❌ 端口3000未在监听")
            return False
    except Exception as e:
        print(f"⚠️  无法检查端口状态: {e}")
    
    # 检查React进程
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'react-scripts' in result.stdout:
            print("✅ React开发服务器进程正在运行")
        else:
            print("❌ React开发服务器进程未运行")
            return False
    except Exception as e:
        print(f"⚠️  无法检查进程状态: {e}")
    
    # 尝试访问前端服务
    print("\n🌐 尝试访问前端服务...")
    max_retries = 6
    for i in range(max_retries):
        try:
            response = requests.get('http://localhost:3000', timeout=5)
            if response.status_code == 200:
                print(f"✅ 前端服务响应正常 (状态码: {response.status_code})")
                print(f"📄 响应长度: {len(response.text)} 字符")
                
                # 检查是否包含预期内容
                if 'EMC' in response.text or 'root' in response.text:
                    print("✅ 页面内容正常")
                else:
                    print("⚠️  页面内容可能有问题")
                
                return True
            else:
                print(f"⚠️  前端服务响应异常 (状态码: {response.status_code})")
        except requests.exceptions.ConnectionError:
            print(f"⏳ 第{i+1}次尝试: 连接失败，等待服务启动...")
            time.sleep(5)
        except requests.exceptions.Timeout:
            print(f"⏳ 第{i+1}次尝试: 响应超时，等待服务启动...")
            time.sleep(5)
        except Exception as e:
            print(f"❌ 第{i+1}次尝试失败: {e}")
            time.sleep(5)
    
    print("❌ 前端服务无法访问")
    return False

def show_service_info():
    """显示服务信息"""
    print("\n" + "=" * 50)
    print("📋 服务信息")
    print("=" * 50)
    print("🌐 前端地址: http://localhost:3000")
    print("🔌 API地址: http://localhost:8000")
    print("📄 日志文件: frontend/frontend.log")
    print("\n💡 常用命令:")
    print("   tail -f frontend/frontend.log  # 查看实时日志")
    print("   ps aux | grep react           # 查看React进程")
    print("   netstat -tlnp | grep 3000     # 查看端口状态")
    print("\n🛠️  故障排除:")
    print("   1. 检查Node.js是否安装: node --version")
    print("   2. 检查npm是否安装: npm --version")
    print("   3. 重新安装依赖: cd frontend && npm install")
    print("   4. 重启服务: cd frontend && npm start")

if __name__ == "__main__":
    success = check_frontend_status()
    show_service_info()
    
    if success:
        print("\n🎉 前端服务运行正常！")
        print("🔗 请在浏览器中访问: http://localhost:3000")
    else:
        print("\n⚠️  前端服务可能还在启动中，请稍等片刻后重试")
        print("📄 查看启动日志: tail -f frontend/frontend.log")