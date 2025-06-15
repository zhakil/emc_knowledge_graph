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
  Dropdown,
  Menu,
  Collapse,
  Switch,
  Tabs,
  Drawer,
  List,
  Badge,
  AutoComplete,
  Segmented,
  Progress,
  Upload
} from 'antd';
import type { RcFile } from 'antd/es/upload/interface';
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

欢迎使用Markdown编辑器！目前没有任何文件。

## 🚀 快速开始

### 📂 文件管理
- 点击左侧工具栏的 **📄** 图标创建新文件
- 点击左侧工具栏的 **📁** 图标创建新文件夹
- 点击左侧工具栏的 **📥** 图标导入单个文件
- 点击左侧工具栏的 **📂** 图标导入整个文件夹

### ✏️ 编辑功能
- **实时预览**: 分屏或独立预览模式
- **语法高亮**: Markdown语法智能识别
- **快捷工具**: 丰富的编辑工具栏
- **自动保存**: 防止数据丢失

### 🔗 链接系统
- **内部链接**: [[文件名]] 格式链接到其他文档
- **标签系统**: #标签 快速分类和检索

## 📝 创建您的第一个文档

1. 点击左侧的 **新建文件** 按钮
2. 开始编写您的Markdown内容
3. 使用 **Ctrl+S** 或点击保存按钮保存文档

### 示例语法
**粗体文本** 和 *斜体文本*

