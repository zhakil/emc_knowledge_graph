import React, { useState, useEffect, useRef } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Input,
  Select,
  Space,
  Tooltip,
  Modal,
  message,
  Tabs,
  Typography,
  Divider,
  Tag,
  Alert,
  Switch,
  Dropdown,
  Menu
} from 'antd';
import {
  EditOutlined,
  EyeOutlined,
  SaveOutlined,
  FolderOpenOutlined,
  FileAddOutlined,
  BoldOutlined,
  ItalicOutlined,
  UnderlineOutlined,
  LinkOutlined,
  PictureOutlined,
  TableOutlined,
  OrderedListOutlined,
  UnorderedListOutlined,
  CodeOutlined,
  FullscreenOutlined,
  SettingOutlined,
  DownloadOutlined,
  ShareAltOutlined,
  HistoryOutlined
} from '@ant-design/icons';

const { TextArea } = Input;
const { Title, Text } = Typography;
const { TabPane } = Tabs;

interface MarkdownFile {
  id: string;
  name: string;
  content: string;
  lastModified: string;
  path: string;
  tags: string[];
}

interface EditorSettings {
  theme: 'light' | 'dark';
  fontSize: number;
  lineHeight: number;
  wordWrap: boolean;
  showLineNumbers: boolean;
  autoSave: boolean;
  autoSaveInterval: number;
}

