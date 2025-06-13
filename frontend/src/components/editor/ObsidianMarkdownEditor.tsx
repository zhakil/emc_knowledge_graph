import React, { useState, useEffect, useRef } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Input,
  Space,
  Tooltip,
  Modal,
  message,
  Typography,
  Divider,
  Tag,
  Alert,
  Tree,
  Upload,
  Dropdown,
  Menu,
  Collapse,
  Switch,
  Tabs,
  Drawer,
  List,
  Badge,
  AutoComplete,
  Segmented
} from 'antd';
import {
  EditOutlined,
  EyeOutlined,
  SaveOutlined,
  FolderOutlined,
  FileOutlined,
  FileAddOutlined,
  BoldOutlined,
  ItalicOutlined,
  LinkOutlined,
  PictureOutlined,
  TableOutlined,
  OrderedListOutlined,
  UnorderedListOutlined,
  CodeOutlined,
  FullscreenOutlined,
  SettingOutlined,
  DownloadOutlined,
  UploadOutlined,
  SearchOutlined,
  FolderOpenOutlined,
  FileMarkdownOutlined,
  CaretRightOutlined,
  CaretDownOutlined,
  DeleteOutlined,
  CopyOutlined,
  PlusOutlined,
  ImportOutlined,
  ExportOutlined,
  SyncOutlined,
  MoreOutlined
} from '@ant-design/icons';
import type { DataNode } from 'antd/es/tree';
import type { RcFile } from 'antd/es/upload';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

interface MarkdownFile {
  id: string;
  name: string;
  content: string;
  lastModified: string;
  path: string;
  tags: string[];
  parentId?: string;
  children?: MarkdownFile[];
  isExpanded?: boolean;
  type: 'file' | 'folder';
  size?: number;
}

interface FileNode extends DataNode {
  fileData: MarkdownFile;
  children?: FileNode[];
}

