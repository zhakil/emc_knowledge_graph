# EMC知识图谱客户端部署指南

## 概述

EMC知识图谱客户端是一个完整的单页面应用程序，专为电磁兼容性（EMC）知识管理而设计。此客户端提供了完整的用户界面和功能，包括知识图谱可视化、智能搜索、文件管理、文档编辑等核心功能。

## 文件结构

```
emc_knowledge_graph/
├── emc_complete_client.html    # 主应用HTML文件
├── emc_client_modules.js       # JavaScript功能模块
├── CLIENT_DEPLOYMENT.md        # 本部署文档
├── FIXES_SUMMARY.md           # 修复总结文档
└── frontend/                  # 原项目前端组件（可选参考）
```

## 核心功能

### 1. 🏛️ 仪表盘
- 系统概览统计
- 实时数据监控
- 快速操作入口
- 最近活动记录

### 2. 🌐 知识图谱
- 交互式图谱可视化
- 节点关系展示
- 图谱统计分析
- 节点搜索和筛选

### 3. 🔍 智能搜索
- 全文检索功能
- 多维度搜索筛选
- 搜索结果分析
- 热门搜索推荐

### 4. 📁 文件管理
- 文件上传（拖拽支持）
- 文件下载功能
- 文件分类管理
- 文件统计分析

### 5. 📝 文档编辑
- Markdown编辑器
- 实时预览功能
- 内部链接支持
- 文档导出功能

### 6. 📊 数据分析
- 图谱统计分析
- 节点分布图表
- 关系类型统计
- 中心性分析

### 7. 📋 标准库
- EMC标准浏览
- 测试方法库
- 标准详情查看
- 相关标准推荐

### 8. ⚙️ 系统设置
- 界面主题设置
- 语言配置
- 系统信息查看
- 设置导入导出

## 部署方式

### 方式一：独立Web服务器部署

1. **环境要求**
   ```
   - Web服务器（Nginx、Apache、IIS等）
   - 现代浏览器支持（Chrome、Firefox、Safari、Edge）
   - 可选：HTTPS支持（推荐生产环境）
   ```

2. **部署步骤**
   ```bash
   # 1. 复制文件到Web服务器根目录
   cp emc_complete_client.html /var/www/html/index.html
   cp emc_client_modules.js /var/www/html/
   
   # 2. 设置文件权限
   chmod 644 /var/www/html/index.html
   chmod 644 /var/www/html/emc_client_modules.js
   
   # 3. 重启Web服务器
   sudo systemctl restart nginx  # 或 apache2
   ```

3. **Nginx配置示例**
   ```nginx
   server {
       listen 80;
       server_name emc-knowledge-graph.local;
       root /var/www/html;
       index index.html;
       
       location / {
           try_files $uri $uri/ =404;
       }
       
       # 启用GZIP压缩
       gzip on;
       gzip_types text/html text/css application/javascript;
   }
   ```

### 方式二：Python简单服务器

```bash
# 在项目目录中启动
python3 -m http.server 8080

# 访问地址
# http://localhost:8080/emc_complete_client.html
```

### 方式三：Node.js静态服务器

```bash
# 安装serve工具
npm install -g serve

# 启动服务器
serve . -p 8080

# 访问地址
# http://localhost:8080/emc_complete_client.html
```

### 方式四：Docker部署

1. **创建Dockerfile**
   ```dockerfile
   FROM nginx:alpine
   COPY emc_complete_client.html /usr/share/nginx/html/index.html
   COPY emc_client_modules.js /usr/share/nginx/html/
   EXPOSE 80
   ```

2. **构建和运行**
   ```bash
   # 构建镜像
   docker build -t emc-knowledge-graph-client .
   
   # 运行容器
   docker run -d -p 8080:80 emc-knowledge-graph-client
   ```

## 配置说明

### 应用配置

客户端支持以下配置选项（在`emc_complete_client.html`中修改）：

