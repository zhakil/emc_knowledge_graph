/**
 * EMC知识图谱客户端 - 功能模块
 * 包含所有页面的完整功能实现
 */

// ================================
// 页面HTML模板
// ================================

// 知识图谱页面HTML
function getGraphHTML() {
    return `
        <div class="grid grid-4" style="margin-bottom: 24px;">
            <div class="card">
                <div class="card-body" style="text-align: center;">
                    <div style="font-size: 2em; color: #1890ff; margin-bottom: 8px;" id="graphNodeCount">0</div>
                    <div style="color: #8c8c8c;">图谱节点</div>
                </div>
            </div>
            <div class="card">
                <div class="card-body" style="text-align: center;">
                    <div style="font-size: 2em; color: #52c41a; margin-bottom: 8px;" id="graphRelCount">0</div>
                    <div style="color: #8c8c8c;">关系连接</div>
                </div>
            </div>
            <div class="card">
                <div class="card-body" style="text-align: center;">
                    <div style="font-size: 2em; color: #faad14; margin-bottom: 8px;">85%</div>
                    <div style="color: #8c8c8c;">连通性</div>
                </div>
            </div>
            <div class="card">
                <div class="card-body" style="text-align: center;">
                    <div style="font-size: 2em; color: #722ed1; margin-bottom: 8px;">3</div>
                    <div style="color: #8c8c8c;">知识域</div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <div class="card-title">🌐 知识图谱可视化</div>
                <div class="graph-controls">
                    <button class="btn btn-sm" onclick="resetGraphLayout()">
                        <span>🔄</span>
                        重置布局
                    </button>
                    <button class="btn btn-sm" onclick="fitGraphToView()">
                        <span>📐</span>
                        适应视图
                    </button>
                    <button class="btn btn-sm" onclick="exportGraphImage()">
                        <span>📷</span>
                        导出图片
                    </button>
                    <button class="btn btn-sm" onclick="toggleGraphPhysics()">
                        <span>⚡</span>
                        物理引擎
                    </button>
                </div>
            </div>
            <div class="card-body" style="padding: 0;">
                <div class="graph-container" id="knowledgeGraphContainer">
                    <div id="knowledgeGraph"></div>
                </div>
            </div>
        </div>

        <div class="grid grid-3">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">🎯 节点筛选</div>
                </div>
                <div class="card-body">
                    <div style="margin-bottom: 16px;">
                        <label style="display: block; margin-bottom: 8px;">节点类型:</label>
                        <select class="input" id="nodeTypeFilter" onchange="filterGraphNodes()">
                            <option value="all">全部类型</option>
                            <option value="Equipment">EMC设备</option>
                            <option value="Standard">EMC标准</option>
                            <option value="Test">EMC测试</option>
                            <option value="Product">产品</option>
                            <option value="Document">文档</option>
                        </select>
                    </div>
                    <div style="margin-bottom: 16px;">
                        <label style="display: block; margin-bottom: 8px;">搜索节点:</label>
                        <input type="text" class="input" id="nodeSearchInput" placeholder="输入节点名称..." onkeyup="searchGraphNodes()" />
                    </div>
                    <button class="btn btn-primary" style="width: 100%;" onclick="addNewNode()">
                        <span>➕</span>
                        添加节点
                    </button>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-title">📊 图谱统计</div>
                </div>
                <div class="card-body">
                    <div id="graphStatistics">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                            <span>设备节点:</span>
                            <span id="equipmentCount">0</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                            <span>标准节点:</span>
                            <span id="standardCount">0</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                            <span>测试节点:</span>
                            <span id="testCount">0</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                            <span>产品节点:</span>
                            <span id="productCount">0</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span>文档节点:</span>
                            <span id="documentCount">0</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-title">ℹ️ 节点详情</div>
                </div>
                <div class="card-body">
                    <div id="nodeDetails">
                        <p style="color: #8c8c8c; text-align: center; padding: 40px 20px;">
                            点击图谱中的节点查看详细信息
                        </p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 搜索页面HTML
function getSearchHTML() {
    return `
        <div class="card">
            <div class="card-header">
                <div class="card-title">🔍 智能搜索引擎</div>
            </div>
            <div class="card-body">
                <div class="grid grid-3" style="margin-bottom: 24px;">
                    <div style="grid-column: span 2;">
                        <input type="text" class="input" id="searchInput" placeholder="输入搜索关键词，如：静电放电、GB/T 17626、抗扰度..." 
                               onkeypress="if(event.key==='Enter') performSearch()" style="height: 48px; font-size: 16px;" />
                    </div>
                    <div>
                        <button class="btn btn-primary" onclick="performSearch()" style="height: 48px; width: 100%;">
                            <span>🔍</span>
                            搜索
                        </button>
                    </div>
                </div>

                <div class="grid grid-4" style="margin-bottom: 24px;">
                    <div>
                        <label style="display: block; margin-bottom: 8px;">搜索范围:</label>
                        <select class="input" id="searchScope">
                            <option value="all">全部内容</option>
                            <option value="nodes">知识节点</option>
                            <option value="relationships">关系连接</option>
                            <option value="files">文件内容</option>
                            <option value="standards">标准库</option>
                        </select>
                    </div>
                    <div>
                        <label style="display: block; margin-bottom: 8px;">内容类型:</label>
                        <select class="input" id="contentType">
                            <option value="all">全部类型</option>
                            <option value="emc-standard">EMC标准</option>
                            <option value="test-report">测试报告</option>
                            <option value="equipment-spec">设备规格</option>
                            <option value="compliance-doc">合规文档</option>
                        </select>
                    </div>
                    <div>
                        <label style="display: block; margin-bottom: 8px;">时间范围:</label>
                        <select class="input" id="timeRange">
                            <option value="all">全部时间</option>
                            <option value="week">最近一周</option>
                            <option value="month">最近一月</option>
                            <option value="year">最近一年</option>
                        </select>
                    </div>
                    <div>
                        <label style="display: block; margin-bottom: 8px;">排序方式:</label>
                        <select class="input" id="sortOrder">
                            <option value="relevance">相关性</option>
                            <option value="date">时间</option>
                            <option value="name">名称</option>
                            <option value="type">类型</option>
                        </select>
                    </div>
                </div>

                <div class="grid grid-6" style="margin-bottom: 24px;">
                    <button class="btn" onclick="quickSearch('GB/T 17626')">GB/T 17626</button>
                    <button class="btn" onclick="quickSearch('静电放电')">静电放电</button>
                    <button class="btn" onclick="quickSearch('EMC测试')">EMC测试</button>
                    <button class="btn" onclick="quickSearch('抗扰度')">抗扰度</button>
                    <button class="btn" onclick="quickSearch('IEC 61000')">IEC 61000</button>
                    <button class="btn" onclick="quickSearch('电磁兼容')">电磁兼容</button>
                </div>
            </div>
        </div>

        <div class="grid grid-3">
            <div style="grid-column: span 2;">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">📋 搜索结果</div>
                        <div id="searchResultCount">准备搜索...</div>
                    </div>
                    <div class="card-body">
                        <div id="searchResults">
                            <div style="text-align: center; padding: 60px 20px; color: #8c8c8c;">
                                <div style="font-size: 3em; margin-bottom: 16px;">🔍</div>
                                <h3>开始您的搜索</h3>
                                <p>输入关键词搜索EMC知识库中的内容</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div>
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">📊 搜索统计</div>
                    </div>
                    <div class="card-body">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                            <span>总节点数:</span>
                            <span id="totalSearchNodes">0</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                            <span>总文件数:</span>
                            <span id="totalSearchFiles">0</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                            <span>搜索次数:</span>
                            <span id="searchCount">0</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span>平均响应:</span>
                            <span id="avgResponseTime">--ms</span>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">🎯 热门搜索</div>
                    </div>
                    <div class="card-body">
                        <div id="popularSearches">
                            <div class="tag tag-blue" onclick="quickSearch('EMC测试')">EMC测试</div>
                            <div class="tag tag-green" onclick="quickSearch('静电放电')">静电放电</div>
                            <div class="tag tag-orange" onclick="quickSearch('GB/T 17626')">GB/T 17626</div>
                            <div class="tag tag-blue" onclick="quickSearch('抗扰度')">抗扰度</div>
                            <div class="tag tag-green" onclick="quickSearch('IEC 61000')">IEC 61000</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">🕒 搜索历史</div>
                    </div>
                    <div class="card-body">
                        <div id="searchHistory">
                            <p style="color: #8c8c8c; text-align: center;">暂无搜索记录</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 文件管理页面HTML
function getFilesHTML() {
    return `
        <div class="grid grid-4" style="margin-bottom: 24px;">
            <div class="card">
                <div class="card-body" style="text-align: center;">
                    <div style="font-size: 2em; color: #1890ff; margin-bottom: 8px;" id="totalFilesCount">0</div>
                    <div style="color: #8c8c8c;">总文件数</div>
                </div>
            </div>
            <div class="card">
                <div class="card-body" style="text-align: center;">
                    <div style="font-size: 2em; color: #52c41a; margin-bottom: 8px;" id="processedFilesCount">0</div>
                    <div style="color: #8c8c8c;">已处理</div>
                </div>
            </div>
            <div class="card">
                <div class="card-body" style="text-align: center;">
                    <div style="font-size: 2em; color: #faad14; margin-bottom: 8px;" id="totalStorageSize">0MB</div>
                    <div style="color: #8c8c8c;">存储空间</div>
                </div>
            </div>
            <div class="card">
                <div class="card-body" style="text-align: center;">
                    <div style="font-size: 2em; color: #722ed1; margin-bottom: 8px;">98%</div>
                    <div style="color: #8c8c8c;">处理成功率</div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <div class="card-title">📤 文件上传</div>
            </div>
            <div class="card-body">
                <div class="upload-area" id="uploadArea" 
                     ondrop="handleFileDrop(event)" 
                     ondragover="handleDragOver(event)" 
                     ondragleave="handleDragLeave(event)"
                     onclick="document.getElementById('fileInput').click()">
                    <div style="font-size: 3em; margin-bottom: 16px;">📁</div>
                    <h3>拖拽文件到此处或点击上传</h3>
                    <p style="color: #8c8c8c; margin-top: 8px;">
                        支持格式: PDF, DOC, DOCX, TXT, XLS, XLSX<br>
                        最大文件大小: 100MB
                    </p>
                    <input type="file" id="fileInput" multiple style="display: none;" 
                           accept=".pdf,.doc,.docx,.txt,.xls,.xlsx" onchange="handleFileSelect(event)" />
                </div>
                
                <div id="uploadProgress" class="hidden" style="margin-top: 16px;">
                    <div style="margin-bottom: 8px;">正在上传...</div>
                    <div class="progress">
                        <div class="progress-bar" id="progressBar" style="width: 0%"></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="grid grid-3">
            <div style="grid-column: span 2;">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">📂 文件列表</div>
                        <div>
                            <select class="input" id="fileFilter" onchange="filterFiles()" style="width: auto; margin-right: 12px;">
                                <option value="all">全部文件</option>
                                <option value="emc-standard">EMC标准</option>
                                <option value="test-report">测试报告</option>
                                <option value="equipment-spec">设备规格</option>
                                <option value="compliance-doc">合规文档</option>
                            </select>
                            <button class="btn btn-sm" onclick="refreshFileList()">
                                <span>🔄</span>
                                刷新
                            </button>
                        </div>
                    </div>
                    <div class="card-body" style="padding: 0;">
                        <table class="table" id="filesTable">
                            <thead>
                                <tr>
                                    <th>文件名</th>
                                    <th>类型</th>
                                    <th>大小</th>
                                    <th>状态</th>
                                    <th>上传时间</th>
                                    <th>操作</th>
                                </tr>
                            </thead>
                            <tbody id="filesTableBody">
                                <!-- 文件列表将在这里动态加载 -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div>
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">📊 文件统计</div>
                    </div>
                    <div class="card-body">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                            <span>PDF文档:</span>
                            <span id="pdfCount">0</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                            <span>Word文档:</span>
                            <span id="wordCount">0</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                            <span>Excel表格:</span>
                            <span id="excelCount">0</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                            <span>文本文件:</span>
                            <span id="textCount">0</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span>其他格式:</span>
                            <span id="otherCount">0</span>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">🔄 最近处理</div>
                    </div>
                    <div class="card-body">
                        <div id="recentProcessed">
                            <div style="margin-bottom: 12px; padding: 8px; background: #f0f9ff; border-radius: 4px;">
                                <div style="font-weight: 600; font-size: 14px;">EMC测试报告.pdf</div>
                                <div style="font-size: 12px; color: #8c8c8c;">5分钟前 • 已完成</div>
                            </div>
                            <div style="margin-bottom: 12px; padding: 8px; background: #f0f9ff; border-radius: 4px;">
                                <div style="font-weight: 600; font-size: 14px;">设备规格书.docx</div>
                                <div style="font-size: 12px; color: #8c8c8c;">15分钟前 • 已完成</div>
                            </div>
                            <div style="margin-bottom: 12px; padding: 8px; background: #fff7e6; border-radius: 4px;">
                                <div style="font-weight: 600; font-size: 14px;">测试数据.xlsx</div>
                                <div style="font-size: 12px; color: #8c8c8c;">30分钟前 • 处理中</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">⚡ 快速操作</div>
                    </div>
                    <div class="card-body">
                        <button class="btn btn-primary" style="width: 100%; margin-bottom: 8px;" onclick="document.getElementById('fileInput').click()">
                            <span>📁</span>
                            选择文件
                        </button>
                        <button class="btn" style="width: 100%; margin-bottom: 8px;" onclick="exportFileList()">
                            <span>📤</span>
                            导出列表
                        </button>
                        <button class="btn" style="width: 100%;" onclick="cleanupFiles()">
                            <span>🗑️</span>
                            清理临时文件
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 文档编辑器页面HTML
function getEditorHTML() {
    return `
        <div class="card">
            <div class="card-header">
                <div class="card-title">📝 Markdown文档编辑器</div>
                <div>
                    <button class="btn btn-sm" onclick="newDocument()">
                        <span>📄</span>
                        新建
                    </button>
                    <button class="btn btn-sm" onclick="openDocument()">
                        <span>📂</span>
                        打开
                    </button>
                    <button class="btn btn-sm btn-primary" onclick="saveDocument()">
                        <span>💾</span>
                        保存
                    </button>
                    <button class="btn btn-sm" onclick="exportDocument()">
                        <span>📤</span>
                        导出
                    </button>
                    <select class="input" id="editorMode" onchange="changeEditorMode()" style="width: auto; margin-left: 12px;">
                        <option value="split">分屏模式</option>
                        <option value="edit">编辑模式</option>
                        <option value="preview">预览模式</option>
                    </select>
                </div>
            </div>
            <div class="card-body" style="padding: 0;">
                <div class="markdown-editor" id="markdownEditor">
                    <div style="display: flex; flex-direction: column;">
                        <div style="padding: 12px; border-bottom: 1px solid var(--border-color); background: var(--bg-secondary);">
                            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                                <button class="btn btn-sm" onclick="insertMarkdown('**', '**')" title="粗体">
                                    <strong>B</strong>
                                </button>
                                <button class="btn btn-sm" onclick="insertMarkdown('*', '*')" title="斜体">
                                    <em>I</em>
                                </button>
                                <button class="btn btn-sm" onclick="insertMarkdown('`', '`')" title="代码">
                                    <span>{'<>'}</span>
                                </button>
                                <button class="btn btn-sm" onclick="insertMarkdown('[', '](url)')" title="链接">
                                    🔗
                                </button>
                                <button class="btn btn-sm" onclick="insertMarkdown('![', '](image-url)')" title="图片">
                                    🖼️
                                </button>
                                <button class="btn btn-sm" onclick="insertHeading()" title="标题">
                                    H
                                </button>
                                <button class="btn btn-sm" onclick="insertList()" title="列表">
                                    📝
                                </button>
                                <button class="btn btn-sm" onclick="insertTable()" title="表格">
                                    📊
                                </button>
                                <button class="btn btn-sm" onclick="insertFileLink()" title="文件链接">
                                    📎
                                </button>
                            </div>
                        </div>
                        <textarea class="editor-textarea" id="markdownTextarea" placeholder="开始编写您的Markdown文档..."
                                  oninput="updatePreview()" style="flex: 1; border: none; outline: none;">
# EMC知识文档

## 概述
欢迎使用EMC知识图谱系统的文档编辑器。

## 功能特性

### 🚀 编辑功能
- **实时预览**: 支持分屏预览，实时查看渲染效果
- **语法高亮**: 智能语法识别和高亮显示
- **快捷操作**: 丰富的工具栏和快捷键支持

### 📊 EMC专业支持
- **标准引用**: 快速插入EMC标准引用
- **测试数据**: 支持表格和图表展示测试数据
- **技术图片**: 便捷的图片插入和管理

## 示例内容

### 测试数据表格

| EMC测试项目 | 标准要求 | 测试结果 | 状态 |
|------------|----------|----------|------|
| 传导发射 | CISPR 32 | 45.2 dBμV | ✅ 通过 |
| 辐射发射 | CISPR 32 | 38.1 dBμV/m | ✅ 通过 |
| 静电放电 | IEC 61000-4-2 | ±8kV | ✅ 通过 |

### 链接示例

**外部链接**:
- [EMC标准数据库](https://example.com/emc-standards)

**内部文件链接**:
- [相关文档](file:doc_1) - 链接到系统内的其他文档

**锚点链接**:
- [跳转到概述](#概述) - 页面内快速导航

---

**最后更新**: ${new Date().toLocaleString('zh-CN')}
                        </textarea>
                    </div>
                    <div class="editor-preview" id="markdownPreview">
                        <!-- 预览内容将在这里显示 -->
                    </div>
                </div>
            </div>
        </div>

        <div class="grid grid-3" style="margin-top: 24px;">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">📂 最近文档</div>
                </div>
                <div class="card-body">
                    <div id="recentDocuments">
                        <div class="search-result" onclick="loadDocument('doc1')">
                            <div class="search-result-title">EMC测试指南.md</div>
                            <div class="search-result-meta">2小时前 • 已保存</div>
                        </div>
                        <div class="search-result" onclick="loadDocument('doc2')">
                            <div class="search-result-title">IEC61000标准解读.md</div>
                            <div class="search-result-meta">1天前 • 已保存</div>
                        </div>
                        <div class="search-result" onclick="loadDocument('doc3')">
                            <div class="search-result-title">产品测试报告模板.md</div>
                            <div class="search-result-meta">3天前 • 已保存</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-title">🎨 编辑器设置</div>
                </div>
                <div class="card-body">
                    <div style="margin-bottom: 16px;">
                        <label style="display: block; margin-bottom: 8px;">字体大小:</label>
                        <select class="input" id="fontSize" onchange="changeFontSize()">
                            <option value="12">12px</option>
                            <option value="14" selected>14px</option>
                            <option value="16">16px</option>
                            <option value="18">18px</option>
                        </select>
                    </div>
                    <div style="margin-bottom: 16px;">
                        <label style="display: block; margin-bottom: 8px;">主题:</label>
                        <select class="input" id="editorTheme" onchange="changeEditorTheme()">
                            <option value="light">浅色主题</option>
                            <option value="dark">深色主题</option>
                        </select>
                    </div>
                    <div style="margin-bottom: 16px;">
                        <label style="display: flex; align-items: center; gap: 8px;">
                            <input type="checkbox" id="autoSave" checked onchange="toggleAutoSave()" />
                            自动保存
                        </label>
                    </div>
                    <div>
                        <label style="display: flex; align-items: center; gap: 8px;">
                            <input type="checkbox" id="wordWrap" checked onchange="toggleWordWrap()" />
                            自动换行
                        </label>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-title">📋 文档统计</div>
                </div>
                <div class="card-body">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <span>字符数:</span>
                        <span id="charCount">0</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <span>单词数:</span>
                        <span id="wordCount">0</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <span>行数:</span>
                        <span id="lineCount">0</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>段落数:</span>
                        <span id="paragraphCount">0</span>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 其他页面HTML模板...
function getAnalysisHTML() {
    return `
        <div class="grid grid-4" style="margin-bottom: 24px;">
            <div class="stat-card">
                <div class="stat-number">150</div>
                <div class="stat-label">总节点数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">300</div>
                <div class="stat-label">总关系数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">85%</div>
                <div class="stat-label">网络密度</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">12</div>
                <div class="stat-label">社区数量</div>
            </div>
        </div>

        <div class="grid grid-2">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">📊 节点分布分析</div>
                </div>
                <div class="card-body">
                    <canvas id="nodeDistributionChart" width="400" height="300"></canvas>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-title">📈 关系类型分析</div>
                </div>
                <div class="card-body">
                    <canvas id="relationshipChart" width="400" height="300"></canvas>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <div class="card-title">🎯 中心性分析</div>
            </div>
            <div class="card-body">
                <div class="grid grid-2">
                    <div>
                        <h4>度中心性排名</h4>
                        <div id="degreeCentrality">
                            <div style="display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #f0f0f0;">
                                <span>GB/T 17626系列标准</span>
                                <span style="color: #1890ff; font-weight: bold;">0.85</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #f0f0f0;">
                                <span>抗扰度测试</span>
                                <span style="color: #1890ff; font-weight: bold;">0.72</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #f0f0f0;">
                                <span>EMC测试设备</span>
                                <span style="color: #1890ff; font-weight: bold;">0.68</span>
                            </div>
                        </div>
                    </div>
                    <div>
                        <h4>介数中心性排名</h4>
                        <div id="betweennessCentrality">
                            <div style="display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #f0f0f0;">
                                <span>抗扰度测试</span>
                                <span style="color: #52c41a; font-weight: bold;">0.92</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #f0f0f0;">
                                <span>EMC测试设备</span>
                                <span style="color: #52c41a; font-weight: bold;">0.78</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #f0f0f0;">
                                <span>IEC 61000系列</span>
                                <span style="color: #52c41a; font-weight: bold;">0.65</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function getStandardsHTML() {
    return `
        <div class="grid grid-3">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">🇨🇳 国家标准 (GB/T)</div>
                </div>
                <div class="card-body">
                    <div class="search-result" onclick="showStandardDetails('GB/T 17626')">
                        <div class="search-result-title">GB/T 17626.1</div>
                        <div class="search-result-meta">概述 (2018版)</div>
                    </div>
                    <div class="search-result" onclick="showStandardDetails('GB/T 17626.2')">
                        <div class="search-result-title">GB/T 17626.2</div>
                        <div class="search-result-meta">静电放电抗扰度试验</div>
                    </div>
                    <div class="search-result" onclick="showStandardDetails('GB/T 17626.3')">
                        <div class="search-result-title">GB/T 17626.3</div>
                        <div class="search-result-meta">射频电磁场辐射抗扰度试验</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-title">🌐 国际标准 (IEC)</div>
                </div>
                <div class="card-body">
                    <div class="search-result" onclick="showStandardDetails('IEC 61000-1')">
                        <div class="search-result-title">IEC 61000-1</div>
                        <div class="search-result-meta">总则 - 基本概念和术语</div>
                    </div>
                    <div class="search-result" onclick="showStandardDetails('IEC 61000-2')">
                        <div class="search-result-title">IEC 61000-2</div>
                        <div class="search-result-meta">环境 - 电磁环境描述</div>
                    </div>
                    <div class="search-result" onclick="showStandardDetails('IEC 61000-4')">
                        <div class="search-result-title">IEC 61000-4</div>
                        <div class="search-result-meta">试验和测量技术</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-title">🚗 行业标准</div>
                </div>
                <div class="card-body">
                    <div class="search-result" onclick="showStandardDetails('CISPR 25')">
                        <div class="search-result-title">CISPR 25</div>
                        <div class="search-result-meta">车用设备EMC要求</div>
                    </div>
                    <div class="search-result" onclick="showStandardDetails('ISO 11452')">
                        <div class="search-result-title">ISO 11452</div>
                        <div class="search-result-meta">道路车辆EMC抗扰度测试</div>
                    </div>
                    <div class="search-result" onclick="showStandardDetails('RTCA DO-160')">
                        <div class="search-result-title">RTCA DO-160</div>
                        <div class="search-result-meta">机载设备EMC要求</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <div class="card-title">🧪 测试方法库</div>
            </div>
            <div class="card-body">
                <table class="table">
                    <thead>
                        <tr>
                            <th>测试项目</th>
                            <th>频率范围</th>
                            <th>标准依据</th>
                            <th>限值要求</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>传导发射</td>
                            <td>150kHz-30MHz</td>
                            <td>CISPR 32</td>
                            <td>Class A/B</td>
                            <td><button class="btn btn-sm">查看详情</button></td>
                        </tr>
                        <tr>
                            <td>辐射发射</td>
                            <td>30MHz-1GHz</td>
                            <td>CISPR 32</td>
                            <td>Class A/B</td>
                            <td><button class="btn btn-sm">查看详情</button></td>
                        </tr>
                        <tr>
                            <td>静电放电</td>
                            <td>±2kV-±15kV</td>
                            <td>IEC 61000-4-2</td>
                            <td>性能判据</td>
                            <td><button class="btn btn-sm">查看详情</button></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

function getSettingsHTML() {
    return `
        <div class="grid grid-2">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">🎨 界面设置</div>
                </div>
                <div class="card-body">
                    <div style="margin-bottom: 16px;">
                        <label style="display: block; margin-bottom: 8px;">主题模式:</label>
                        <select class="input" id="themeMode" onchange="changeTheme()">
                            <option value="light">浅色主题</option>
                            <option value="dark">深色主题</option>
                            <option value="auto">跟随系统</option>
                        </select>
                    </div>
                    <div style="margin-bottom: 16px;">
                        <label style="display: block; margin-bottom: 8px;">语言设置:</label>
                        <select class="input" id="language">
                            <option value="zh-CN">简体中文</option>
                            <option value="en-US">English</option>
                        </select>
                    </div>
                    <div>
                        <label style="display: flex; align-items: center; gap: 8px;">
                            <input type="checkbox" id="animations" checked />
                            启用动画效果
                        </label>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-title">🔧 系统设置</div>
                </div>
                <div class="card-body">
                    <div style="margin-bottom: 16px;">
                        <label style="display: flex; align-items: center; gap: 8px;">
                            <input type="checkbox" id="autoSaveSettings" checked />
                            自动保存设置
                        </label>
                    </div>
                    <div style="margin-bottom: 16px;">
                        <label style="display: flex; align-items: center; gap: 8px;">
                            <input type="checkbox" id="notifications" checked />
                            显示通知
                        </label>
                    </div>
                    <div>
                        <button class="btn" onclick="resetSettings()">
                            <span>🔄</span>
                            重置为默认设置
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <div class="card-title">📊 系统信息</div>
            </div>
            <div class="card-body">
                <table class="table">
                    <tbody>
                        <tr>
                            <td>版本号</td>
                            <td>v1.0.0</td>
                        </tr>
                        <tr>
                            <td>构建日期</td>
                            <td>${new Date().toLocaleDateString('zh-CN')}</td>
                        </tr>
                        <tr>
                            <td>浏览器</td>
                            <td>${navigator.userAgent.split(' ')[0]}</td>
                        </tr>
                        <tr>
                            <td>屏幕分辨率</td>
                            <td>${screen.width} × ${screen.height}</td>
                        </tr>
                        <tr>
                            <td>本地存储</td>
                            <td>可用</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

// ================================
// 页面初始化函数
// ================================

function initializeDashboard() {
    updateStats();
    initializeCharts();
}

function initializeGraph() {
    updateGraphStats();
    renderKnowledgeGraph();
}

function initializeSearch() {
    updateSearchStats();
}

function initializeFiles() {
    updateFileStats();
    renderFileList();
}

function initializeEditor() {
    updatePreview();
    updateDocumentStats();
}

function initializeAnalysis() {
    renderAnalysisCharts();
}

function initializeStandards() {
    // 标准库初始化
}

function initializeSettings() {
    loadSettings();
}

// ================================
// 工具函数
// ================================

// 更新统计数据
function updateStats() {
    const stats = AppState.data.stats;
    document.getElementById('statNodes').textContent = stats.totalNodes || 0;
    document.getElementById('statRelationships').textContent = stats.totalRelationships || 0;
    document.getElementById('statFiles').textContent = stats.totalFiles || 0;
    document.getElementById('statHealth').textContent = (stats.systemHealth || 100) + '%';
}

// 显示通知
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    const content = notification.querySelector('.notification-content');
    
    content.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// 侧边栏切换
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggleIcon = document.getElementById('toggleIcon');
    
    sidebar.classList.toggle('collapsed');
    AppState.sidebarCollapsed = !AppState.sidebarCollapsed;
    
    toggleIcon.textContent = AppState.sidebarCollapsed ? '›' : '‹';
}

// 设置事件监听
function setupEventListeners() {
    // 键盘快捷键
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 's':
                    e.preventDefault();
                    if (AppState.currentPage === 'editor') {
                        saveDocument();
                    }
                    break;
                case 'f':
                    e.preventDefault();
                    if (AppState.currentPage === 'search') {
                        document.getElementById('searchInput').focus();
                    }
                    break;
            }
        }
    });

    // 窗口大小改变
    window.addEventListener('resize', function() {
        if (AppState.currentPage === 'graph') {
            // 重新调整图谱大小
            setTimeout(renderKnowledgeGraph, 100);
        }
    });
}

// 加载和保存设置
function loadSettings() {
    try {
        const saved = localStorage.getItem('emcAppSettings');
        if (saved) {
            AppState.settings = { ...AppState.settings, ...JSON.parse(saved) };
        }
    } catch (error) {
        console.warn('无法加载设置:', error);
    }
}

function saveSettings() {
    try {
        localStorage.setItem('emcAppSettings', JSON.stringify(AppState.settings));
    } catch (error) {
        console.warn('无法保存设置:', error);
    }
}

// 全局函数
function refreshData() {
    showNotification('正在刷新数据...', 'info');
    loadInitialData();
}

function exportData() {
    const data = JSON.stringify(AppState.data, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `emc_data_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showNotification('数据导出成功');
}

function showHelp() {
    const helpContent = `
        <div class="modal-header">
            <h3>❓ 使用帮助</h3>
            <button onclick="closeModal()" style="background: none; border: none; font-size: 20px;">&times;</button>
        </div>
        <div class="modal-body">
            <h4>🌐 知识图谱</h4>
            <p>• 点击节点查看详情<br>• 拖拽移动节点<br>• 滚轮缩放视图</p>
            
            <h4>🔍 智能搜索</h4>
            <p>• 支持关键词搜索<br>• 支持模糊匹配<br>• 点击结果定位节点</p>
            
            <h4>📁 文件处理</h4>
            <p>• 拖拽上传文件<br>• 自动提取知识<br>• 支持多种格式</p>
            
            <h4>📝 文档编辑</h4>
            <p>• Markdown语法支持<br>• 实时预览<br>• 内部链接功能</p>
        </div>
        <div class="modal-footer">
            <button class="btn btn-primary" onclick="closeModal()">确定</button>
        </div>
    `;
    
    document.getElementById('modalContent').innerHTML = helpContent;
    document.getElementById('modal').classList.add('show');
}

function closeModal() {
    document.getElementById('modal').classList.remove('show');
}

// ================================
// 具体功能实现
// ================================

// 知识图谱相关功能
function renderKnowledgeGraph() {
    const container = document.getElementById('knowledgeGraph');
    if (!container) return;

    const data = {
        nodes: AppState.data.nodes.map(node => ({
            id: node.id,
            label: node.label,
            color: getNodeColor(node.type),
            font: { color: '#2c3e50', size: 12 },
            borderWidth: 2,
            borderColor: '#fff'
        })),
        edges: AppState.data.relationships.map(rel => ({
            from: rel.source,
            to: rel.target,
            label: rel.type,
            color: '#999',
            arrows: 'to'
        }))
    };

    const options = {
        physics: {
            enabled: true,
            stabilization: { iterations: 100 }
        },
        interaction: {
            dragNodes: true,
            zoomView: true
        },
        nodes: {
            shape: 'circle',
            size: 20
        }
    };

    try {
        if (typeof vis !== 'undefined') {
            new vis.Network(container, data, options);
        } else {
            container.innerHTML = '<div style="text-align: center; padding: 40px;">知识图谱加载中...</div>';
        }
    } catch (error) {
        container.innerHTML = '<div style="text-align: center; padding: 40px;">图谱渲染失败</div>';
    }
}

function getNodeColor(type) {
    const colors = {
        'Equipment': '#1890ff',
        'Standard': '#52c41a',
        'Test': '#faad14',
        'Product': '#722ed1',
        'Document': '#eb2f96'
    };
    return colors[type] || '#d4af37';
}

function updateGraphStats() {
    const stats = calculateGraphStats();
    document.getElementById('graphNodeCount').textContent = stats.nodeCount;
    document.getElementById('graphRelCount').textContent = stats.relCount;
    
    updateStatCounts(stats);
}

function calculateGraphStats() {
    const nodes = AppState.data.nodes || [];
    const relationships = AppState.data.relationships || [];
    
    return {
        nodeCount: nodes.length,
        relCount: relationships.length,
        equipmentCount: nodes.filter(n => n.type === 'Equipment').length,
        standardCount: nodes.filter(n => n.type === 'Standard').length,
        testCount: nodes.filter(n => n.type === 'Test').length,
        productCount: nodes.filter(n => n.type === 'Product').length,
        documentCount: nodes.filter(n => n.type === 'Document').length
    };
}

function updateStatCounts(stats) {
    const elements = ['equipment', 'standard', 'test', 'product', 'document'];
    elements.forEach(type => {
        const element = document.getElementById(type + 'Count');
        if (element) {
            element.textContent = stats[type + 'Count'] || 0;
        }
    });
}

// 图谱控制功能
function resetGraphLayout() {
    showNotification('重置图谱布局');
    renderKnowledgeGraph();
}

function fitGraphToView() {
    showNotification('适应视图');
}

function exportGraphImage() {
    showNotification('导出图片功能开发中');
}

function toggleGraphPhysics() {
    showNotification('切换物理引擎');
}

function filterGraphNodes() {
    const filter = document.getElementById('nodeTypeFilter').value;
    showNotification(`筛选节点类型: ${filter}`);
    renderKnowledgeGraph();
}

function searchGraphNodes() {
    const searchTerm = document.getElementById('nodeSearchInput').value;
    showNotification(`搜索节点: ${searchTerm}`);
}

function addNewNode() {
    const nodeType = document.getElementById('nodeTypeFilter').value;
    showNotification('添加新节点功能开发中');
}

// 搜索功能
function performSearch() {
    const searchTerm = document.getElementById('searchInput').value;
    const scope = document.getElementById('searchScope').value;
    const contentType = document.getElementById('contentType').value;
    
    if (!searchTerm.trim()) {
        showNotification('请输入搜索关键词', 'warning');
        return;
    }

    showNotification('正在搜索...', 'info');
    
    setTimeout(() => {
        const results = mockSearch(searchTerm, scope, contentType);
        displaySearchResults(results);
        updateSearchStats();
    }, 800);
}

function mockSearch(term, scope, type) {
    const mockResults = [
        {
            title: `EMC测试标准 - ${term}`,
            summary: `包含关键词"${term}"的EMC测试标准文档，详细描述了相关测试方法和要求。`,
            type: 'standard',
            relevance: 0.95,
            source: 'GB/T 17626.3-2018'
        },
        {
            title: `${term}相关设备规格`,
            summary: `关于${term}的设备技术规格和操作说明，包含详细的参数配置信息。`,
            type: 'equipment',
            relevance: 0.87,
            source: '设备手册'
        },
        {
            title: `${term}测试报告`,
            summary: `针对${term}进行的专业测试报告，包含测试数据和分析结果。`,
            type: 'report',
            relevance: 0.82,
            source: '测试实验室'
        }
    ];
    
    return mockResults;
}

function displaySearchResults(results) {
    const container = document.getElementById('searchResults');
    const countElement = document.getElementById('searchResultCount');
    
    countElement.textContent = `找到 ${results.length} 个结果`;
    
    container.innerHTML = results.map(result => `
        <div class="search-result" onclick="openSearchResult('${result.source}')">
            <div class="search-result-title">${result.title}</div>
            <div class="search-result-meta">${result.source} • 相关度: ${(result.relevance * 100).toFixed(0)}%</div>
            <div style="margin-top: 8px; color: #595959;">${result.summary}</div>
        </div>
    `).join('');
}

function quickSearch(term) {
    document.getElementById('searchInput').value = term;
    performSearch();
}

function updateSearchStats() {
    const stats = AppState.data.stats;
    document.getElementById('totalSearchNodes').textContent = stats.totalNodes || 0;
    document.getElementById('totalSearchFiles').textContent = stats.totalFiles || 0;
    
    const searchCount = parseInt(document.getElementById('searchCount').textContent) + 1;
    document.getElementById('searchCount').textContent = searchCount;
    document.getElementById('avgResponseTime').textContent = '250ms';
}

function openSearchResult(source) {
    showNotification(`打开结果: ${source}`);
}

// 文件管理功能
function updateFileStats() {
    const stats = AppState.data.stats;
    const files = AppState.data.files || [];
    
    document.getElementById('totalFilesCount').textContent = files.length;
    document.getElementById('processedFilesCount').textContent = files.filter(f => f.status === 'active').length;
    document.getElementById('totalStorageSize').textContent = calculateTotalSize(files);
    
    updateFileTypeCounts(files);
}

function calculateTotalSize(files) {
    const totalBytes = files.reduce((sum, file) => sum + (file.size || 0), 0);
    return formatFileSize(totalBytes);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0MB';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + sizes[i];
}

function updateFileTypeCounts(files) {
    const counts = {
        pdf: files.filter(f => f.name.endsWith('.pdf')).length,
        word: files.filter(f => f.name.endsWith('.docx') || f.name.endsWith('.doc')).length,
        excel: files.filter(f => f.name.endsWith('.xlsx') || f.name.endsWith('.xls')).length,
        text: files.filter(f => f.name.endsWith('.txt')).length,
        other: files.filter(f => !['pdf', 'docx', 'doc', 'xlsx', 'xls', 'txt'].some(ext => f.name.endsWith(ext))).length
    };
    
    Object.keys(counts).forEach(type => {
        const element = document.getElementById(type + 'Count');
        if (element) element.textContent = counts[type];
    });
}

function renderFileList() {
    const tbody = document.getElementById('filesTableBody');
    if (!tbody) return;
    
    const files = AppState.data.files || [];
    
    tbody.innerHTML = files.map(file => `
        <tr>
            <td>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span>${getFileIcon(file.name)}</span>
                    <span>${file.name}</span>
                    ${file.status === 'processing' ? '<span class="tag tag-orange">处理中</span>' : ''}
                </div>
            </td>
            <td>${file.category || '通用'}</td>
            <td>${formatFileSize(file.size || 0)}</td>
            <td><span class="tag tag-green">正常</span></td>
            <td>${file.date || '2025-06-13'}</td>
            <td>
                <button class="btn btn-sm" onclick="downloadFile('${file.id}')">
                    <span>📥</span>
                    下载
                </button>
            </td>
        </tr>
    `).join('');
}

function getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const icons = {
        'pdf': '📄',
        'doc': '📝', 'docx': '📝',
        'xls': '📊', 'xlsx': '📊',
        'txt': '📄',
        'zip': '📦', 'rar': '📦'
    };
    return icons[ext] || '📋';
}

function downloadFile(fileId) {
    const file = AppState.data.files.find(f => f.id === fileId);
    if (file) {
        showNotification(`开始下载: ${file.name}`);
        // 模拟下载
        setTimeout(() => {
            showNotification(`下载完成: ${file.name}`, 'success');
        }, 2000);
    }
}

// 文件上传功能
function handleFileDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    
    const uploadArea = document.getElementById('uploadArea');
    uploadArea.classList.remove('dragover');
    
    const files = Array.from(event.dataTransfer.files);
    handleFileUpload(files);
}

function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    
    const uploadArea = document.getElementById('uploadArea');
    uploadArea.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    
    const uploadArea = document.getElementById('uploadArea');
    uploadArea.classList.remove('dragover');
}

function handleFileSelect(event) {
    const files = Array.from(event.target.files);
    handleFileUpload(files);
}

function handleFileUpload(files) {
    if (files.length === 0) return;
    
    const progressContainer = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('progressBar');
    
    progressContainer.classList.remove('hidden');
    progressBar.style.width = '0%';
    
    // 模拟上传进度
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
            
            setTimeout(() => {
                progressContainer.classList.add('hidden');
                showNotification(`成功上传 ${files.length} 个文件`, 'success');
                
                // 添加到文件列表
                files.forEach(file => {
                    AppState.data.files.push({
                        id: 'file_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
                        name: file.name,
                        size: file.size,
                        category: 'general',
                        status: 'active',
                        date: new Date().toISOString().split('T')[0]
                    });
                });
                
                updateFileStats();
                renderFileList();
            }, 500);
        }
        progressBar.style.width = progress + '%';
    }, 100);
}

