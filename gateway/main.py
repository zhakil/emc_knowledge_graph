"""
EMC知识图谱系统 - 完整版网关
包含实用的文件上传界面
"""

import os
import logging
from datetime import datetime
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="EMC知识图谱系统",
    description="实用的EMC知识管理平台",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建上传目录
os.makedirs("/app/uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="/app/uploads"), name="uploads")

@app.get("/")
async def root():
    """系统根路径"""
    return {
        "name": "EMC知识图谱系统",
        "version": "1.0.0",
        "status": "running",
        "快速访问": {
            "📁 文件上传页面": "http://localhost:8001/upload",
            "📖 API文档": "http://localhost:8001/docs", 
            "🔍 健康检查": "http://localhost:8001/health",
            "🧪 测试接口": "http://localhost:8001/api/test"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/upload", response_class=HTMLResponse)
async def upload_page():
    """🚀 实用文件上传界面 - 立即可用"""
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📁 EMC知识图谱 - 文件导入</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; padding: 20px;
            }
            .container { 
                max-width: 900px; margin: 0 auto; 
                background: white; border-radius: 15px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header { 
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white; padding: 30px; text-align: center;
            }
            .header h1 { font-size: 2.5em; margin-bottom: 10px; }
            .header p { opacity: 0.9; font-size: 1.1em; }
            
            .upload-section { padding: 40px; }
            .upload-area { 
                border: 3px dashed #ddd; border-radius: 15px;
                padding: 60px 20px; text-align: center; 
                margin: 20px 0; cursor: pointer;
                transition: all 0.3s ease;
                background: #fafafa;
            }
            .upload-area:hover { 
                border-color: #667eea; background: #f0f4ff;
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.1);
            }
            .upload-area.dragover {
                border-color: #667eea; background: #e8f2ff;
            }
            
            .upload-icon { font-size: 4em; margin-bottom: 20px; opacity: 0.6; }
            .upload-text { font-size: 1.3em; color: #333; margin-bottom: 10px; }
            .upload-hint { color: #666; font-size: 0.95em; }
            
            .file-list { margin: 20px 0; }
            .file-item { 
                background: #f8f9fa; border: 1px solid #e9ecef;
                border-radius: 8px; padding: 15px; margin: 10px 0;
                display: flex; justify-content: space-between; align-items: center;
            }
            .file-info { flex-grow: 1; }
            .file-name { font-weight: bold; color: #333; }
            .file-size { color: #666; font-size: 0.9em; }
            
            .btn { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; border: none; padding: 15px 30px;
                border-radius: 25px; cursor: pointer; font-size: 1.1em;
                transition: all 0.3s ease; margin: 10px 5px;
            }
            .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }
            .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
            
            .btn-danger { background: linear-gradient(135deg, #ff6b6b 0%, #ff5252 100%); }
            .btn-success { background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%); }
            
            .results { margin: 20px 0; }
            .result-item { 
                padding: 15px; margin: 10px 0; border-radius: 8px;
                border-left: 4px solid #28a745;
            }
            .result-success { background: #d4edda; border-color: #28a745; }
            .result-error { background: #f8d7da; border-color: #dc3545; }
            
            .progress { 
                width: 100%; height: 6px; background: #eee; 
                border-radius: 3px; overflow: hidden; margin: 10px 0;
            }
            .progress-bar { 
                height: 100%; background: linear-gradient(90deg, #667eea, #764ba2);
                width: 0%; transition: width 0.3s ease;
            }
            
            .stats { 
                display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px; margin: 20px 0;
            }
            .stat-card { 
                background: #f8f9fa; padding: 20px; border-radius: 10px;
                text-align: center; border: 1px solid #e9ecef;
            }
            .stat-number { font-size: 2em; font-weight: bold; color: #667eea; }
            .stat-label { color: #666; margin-top: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📁 EMC知识图谱文件导入</h1>
                <p>支持 PDF、Word、Excel、CSV、JSON、XML、TXT 等格式</p>
            </div>
            
            <div class="upload-section">
                <div class="upload-area" id="uploadArea">
                    <div class="upload-icon">📤</div>
                    <div class="upload-text">点击选择文件或拖拽文件到此处</div>
                    <div class="upload-hint">支持格式: PDF, DOCX, XLSX, CSV, JSON, XML, TXT</div>
                    <input type="file" id="fileInput" style="display: none;" multiple 
                           accept=".pdf,.docx,.xlsx,.csv,.json,.xml,.txt">
                </div>
                
                <div id="fileList" class="file-list"></div>
                
                <div style="text-align: center;">
                    <button class="btn" onclick="uploadFiles()" id="uploadBtn" disabled>🚀 开始上传</button>
                    <button class="btn btn-danger" onclick="clearFiles()" id="clearBtn" disabled>🗑️ 清空列表</button>
                </div>
                
                <div class="stats" id="stats" style="display: none;">
                    <div class="stat-card">
                        <div class="stat-number" id="totalFiles">0</div>
                        <div class="stat-label">总文件数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="successCount">0</div>
                        <div class="stat-label">成功上传</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="failedCount">0</div>
                        <div class="stat-label">上传失败</div>
                    </div>
                </div>
                
                <div class="progress" id="progressContainer" style="display: none;">
                    <div class="progress-bar" id="progressBar"></div>
                </div>
                
                <div id="results" class="results"></div>
            </div>
        </div>
        
        <script>
            let selectedFiles = [];
            let uploadStats = { total: 0, success: 0, failed: 0 };
            
            // 文件输入和拖拽处理
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            
            uploadArea.addEventListener('click', () => fileInput.click());
            
            fileInput.addEventListener('change', function(e) {
                handleFiles(Array.from(e.target.files));
            });
            
            // 拖拽功能
            uploadArea.addEventListener('dragover', function(e) {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', function(e) {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', function(e) {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                handleFiles(Array.from(e.dataTransfer.files));
            });
            
            function handleFiles(files) {
                selectedFiles = [...selectedFiles, ...files];
                displayFileList();
                updateButtons();
            }
            
            function displayFileList() {
                const fileList = document.getElementById('fileList');
                fileList.innerHTML = '';
                
                selectedFiles.forEach((file, index) => {
                    const fileItem = document.createElement('div');
                    fileItem.className = 'file-item';
                    fileItem.innerHTML = `
                        <div class="file-info">
                            <div class="file-name">📄 ${file.name}</div>
                            <div class="file-size">${(file.size / 1024 / 1024).toFixed(2)} MB</div>
                        </div>
                        <button class="btn btn-danger" onclick="removeFile(${index})" style="padding: 5px 15px;">删除</button>
                    `;
                    fileList.appendChild(fileItem);
                });
                
                document.getElementById('totalFiles').textContent = selectedFiles.length;
                if (selectedFiles.length > 0) {
                    document.getElementById('stats').style.display = 'grid';
                }
            }
            
            function removeFile(index) {
                selectedFiles.splice(index, 1);
                displayFileList();
                updateButtons();
            }
            
            function clearFiles() {
                selectedFiles = [];
                displayFileList();
                updateButtons();
                document.getElementById('results').innerHTML = '';
                document.getElementById('stats').style.display = 'none';
                fileInput.value = '';
            }
            
            function updateButtons() {
                const hasFiles = selectedFiles.length > 0;
                document.getElementById('uploadBtn').disabled = !hasFiles;
                document.getElementById('clearBtn').disabled = !hasFiles;
            }
            
            async function uploadFiles() {
                if (selectedFiles.length === 0) return;
                
                const results = document.getElementById('results');
                const progressContainer = document.getElementById('progressContainer');
                const progressBar = document.getElementById('progressBar');
                
                results.innerHTML = '';
                progressContainer.style.display = 'block';
                uploadStats = { total: selectedFiles.length, success: 0, failed: 0 };
                
                document.getElementById('uploadBtn').disabled = true;
                
                for (let i = 0; i < selectedFiles.length; i++) {
                    const file = selectedFiles[i];
                    const progress = ((i + 1) / selectedFiles.length) * 100;
                    progressBar.style.width = progress + '%';
                    
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    try {
                        const response = await fetch('/api/upload', {
                            method: 'POST',
                            body: formData
                        });
                        
                        const result = await response.json();
                        
                        if (response.ok) {
                            uploadStats.success++;
                            results.innerHTML += `
                                <div class="result-item result-success">
                                    ✅ <strong>${file.name}</strong> 上传成功
                                    <br>📎 <a href="${result.download_url}" target="_blank" style="color: #155724;">点击下载</a>
                                    <br>📊 大小: ${(result.size / 1024).toFixed(1)} KB
                                </div>
                            `;
                        } else {
                            uploadStats.failed++;
                            results.innerHTML += `
                                <div class="result-item result-error">
                                    ❌ <strong>${file.name}</strong> 上传失败
                                    <br>💬 错误: ${result.error || '未知错误'}
                                </div>
                            `;
                        }
                        
                        // 更新统计
                        document.getElementById('successCount').textContent = uploadStats.success;
                        document.getElementById('failedCount').textContent = uploadStats.failed;
                        
                    } catch (error) {
                        uploadStats.failed++;
                        results.innerHTML += `
                            <div class="result-item result-error">
                                ❌ <strong>${file.name}</strong> 网络错误
                                <br>💬 ${error.message}
                            </div>
                        `;
                        document.getElementById('failedCount').textContent = uploadStats.failed;
                    }
                }
                
                progressContainer.style.display = 'none';
                document.getElementById('uploadBtn').disabled = false;
                
                // 上传完成后清空列表
                setTimeout(() => {
                    if (uploadStats.success === uploadStats.total) {
                        clearFiles();
                    }
                }, 2000);
            }
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "services": {
            "api": True,
            "upload_interface": True,
            "upload_directory": os.path.exists("/app/uploads")
        },
        "file_count": len(os.listdir("/app/uploads")),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/test")
async def test_api():
    """API测试"""
    return {
        "message": "EMC知识图谱API测试成功",
        "interfaces": {
            "upload_page": "http://localhost:8001/upload",
            "api_docs": "http://localhost:8001/docs",
            "file_upload": "http://localhost:8001/api/upload"
        },
        "file_stats": {
            "upload_directory": "/app/uploads",
            "files_count": len(os.listdir("/app/uploads"))
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """文件上传API"""
    try:
        # 验证文件类型
        allowed_extensions = {'.pdf', '.docx', '.xlsx', '.csv', '.json', '.xml', '.txt'}
        file_ext = os.path.splitext(file.filename or "")[1].lower()
        
        if file_ext not in allowed_extensions:
            return {
                "error": f"不支持的文件类型: {file_ext}",
                "supported": list(allowed_extensions)
            }
        
        # 保存文件
        file_path = f"/app/uploads/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return {
            "message": "文件上传成功",
            "filename": file.filename,
            "size": len(content),
            "file_type": file_ext,
            "download_url": f"http://localhost:8001/uploads/{file.filename}",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return {"error": f"上传失败: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)