```javascript
// 全局应用状态配置
const AppState = {
    currentPage: 'dashboard',    // 默认页面
    sidebarCollapsed: false,     // 侧边栏状态
    settings: {
        theme: 'light',          // 主题模式：light/dark/auto
        language: 'zh-CN',       // 语言设置
        autoSave: true           // 自动保存
    }
};
```

### API配置

如果需要连接后端API，请在JavaScript中修改API端点：

```javascript
// 在emc_client_modules.js中修改
const API_BASE_URL = 'http://localhost:8000/api';  // 修改为实际API地址

// 示例API调用
async function loadNodes() {
    const response = await fetch(`${API_BASE_URL}/knowledge-graph/nodes`);
    return response.json();
}
```

### 外部依赖配置

客户端使用以下外部库（CDN方式加载）：

```html
<!-- 可视化库 -->
<script src="https://d3js.org/d3.v7.min.js"></script>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>

<!-- 图表库 -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- Markdown渲染 -->
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
```

## 浏览器兼容性

### 支持的浏览器

| 浏览器 | 最低版本 | 推荐版本 |
|--------|----------|----------|
| Chrome | 80+ | 最新版 |
| Firefox | 75+ | 最新版 |
| Safari | 13+ | 最新版 |
| Edge | 80+ | 最新版 |

### 功能特性要求

- ES6+ JavaScript支持
- CSS Grid和Flexbox支持
- Fetch API支持
- Canvas 2D渲染支持
- LocalStorage支持

## 性能优化

### 1. 资源优化
```bash
# 压缩JavaScript（可选）
npx terser emc_client_modules.js -o emc_client_modules.min.js

# 压缩CSS（内联样式）
# 使用在线CSS压缩工具
```

### 2. 缓存策略
```nginx
# Nginx缓存配置
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. 图片优化
- 使用WebP格式图像
- 启用图像懒加载
- 优化图标使用

## 安全考虑

### 1. 内容安全策略（CSP）
```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' 'unsafe-inline' https://d3js.org https://unpkg.com https://cdn.jsdelivr.net; 
               style-src 'self' 'unsafe-inline';">
```

### 2. 数据验证
- 用户输入验证
- 文件上传类型检查
- XSS防护

### 3. HTTPS部署
```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # 其他配置...
}
```

## 监控和日志

### 1. 访问日志
```nginx
# Nginx访问日志配置
access_log /var/log/nginx/emc_access.log combined;
error_log /var/log/nginx/emc_error.log;
```

### 2. 应用监控
```javascript
// 在JavaScript中添加监控代码
window.addEventListener('error', function(e) {
    console.error('应用错误:', e.error);
    // 发送错误报告到监控服务
});
```

## 维护和更新

### 1. 版本管理
- 使用语义化版本号
- 维护更新日志
- 备份配置文件

### 2. 定期维护
- 检查外部依赖更新
- 清理临时文件
- 优化性能指标

### 3. 备份策略
```bash
# 备份脚本示例
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/emc_client_$DATE"
mkdir -p $BACKUP_DIR
cp emc_complete_client.html $BACKUP_DIR/
cp emc_client_modules.js $BACKUP_DIR/
tar -czf "$BACKUP_DIR.tar.gz" $BACKUP_DIR
rm -rf $BACKUP_DIR
```

## 故障排除

### 常见问题

1. **页面无法加载**
   - 检查Web服务器状态
   - 验证文件路径和权限
   - 查看浏览器控制台错误

2. **功能异常**
   - 检查JavaScript控制台错误
   - 验证外部依赖加载
   - 确认浏览器兼容性

3. **性能问题**
   - 检查网络连接
   - 监控资源使用情况
   - 优化图片和脚本

### 调试模式

在浏览器中启用调试：

```javascript
// 在控制台中设置调试模式
localStorage.setItem('debug', 'true');
// 刷新页面以启用详细日志
location.reload();
```

## 联系支持

如有问题或需要支持，请：

1. 查看浏览器控制台错误信息
2. 检查此文档的故障排除部分
3. 联系技术支持团队

---

**版本**: v1.0.0  
**更新日期**: 2025-06-13  
**维护者**: EMC知识图谱开发团队