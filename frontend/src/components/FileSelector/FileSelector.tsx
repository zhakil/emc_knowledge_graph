import React, { useState, useEffect } from 'react';
import { Select, Button, Space, Tag, Card, List, Avatar, message } from 'antd';
import { FileOutlined, FolderOpenOutlined, ReloadOutlined } from '@ant-design/icons';

const { Option } = Select;

interface FileInfo {
  id: string;
  name: string;
  path: string;
  size: number;
  type: string;
  uploadTime: string;
  status: 'uploaded' | 'processing' | 'processed' | 'error';
}

interface FileSelectorProps {
  value?: string[];
  onChange?: (fileIds: string[]) => void;
  multiple?: boolean;
  title?: string;
  placeholder?: string;
  allowedTypes?: string[];
  maxCount?: number;
}

const FileSelector: React.FC<FileSelectorProps> = ({
  value = [],
  onChange,
  multiple = true,
  title = "选择文件",
  placeholder = "请选择要处理的文件",
  allowedTypes = ['pdf', 'docx', 'txt', 'md', 'html'],
  maxCount = 10
}) => {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  // 模拟文件数据
  const mockFiles: FileInfo[] = [
    {
      id: '1',
      name: 'EMC测试报告_充电器.pdf',
      path: '/uploads/emc_test_report_charger.pdf',
      size: 2048576,
      type: 'pdf',
      uploadTime: '2024-06-14 10:30:00',
      status: 'uploaded'
    },
    {
      id: '2',
      name: 'CE认证标准_EN55011.docx',
      path: '/uploads/ce_standard_en55011.docx',
      size: 1024000,
      type: 'docx',
      uploadTime: '2024-06-14 09:15:00',
      status: 'processed'
    },
    {
      id: '3',
      name: '电磁兼容性指南.txt',
      path: '/uploads/emc_guide.txt',
      size: 512000,
      type: 'txt',
      uploadTime: '2024-06-14 08:45:00',
      status: 'uploaded'
    },
    {
      id: '4',
      name: 'FCC认证流程.md',
      path: '/uploads/fcc_process.md',
      size: 256000,
      type: 'md',
      uploadTime: '2024-06-13 16:20:00',
      status: 'uploaded'
    },
    {
      id: '5',
      name: '辐射发射测试数据.html',
      path: '/uploads/radiation_test_data.html',
      size: 768000,
      type: 'html',
      uploadTime: '2024-06-13 14:10:00',
      status: 'error'
    }
  ];

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    setLoading(true);
    try {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 500));
      const filteredFiles = mockFiles.filter(file => 
        allowedTypes.includes(file.type.toLowerCase())
      );
      setFiles(filteredFiles);
    } catch (error) {
      message.error('加载文件列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (selectedIds: string[]) => {
    if (!multiple && selectedIds.length > 1) {
      selectedIds = [selectedIds[selectedIds.length - 1]];
    }
    if (selectedIds.length > maxCount) {
      message.warning(`最多只能选择 ${maxCount} 个文件`);
      return;
    }
    onChange?.(selectedIds);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusColor = (status: FileInfo['status']) => {
    switch (status) {
      case 'uploaded': return 'blue';
      case 'processing': return 'orange';
      case 'processed': return 'green';
      case 'error': return 'red';
      default: return 'default';
    }
  };

  const getStatusText = (status: FileInfo['status']) => {
    switch (status) {
      case 'uploaded': return '已上传';
      case 'processing': return '处理中';
      case 'processed': return '已处理';
      case 'error': return '错误';
      default: return '未知';
    }
  };

  const getFileIcon = (type: string) => {
    const iconMap: { [key: string]: string } = {
      'pdf': '📄',
      'docx': '📝',
      'txt': '📃',
      'md': '📖',
      'html': '🌐'
    };
    return iconMap[type.toLowerCase()] || '📄';
  };

  const selectedFiles = files.filter(file => value.includes(file.id));

  return (
    <div style={{ width: '100%' }}>
      <Card 
        title={
          <Space>
            <FolderOpenOutlined />
            {title}
          </Space>
        }
        extra={
          <Space>
            <Button 
              icon={<ReloadOutlined />} 
              onClick={loadFiles} 
              loading={loading}
              size="small"
            >
              刷新
            </Button>
            <Button 
              type="link" 
              size="small"
              onClick={() => setShowDetails(!showDetails)}
            >
              {showDetails ? '隐藏详情' : '显示详情'}
            </Button>
          </Space>
        }
        size="small"
      >
        <Select
          mode={multiple ? "multiple" : undefined}
          value={value}
          onChange={handleSelect}
          placeholder={placeholder}
          style={{ width: '100%', marginBottom: 12 }}
          loading={loading}
          showSearch
          filterOption={(input, option) => 
            option?.children?.toString().toLowerCase().includes(input.toLowerCase()) ?? false
          }
          maxTagCount={3}
          maxTagPlaceholder={(omittedValues) => `+${omittedValues.length}...`}
        >
          {files.map(file => (
            <Option key={file.id} value={file.id}>
              <Space>
                <span>{getFileIcon(file.type)}</span>
                <span>{file.name}</span>
                <Tag color={getStatusColor(file.status)}>
                  {getStatusText(file.status)}
                </Tag>
              </Space>
            </Option>
          ))}
        </Select>

        {/* 已选择文件摘要 */}
        {selectedFiles.length > 0 && (
          <div style={{ marginBottom: 12 }}>
            <Space wrap>
              <span style={{ color: '#666' }}>已选择:</span>
              {selectedFiles.map(file => (
                <Tag 
                  key={file.id} 
                  color={getStatusColor(file.status)}
                  style={{ marginBottom: 4 }}
                >
                  {getFileIcon(file.type)} {file.name}
                </Tag>
              ))}
            </Space>
          </div>
        )}

        {/* 详细文件列表 */}
        {showDetails && (
          <List
            size="small"
            dataSource={files}
            renderItem={file => (
              <List.Item
                style={{ 
                  backgroundColor: value.includes(file.id) ? '#f6ffed' : 'transparent',
                  border: value.includes(file.id) ? '1px solid #b7eb8f' : 'none',
                  borderRadius: 4,
                  padding: '8px 12px',
                  marginBottom: 4
                }}
              >
                <List.Item.Meta
                  avatar={
                    <Avatar 
                      icon={<FileOutlined />} 
                      style={{ backgroundColor: getStatusColor(file.status) === 'green' ? '#52c41a' : '#1890ff' }}
                    />
                  }
                  title={
                    <Space>
                      <span>{getFileIcon(file.type)}</span>
                      <span>{file.name}</span>
                      <Tag color={getStatusColor(file.status)}>
                        {getStatusText(file.status)}
                      </Tag>
                    </Space>
                  }
                  description={
                    <Space split={<span>|</span>}>
                      <span>{formatFileSize(file.size)}</span>
                      <span>{file.type.toUpperCase()}</span>
                      <span>{file.uploadTime}</span>
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        )}

        {files.length === 0 && !loading && (
          <div style={{ textAlign: 'center', color: '#999', padding: '20px 0' }}>
            <FileOutlined style={{ fontSize: 24, marginBottom: 8 }} />
            <div>暂无可选择的文件</div>
            <div style={{ fontSize: 12 }}>请先前往"文件上传"页面上传文件</div>
          </div>
        )}
      </Card>
    </div>
  );
};

export default FileSelector;