const MarkdownEditor: React.FC = () => {
  const [markdownContent, setMarkdownContent] = useState('');
  const [currentFile, setCurrentFile] = useState<MarkdownFile | null>(null);
  const [files, setFiles] = useState<MarkdownFile[]>([]);
  const [previewMode, setPreviewMode] = useState<'edit' | 'preview' | 'split'>('split');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState<EditorSettings>({
    theme: 'light',
    fontSize: 14,
    lineHeight: 1.6,
    wordWrap: true,
    showLineNumbers: true,
    autoSave: true,
    autoSaveInterval: 30
  });
  const [unsavedChanges, setUnsavedChanges] = useState(false);
  const editorRef = useRef<HTMLTextAreaElement>(null);
  const autoSaveTimerRef = useRef<NodeJS.Timeout>();

  const defaultContent = `# 📝 EMC知识文档

## 概述
欢迎使用EMC知识图谱系统的Markdown编辑器。您可以在这里创建和编辑技术文档、测试报告、标准说明等内容。

## 功能特性

### 🚀 编辑功能
- **实时预览**: 支持分屏预览，实时查看渲染效果
- **语法高亮**: 智能语法识别和高亮显示
- **快捷操作**: 丰富的工具栏和快捷键支持
- **自动保存**: 防止数据丢失的自动保存功能

### 📊 EMC专业支持
- **标准引用**: 快速插入EMC标准引用
- **测试数据**: 支持表格和图表展示测试数据
- **技术图片**: 便捷的图片插入和管理
- **公式支持**: LaTeX数学公式渲染

## 快速开始

### 1. 创建新文档
点击"新建文档"按钮开始创建您的第一个Markdown文档。

### 2. 编辑内容
使用工具栏快速插入常用元素：

**文本格式**:
- **粗体文本** - 强调重要内容
- *斜体文本* - 突出特殊说明
- \`行内代码\` - 标记代码片段

**列表**:
1. 有序列表项目1
2. 有序列表项目2
3. 有序列表项目3

- 无序列表项目A
- 无序列表项目B
- 无序列表项目C

### 3. 插入表格

| EMC测试项目 | 标准要求 | 测试结果 | 状态 |
|------------|----------|----------|------|
| 传导发射 | CISPR 32 | 45.2 dBμV | ✅ 通过 |
| 辐射发射 | CISPR 32 | 38.1 dBμV/m | ✅ 通过 |
| 静电放电 | IEC 61000-4-2 | ±8kV | ✅ 通过 |

### 4. 代码块

\`\`\`python
# EMC测试数据分析示例
import numpy as np
import matplotlib.pyplot as plt

def analyze_emc_data(frequencies, amplitudes):
    """分析EMC测试数据"""
    max_amplitude = np.max(amplitudes)
    limit_line = get_cispr_limit(frequencies)
    
    return {
        'max_amplitude': max_amplitude,
        'compliance': np.all(amplitudes < limit_line),
        'margin': limit_line - max_amplitude
    }
\`\`\`

## 高级功能

### 🔗 链接和引用
- [EMC标准数据库](https://example.com/emc-standards)
- [测试设备手册](https://example.com/equipment-manual)

### 📝 注释和备注
> 💡 **提示**: 在进行EMC测试时，确保测试环境符合标准要求，避免外界干扰影响测试结果。

### ⚠️ 警告信息
> ⚠️ **注意**: 高压测试具有危险性，请确保操作人员具备相应资质并采取适当的安全防护措施。

---

## 快捷键参考

| 功能 | 快捷键 | 说明 |
|------|--------|------|
| 保存 | Ctrl+S | 保存当前文档 |
| 粗体 | Ctrl+B | 加粗选中文本 |
| 斜体 | Ctrl+I | 斜体选中文本 |
| 撤销 | Ctrl+Z | 撤销上一步操作 |
| 重做 | Ctrl+Y | 重做操作 |
| 查找 | Ctrl+F | 查找文本 |

---

**最后更新**: ${new Date().toLocaleString('zh-CN')}  
**文档版本**: 1.0.0  
**编辑器**: EMC知识图谱系统`;

  useEffect(() => {
    loadFiles();
    if (!currentFile) {
      setMarkdownContent(defaultContent);
    }
  }, []);

  useEffect(() => {
    if (settings.autoSave && unsavedChanges) {
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current);
      }
      autoSaveTimerRef.current = setTimeout(() => {
        handleSave();
      }, settings.autoSaveInterval * 1000);
    }

    return () => {
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current);
      }
    };
  }, [markdownContent, settings.autoSave, settings.autoSaveInterval]);

  const loadFiles = async () => {
    try {
      const response = await fetch('/api/markdown-files');
      if (response.ok) {
        const data = await response.json();
        setFiles(data);
      } else {
        // 使用模拟数据
        const mockFiles: MarkdownFile[] = [
          {
            id: 'md_1',
            name: 'EMC测试指南.md',
            content: '# EMC测试指南\n\n这是一个EMC测试的详细指南...',
            lastModified: '2025-06-11 15:30:00',
            path: '/docs/',
            tags: ['指南', 'EMC', '测试']
          },
          {
            id: 'md_2',
            name: '标准解读_IEC61000.md',
            content: '# IEC 61000标准解读\n\n## 概述\n\nIEC 61000系列标准...',
            lastModified: '2025-06-10 14:20:00',
            path: '/standards/',
            tags: ['标准', 'IEC', '解读']
          }
        ];
        setFiles(mockFiles);
      }
    } catch (error) {
      console.error('加载Markdown文件失败:', error);
    }
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMarkdownContent(e.target.value);
    setUnsavedChanges(true);
  };

  const handleSave = async () => {
    try {
      const fileData = {
        id: currentFile?.id || `md_${Date.now()}`,
        name: currentFile?.name || '未命名文档.md',
        content: markdownContent,
        lastModified: new Date().toLocaleString('zh-CN'),
        path: currentFile?.path || '/docs/',
        tags: currentFile?.tags || []
      };

      const response = await fetch('/api/markdown-files', {
        method: currentFile ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(fileData)
      });

      if (response.ok) {
        setUnsavedChanges(false);
        setCurrentFile(fileData);
        message.success('文档保存成功');
        loadFiles();
      } else {
        throw new Error('保存失败');
      }
    } catch (error) {
      message.error('文档保存失败');
    }
  };

  const handleNewFile = () => {
    if (unsavedChanges) {
      Modal.confirm({
        title: '未保存的更改',
        content: '当前文档有未保存的更改，是否保存？',
        okText: '保存',
        cancelText: '不保存',
        onOk: () => {
          handleSave();
          createNewFile();
        },
        onCancel: createNewFile
      });
    } else {
      createNewFile();
    }
  };

  const createNewFile = () => {
    setCurrentFile(null);
    setMarkdownContent('# 新建文档\n\n开始编写您的内容...\n');
    setUnsavedChanges(false);
  };

  const handleOpenFile = (file: MarkdownFile) => {
    if (unsavedChanges) {
      Modal.confirm({
        title: '未保存的更改',
        content: '当前文档有未保存的更改，是否保存？',
        okText: '保存',
        cancelText: '不保存',
        onOk: () => {
          handleSave();
          openFile(file);
        },
        onCancel: () => openFile(file)
      });
    } else {
      openFile(file);
    }
  };

  const openFile = (file: MarkdownFile) => {
    setCurrentFile(file);
    setMarkdownContent(file.content);
    setUnsavedChanges(false);
  };

  const insertMarkdown = (syntax: string, placeholder: string = '') => {
    if (editorRef.current) {
      const textarea = editorRef.current;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const selectedText = markdownContent.substring(start, end);
      const replacement = syntax.replace(placeholder, selectedText || placeholder);
      
      const newContent = 
        markdownContent.substring(0, start) + 
        replacement + 
        markdownContent.substring(end);
      
      setMarkdownContent(newContent);
      setUnsavedChanges(true);
      
      // 重新聚焦并设置光标位置
      setTimeout(() => {
        textarea.focus();
        const newPosition = start + replacement.length;
        textarea.setSelectionRange(newPosition, newPosition);
      }, 0);
    }
  };

  const toolbarItems = [
    {
      key: 'bold',
      icon: <BoldOutlined />,
      tooltip: '粗体 (Ctrl+B)',
      action: () => insertMarkdown('**{text}**', '{text}')
    },
    {
      key: 'italic',
      icon: <ItalicOutlined />,
      tooltip: '斜体 (Ctrl+I)',
      action: () => insertMarkdown('*{text}*', '{text}')
    },
    {
      key: 'code',
      icon: <CodeOutlined />,
      tooltip: '行内代码',
      action: () => insertMarkdown('`{text}`', '{text}')
    },
    {
      key: 'link',
      icon: <LinkOutlined />,
      tooltip: '链接',
      action: () => insertMarkdown('[{text}](url)', '{text}')
    },
    {
      key: 'image',
      icon: <PictureOutlined />,
      tooltip: '图片',
      action: () => insertMarkdown('![{text}](image-url)', '{text}')
    },
    {
      key: 'table',
      icon: <TableOutlined />,
      tooltip: '表格',
      action: () => insertMarkdown('\n| 列1 | 列2 | 列3 |\n|------|------|------|\n| 数据1 | 数据2 | 数据3 |\n')
    },
    {
      key: 'ul',
      icon: <UnorderedListOutlined />,
      tooltip: '无序列表',
      action: () => insertMarkdown('\n- 列表项\n- 列表项\n- 列表项\n')
    },
    {
      key: 'ol',
      icon: <OrderedListOutlined />,
      tooltip: '有序列表',
      action: () => insertMarkdown('\n1. 列表项\n2. 列表项\n3. 列表项\n')
    }
  ];

  const renderPreview = () => {
    // 简单的Markdown预览实现
    let html = markdownContent
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/gim, '<em>$1</em>')
      .replace(/`(.*?)`/gim, '<code>$1</code>')
      .replace(/^\- (.*$)/gim, '<li>$1</li>')
      .replace(/^\d+\. (.*$)/gim, '<li>$1</li>')
      .replace(/\n/gim, '<br>');

    return (
      <div 
        className="markdown-preview"
        style={{ 
          padding: '16px',
          minHeight: '500px',
          backgroundColor: '#fff',
          border: '1px solid #d9d9d9',
          borderRadius: '6px',
          fontFamily: '"Chinese Quote", -apple-system, BlinkMacSystemFont, "Segoe UI"'
        }}
        dangerouslySetInnerHTML={{ __html: html }}
      />
    );
  };

  const fileSelectMenu = (
    <Menu>
      {files.map(file => (
        <Menu.Item key={file.id} onClick={() => handleOpenFile(file)}>
          <Space>
            <EditOutlined />
            {file.name}
            <Text type="secondary" style={{ fontSize: '12px' }}>
              {file.lastModified}
            </Text>
          </Space>
        </Menu.Item>
      ))}
    </Menu>
  );

  return (
    <div className="fade-in-up" style={{ height: isFullscreen ? '100vh' : 'auto' }}>
      <Title level={2} style={{ textAlign: 'center', marginBottom: 24 }}>
        📝 Markdown智能编辑器
      </Title>

      {/* 工具栏 */}
      <Card className="chinese-card" style={{ marginBottom: 16 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space wrap>
              <Dropdown overlay={fileSelectMenu} trigger={['click']}>
                <Button icon={<FolderOpenOutlined />}>
                  打开文件 ({files.length})
                </Button>
              </Dropdown>
              <Button 
                icon={<FileAddOutlined />}
                onClick={handleNewFile}
              >
                新建文档
              </Button>
              <Button 
                type="primary"
                icon={<SaveOutlined />}
                onClick={handleSave}
                className="chinese-btn-primary"
                disabled={!unsavedChanges}
              >
                保存 {unsavedChanges && '*'}
              </Button>
              <Divider type="vertical" />
              {toolbarItems.map(item => (
                <Tooltip key={item.key} title={item.tooltip}>
                  <Button 
                    icon={item.icon}
                    size="small"
                    onClick={item.action}
                  />
                </Tooltip>
              ))}
            </Space>
          </Col>
          <Col>
            <Space>
              <Select
                value={previewMode}
                onChange={setPreviewMode}
                size="small"
                className="chinese-input"
              >
                <Select.Option value="edit">编辑</Select.Option>
                <Select.Option value="preview">预览</Select.Option>
                <Select.Option value="split">分屏</Select.Option>
              </Select>
              <Button 
                icon={<SettingOutlined />}
                size="small"
                onClick={() => setShowSettings(true)}
              />
              <Button 
                icon={<FullscreenOutlined />}
                size="small"
                onClick={() => setIsFullscreen(!isFullscreen)}
              />
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 文件信息 */}
      {currentFile && (
        <Alert
          message={
            <Space>
              <Text strong>当前文件: {currentFile.name}</Text>
              <Text type="secondary">最后修改: {currentFile.lastModified}</Text>
              {currentFile.tags.map(tag => (
                <Tag key={tag} color="blue">{tag}</Tag>
              ))}
            </Space>
          }
          type="info"
          style={{ marginBottom: 16 }}
        />
      )}

      {/* 编辑器主体 */}
      <Card className="chinese-card">
        <Row gutter={16}>
          {(previewMode === 'edit' || previewMode === 'split') && (
            <Col xs={24} lg={previewMode === 'split' ? 12 : 24}>
              <div style={{ position: 'relative' }}>
                <TextArea
                  ref={editorRef}
                  value={markdownContent}
                  onChange={handleContentChange}
                  placeholder="开始编写您的Markdown文档..."
                  style={{
                    minHeight: '600px',
                    fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
                    fontSize: settings.fontSize,
                    lineHeight: settings.lineHeight,
                    resize: 'vertical'
                  }}
                  className="chinese-input"
                />
                {settings.showLineNumbers && (
                  <div style={{
                    position: 'absolute',
                    left: 0,
                    top: 0,
                    bottom: 0,
                    width: '40px',
                    backgroundColor: '#f5f5f5',
                    borderRight: '1px solid #d9d9d9',
                    fontSize: '12px',
                    color: '#999',
                    padding: '8px 4px',
                    fontFamily: 'Monaco, Menlo, monospace',
                    pointerEvents: 'none'
                  }}>
                    {markdownContent.split('\n').map((_, index) => (
                      <div key={index} style={{ height: `${settings.lineHeight}em` }}>
                        {index + 1}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </Col>
          )}
          
          {(previewMode === 'preview' || previewMode === 'split') && (
            <Col xs={24} lg={previewMode === 'split' ? 12 : 24}>
              <div style={{ 
                border: '1px solid #d9d9d9',
                borderRadius: '6px',
                minHeight: '600px',
                backgroundColor: '#fafafa'
              }}>
                <div style={{
                  padding: '8px 16px',
                  borderBottom: '1px solid #d9d9d9',
                  backgroundColor: '#f0f0f0',
                  fontWeight: 'bold',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8
                }}>
                  <EyeOutlined />
                  预览效果
                </div>
                {renderPreview()}
              </div>
            </Col>
          )}
        </Row>
      </Card>

      {/* 设置模态框 */}
      <Modal
        title="编辑器设置"
        open={showSettings}
        onCancel={() => setShowSettings(false)}
        onOk={() => setShowSettings(false)}
        className="chinese-card"
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>主题:</Text>
            <Select
              value={settings.theme}
              onChange={(value) => setSettings(prev => ({ ...prev, theme: value }))}
              style={{ width: '100%', marginTop: 8 }}
              className="chinese-input"
            >
              <Select.Option value="light">浅色主题</Select.Option>
              <Select.Option value="dark">深色主题</Select.Option>
            </Select>
          </div>
          
          <div>
            <Text strong>字体大小:</Text>
            <Select
              value={settings.fontSize}
              onChange={(value) => setSettings(prev => ({ ...prev, fontSize: value }))}
              style={{ width: '100%', marginTop: 8 }}
              className="chinese-input"
            >
              <Select.Option value={12}>12px</Select.Option>
              <Select.Option value={14}>14px</Select.Option>
              <Select.Option value={16}>16px</Select.Option>
              <Select.Option value={18}>18px</Select.Option>
            </Select>
          </div>

          <div>
            <Text strong>自动换行:</Text>
            <Switch
              checked={settings.wordWrap}
              onChange={(checked) => setSettings(prev => ({ ...prev, wordWrap: checked }))}
              style={{ marginLeft: 16 }}
            />
          </div>

          <div>
            <Text strong>显示行号:</Text>
            <Switch
              checked={settings.showLineNumbers}
              onChange={(checked) => setSettings(prev => ({ ...prev, showLineNumbers: checked }))}
              style={{ marginLeft: 16 }}
            />
          </div>

          <div>
            <Text strong>自动保存:</Text>
            <Switch
              checked={settings.autoSave}
              onChange={(checked) => setSettings(prev => ({ ...prev, autoSave: checked }))}
              style={{ marginLeft: 16 }}
            />
          </div>
        </Space>
      </Modal>
    </div>
  );
};

export default MarkdownEditor;