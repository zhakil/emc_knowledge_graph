#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys

PORT = 3001
os.chdir('build')

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")

print("🚀 启动EMC知识图谱系统...")
print(f"📡 服务器端口: {PORT}")
print(f"📁 服务目录: {os.getcwd()}")

try:
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"✅ EMC知识图谱系统已启动: http://localhost:{PORT}")
        print("按 Ctrl+C 停止服务器")
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\n🛑 服务器已停止")
except Exception as e:
    print(f"❌ 服务器启动失败: {e}")