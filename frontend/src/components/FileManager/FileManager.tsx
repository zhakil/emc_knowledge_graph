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
  Divider
} from 'antd';
import {
  FileTextOutlined,
  FolderOutlined,
  SearchOutlined,
  DeleteOutlined,
  DownloadOutlined,
  EyeOutlined,
  EditOutlined,
  ShareAltOutlined,
  FolderAddOutlined,
  FileAddOutlined,
  SortAscendingOutlined,
  FilterOutlined,
  ReloadOutlined,
  CloudUploadOutlined,
  FileExcelOutlined,
  FilePdfOutlined,
  FileWordOutlined,
  FileImageOutlined,
  FileZipOutlined,
  FileUnknownOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
// import type { DataNode } from 'antd/es/tree';

const { Search } = Input;
const { Option } = Select;
const { Title, Text } = Typography;

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
  analysis?: {
    entities: string[];
    keywords: string[];
    summary: string;
  };
}

const FileManager: React.FC = () => {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [filteredFiles, setFilteredFiles] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null);
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false);
  const [viewMode, setViewMode] = useState<'table' | 'tree'>('table');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'name' | 'size' | 'createTime'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [currentPath, setCurrentPath] = useState('/');
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

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
  }, [files, searchTerm, selectedCategory, sortBy, sortOrder]);

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
          {
            id: 'file_1',
            name: 'IEC61000-4-3标准文档.pdf',
            type: 'file',
            size: 2048576,
            category: 'emc-standard',
            tags: ['IEC', 'EMC', '抗扰度'],
            createTime: '2025-06-10 09:30:00',
            updateTime: '2025-06-10 09:30:00',
            path: '/standards/',
            extension: 'pdf',
            status: 'active',
            analysis: {
              entities: ['IEC 61000-4-3', '射频电磁场', '抗扰度测试'],
              keywords: ['EMC', '标准', '测试方法'],
              summary: '射频电磁场辐射抗扰度测试标准文档'
            }
          },
          {
            id: 'file_2',
            name: 'EMC测试报告_设备A.docx',
            type: 'file',
            size: 1536000,
            category: 'test-report',
            tags: ['测试报告', '设备A', 'EMC'],
            createTime: '2025-06-11 14:20:00',
            updateTime: '2025-06-11 14:20:00',
            path: '/reports/',
            extension: 'docx',
            status: 'active',
            analysis: {
              entities: ['设备A', 'EMC测试', '合规性'],
              keywords: ['测试', '结果', '分析'],
              summary: '设备A的完整EMC测试报告和分析结果'
            }
          },
          {
            id: 'file_3',
            name: '设备规格说明.xlsx',
            type: 'file',
            size: 512000,
            category: 'equipment-spec',
            tags: ['规格', '参数', '技术'],
            createTime: '2025-06-09 16:45:00',
            updateTime: '2025-06-09 16:45:00',
            path: '/specs/',
            extension: 'xlsx',
            status: 'active'
          },
          {
            id: 'folder_1',
            name: 'EMC标准库',
            type: 'folder',
            size: 0,
            category: 'emc-standard',
            tags: ['标准', '文档库'],
            createTime: '2025-06-08 10:00:00',
            updateTime: '2025-06-11 15:30:00',
            path: '/',
            status: 'active'
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
  };

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

  const handleFileDownload = (file: FileItem) => {
    if (file.url) {
      const link = document.createElement('a');
      link.href = file.url;
      link.download = file.name;
      link.click();
      message.success('开始下载文件');
    } else {
      message.error('文件下载链接不可用');
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
      width: '20%',
      render: (tags: string[]) => (
        <Space wrap>
          {tags.map(tag => (
            <Tag key={tag} color="default">{tag}</Tag>
          ))}
        </Space>
      ),
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
    <div className="fade-in-up">
      <Title level={2} style={{ textAlign: 'center', marginBottom: 24 }}>
        📂 智能文件管理器
      </Title>

      <Card className="chinese-card" style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={12} md={8}>
            <Search
              placeholder="搜索文件名、标签..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onSearch={setSearchTerm}
              className="chinese-input"
              allowClear
            />
          </Col>
          <Col xs={24} sm={6} md={4}>
            <Select
              value={selectedCategory}
              onChange={setSelectedCategory}
              style={{ width: '100%' }}
              className="chinese-input"
            >
              {categories.map(cat => (
                <Option key={cat.key} value={cat.key}>
                  {cat.label}
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={6} md={4}>
            <Select
              value={`${sortBy}_${sortOrder}`}
              onChange={(value) => {
                const [field, order] = value.split('_');
                setSortBy(field as any);
                setSortOrder(order as any);
              }}
              style={{ width: '100%' }}
              className="chinese-input"
            >
              <Option value="name_asc">名称 A-Z</Option>
              <Option value="name_desc">名称 Z-A</Option>
              <Option value="size_asc">大小 小-大</Option>
              <Option value="size_desc">大小 大-小</Option>
              <Option value="createTime_desc">时间 新-旧</Option>
              <Option value="createTime_asc">时间 旧-新</Option>
            </Select>
          </Col>
          <Col xs={24} sm={24} md={8}>
            <Space>
              <Button
                icon={<ReloadOutlined />}
                onClick={loadFiles}
                loading={loading}
              >
                刷新
              </Button>
              {selectedRowKeys.length > 0 && (
                <Button
                  danger
                  icon={<DeleteOutlined />}
                  onClick={handleBatchDelete}
                >
                  批量删除 ({selectedRowKeys.length})
                </Button>
              )}
            </Space>
          </Col>
        </Row>
      </Card>

      <Card 
        title={
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Space>
              <FileTextOutlined />
              文件列表
              <Tag color="blue">{filteredFiles.length} 项</Tag>
            </Space>
            <Space>
              <Text type="secondary">
                当前路径: {currentPath}
              </Text>
            </Space>
          </div>
        }
        className="chinese-card"
      >
        <Table
          columns={tableColumns}
          dataSource={filteredFiles}
          rowKey="id"
          loading={loading}
          rowSelection={rowSelection}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `第 ${range[0]}-${range[1]} 项，共 ${total} 项`
          }}
          scroll={{ x: 800 }}
        />
      </Card>

      {/* 文件详情抽屉 */}
      <Drawer
        title={selectedFile ? `文件详情: ${selectedFile.name}` : '文件详情'}
        placement="right"
        onClose={() => setDetailDrawerVisible(false)}
        open={detailDrawerVisible}
        width={500}
      >
        {selectedFile && (
          <div>
            <Space style={{ marginBottom: 16 }}>
              {getFileIcon(selectedFile)}
              <Title level={4} style={{ margin: 0 }}>{selectedFile.name}</Title>
            </Space>

            <Alert
              message="文件信息"
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />

            <Descriptions bordered column={1} size="small">
              <Descriptions.Item label="文件ID">{selectedFile.id}</Descriptions.Item>
              <Descriptions.Item label="文件大小">
                {formatFileSize(selectedFile.size)}
              </Descriptions.Item>
              <Descriptions.Item label="文件类型">{selectedFile.extension || '文件夹'}</Descriptions.Item>
              <Descriptions.Item label="分类">
                {categories.find(c => c.key === selectedFile.category)?.label || selectedFile.category}
              </Descriptions.Item>
              <Descriptions.Item label="创建时间">{selectedFile.createTime}</Descriptions.Item>
              <Descriptions.Item label="修改时间">{selectedFile.updateTime}</Descriptions.Item>
              <Descriptions.Item label="文件路径">{selectedFile.path}</Descriptions.Item>
            </Descriptions>

            <Divider>标签</Divider>
            <Space wrap>
              {selectedFile.tags.map(tag => (
                <Tag key={tag} color="processing">{tag}</Tag>
              ))}
            </Space>

            {selectedFile.analysis && (
              <>
                <Divider>AI分析结果</Divider>
                <Card size="small" className="chinese-card">
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
                </Card>
              </>
            )}

            <Divider>操作</Divider>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button
                type="primary"
                icon={<DownloadOutlined />}
                block
                onClick={() => handleFileDownload(selectedFile)}
                className="chinese-btn-primary"
              >
                下载文件
              </Button>
              <Button
                icon={<EditOutlined />}
                block
              >
                编辑属性
              </Button>
              <Button
                icon={<ShareAltOutlined />}
                block
              >
                生成分享链接
              </Button>
              <Popconfirm
                title="确定要删除这个文件吗？"
                onConfirm={() => {
                  handleFileDelete(selectedFile.id);
                  setDetailDrawerVisible(false);
                }}
                okText="确定"
                cancelText="取消"
              >
                <Button
                  danger
                  icon={<DeleteOutlined />}
                  block
                >
                  删除文件
                </Button>
              </Popconfirm>
            </Space>
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default FileManager;