import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Input,
  Select,
  Tag,
  Modal,
  message,
  Popconfirm,
  Tooltip,
  Row,
  Col,
  Typography,
  Drawer,
  Descriptions,
  Alert,
  Divider,
  Upload,
  Progress,
  Tree,
  Layout,
  Dropdown,
  Menu
} from 'antd';
import {
  FileTextOutlined,
  FolderOutlined,
  DeleteOutlined,
  DownloadOutlined,
  EyeOutlined,
  EditOutlined,
  ReloadOutlined,
  CloudUploadOutlined,
  FileExcelOutlined,
  FilePdfOutlined,
  FileWordOutlined,
  FileImageOutlined,
  FileZipOutlined,
  FileUnknownOutlined,
  UploadOutlined,
  InboxOutlined,
  FolderAddOutlined,
  FileAddOutlined,
  MoreOutlined,
  PlusOutlined,
  FolderOpenOutlined,
  CaretRightOutlined,
  CaretDownOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { DataNode } from 'antd/es/tree';
import type { MenuProps } from 'antd';

const { Search } = Input;
const { Option } = Select;
const { Title, Text } = Typography;
const { Sider, Content } = Layout;
const { DirectoryTree } = Tree;

interface FileItem {
  id: string;
  name: string;
  type: 'file' | 'folder';
  size: number;
  category: string;
  tags: string[];
  createTime: string;
  updateTime: string;
  path: string;
  parentId?: string;
  extension?: string;
  url?: string;
  thumbnail?: string;
  status: 'active' | 'processing' | 'error';
  extractionStatus: 'not_extracted' | 'extracted' | 'processing' | 'failed';
  children?: FileItem[];
  isExpanded?: boolean;
  analysis?: {
    entities: string[];
    keywords: string[];
    summary: string;
  };
}

interface TreeFileNode extends DataNode {
  key: string;
  title: React.ReactNode;
  icon?: React.ReactNode;
  children?: TreeFileNode[];
  isLeaf?: boolean;
  fileData: FileItem;
}

const FileManager: React.FC = () => {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [filteredFiles, setFilteredFiles] = useState<FileItem[]>([]);
  const [treeData, setTreeData] = useState<TreeFileNode[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null);
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false);
  const [viewMode, setViewMode] = useState<'tree' | 'table'>('tree');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedExtractionStatus, setSelectedExtractionStatus] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'name' | 'size' | 'createTime'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [currentPath, setCurrentPath] = useState('/');
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [expandedKeys, setExpandedKeys] = useState<React.Key[]>([]);
  const [selectedKeys, setSelectedKeys] = useState<React.Key[]>([]);
  const [showNewFolderModal, setShowNewFolderModal] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');

  const categories = [
    { key: 'all', label: '全部文件', color: 'default' },
    { key: 'emc-standard', label: 'EMC标准', color: 'blue' },
    { key: 'test-report', label: '测试报告', color: 'green' },
    { key: 'equipment-spec', label: '设备规格', color: 'orange' },
    { key: 'compliance-doc', label: '合规文档', color: 'purple' },
    { key: 'general', label: '通用文档', color: 'default' }
  ];

  useEffect(() => {
    loadFiles();
  }, []);

  useEffect(() => {
    filterAndSortFiles();
  }, [files, searchTerm, selectedCategory, selectedExtractionStatus, sortBy, sortOrder]);

  const loadFiles = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/files');
      if (response.ok) {
        const data = await response.json();
        setFiles(data);
      } else {
        // 使用模拟数据
        const mockFiles: FileItem[] = [
          // 根目录文件夹
          {
            id: 'folder_standards',
            name: 'EMC标准',
            type: 'folder',
            size: 0,
            category: 'emc-standard',
            tags: ['标准', '规范'],
            createTime: '2025-06-01 09:00:00',
            updateTime: '2025-06-12 16:30:00',
            path: '/',
            status: 'active',
            extractionStatus: 'not_extracted'
          },
          {
            id: 'folder_reports',
            name: '测试报告',
            type: 'folder',
            size: 0,
            category: 'test-report',
            tags: ['报告', '测试'],
            createTime: '2025-06-01 09:00:00',
            updateTime: '2025-06-12 14:20:00',
            path: '/',
            status: 'active',
            extractionStatus: 'not_extracted'
          },
          {
            id: 'folder_specs',
            name: '设备规格',
            type: 'folder',
            size: 0,
            category: 'equipment-spec',
            tags: ['规格', '技术'],
            createTime: '2025-06-01 09:00:00',
            updateTime: '2025-06-11 16:45:00',
            path: '/',
            status: 'active',
            extractionStatus: 'not_extracted'
          },
          {
            id: 'folder_compliance',
            name: '合规文档',
            type: 'folder',
            size: 0,
            category: 'compliance-doc',
            tags: ['合规', '认证'],
            createTime: '2025-06-01 09:00:00',
            updateTime: '2025-06-10 11:00:00',
            path: '/',
            status: 'active',
            extractionStatus: 'not_extracted'
          },
          
          // EMC标准文件夹下的子文件夹和文件
          {
            id: 'folder_iec',
            name: 'IEC标准',
            type: 'folder',
            size: 0,
            category: 'emc-standard',
            tags: ['IEC', '国际标准'],
            createTime: '2025-06-01 09:00:00',
            updateTime: '2025-06-10 09:30:00',
            path: '/EMC标准/',
            parentId: 'folder_standards',
            status: 'active',
            extractionStatus: 'not_extracted'
          },
          {
            id: 'folder_en',
            name: 'EN标准',
            type: 'folder',
            size: 0,
            category: 'emc-standard',
            tags: ['EN', '欧洲标准'],
            createTime: '2025-06-01 09:00:00',
            updateTime: '2025-06-09 14:00:00',
            path: '/EMC标准/',
            parentId: 'folder_standards',
            status: 'active',
            extractionStatus: 'not_extracted'
          },
          
          // IEC标准文件夹下的文件
          {
            id: 'file_iec_61000_4_3',
            name: 'IEC 61000-4-3.pdf',
            type: 'file',
            size: 2048576,
            category: 'emc-standard',
            tags: ['IEC', 'EMC', '抗扰度'],
            createTime: '2025-06-10 09:30:00',
            updateTime: '2025-06-10 09:30:00',
            path: '/EMC标准/IEC标准/',
            parentId: 'folder_iec',
            extension: 'pdf',
            url: '/api/files/file_iec_61000_4_3/download',
            status: 'active',
            extractionStatus: 'extracted',
            analysis: {
              entities: ['IEC 61000-4-3', '射频电磁场', '抗扰度测试'],
              keywords: ['EMC', '标准', '测试方法'],
              summary: '射频电磁场辐射抗扰度测试标准文档'
            }
          },
          {
            id: 'file_iec_61000_4_6',
            name: 'IEC 61000-4-6.pdf',
            type: 'file',
            size: 1890432,
            category: 'emc-standard',
            tags: ['IEC', 'EMC', '传导抗扰度'],
            createTime: '2025-06-09 15:20:00',
            updateTime: '2025-06-09 15:20:00',
            path: '/EMC标准/IEC标准/',
            parentId: 'folder_iec',
            extension: 'pdf',
            url: '/api/files/file_iec_61000_4_6/download',
            status: 'active',
            extractionStatus: 'extracted'
          },
          
          // EN标准文件夹下的文件
          {
            id: 'file_en_55011',
            name: 'EN 55011.pdf',
            type: 'file',
            size: 1654321,
            category: 'emc-standard',
            tags: ['EN', '发射', '工业设备'],
            createTime: '2025-06-09 14:00:00',
            updateTime: '2025-06-09 14:00:00',
            path: '/EMC标准/EN标准/',
            parentId: 'folder_en',
            extension: 'pdf',
            url: '/api/files/file_en_55011/download',
            status: 'active',
            extractionStatus: 'not_extracted'
          },
          
          // 测试报告文件夹下的文件
          {
            id: 'file_report_device_a',
            name: 'EMC测试报告_设备A.docx',
            type: 'file',
            size: 1536000,
            category: 'test-report',
            tags: ['测试报告', '设备A', 'EMC'],
            createTime: '2025-06-11 14:20:00',
            updateTime: '2025-06-11 14:20:00',
            path: '/测试报告/',
            parentId: 'folder_reports',
            extension: 'docx',
            url: '/api/files/file_report_device_a/download',
            status: 'active',
            extractionStatus: 'extracted',
            analysis: {
              entities: ['设备A', 'EMC测试', '合规性'],
              keywords: ['测试', '结果', '分析'],
              summary: '设备A的完整EMC测试报告和分析结果'
            }
          },
          {
            id: 'file_report_device_b',
            name: 'EMC测试报告_设备B.docx',
            type: 'file',
            size: 1423789,
            category: 'test-report',
            tags: ['测试报告', '设备B', 'EMC'],
            createTime: '2025-06-12 10:15:00',
            updateTime: '2025-06-12 10:15:00',
            path: '/测试报告/',
            parentId: 'folder_reports',
            extension: 'docx',
            url: '/api/files/file_report_device_b/download',
            status: 'active',
            extractionStatus: 'processing'
          },
          
          // 设备规格文件夹下的文件
          {
            id: 'file_spec_charger',
            name: '充电器规格说明.xlsx',
            type: 'file',
            size: 512000,
            category: 'equipment-spec',
            tags: ['规格', '充电器', '技术'],
            createTime: '2025-06-09 16:45:00',
            updateTime: '2025-06-09 16:45:00',
            path: '/设备规格/',
            parentId: 'folder_specs',
            extension: 'xlsx',
            url: '/api/files/file_spec_charger/download',
            status: 'active',
            extractionStatus: 'not_extracted'
          },
          
          // 合规文档文件夹下的文件
          {
            id: 'file_compliance_cert',
            name: '产品认证证书.pdf',
            type: 'file',
            size: 890123,
            category: 'compliance-doc',
            tags: ['认证', '证书', '合规'],
            createTime: '2025-06-10 11:00:00',
            updateTime: '2025-06-10 11:00:00',
            path: '/合规文档/',
            parentId: 'folder_compliance',
            extension: 'pdf',
            url: '/api/files/file_compliance_cert/download',
            status: 'active',
            extractionStatus: 'extracted'
          }
        ];
        setFiles(mockFiles);
        message.info('使用模拟数据展示文件');
      }
    } catch (error) {
      console.error('加载文件失败:', error);
      message.error('加载文件失败');
    } finally {
      setLoading(false);
    }
  };

  const filterAndSortFiles = () => {
    let filtered = files;

    // 搜索过滤
    if (searchTerm) {
      filtered = filtered.filter(file =>
        file.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        file.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    // 分类过滤
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(file => file.category === selectedCategory);
    }

    // 提取状态过滤
    if (selectedExtractionStatus !== 'all') {
      filtered = filtered.filter(file => file.extractionStatus === selectedExtractionStatus);
    }

    // 排序
    filtered.sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name);
          break;
        case 'size':
          comparison = a.size - b.size;
          break;
        case 'createTime':
          comparison = new Date(a.createTime).getTime() - new Date(b.createTime).getTime();
          break;
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });

    setFilteredFiles(filtered);
    buildTreeData(filtered);
  };

  const buildTreeData = (fileList: FileItem[]) => {
    const rootNodes: TreeFileNode[] = [];
    const nodeMap = new Map<string, TreeFileNode>();

    // 首先创建所有节点
    fileList.forEach(file => {
      const node: TreeFileNode = {
        key: file.id,
        title: (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Space>
              {getFileIcon(file)}
              <span>{file.name}</span>
              {file.type === 'file' && (
                <Tag color={getExtractionStatusColor(file.extractionStatus)} size="small">
                  {getExtractionStatusText(file.extractionStatus)}
                </Tag>
              )}
            </Space>
            {file.type === 'file' && (
              <Space>
                <Tooltip title="查看详情">
                  <Button
                    type="text"
                    size="small"
                    icon={<EyeOutlined />}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleFileView(file);
                    }}
                  />
                </Tooltip>
                <Dropdown
                  menu={{
                    items: getFileContextMenu(file)
                  }}
                  trigger={['click']}
                >
                  <Button
                    type="text"
                    size="small"
                    icon={<MoreOutlined />}
                    onClick={(e) => e.stopPropagation()}
                  />
                </Dropdown>
              </Space>
            )}
          </div>
        ),
        icon: getFileIcon(file),
        isLeaf: file.type === 'file',
        fileData: file,
        children: []
      };
      nodeMap.set(file.id, node);
    });

    // 构建树结构
    fileList.forEach(file => {
      const node = nodeMap.get(file.id)!;
      if (!file.parentId) {
        rootNodes.push(node);
      } else {
        const parentNode = nodeMap.get(file.parentId);
        if (parentNode && parentNode.children) {
          parentNode.children.push(node);
        }
      }
    });

    setTreeData(rootNodes);
  };

  const getExtractionStatusColor = (status: string) => {
    switch (status) {
      case 'extracted': return 'green';
      case 'processing': return 'blue';
      case 'failed': return 'red';
      default: return 'default';
    }
  };

  const getExtractionStatusText = (status: string) => {
    switch (status) {
      case 'extracted': return '已提取';
      case 'processing': return '处理中';
      case 'failed': return '失败';
      default: return '未提取';
    }
  };

  const getFileContextMenu = (file: FileItem): MenuProps['items'] => [
    {
      key: 'view',
      label: '查看详情',
      icon: <EyeOutlined />,
      onClick: () => handleFileView(file)
    },
    {
      key: 'download',
      label: '下载',
      icon: <DownloadOutlined />,
      onClick: () => handleFileDownload(file)
    },
    {
      type: 'divider'
    },
    {
      key: 'delete',
      label: '删除',
      icon: <DeleteOutlined />,
      danger: true,
      onClick: () => handleFileDelete(file.id)
    }
  ];

  const getFileIcon = (file: FileItem) => {
    if (file.type === 'folder') {
      return <FolderOutlined style={{ color: '#faad14' }} />;
    }

    switch (file.extension) {
      case 'pdf':
        return <FilePdfOutlined style={{ color: '#ff4d4f' }} />;
      case 'docx':
      case 'doc':
        return <FileWordOutlined style={{ color: '#1890ff' }} />;
      case 'xlsx':
      case 'xls':
        return <FileExcelOutlined style={{ color: '#52c41a' }} />;
      case 'png':
      case 'jpg':
      case 'jpeg':
        return <FileImageOutlined style={{ color: '#722ed1' }} />;
      case 'zip':
      case 'rar':
        return <FileZipOutlined style={{ color: '#faad14' }} />;
      default:
        return <FileUnknownOutlined style={{ color: '#8c8c8c' }} />;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '-';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleFileView = (file: FileItem) => {
    setSelectedFile(file);
    setDetailDrawerVisible(true);
  };

  const handleFileDelete = async (fileId: string) => {
    try {
      const response = await fetch(`/api/files/${fileId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        setFiles(prev => prev.filter(f => f.id !== fileId));
        message.success('文件删除成功');
      } else {
        throw new Error('删除失败');
      }
    } catch (error) {
      message.error('文件删除失败');
    }
  };

  const handleFileDownload = async (file: FileItem) => {
    try {
      // 如果文件有直接下载链接，使用该链接
      if (file.url) {
        const link = document.createElement('a');
        link.href = file.url;
        link.download = file.name;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        message.success('开始下载文件');
        return;
      }

      // 否则通过API下载
      const response = await fetch(`/api/files/${file.id}/download`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error('下载请求失败');
      }

      // 创建blob对象
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      
      // 创建下载链接
      const link = document.createElement('a');
      link.href = url;
      link.download = file.name;
      document.body.appendChild(link);
      link.click();
      
      // 清理
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      message.success('文件下载成功');
    } catch (error) {
      console.error('下载失败:', error);
      message.error('文件下载失败，请重试');
    }
  };

  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请选择要删除的文件');
      return;
    }

    Modal.confirm({
      title: '批量删除文件',
      content: `确定要删除选中的 ${selectedRowKeys.length} 个文件吗？`,
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          for (const fileId of selectedRowKeys) {
            await fetch(`/api/files/${fileId}`, { method: 'DELETE' });
          }
          setFiles(prev => prev.filter(f => !selectedRowKeys.includes(f.id)));
          setSelectedRowKeys([]);
          message.success('批量删除成功');
        } catch (error) {
          message.error('批量删除失败');
        }
      }
    });
  };

  const handleUpload = async (file: File) => {
    setUploading(true);
    setUploadProgress(0);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('category', 'general');
      
      // 模拟上传进度
      const uploadInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(uploadInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);
      
      // 模拟上传API调用
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      clearInterval(uploadInterval);
      setUploadProgress(100);
      
      // 创建新文件记录
      const newFile: FileItem = {
        id: `file_${Date.now()}`,
        name: file.name,
        type: 'file',
        size: file.size,
        category: 'general',
        tags: ['新上传'],
        createTime: new Date().toISOString(),
        updateTime: new Date().toISOString(),
        path: `/uploads/${file.name}`,
        extension: file.name.split('.').pop()?.toLowerCase(),
        status: 'active',
        extractionStatus: 'not_extracted'
      };
      
      // 添加到文件列表
      setFiles(prev => [newFile, ...prev]);
      
      message.success(`文件 ${file.name} 上传成功`);
      setUploadModalVisible(false);
      
    } catch (error) {
      message.error('文件上传失败，请重试');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const { Dragger } = Upload;

  const uploadProps = {
    name: 'file',
    multiple: true,
    showUploadList: false,
    beforeUpload: (file: File) => {
      handleUpload(file);
      return false; // 阻止默认上传
    },
    accept: '.pdf,.docx,.doc,.txt,.md,.html,.xlsx,.xls',
  };

  const createNewFolder = () => {
    if (!newFolderName.trim()) {
      message.error('请输入文件夹名称');
      return;
    }

    const newFolder: FileItem = {
      id: `folder_${Date.now()}`,
      name: newFolderName,
      type: 'folder',
      size: 0,
      category: 'general',
      tags: ['新建文件夹'],
      createTime: new Date().toISOString(),
      updateTime: new Date().toISOString(),
      path: currentPath,
      status: 'active',
      extractionStatus: 'not_extracted'
    };

    setFiles(prev => [newFolder, ...prev]);
    setNewFolderName('');
    setShowNewFolderModal(false);
    message.success('文件夹创建成功');
  };

  const handleTreeSelect = (selectedKeysArray: React.Key[], info: any) => {
    if (selectedKeysArray.length > 0) {
      const selectedKey = selectedKeysArray[0];
      setSelectedKeys([selectedKey]);
      
      const node = info.node;
      if (node && node.fileData) {
        setSelectedFile(node.fileData);
        if (node.fileData.type === 'file') {
          setDetailDrawerVisible(true);
        }
      }
    }
  };

  const handleTreeExpand = (expandedKeysArray: React.Key[]) => {
    setExpandedKeys(expandedKeysArray);
  };

  const tableColumns: ColumnsType<FileItem> = [
    {
      title: '文件名',
      dataIndex: 'name',
      key: 'name',
      width: '35%',
      render: (text, record) => (
        <Space>
          {getFileIcon(record)}
          <span style={{ fontWeight: 500 }}>{text}</span>
          {record.status === 'processing' && (
            <Tag color="processing">处理中</Tag>
          )}
        </Space>
      ),
    },
    {
      title: '大小',
      dataIndex: 'size',
      key: 'size',
      width: '10%',
      render: (size) => formatFileSize(size),
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: '15%',
      render: (category) => {
        const cat = categories.find(c => c.key === category);
        return cat ? <Tag color={cat.color}>{cat.label}</Tag> : category;
      },
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      width: '15%',
      render: (tags: string[]) => (
        <Space wrap>
          {tags.map(tag => (
            <Tag key={tag} color="default">{tag}</Tag>
          ))}
        </Space>
      ),
    },
    {
      title: '提取状态',
      dataIndex: 'extractionStatus',
      key: 'extractionStatus',
      width: '10%',
      render: (status: string) => {
        const statusConfig = {
          'extracted': { color: 'green', text: '已提取' },
          'not_extracted': { color: 'default', text: '未提取' },
          'processing': { color: 'blue', text: '处理中' },
          'failed': { color: 'red', text: '失败' }
        };
        const config = statusConfig[status as keyof typeof statusConfig] || { color: 'default', text: status };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '修改时间',
      dataIndex: 'updateTime',
      key: 'updateTime',
      width: '12%',
      render: (time) => new Date(time).toLocaleDateString('zh-CN'),
    },
    {
      title: '操作',
      key: 'actions',
      width: '8%',
      render: (_, record) => (
        <Space>
          <Tooltip title="查看详情">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => handleFileView(record)}
            />
          </Tooltip>
          <Tooltip title="下载">
            <Button
              type="text"
              size="small"
              icon={<DownloadOutlined />}
              onClick={() => handleFileDownload(record)}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个文件吗？"
            onConfirm={() => handleFileDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button
                type="text"
                size="small"
                icon={<DeleteOutlined />}
                danger
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const rowSelection = {
    selectedRowKeys,
    onChange: (newSelectedRowKeys: React.Key[]) => {
      setSelectedRowKeys(newSelectedRowKeys);
    },
  };

  return (
    <div style={{ height: 'calc(100vh - 120px)' }}>
      <Title level={2} style={{ marginBottom: 16 }}>
        文件管理
      </Title>

      <Layout style={{ height: '100%', border: '1px solid #d9d9d9', borderRadius: 8 }}>
        {/* 左侧文件树 */}
        <Sider 
          width={300} 
          style={{ 
            background: '#fafafa',
            borderRight: '1px solid #d9d9d9'
          }}
        >
          {/* 工具栏 */}
          <div style={{ 
            padding: '12px 16px', 
            borderBottom: '1px solid #d9d9d9',
            background: '#fff'
          }}>
            <Space size="small" style={{ width: '100%', justifyContent: 'space-between' }}>
              <Space size="small">
                <Tooltip title="新建文件夹">
                  <Button 
                    type="text" 
                    size="small" 
                    icon={<FolderAddOutlined />}
                    onClick={() => setShowNewFolderModal(true)}
                  />
                </Tooltip>
                <Tooltip title="上传文件">
                  <Button 
                    type="text" 
                    size="small" 
                    icon={<UploadOutlined />}
                    onClick={() => setUploadModalVisible(true)}
                  />
                </Tooltip>
                <Tooltip title="刷新">
                  <Button 
                    type="text" 
                    size="small" 
                    icon={<ReloadOutlined />}
                    onClick={loadFiles}
                    loading={loading}
                  />
                </Tooltip>
              </Space>
              <Dropdown
                menu={{
                  items: [
                    {
                      key: 'tree',
                      label: '树状视图',
                      icon: viewMode === 'tree' ? <CaretDownOutlined /> : <CaretRightOutlined />,
                      onClick: () => setViewMode('tree')
                    },
                    {
                      key: 'table',
                      label: '表格视图',
                      icon: viewMode === 'table' ? <CaretDownOutlined /> : <CaretRightOutlined />,
                      onClick: () => setViewMode('table')
                    }
                  ]
                }}
                trigger={['click']}
              >
                <Button type="text" size="small" icon={<MoreOutlined />} />
              </Dropdown>
            </Space>
          </div>

          {/* 搜索和过滤 */}
          <div style={{ padding: '12px 16px' }}>
            <Space direction="vertical" style={{ width: '100%' }} size="small">
              <Search
                placeholder="搜索文件..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                size="small"
                allowClear
              />
              <Select
                value={selectedExtractionStatus}
                onChange={setSelectedExtractionStatus}
                style={{ width: '100%' }}
                size="small"
                placeholder="提取状态"
              >
                <Option value="all">全部状态</Option>
                <Option value="extracted">已提取</Option>
                <Option value="not_extracted">未提取</Option>
                <Option value="processing">处理中</Option>
                <Option value="failed">失败</Option>
              </Select>
            </Space>
          </div>

          {/* 文件树 */}
          <div style={{ 
            flex: 1, 
            overflow: 'auto',
            padding: '0 8px'
          }}>
            <DirectoryTree
              treeData={treeData}
              expandedKeys={expandedKeys}
              selectedKeys={selectedKeys}
              onExpand={handleTreeExpand}
              onSelect={handleTreeSelect}
              showIcon={false}
              style={{
                background: 'transparent'
              }}
            />
          </div>
        </Sider>

        {/* 右侧内容区 */}
        <Content style={{ background: '#fff', padding: 16 }}>
          {viewMode === 'table' ? (
            <div>
              {/* 表格视图工具栏 */}
              <div style={{ 
                marginBottom: 16,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <Space>
                  <Select
                    value={selectedCategory}
                    onChange={setSelectedCategory}
                    style={{ width: 150 }}
                    size="small"
                    placeholder="文件分类"
                  >
                    {categories.map(cat => (
                      <Option key={cat.key} value={cat.key}>
                        {cat.label}
                      </Option>
                    ))}
                  </Select>
                  <Select
                    value={`${sortBy}_${sortOrder}`}
                    onChange={(value) => {
                      const [field, order] = value.split('_');
                      setSortBy(field as any);
                      setSortOrder(order as any);
                    }}
                    style={{ width: 150 }}
                    size="small"
                  >
                    <Option value="name_asc">名称 A-Z</Option>
                    <Option value="name_desc">名称 Z-A</Option>
                    <Option value="size_asc">大小 小-大</Option>
                    <Option value="size_desc">大小 大-小</Option>
                    <Option value="createTime_desc">时间 新-旧</Option>
                    <Option value="createTime_asc">时间 旧-新</Option>
                  </Select>
                </Space>
                <Space>
                  <Text type="secondary">{filteredFiles.length} 项</Text>
                  {selectedRowKeys.length > 0 && (
                    <Button
                      danger
                      size="small"
                      icon={<DeleteOutlined />}
                      onClick={handleBatchDelete}
                    >
                      删除 ({selectedRowKeys.length})
                    </Button>
                  )}
                </Space>
              </div>

              {/* 表格视图 */}
              <Table
                columns={tableColumns}
                dataSource={filteredFiles}
                rowKey="id"
                loading={loading}
                rowSelection={rowSelection}
                pagination={{
                  pageSize: 15,
                  showSizeChanger: true,
                  showQuickJumper: true,
                  showTotal: (total, range) => 
                    `第 ${range[0]}-${range[1]} 项，共 ${total} 项`
                }}
                size="small"
                scroll={{ x: 800 }}
              />
            </div>
          ) : (
            /* 树状视图主区域 */
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              minHeight: 400
            }}>
              {selectedFile ? (
                <Card style={{ width: '100%', maxWidth: 600 }}>
                  <Space style={{ marginBottom: 16 }}>
                    {getFileIcon(selectedFile)}
                    <Title level={4} style={{ margin: 0 }}>{selectedFile.name}</Title>
                    <Tag color={getExtractionStatusColor(selectedFile.extractionStatus)}>
                      {getExtractionStatusText(selectedFile.extractionStatus)}
                    </Tag>
                  </Space>

                  <Descriptions bordered column={1} size="small">
                    <Descriptions.Item label="文件大小">
                      {formatFileSize(selectedFile.size)}
                    </Descriptions.Item>
                    <Descriptions.Item label="文件类型">
                      {selectedFile.extension || '文件夹'}
                    </Descriptions.Item>
                    <Descriptions.Item label="创建时间">
                      {new Date(selectedFile.createTime).toLocaleString('zh-CN')}
                    </Descriptions.Item>
                    <Descriptions.Item label="文件路径">
                      {selectedFile.path}
                    </Descriptions.Item>
                  </Descriptions>

                  {selectedFile.tags.length > 0 && (
                    <>
                      <Divider>标签</Divider>
                      <Space wrap>
                        {selectedFile.tags.map(tag => (
                          <Tag key={tag} color="processing">{tag}</Tag>
                        ))}
                      </Space>
                    </>
                  )}

                  {selectedFile.analysis && (
                    <>
                      <Divider>AI分析结果</Divider>
                      <Descriptions column={1} size="small">
                        <Descriptions.Item label="识别实体">
                          <Space wrap>
                            {selectedFile.analysis.entities.map(entity => (
                              <Tag key={entity} color="blue">{entity}</Tag>
                            ))}
                          </Space>
                        </Descriptions.Item>
                        <Descriptions.Item label="关键词">
                          <Space wrap>
                            {selectedFile.analysis.keywords.map(keyword => (
                              <Tag key={keyword} color="green">{keyword}</Tag>
                            ))}
                          </Space>
                        </Descriptions.Item>
                        <Descriptions.Item label="内容摘要">
                          <Text>{selectedFile.analysis.summary}</Text>
                        </Descriptions.Item>
                      </Descriptions>
                    </>
                  )}

                  <div style={{ marginTop: 16 }}>
                    <Space>
                      <Button 
                        type="primary" 
                        icon={<DownloadOutlined />}
                        onClick={() => handleFileDownload(selectedFile)}
                      >
                        下载
                      </Button>
                      <Button 
                        danger 
                        icon={<DeleteOutlined />}
                        onClick={() => handleFileDelete(selectedFile.id)}
                      >
                        删除
                      </Button>
                    </Space>
                  </div>
                </Card>
              ) : (
                <div style={{ textAlign: 'center', color: '#999' }}>
                  <FolderOpenOutlined style={{ fontSize: 64, marginBottom: 16 }} />
                  <div>请从左侧文件树中选择一个文件查看详情</div>
                </div>
              )}
            </div>
          )}
        </Content>
      </Layout>

      {/* 模态框 */}
      {/* 新建文件夹模态框 */}
      <Modal
        title="新建文件夹"
        open={showNewFolderModal}
        onOk={createNewFolder}
        onCancel={() => {
          setShowNewFolderModal(false);
          setNewFolderName('');
        }}
        okText="创建"
        cancelText="取消"
      >
        <Input
          placeholder="请输入文件夹名称"
          value={newFolderName}
          onChange={(e) => setNewFolderName(e.target.value)}
          onPressEnter={createNewFolder}
        />
      </Modal>

      {/* 上传文件模态框 */}
      <Modal
        title="上传文件"
        open={uploadModalVisible}
        onCancel={() => setUploadModalVisible(false)}
        footer={null}
        width={600}
      >
        <Dragger {...uploadProps}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持 PDF、Word、Excel、文本等格式文件
          </p>
        </Dragger>
        
        {uploading && (
          <div style={{ marginTop: 16 }}>
            <Progress percent={uploadProgress} status="active" />
          </div>
        )}
      </Modal>

    </div>
  );
};

export default FileManager;