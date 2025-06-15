#!/usr/bin/env python3
import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'md'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 文件数据库（简单的JSON存储）
FILES_DB = 'files_db.json'

def load_files_db():
    if os.path.exists(FILES_DB):
        with open(FILES_DB, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_files_db(data):
    with open(FILES_DB, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/files', methods=['GET'])
def get_files():
    """获取文件列表"""
    files_db = load_files_db()
    files_list = []
    
    for file_id, file_info in files_db.items():
        file_path = os.path.join(UPLOAD_FOLDER, file_info['filename'])
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            files_list.append({
                'id': file_id,
                'name': file_info['original_name'],
                'filename': file_info['filename'],
                'size': stat.st_size,
                'upload_time': file_info['upload_time'],
                'extraction_status': file_info.get('extraction_status', 'not_extracted'),
                'file_type': file_info.get('file_type', 'unknown')
            })
    
    return jsonify({'files': files_list, 'total': len(files_list)})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传文件"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件被上传'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        stored_filename = f"{file_id}.{file_ext}"
        
        # 保存文件
        file_path = os.path.join(UPLOAD_FOLDER, stored_filename)
        file.save(file_path)
        
        # 更新文件数据库
        files_db = load_files_db()
        files_db[file_id] = {
            'original_name': filename,
            'filename': stored_filename,
            'upload_time': datetime.now().isoformat(),
            'extraction_status': 'not_extracted',
            'file_type': file_ext
        }
        save_files_db(files_db)
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'message': f'文件 {filename} 上传成功'
        })
    
    return jsonify({'error': '不支持的文件类型'}), 400

@app.route('/api/files/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """删除文件"""
    files_db = load_files_db()
    
    if file_id not in files_db:
        return jsonify({'error': '文件不存在'}), 404
    
    # 删除物理文件
    file_info = files_db[file_id]
    file_path = os.path.join(UPLOAD_FOLDER, file_info['filename'])
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # 从数据库中删除
    del files_db[file_id]
    save_files_db(files_db)
    
    return jsonify({'success': True, 'message': '文件删除成功'})

@app.route('/api/files/<file_id>/content', methods=['GET'])
def get_file_content(file_id):
    """获取文件内容（仅支持文本文件）"""
    files_db = load_files_db()
    
    if file_id not in files_db:
        return jsonify({'error': '文件不存在'}), 404
    
    file_info = files_db[file_id]
    file_path = os.path.join(UPLOAD_FOLDER, file_info['filename'])
    
    if not os.path.exists(file_path):
        return jsonify({'error': '文件不存在'}), 404
    
    # 只支持文本文件
    if file_info['file_type'] in ['txt', 'md']:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({'content': content, 'file_type': file_info['file_type']})
        except UnicodeDecodeError:
            return jsonify({'error': '无法读取文件内容，可能不是文本文件'}), 400
    else:
        return jsonify({'error': '不支持的文件类型，无法编辑'}), 400

@app.route('/api/files/<file_id>/content', methods=['PUT'])
def update_file_content(file_id):
    """更新文件内容"""
    files_db = load_files_db()
    
    if file_id not in files_db:
        return jsonify({'error': '文件不存在'}), 404
    
    data = request.get_json()
    if 'content' not in data:
        return jsonify({'error': '缺少文件内容'}), 400
    
    file_info = files_db[file_id]
    file_path = os.path.join(UPLOAD_FOLDER, file_info['filename'])
    
    # 只支持文本文件
    if file_info['file_type'] in ['txt', 'md']:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(data['content'])
            return jsonify({'success': True, 'message': '文件保存成功'})
        except Exception as e:
            return jsonify({'error': f'保存文件失败: {str(e)}'}), 500
    else:
        return jsonify({'error': '不支持的文件类型，无法编辑'}), 400

@app.route('/api/files/batch-delete', methods=['POST'])
def batch_delete_files():
    """批量删除文件"""
    data = request.get_json()
    if 'file_ids' not in data:
        return jsonify({'error': '缺少文件ID列表'}), 400
    
    file_ids = data['file_ids']
    files_db = load_files_db()
    deleted_count = 0
    errors = []
    
    for file_id in file_ids:
        if file_id in files_db:
            try:
                # 删除物理文件
                file_info = files_db[file_id]
                file_path = os.path.join(UPLOAD_FOLDER, file_info['filename'])
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                # 从数据库中删除
                del files_db[file_id]
                deleted_count += 1
            except Exception as e:
                errors.append(f"删除文件 {file_id} 失败: {str(e)}")
        else:
            errors.append(f"文件 {file_id} 不存在")
    
    save_files_db(files_db)
    
    return jsonify({
        'success': True,
        'deleted_count': deleted_count,
        'errors': errors,
        'message': f'成功删除 {deleted_count} 个文件'
    })

@app.route('/api/extract', methods=['POST'])
def extract_entities():
    """实体关系提取（模拟）"""
    data = request.get_json()
    if 'file_ids' not in data:
        return jsonify({'error': '缺少文件ID列表'}), 400
    
    file_ids = data['file_ids']
    files_db = load_files_db()
    
    # 模拟提取过程
    for file_id in file_ids:
        if file_id in files_db:
            files_db[file_id]['extraction_status'] = 'extracted'
    
    save_files_db(files_db)
    
    return jsonify({
        'success': True,
        'message': f'已完成 {len(file_ids)} 个文件的实体关系提取',
        'extracted_files': file_ids
    })

@app.route('/')
def serve_index():
    """提供主页面"""
    return send_from_directory('build', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """提供静态文件"""
    return send_from_directory('build', filename)

if __name__ == '__main__':
    print("🚀 启动EMC知识图谱API服务器...")
    print("📡 API端口: 5000")
    print("🌐 前端地址: http://localhost:5000")
    print("📁 上传目录:", os.path.abspath(UPLOAD_FOLDER))
    
    app.run(host='0.0.0.0', port=5000, debug=True)