function filterFiles() {
    const filter = document.getElementById('fileFilter').value;
    showNotification(`筛选文件类型: ${filter}`);
    renderFileList();
}

function refreshFileList() {
    showNotification('刷新文件列表');
    renderFileList();
}

function exportFileList() {
    const data = JSON.stringify(AppState.data.files, null, 2);
    downloadTextFile(data, 'file_list_export.json');
    showNotification('文件列表导出成功');
}

function cleanupFiles() {
    showNotification('清理临时文件功能开发中');
}

// Markdown编辑器功能
function updatePreview() {
    const textarea = document.getElementById('markdownTextarea');
    const preview = document.getElementById('markdownPreview');
    
    if (!textarea || !preview) return;
    
    const content = textarea.value;
    
    try {
        if (typeof marked !== 'undefined') {
            preview.innerHTML = marked.parse(content);
        } else {
            // 简单的Markdown渲染
            let html = content
                .replace(/^# (.*$)/gim, '<h1>$1</h1>')
                .replace(/^## (.*$)/gim, '<h2>$1</h2>')
                .replace(/^### (.*$)/gim, '<h3>$1</h3>')
                .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
                .replace(/\*(.*)\*/gim, '<em>$1</em>')
                .replace(/\n/gim, '<br>');
            preview.innerHTML = html;
        }
        
        // 处理内部链接
        processInternalLinks(preview);
        updateDocumentStats();
    } catch (error) {
        preview.innerHTML = '<div style="color: red;">预览渲染失败</div>';
    }
}

function processInternalLinks(container) {
    const links = container.querySelectorAll('a');
    links.forEach(link => {
        const href = link.getAttribute('href');
        if (href) {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                handleInternalLink(href);
            });
        }
    });
}

function handleInternalLink(url) {
    if (url.startsWith('#')) {
        // 锚点链接
        const target = document.querySelector(url);
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    } else if (url.startsWith('file:')) {
        // 文件链接
        const fileId = url.substring(5);
        showNotification(`打开文件: ${fileId}`);
    } else if (url.startsWith('/')) {
        // 内部路由
        showNotification(`导航到: ${url}`);
    } else {
        // 外部链接
        window.open(url, '_blank');
    }
}

function updateDocumentStats() {
    const textarea = document.getElementById('markdownTextarea');
    if (!textarea) return;
    
    const content = textarea.value;
    const stats = {
        charCount: content.length,
        wordCount: content.trim() ? content.trim().split(/\s+/).length : 0,
        lineCount: content.split('\n').length,
        paragraphCount: content.split(/\n\s*\n/).length
    };
    
    Object.keys(stats).forEach(key => {
        const element = document.getElementById(key);
        if (element) element.textContent = stats[key];
    });
}

// 编辑器工具栏功能
function insertMarkdown(before, after) {
    const textarea = document.getElementById('markdownTextarea');
    if (!textarea) return;
    
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    
    const newText = before + selectedText + after;
    textarea.value = textarea.value.substring(0, start) + newText + textarea.value.substring(end);
    
    textarea.focus();
    textarea.setSelectionRange(start + before.length, start + before.length + selectedText.length);
    updatePreview();
}

function insertHeading() {
    insertMarkdown('## ', '');
}

function insertList() {
    insertMarkdown('- ', '');
}

function insertTable() {
    const table = `\n| 列1 | 列2 | 列3 |\n|-----|-----|-----|\n| 数据1 | 数据2 | 数据3 |\n`;
    insertMarkdown(table, '');
}

function insertFileLink() {
    const fileId = prompt('请输入文件ID:');
    if (fileId) {
        insertMarkdown(`[文件链接](file:${fileId})`, '');
    }
}

// 编辑器设置
function changeFontSize() {
    const fontSize = document.getElementById('fontSize').value;
    const textarea = document.getElementById('markdownTextarea');
    if (textarea) {
        textarea.style.fontSize = fontSize + 'px';
    }
}

function changeEditorTheme() {
    const theme = document.getElementById('editorTheme').value;
    showNotification(`切换主题: ${theme}`);
}

function toggleAutoSave() {
    const autoSave = document.getElementById('autoSave').checked;
    AppState.settings.autoSave = autoSave;
    saveSettings();
    showNotification(`自动保存: ${autoSave ? '开启' : '关闭'}`);
}

function toggleWordWrap() {
    const wordWrap = document.getElementById('wordWrap').checked;
    const textarea = document.getElementById('markdownTextarea');
    if (textarea) {
        textarea.style.whiteSpace = wordWrap ? 'pre-wrap' : 'pre';
    }
}

function changeEditorMode() {
    const mode = document.getElementById('editorMode').value;
    const editor = document.getElementById('markdownEditor');
    if (!editor) return;
    
    switch (mode) {
        case 'edit':
            editor.style.gridTemplateColumns = '1fr 0fr';
            break;
        case 'preview':
            editor.style.gridTemplateColumns = '0fr 1fr';
            break;
        default: // split
            editor.style.gridTemplateColumns = '1fr 1fr';
    }
}

// 文档操作
function newDocument() {
    const textarea = document.getElementById('markdownTextarea');
    if (textarea) {
        textarea.value = '# 新文档\n\n开始编写您的内容...\n';
        updatePreview();
    }
    showNotification('创建新文档');
}

function openDocument() {
    showNotification('打开文档功能开发中');
}

function saveDocument() {
    const textarea = document.getElementById('markdownTextarea');
    if (textarea) {
        const content = textarea.value;
        downloadTextFile(content, 'document.md');
        showNotification('文档保存成功');
    }
}

function exportDocument() {
    const preview = document.getElementById('markdownPreview');
    if (preview) {
        const htmlContent = `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>导出文档</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1, h2, h3 { color: #333; }
                code { background: #f5f5f5; padding: 2px 4px; border-radius: 3px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            ${preview.innerHTML}
        </body>
        </html>`;
        
        downloadTextFile(htmlContent, 'document.html');
        showNotification('文档导出成功');
    }
}

function loadDocument(docId) {
    showNotification(`加载文档: ${docId}`);
}

// 图表渲染功能
function initializeCharts() {
    renderOverviewChart();
    renderActivityChart();
}

function renderOverviewChart() {
    const canvas = document.getElementById('overviewChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // 简单的饼图渲染
    const data = [
        { label: '设备', value: 30, color: '#1890ff' },
        { label: '标准', value: 25, color: '#52c41a' },
        { label: '测试', value: 20, color: '#faad14' },
        { label: '文档', value: 25, color: '#722ed1' }
    ];
    
    renderPieChart(ctx, data, 150, 100);
}

function renderActivityChart() {
    const canvas = document.getElementById('activityChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // 简单的线图渲染
    const data = [10, 15, 12, 20, 18, 25, 22];
    renderLineChart(ctx, data, 400, 200);
}

function renderPieChart(ctx, data, centerX, centerY) {
    const radius = 60;
    let currentAngle = 0;
    const total = data.reduce((sum, item) => sum + item.value, 0);
    
    data.forEach(item => {
        const sliceAngle = (item.value / total) * 2 * Math.PI;
        
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
        ctx.lineTo(centerX, centerY);
        ctx.fillStyle = item.color;
        ctx.fill();
        
        currentAngle += sliceAngle;
    });
}

function renderLineChart(ctx, data, width, height) {
    const padding = 40;
    const chartWidth = width - 2 * padding;
    const chartHeight = height - 2 * padding;
    const maxValue = Math.max(...data);
    
    ctx.beginPath();
    ctx.strokeStyle = '#1890ff';
    ctx.lineWidth = 2;
    
    data.forEach((value, index) => {
        const x = padding + (index / (data.length - 1)) * chartWidth;
        const y = padding + chartHeight - (value / maxValue) * chartHeight;
        
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    
    ctx.stroke();
}

function renderAnalysisCharts() {
    // 数据分析图表渲染
    setTimeout(() => {
        try {
            renderNodeDistributionChart();
            renderRelationshipChart();
        } catch (error) {
            console.warn('图表渲染失败:', error);
        }
    }, 100);
}

function renderNodeDistributionChart() {
    const canvas = document.getElementById('nodeDistributionChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const stats = calculateGraphStats();
    const data = [
        { label: '设备', value: stats.equipmentCount, color: '#1890ff' },
        { label: '标准', value: stats.standardCount, color: '#52c41a' },
        { label: '测试', value: stats.testCount, color: '#faad14' },
        { label: '产品', value: stats.productCount, color: '#722ed1' },
        { label: '文档', value: stats.documentCount, color: '#eb2f96' }
    ];
    
    renderPieChart(ctx, data, 200, 150);
}

function renderRelationshipChart() {
    const canvas = document.getElementById('relationshipChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const data = [8, 12, 6, 15, 10];
    renderLineChart(ctx, data, 400, 300);
}

// 标准库功能
function showStandardDetails(standardId) {
    showNotification(`查看标准详情: ${standardId}`);
}

// 设置功能
function changeTheme() {
    const theme = document.getElementById('themeMode').value;
    AppState.settings.theme = theme;
    saveSettings();
    showNotification(`主题切换为: ${theme}`);
}

function resetSettings() {
    AppState.settings = {
        theme: 'light',
        language: 'zh-CN',
        autoSave: true
    };
    saveSettings();
    showNotification('设置已重置为默认值');
}

// 辅助函数
function downloadTextFile(content, filename) {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

// 导出模块
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getGraphHTML,
        getSearchHTML,
        getFilesHTML,
        getEditorHTML,
        getAnalysisHTML,
        getStandardsHTML,
        getSettingsHTML,
        renderKnowledgeGraph,
        performSearch,
        updatePreview,
        // ... 其他函数
    };
}