\`\`\`javascript
// 代码示例
console.log("Hello World!");
\`\`\`

| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 数据1 | 数据2 | 数据3 |

#标签示例 #markdown #编辑器

---

开始您的知识管理之旅吧！
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
        // 初始状态为空，没有任何文件或文件夹
        setFiles([]);
      }
    } catch (error) {
      console.error('加载文件失败:', error);
      message.error('加载文件失败');
    }
  };

  const buildFileTree = () => {
    const getContextMenu = (item: MarkdownFile) => {
      const menuItems = [
        {
          key: 'new-file',
          label: '新建文件',
          icon: <FileAddOutlined />,
          onClick: () => handleNewFile(item.type === 'folder' ? item : undefined)
        },
        {
          key: 'new-folder',
          label: '新建文件夹',
          icon: <FolderOutlined />,
          onClick: () => handleNewFolder(item.type === 'folder' ? item : undefined)
        },
        { type: 'divider' as const },
        {
          key: 'rename',
          label: '重命名',
          icon: <EditOutlined />,
          onClick: () => handleRenameItem(item)
        },
        {
          key: 'delete',
          label: '删除',
          icon: <DeleteOutlined />,
          danger: true,
          onClick: () => handleDeleteItem(item)
        }
      ];

      return {
        items: menuItems
      };
    };

    const buildNodes = (items: MarkdownFile[]): FileNode[] => {
      return items.map(item => ({
        key: item.id,
        title: (
          <Dropdown
            menu={getContextMenu(item)}
            trigger={['contextMenu']}
          >
            <div 
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 8,
                padding: '2px 4px',
                borderRadius: 4,
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f5f5f5';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              {item.type === 'folder' ? (
                <FolderOutlined style={{ color: '#faad14' }} />
              ) : (
                <FileMarkdownOutlined style={{ color: '#1890ff' }} />
              )}
              <span style={{ userSelect: 'none' }}>{item.name}</span>
              {item.tags.length > 0 && (
                <Badge count={item.tags.length} size="small" />
              )}
            </div>
          </Dropdown>
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

  const handleNewFile = (parentFolder?: MarkdownFile) => {
    const newFile: MarkdownFile = {
      id: `file_${Date.now()}`,
      name: '新建文档.md',
      content: '# 新建文档\n\n开始编写您的内容...\n',
      lastModified: new Date().toISOString().split('T')[0],
      path: parentFolder ? `${parentFolder.path}${parentFolder.name}/` : '/',
      tags: [],
      type: 'file',
      size: 0,
      parentId: parentFolder?.id
    };

    if (unsavedChanges) {
      Modal.confirm({
        title: '未保存的更改',
        content: '当前文档有未保存的更改，是否保存？',
        okText: '保存',
        cancelText: '不保存',
        onOk: () => {
          handleSave();
          createNewFile(newFile, parentFolder);
        },
        onCancel: () => createNewFile(newFile, parentFolder)
      });
    } else {
      createNewFile(newFile, parentFolder);
    }
  };

  const handleNewFolder = (parentFolder?: MarkdownFile) => {
    Modal.confirm({
      title: '创建新文件夹',
      content: (
        <Input 
          placeholder="请输入文件夹名称"
          id="folder-name-input"
          onPressEnter={(e) => {
            const folderName = (e.target as HTMLInputElement).value;
            if (folderName) {
              createNewFolder(folderName, parentFolder);
              Modal.destroyAll();
            }
          }}
        />
      ),
      onOk: () => {
        const folderName = (document.getElementById('folder-name-input') as HTMLInputElement)?.value;
        if (folderName) {
          createNewFolder(folderName, parentFolder);
        } else {
          message.warning('请输入文件夹名称');
        }
      }
    });
  };

  const createNewFolder = (folderName: string, parentFolder?: MarkdownFile) => {
    const newFolder: MarkdownFile = {
      id: `folder_${Date.now()}`,
      name: folderName,
      content: '',
      lastModified: new Date().toISOString().split('T')[0],
      path: parentFolder ? `${parentFolder.path}${parentFolder.name}/` : '/',
      tags: [],
      type: 'folder',
      parentId: parentFolder?.id,
      children: []
    };

    if (parentFolder) {
      // 添加到父文件夹
      const updateFiles = (items: MarkdownFile[]): MarkdownFile[] => {
        return items.map(item => {
          if (item.id === parentFolder.id) {
            return {
              ...item,
              children: [...(item.children || []), newFolder]
            };
          }
          if (item.children) {
            return { ...item, children: updateFiles(item.children) };
          }
          return item;
        });
      };
      setFiles(updateFiles(files));
    } else {
      // 添加到根目录
      setFiles(prev => [...prev, newFolder]);
    }

    message.success('文件夹创建成功');
  };

  const createNewFile = (newFile: MarkdownFile, parentFolder?: MarkdownFile) => {
    if (parentFolder) {
      // 添加到父文件夹
      const updateFiles = (items: MarkdownFile[]): MarkdownFile[] => {
        return items.map(item => {
          if (item.id === parentFolder.id) {
            return {
              ...item,
              children: [...(item.children || []), newFile]
            };
          }
          if (item.children) {
            return { ...item, children: updateFiles(item.children) };
          }
          return item;
        });
      };
      setFiles(updateFiles(files));
    } else {
      // 添加到根目录
      setFiles(prev => [...prev, newFile]);
    }
    
    setCurrentFile(newFile);
    setMarkdownContent(newFile.content);
    setUnsavedChanges(false);
  };

  const handleRenameItem = (item: MarkdownFile) => {
    Modal.confirm({
      title: `重命名${item.type === 'folder' ? '文件夹' : '文件'}`,
      content: (
        <Input 
          placeholder={`请输入新的${item.type === 'folder' ? '文件夹' : '文件'}名称`}
          defaultValue={item.name}
          id="rename-input"
          onPressEnter={(e) => {
            const newName = (e.target as HTMLInputElement).value;
            if (newName && newName !== item.name) {
              performRename(item, newName);
              Modal.destroyAll();
            }
          }}
        />
      ),
      onOk: () => {
        const newName = (document.getElementById('rename-input') as HTMLInputElement)?.value;
        if (newName && newName !== item.name) {
          performRename(item, newName);
        } else {
          message.warning('请输入有效的名称');
        }
      }
    });
  };

  const performRename = (item: MarkdownFile, newName: string) => {
    const updateFiles = (items: MarkdownFile[]): MarkdownFile[] => {
      return items.map(fileItem => {
        if (fileItem.id === item.id) {
          return {
            ...fileItem,
            name: newName,
            lastModified: new Date().toISOString().split('T')[0]
          };
        }
        if (fileItem.children) {
          return { ...fileItem, children: updateFiles(fileItem.children) };
        }
        return fileItem;
      });
    };

    setFiles(updateFiles(files));
    if (currentFile?.id === item.id) {
      setCurrentFile({ ...currentFile, name: newName });
    }
    message.success(`${item.type === 'folder' ? '文件夹' : '文件'}重命名成功`);
  };

  const handleDeleteItem = (item: MarkdownFile) => {
    Modal.confirm({
      title: `删除${item.type === 'folder' ? '文件夹' : '文件'}`,
      content: `确定要删除${item.type === 'folder' ? '文件夹' : '文件'} "${item.name}" 吗？${item.type === 'folder' ? '此操作将删除文件夹内的所有内容。' : ''}`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: () => {
        performDelete(item);
      }
    });
  };

  const performDelete = (item: MarkdownFile) => {
    const updateFiles = (items: MarkdownFile[]): MarkdownFile[] => {
      return items.filter(fileItem => {
        if (fileItem.id === item.id) {
          return false;
        }
        if (fileItem.children) {
          fileItem.children = updateFiles(fileItem.children);
        }
        return true;
      });
    };

    setFiles(updateFiles(files));
    
    // 如果删除的是当前打开的文件，清空编辑器
    if (currentFile?.id === item.id) {
      setCurrentFile(null);
      setMarkdownContent('');
      setUnsavedChanges(false);
    }
    
    message.success(`${item.type === 'folder' ? '文件夹' : '文件'}删除成功`);
  };

  const handleImportFiles = async (fileList: RcFile[]) => {
    console.log('开始导入文件，数量:', fileList.length);
    setImportProgress(0);
    setShowImportModal(true);

    try {
      setImportProgress(10);

      // 按文件夹路径组织文件
      const filesByPath: { [path: string]: RcFile[] } = {};
      const folderStructure: { [path: string]: string[] } = {};

      console.log('分析文件结构...');

      fileList.forEach(file => {
        const fullPath = file.webkitRelativePath || file.name;
        const pathParts = fullPath.split('/');
        
        // 构建文件夹结构
        let currentPath = '';
        pathParts.slice(0, -1).forEach((part: string) => {
          const parentPath = currentPath;
          currentPath = currentPath ? `${currentPath}/${part}` : part;
          
          if (!folderStructure[parentPath]) {
            folderStructure[parentPath] = [];
          }
          if (!folderStructure[parentPath].includes(currentPath)) {
            folderStructure[parentPath].push(currentPath);
          }
        });

        // 按路径分组文件
        const dirPath = pathParts.slice(0, -1).join('/');
        if (!filesByPath[dirPath]) {
          filesByPath[dirPath] = [];
        }
        filesByPath[dirPath].push(file);
      });

      setImportProgress(30);

      // 创建文件夹结构
      const newFolders: { [path: string]: MarkdownFile } = {};
      const rootFolders: MarkdownFile[] = [];

      // 按路径深度排序，确保父文件夹先创建
      const sortedPaths = Object.keys(folderStructure).sort((a, b) => {
        const depthA = a.split('/').filter(p => p).length;
        const depthB = b.split('/').filter(p => p).length;
        return depthA - depthB;
      });

      sortedPaths.forEach(parentPath => {
        folderStructure[parentPath].forEach(folderPath => {
          if (!newFolders[folderPath]) {
            const pathParts = folderPath.split('/');
            const folderName = pathParts[pathParts.length - 1];
            const parentFolderPath = pathParts.slice(0, -1).join('/');

            const newFolder: MarkdownFile = {
              id: `folder_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
              name: folderName,
              content: '',
              lastModified: new Date().toISOString().split('T')[0],
              path: parentFolderPath ? `/${parentFolderPath}/` : '/',
              tags: [],
              type: 'folder',
              children: [],
              parentId: parentFolderPath ? newFolders[parentFolderPath]?.id : undefined
            };

            newFolders[folderPath] = newFolder;

            if (parentFolderPath && newFolders[parentFolderPath]) {
              newFolders[parentFolderPath].children!.push(newFolder);
            } else {
              rootFolders.push(newFolder);
            }
          }
        });
      });

      setImportProgress(50);

      // 处理文件
      let processedFiles = 0;
      const totalFiles = fileList.length;

      for (const [dirPath, files] of Object.entries(filesByPath)) {
        for (const file of files) {
          try {
            const content = await readFileContent(file);
            const fileName = file.name;

            const newFile: MarkdownFile = {
              id: `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
              name: fileName,
              content: content,
              lastModified: new Date().toISOString().split('T')[0],
              path: dirPath ? `/${dirPath}/` : '/',
              tags: extractTagsFromContent(content),
              type: 'file',
              size: file.size,
              parentId: dirPath ? newFolders[dirPath]?.id : undefined
            };

            if (dirPath && newFolders[dirPath]) {
              newFolders[dirPath].children!.push(newFile);
            } else {
              rootFolders.push(newFile);
            }

            processedFiles++;
            setImportProgress(50 + (processedFiles / totalFiles) * 40);
          } catch (error) {
            console.error(`读取文件失败 ${file.name}:`, error);
          }
        }
      }

      // 添加到文件列表
      setFiles(prev => [...prev, ...rootFolders]);
      setImportProgress(100);

      message.success(`成功导入 ${processedFiles} 个文件`);
      
      setTimeout(() => {
        setShowImportModal(false);
        setImportProgress(0);
      }, 1000);

    } catch (error) {
      console.error('文件导入失败:', error);
      message.error('文件导入失败，请重试');
      setShowImportModal(false);
      setImportProgress(0);
    }
  };

  // 从内容中提取标签
  const extractTagsFromContent = (content: string): string[] => {
    const tagRegex = /#(\w+)/g;
    const tags: string[] = [];
    let match;
    
    while ((match = tagRegex.exec(content)) !== null) {
      if (!tags.includes(match[1])) {
        tags.push(match[1]);
      }
    }
    
    return tags;
  };

  const handleImportFolder = () => {
    try {
      // 检查浏览器是否支持文件夹选择
      if (!('webkitdirectory' in document.createElement('input'))) {
        message.error('您的浏览器不支持文件夹选择功能，请使用Chrome、Edge或Firefox浏览器');
        return;
      }

      // 创建一个文件选择器，支持选择多个文件
      const input = document.createElement('input');
      input.type = 'file';
      input.multiple = true;
      input.accept = '.md,.markdown,.txt,.html,.htm';
      input.setAttribute('webkitdirectory', 'true'); // 支持文件夹选择
      
      input.onchange = (e) => {
        try {
          const target = e.target as HTMLInputElement;
          console.log('文件选择器触发，文件数量:', target.files?.length);
          
          if (target.files && target.files.length > 0) {
            const fileList = Array.from(target.files);
            console.log('选择的文件:', fileList.map(f => f.name));
            
            // 过滤只保留markdown和文本文件
            const validFiles = fileList.filter(file => {
              const isValid = /\.(md|markdown|txt|html|htm)$/i.test(file.name);
              if (!isValid) {
                console.log('跳过非markdown文件:', file.name);
              }
              return isValid;
            });
            
            if (validFiles.length === 0) {
              message.warning('选择的文件夹中没有找到markdown文件(.md, .markdown, .txt)');
              return;
            }
            
            console.log('有效文件数量:', validFiles.length);
            handleImportFiles(validFiles as RcFile[]);
          } else {
            console.log('未选择任何文件');
            message.info('未选择任何文件');
          }
        } catch (error) {
          console.error('文件选择处理错误:', error);
          message.error('文件选择处理失败，请重试');
        }
      };
      
      input.onerror = (error) => {
        console.error('文件输入错误:', error);
        message.error('文件选择失败，请重试');
      };
      
      // 触发文件选择器
      input.click();
      
    } catch (error) {
      console.error('创建文件选择器失败:', error);
      message.error('无法创建文件选择器，请检查浏览器设置');
    }
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
    // 处理YAML Front Matter
    const processYAMLFrontMatter = (content: string) => {
      const yamlRegex = /^---\n([\s\S]*?)\n---/;
      const match = content.match(yamlRegex);
      
      if (match) {
        const yamlContent = match[1];
        const remainingContent = content.replace(yamlRegex, '').trim();
        
        // 解析YAML内容
        const yamlLines = yamlContent.split('\n').filter(line => line.trim());
        const yamlHtml = yamlLines.map(line => {
          if (line.includes(':')) {
            const [key, value] = line.split(':').map(s => s.trim());
            return `<div style="margin: 4px 0;">
              <span style="color: #1890ff; font-weight: 500;">${key}:</span> 
              <span style="color: #52c41a; margin-left: 8px;">${value}</span>
            </div>`;
          }
          return `<div style="color: #666; margin: 2px 0;">${line}</div>`;
        }).join('');
        
        const frontMatterHtml = `
          <div style="
            background: linear-gradient(135deg, #f6f9fc 0%, #e9f3ff 100%);
            border: 2px dashed #1890ff;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 20px;
            font-family: 'Courier New', monospace;
          ">
            <div style="
              color: #1890ff; 
              font-weight: bold; 
              margin-bottom: 8px;
              display: flex;
              align-items: center;
              gap: 8px;
            ">
              📋 YAML Front Matter
            </div>
            ${yamlHtml}
          </div>
        `;
        
        return { frontMatter: frontMatterHtml, content: remainingContent };
      }
      
      return { frontMatter: '', content };
    };

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

    // 处理YAML Front Matter
    const { frontMatter, content } = processYAMLFrontMatter(markdownContent);

    // 基础Markdown处理
    let html = content
      .replace(/^# (.*$)/gim, '<h1 style="color: #2c3e50; border-bottom: 2px solid #d4af37; padding-bottom: 8px;">$1</h1>')
      .replace(/^## (.*$)/gim, '<h2 style="color: #34495e; border-bottom: 1px solid #d4af37; padding-bottom: 4px;">$1</h2>')
      .replace(/^### (.*$)/gim, '<h3 style="color: #34495e;">$1</h3>')
      .replace(/\*\*(.*?)\*\*/gim, '<strong style="color: #2c3e50;">$1</strong>')
      .replace(/\*(.*?)\*/gim, '<em style="color: #34495e;">$1</em>')
      .replace(/`(.*?)`/gim, '<code style="background: #f4f4f4; padding: 2px 4px; border-radius: 3px; color: #e74c3c;">$1</code>')
      .replace(/^- (.*$)/gim, '<li style="margin: 4px 0;">$1</li>')
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
        dangerouslySetInnerHTML={{ __html: frontMatter + html }}
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
                      onClick={() => handleNewFile()}
                    />
                  </Tooltip>
                  <Tooltip title="新建文件夹">
                    <Button 
                      type="text" 
                      size="small" 
                      icon={<FolderOutlined />} 
                      onClick={() => handleNewFolder()}
                    />
                  </Tooltip>
                  <Tooltip title="导入文件">
                    <Upload
                      multiple
                      accept=".md,.markdown,.txt,.html,.htm"
                      showUploadList={false}
                      beforeUpload={(file: RcFile, fileList: RcFile[]) => {
                        console.log('通过Upload组件导入文件:', fileList.length);
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
                      icon={<FolderOpenOutlined />} 
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
              ) : fileTree.length > 0 ? (
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
              ) : (
                <div style={{ 
                  textAlign: 'center', 
                  padding: '40px 20px', 
                  color: '#999',
                  fontSize: '14px'
                }}>
                  <div style={{ marginBottom: 16 }}>
                    <FolderOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
                  </div>
                  <div style={{ marginBottom: 8 }}>暂无文件</div>
                  <div style={{ fontSize: '12px' }}>
                    点击上方按钮创建文件或导入文件夹
                  </div>
                </div>
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
          <Progress 
            percent={Math.round(importProgress)} 
            status={importProgress === 100 ? 'success' : 'active'}
            strokeColor={{ from: '#108ee9', to: '#87d068' }}
          />
        </div>
      </Modal>
    </div>
  );
};

export default ObsidianMarkdownEditor;