const ObsidianMarkdownEditor: React.FC = () => {
  const [markdownContent, setMarkdownContent] = useState('');
  const [currentFile, setCurrentFile] = useState<MarkdownFile | null>(null);
  const [files, setFiles] = useState<MarkdownFile[]>([]);
  const [fileTree, setFileTree] = useState<FileNode[]>([]);
  const [previewMode, setPreviewMode] = useState<'edit' | 'preview' | 'split'>('split');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showFileTree, setShowFileTree] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredFiles, setFilteredFiles] = useState<MarkdownFile[]>([]);
  const [unsavedChanges, setUnsavedChanges] = useState(false);
  const [expandedKeys, setExpandedKeys] = useState<React.Key[]>([]);
  const [selectedKeys, setSelectedKeys] = useState<React.Key[]>([]);
  const [showImportModal, setShowImportModal] = useState(false);
  const [importProgress, setImportProgress] = useState(0);
  
  const editorRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadFiles();
    initializeDefaultContent();
  }, []);

  useEffect(() => {
    buildFileTree();
  }, [files]);

  useEffect(() => {
    filterFiles();
  }, [files, searchTerm]);

  const initializeDefaultContent = () => {
    const defaultContent = `# 📚 Obsidian风格Markdown编辑器

## 🌟 主要功能

### 📂 文件管理
- **树形结构**: 类似Obsidian的文件夹展开/折叠
- **快速搜索**: 实时搜索文件名和内容
- **批量导入**: 支持从外部导入多个.md文件
- **文件组织**: 拖拽文件到不同文件夹

### ✏️ 编辑功能
- **实时预览**: 分屏或独立预览模式
- **语法高亮**: Markdown语法智能识别
- **快捷工具**: 丰富的编辑工具栏
- **自动保存**: 防止数据丢失

### 🔗 链接系统
- **内部链接**: [[文件名]] 格式链接到其他文档
- **标签系统**: #标签 快速分类和检索
- **反向链接**: 查看哪些文档引用了当前文档

## 📝 语法示例

### 基础格式
**粗体文本** 和 *斜体文本*

### 列表
1. 有序列表项 1
2. 有序列表项 2
   - 嵌套无序列表
   - 另一个项目

### 代码块
\`\`\`javascript
// EMC数据分析示例
function analyzeEMCData(data) {
  return data.filter(item => item.compliance);
}
\`\`\`

### 表格
| 测试项目 | 标准 | 结果 | 状态 |
|---------|------|------|------|
| 传导发射 | CISPR 32 | 通过 | ✅ |
| 辐射发射 | CISPR 32 | 通过 | ✅ |
| 静电放电 | IEC 61000-4-2 | 通过 | ✅ |

### 内部链接示例
- [[EMC测试指南]]
- [[设备规格文档]]
- [[标准解读文档]]

### 标签
#EMC #测试 #文档 #知识管理

---

**开始使用**: 左侧文件树可以创建新文档或导入现有文件
`;
    setMarkdownContent(defaultContent);
  };

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
            id: 'folder_1',
            name: 'EMC知识库',
            content: '',
            lastModified: '2025-06-12',
            path: '/',
            tags: [],
            type: 'folder',
            children: [
              {
                id: 'file_1',
                name: 'EMC测试指南.md',
                content: '# EMC测试指南\\n\\n这是一个完整的EMC测试指南文档...',
                lastModified: '2025-06-12',
                path: '/EMC知识库/',
                tags: ['EMC', '测试', '指南'],
                parentId: 'folder_1',
                type: 'file',
                size: 1024
              },
              {
                id: 'file_2',
                name: '标准解读_IEC61000.md',
                content: '# IEC 61000标准解读\\n\\n## 概述\\n\\nIEC 61000系列标准...',
                lastModified: '2025-06-11',
                path: '/EMC知识库/',
                tags: ['标准', 'IEC', '解读'],
                parentId: 'folder_1',
                type: 'file',
                size: 2048
              }
            ]
          },
          {
            id: 'folder_2',
            name: '设备文档',
            content: '',
            lastModified: '2025-06-10',
            path: '/',
            tags: [],
            type: 'folder',
            children: [
              {
                id: 'file_3',
                name: '设备A规格说明.md',
                content: '# 设备A规格说明\\n\\n## 技术参数\\n\\n...',
                lastModified: '2025-06-10',
                path: '/设备文档/',
                tags: ['设备', '规格', '技术'],
                parentId: 'folder_2',
                type: 'file',
                size: 1536
              }
            ]
          }
        ];
        setFiles(mockFiles);
      }
    } catch (error) {
      console.error('加载文件失败:', error);
      message.error('加载文件失败');
    }
  };

  const buildFileTree = () => {
    const buildNodes = (items: MarkdownFile[]): FileNode[] => {
      return items.map(item => ({
        key: item.id,
        title: (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            {item.type === 'folder' ? (
              <FolderOutlined style={{ color: '#faad14' }} />
            ) : (
              <FileMarkdownOutlined style={{ color: '#1890ff' }} />
            )}
            <span>{item.name}</span>
            {item.tags.length > 0 && (
              <Badge count={item.tags.length} size="small" />
            )}
          </div>
        ),
        fileData: item,
        children: item.children ? buildNodes(item.children) : undefined,
        isLeaf: item.type === 'file'
      }));
    };
    
    setFileTree(buildNodes(files));
  };

  const filterFiles = () => {
    if (!searchTerm) {
      setFilteredFiles([]);
      return;
    }

    const getAllFiles = (items: MarkdownFile[]): MarkdownFile[] => {
      const result: MarkdownFile[] = [];
      items.forEach(item => {
        if (item.type === 'file') {
          result.push(item);
        }
        if (item.children) {
          result.push(...getAllFiles(item.children));
        }
      });
      return result;
    };

    const allFiles = getAllFiles(files);
    const filtered = allFiles.filter(file =>
      file.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      file.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
      file.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    );
    setFilteredFiles(filtered);
  };

  const handleFileSelect = (selectedKeys: React.Key[], info: any) => {
    if (selectedKeys.length > 0) {
      const node = info.node;
      if (node.fileData.type === 'file') {
        if (unsavedChanges) {
          Modal.confirm({
            title: '未保存的更改',
            content: '当前文档有未保存的更改，是否保存？',
            okText: '保存',
            cancelText: '不保存',
            onOk: () => {
              handleSave();
              openFile(node.fileData);
            },
            onCancel: () => openFile(node.fileData)
          });
        } else {
          openFile(node.fileData);
        }
      }
    }
    setSelectedKeys(selectedKeys);
  };

  const openFile = (file: MarkdownFile) => {
    setCurrentFile(file);
    setMarkdownContent(file.content);
    setUnsavedChanges(false);
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMarkdownContent(e.target.value);
    setUnsavedChanges(true);
  };

  const handleSave = async () => {
    if (!currentFile) {
      message.warning('请先选择或创建一个文件');
      return;
    }

    try {
      const fileData = {
        ...currentFile,
        content: markdownContent,
        lastModified: new Date().toISOString().split('T')[0]
      };

      // 更新本地状态
      const updateFiles = (items: MarkdownFile[]): MarkdownFile[] => {
        return items.map(item => {
          if (item.id === currentFile.id) {
            return fileData;
          }
          if (item.children) {
            return { ...item, children: updateFiles(item.children) };
          }
          return item;
        });
      };

      setFiles(updateFiles(files));
      setCurrentFile(fileData);
      setUnsavedChanges(false);
      message.success('文档保存成功');
    } catch (error) {
      message.error('文档保存失败');
    }
  };

  const handleNewFile = () => {
    const newFile: MarkdownFile = {
      id: `file_${Date.now()}`,
      name: '新建文档.md',
      content: '# 新建文档\n\n开始编写您的内容...\n',
      lastModified: new Date().toISOString().split('T')[0],
      path: '/',
      tags: [],
      type: 'file',
      size: 0
    };

    if (unsavedChanges) {
      Modal.confirm({
        title: '未保存的更改',
        content: '当前文档有未保存的更改，是否保存？',
        okText: '保存',
        cancelText: '不保存',
        onOk: () => {
          handleSave();
          createNewFile(newFile);
        },
        onCancel: () => createNewFile(newFile)
      });
    } else {
      createNewFile(newFile);
    }
  };

  const createNewFile = (newFile: MarkdownFile) => {
    setFiles(prev => [...prev, newFile]);
    setCurrentFile(newFile);
    setMarkdownContent(newFile.content);
    setUnsavedChanges(false);
  };

  const handleImportFiles = async (fileList: RcFile[]) => {
    setImportProgress(0);
    setShowImportModal(true);

    try {
      // 创建FormData来上传文件
      const formData = new FormData();
      fileList.forEach((file) => {
        formData.append('files', file);
      });

      setImportProgress(20);

      // 调用后端API导入文件夹
      const response = await fetch('/api/markdown-files/import-folder', {
        method: 'POST',
        body: formData,
      });

      setImportProgress(70);

      if (response.ok) {
        const result = await response.json();
        setImportProgress(90);

        // 重新加载文件列表
        await loadFiles();
        setImportProgress(100);

        message.success(result.message);
        
        setTimeout(() => {
          setShowImportModal(false);
          setImportProgress(0);
        }, 1000);
      } else {
        throw new Error('导入失败');
      }
    } catch (error) {
      message.error('文件导入失败');
      setShowImportModal(false);
      setImportProgress(0);
    }
  };

  const handleImportFolder = () => {
    // 创建一个文件选择器，支持选择多个文件
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = '.md,.markdown,.txt,.html,.htm';
    input.setAttribute('webkitdirectory', 'true'); // 支持文件夹选择
    
    input.onchange = (e) => {
      const target = e.target as HTMLInputElement;
      if (target.files && target.files.length > 0) {
        const fileList = Array.from(target.files) as RcFile[];
        handleImportFiles(fileList);
      }
    };
    
    input.click();
  };

  const readFileContent = (file: RcFile): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        resolve(e.target?.result as string);
      };
      reader.onerror = reject;
      reader.readAsText(file, 'UTF-8');
    });
  };

  // 查找并打开链接的文件
  const findAndOpenLinkedFile = (linkText: string) => {
    const getAllFiles = (items: MarkdownFile[]): MarkdownFile[] => {
      const result: MarkdownFile[] = [];
      items.forEach(item => {
        if (item.type === 'file') {
          result.push(item);
        }
        if (item.children) {
          result.push(...getAllFiles(item.children));
        }
      });
      return result;
    };

    const allFiles = getAllFiles(files);
    const targetFile = allFiles.find(file => 
      file.name === `${linkText}.md` || 
      file.name === linkText ||
      file.name.includes(linkText)
    );

    if (targetFile) {
      if (unsavedChanges) {
        Modal.confirm({
          title: '未保存的更改',
          content: '当前文档有未保存的更改，是否保存？',
          okText: '保存',
          cancelText: '不保存',
          onOk: () => {
            handleSave();
            openFile(targetFile);
          },
          onCancel: () => openFile(targetFile)
        });
      } else {
        openFile(targetFile);
      }
    } else {
      message.info(`未找到文档: ${linkText}`);
    }
  };

  const renderPreview = () => {
    // 处理内部链接
    const processInternalLinks = (content: string) => {
      return content.replace(/\[\[(.*?)\]\]/gim, (match, linkText) => {
        return `<span 
          class="internal-link" 
          data-link="${linkText}"
          style="
            color: #1890ff; 
            background: #e6f7ff; 
            padding: 2px 6px; 
            border-radius: 4px;
            cursor: pointer;
            border: 1px solid #91d5ff;
            display: inline-block;
            margin: 0 2px;
            transition: all 0.3s ease;
          "
          onmouseover="this.style.background='#bae7ff'; this.style.transform='scale(1.05)'"
          onmouseout="this.style.background='#e6f7ff'; this.style.transform='scale(1)'"
        >🔗 ${linkText}</span>`;
      });
    };

    // 处理标签
    const processTags = (content: string) => {
      return content.replace(/#(\w+)/gim, (match, tagText) => {
        return `<span 
          class="tag-link"
          style="
            color: #722ed1; 
            background: #f9f0ff; 
            padding: 2px 6px; 
            border-radius: 4px;
            border: 1px solid #d3adf7;
            display: inline-block;
            margin: 0 2px;
            font-size: 12px;
          "
        >#${tagText}</span>`;
      });
    };

    // 基础Markdown处理
    let html = markdownContent
      .replace(/^# (.*$)/gim, '<h1 style="color: #2c3e50; border-bottom: 2px solid #d4af37; padding-bottom: 8px;">$1</h1>')
      .replace(/^## (.*$)/gim, '<h2 style="color: #34495e; border-bottom: 1px solid #d4af37; padding-bottom: 4px;">$1</h2>')
      .replace(/^### (.*$)/gim, '<h3 style="color: #34495e;">$1</h3>')
      .replace(/\*\*(.*?)\*\*/gim, '<strong style="color: #2c3e50;">$1</strong>')
      .replace(/\*(.*?)\*/gim, '<em style="color: #34495e;">$1</em>')
      .replace(/`(.*?)`/gim, '<code style="background: #f4f4f4; padding: 2px 4px; border-radius: 3px; color: #e74c3c;">$1</code>')
      .replace(/^\- (.*$)/gim, '<li style="margin: 4px 0;">$1</li>')
      .replace(/^\d+\. (.*$)/gim, '<li style="margin: 4px 0;">$1</li>')
      .replace(/\n/gim, '<br>');

    // 处理内部链接和标签
    html = processInternalLinks(html);
    html = processTags(html);

    // 处理表格
    html = html.replace(/\|(.+)\|/g, (match) => {
      const cells = match.split('|').filter(cell => cell.trim());
      return '<tr>' + cells.map(cell => `<td style="border: 1px solid #d9d9d9; padding: 8px;">${cell.trim()}</td>`).join('') + '</tr>';
    });

    return (
      <div 
        className="markdown-preview"
        style={{ 
          padding: '16px',
          minHeight: '500px',
          backgroundColor: '#fff',
          border: '1px solid #d9d9d9',
          borderRadius: '6px',
          fontFamily: 'SimSun, 宋体, serif',
          lineHeight: '1.6'
        }}
        dangerouslySetInnerHTML={{ __html: html }}
        onClick={(e) => {
          const target = e.target as HTMLElement;
          if (target.classList.contains('internal-link')) {
            const linkText = target.getAttribute('data-link');
            if (linkText) {
              findAndOpenLinkedFile(linkText);
            }
          }
        }}
      />
    );
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
      key: 'link',
      icon: <LinkOutlined />,
      tooltip: '内部链接',
      action: () => insertMarkdown('[[{text}]]', '{text}')
    },
    {
      key: 'code',
      icon: <CodeOutlined />,
      tooltip: '行内代码',
      action: () => insertMarkdown('`{text}`', '{text}')
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
      action: () => insertMarkdown('\n- 列表项\n- 列表项\n')
    },
    {
      key: 'ol',
      icon: <OrderedListOutlined />,
      tooltip: '有序列表',
      action: () => insertMarkdown('\n1. 列表项\n2. 列表项\n')
    }
  ];

  return (
    <div className="fade-in-up" style={{ height: isFullscreen ? '100vh' : 'auto' }}>
      <Title level={2} style={{ textAlign: 'center', marginBottom: 24 }}>
        📚 Obsidian风格Markdown编辑器
      </Title>

      <Row gutter={16} style={{ height: isFullscreen ? 'calc(100vh - 120px)' : '700px' }}>
        {/* 左侧文件树 */}
        {showFileTree && (
          <Col xs={24} sm={8} md={6} style={{ height: '100%' }}>
            <Card 
              title={
                <Space>
                  <FolderOutlined />
                  文件管理器
                </Space>
              }
              size="small"
              className="chinese-card"
              style={{ height: '100%' }}
              bodyStyle={{ padding: '8px', height: 'calc(100% - 45px)', overflow: 'auto' }}
              extra={
                <Space>
                  <Tooltip title="新建文件">
                    <Button 
                      type="text" 
                      size="small" 
                      icon={<FileAddOutlined />} 
                      onClick={handleNewFile}
                    />
                  </Tooltip>
                  <Tooltip title="导入文件">
                    <Upload
                      multiple
                      accept=".md,.markdown,.txt,.html,.htm"
                      showUploadList={false}
                      beforeUpload={(file, fileList) => {
                        handleImportFiles(fileList as RcFile[]);
                        return false;
                      }}
                    >
                      <Button type="text" size="small" icon={<ImportOutlined />} />
                    </Upload>
                  </Tooltip>
                  <Tooltip title="导入文件夹">
                    <Button 
                      type="text" 
                      size="small" 
                      icon={<FolderOutlined />} 
                      onClick={handleImportFolder}
                    />
                  </Tooltip>
                </Space>
              }
            >
              <Space direction="vertical" style={{ width: '100%', marginBottom: 8 }}>
                <Input
                  size="small"
                  placeholder="搜索文件..."
                  prefix={<SearchOutlined />}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  allowClear
                />
              </Space>

              {searchTerm && filteredFiles.length > 0 ? (
                <List
                  size="small"
                  dataSource={filteredFiles}
                  renderItem={(file) => (
                    <List.Item
                      style={{ padding: '4px 0', cursor: 'pointer' }}
                      onClick={() => openFile(file)}
                    >
                      <Space>
                        <FileMarkdownOutlined style={{ color: '#1890ff' }} />
                        <Text ellipsis={{ tooltip: file.name }} style={{ maxWidth: 150 }}>
                          {file.name}
                        </Text>
                      </Space>
                    </List.Item>
                  )}
                />
              ) : (
                <Tree
                  showLine
                  switcherIcon={<CaretDownOutlined />}
                  treeData={fileTree}
                  expandedKeys={expandedKeys}
                  selectedKeys={selectedKeys}
                  onExpand={setExpandedKeys}
                  onSelect={handleFileSelect}
                  style={{ background: 'transparent' }}
                />
              )}
            </Card>
          </Col>
        )}

        {/* 右侧编辑区域 */}
        <Col xs={24} sm={showFileTree ? 16 : 24} md={showFileTree ? 18 : 24} style={{ height: '100%' }}>
          <Card 
            className="chinese-card" 
            style={{ height: '100%' }}
            bodyStyle={{ padding: '12px', height: 'calc(100% - 45px)' }}
            title={
              <Space>
                <FileMarkdownOutlined />
                {currentFile ? currentFile.name : '新建文档'}
                {unsavedChanges && <Tag color="warning">未保存</Tag>}
              </Space>
            }
            extra={
              <Space>
                <Button
                  type={showFileTree ? 'default' : 'primary'}
                  size="small"
                  icon={<FolderOutlined />}
                  onClick={() => setShowFileTree(!showFileTree)}
                >
                  {showFileTree ? '隐藏' : '显示'}文件树
                </Button>
                <Segmented
                  size="small"
                  value={previewMode}
                  onChange={setPreviewMode}
                  options={[
                    { label: '编辑', value: 'edit', icon: <EditOutlined /> },
                    { label: '预览', value: 'preview', icon: <EyeOutlined /> },
                    { label: '分屏', value: 'split' }
                  ]}
                />
                <Button
                  type="primary"
                  size="small"
                  icon={<SaveOutlined />}
                  onClick={handleSave}
                  disabled={!unsavedChanges}
                >
                  保存
                </Button>
              </Space>
            }
          >
            {/* 工具栏 */}
            <Space wrap style={{ marginBottom: 12, padding: '8px', background: '#fafafa', borderRadius: '6px' }}>
              {toolbarItems.map(item => (
                <Tooltip key={item.key} title={item.tooltip}>
                  <Button 
                    icon={item.icon}
                    size="small"
                    onClick={item.action}
                  />
                </Tooltip>
              ))}
              <Divider type="vertical" />
              <Tooltip title="插入标签">
                <Button 
                  size="small" 
                  onClick={() => insertMarkdown('#标签名 ')}
                >
                  #标签
                </Button>
              </Tooltip>
              <Tooltip title="插入内部链接">
                <Button 
                  size="small" 
                  onClick={() => insertMarkdown('[[文档名]] ')}
                >
                  [[链接]]
                </Button>
              </Tooltip>
            </Space>

            {/* 编辑器主体 */}
            <div style={{ height: 'calc(100% - 80px)' }}>
              <Row gutter={8} style={{ height: '100%' }}>
                {(previewMode === 'edit' || previewMode === 'split') && (
                  <Col xs={24} lg={previewMode === 'split' ? 12 : 24} style={{ height: '100%' }}>
                    <TextArea
                      ref={editorRef}
                      value={markdownContent}
                      onChange={handleContentChange}
                      placeholder="开始编写您的Markdown文档...&#10;&#10;💡 使用 [[文档名]] 创建内部链接&#10;💡 使用 #标签 添加标签&#10;💡 支持拖拽导入.md文件"
                      style={{
                        height: '100%',
                        fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
                        fontSize: '14px',
                        lineHeight: 1.6,
                        resize: 'none',
                        border: '1px solid #d9d9d9',
                        borderRadius: '6px'
                      }}
                      className="chinese-input"
                    />
                  </Col>
                )}
                
                {(previewMode === 'preview' || previewMode === 'split') && (
                  <Col xs={24} lg={previewMode === 'split' ? 12 : 24} style={{ height: '100%' }}>
                    <div style={{ 
                      height: '100%',
                      border: '1px solid #d9d9d9',
                      borderRadius: '6px',
                      backgroundColor: '#fafafa',
                      overflow: 'auto'
                    }}>
                      <div style={{
                        padding: '8px 16px',
                        borderBottom: '1px solid #d9d9d9',
                        backgroundColor: '#f0f0f0',
                        fontWeight: 'bold',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 8,
                        position: 'sticky',
                        top: 0,
                        zIndex: 1
                      }}>
                        <EyeOutlined />
                        预览效果
                      </div>
                      <div style={{ height: 'calc(100% - 41px)', overflow: 'auto' }}>
                        {renderPreview()}
                      </div>
                    </div>
                  </Col>
                )}
              </Row>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 导入进度模态框 */}
      <Modal
        title="导入Markdown文件"
        open={showImportModal}
        footer={null}
        closable={false}
        centered
      >
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <div style={{ marginBottom: 16 }}>
            <SyncOutlined spin style={{ fontSize: 24, color: '#1890ff' }} />
          </div>
          <div style={{ marginBottom: 16 }}>
            正在导入文件... {Math.round(importProgress)}%
          </div>
          <div style={{ 
            width: '100%', 
            height: 6, 
            backgroundColor: '#f0f0f0', 
            borderRadius: 3,
            overflow: 'hidden'
          }}>
            <div 
              style={{ 
                width: `${importProgress}%`, 
                height: '100%', 
                backgroundColor: '#1890ff',
                transition: 'width 0.3s ease'
              }} 
            />
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default ObsidianMarkdownEditor;