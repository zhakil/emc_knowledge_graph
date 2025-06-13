import React, { useState, useCallback } from 'react';
import {
  Upload,
  Card,
  Progress,
  Tag,
  Space,
  Button,
  Select,
  Input,
  message,
  Alert,
  Row,
  Col,
  Divider,
  List,
  Typography,
  Popconfirm
} from 'antd';
import {
  InboxOutlined,
  FileTextOutlined,
  CloudUploadOutlined,
  DeleteOutlined,
  EyeOutlined,
  FolderOpenOutlined,
  TagsOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  LoadingOutlined
} from '@ant-design/icons';
import type { UploadProps, UploadFile } from 'antd';

const { Dragger } = Upload;
const { Option } = Select;
const { Text, Title } = Typography;

interface FileCategory {
  key: string;
  label: string;
  color: string;
  icon: React.ReactNode;
}

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  category: string;
  tags: string[];
  uploadTime: string;
  status: 'uploading' | 'success' | 'error' | 'processing';
  progress: number;
  url?: string;
  analysis?: any;
}

const FileUploadArea: React.FC = () => {
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('general');
  const [customTags, setCustomTags] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);

  const categories: FileCategory[] = [
    {
      key: 'document',
      label: '文档类',
      color: 'blue',
      icon: <FileTextOutlined />
    },
    {
      key: 'image',
      label: '图片类',
      color: 'green',
      icon: <EyeOutlined />
    },
    {
      key: 'web',
      label: '网页类',
      color: 'orange',
      icon: <CloudUploadOutlined />
    },
    {
      key: 'code',
      label: '代码类',
      color: 'purple',
      icon: <FolderOpenOutlined />
    },
    {
      key: 'spreadsheet',
      label: '表格类',
      color: 'cyan',
      icon: <TagsOutlined />
    },
    {
      key: 'emc-data',
      label: 'EMC数据',
      color: 'red',
      icon: <ExclamationCircleOutlined />
    },
    {
      key: 'general',
      label: '其他文件',
      color: 'default',
      icon: <FileTextOutlined />
    }
  ];

  const allowedTypes = [
    // 文档类
    '.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt',
    // 表格类  
    '.xls', '.xlsx', '.csv', '.ods',
    // 图片类
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.tiff', '.ico',
    // 网页类
    '.html', '.htm', '.xml', '.xhtml',
    // 代码类
    '.js', '.ts', '.py', '.java', '.cpp', '.c', '.h', '.css', '.scss', '.less', '.json', '.yaml', '.yml',
    // Markdown类
    '.md', '.markdown',
    // 压缩包类
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
    // 音频类
    '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a',
    // 视频类
    '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
    // EMC特定
    '.emc', '.emi', '.ems'
  ];

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: true,
    accept: allowedTypes.join(','),
    fileList,
    beforeUpload: (file) => {
      const isAllowedType = allowedTypes.some(type => 
        file.name.toLowerCase().endsWith(type)
      );
      
      if (!isAllowedType) {
        message.error(`不支持的文件类型: ${file.name}`);
        return false;
      }

      const isLt100M = file.size / 1024 / 1024 < 100;
      if (!isLt100M) {
        message.error('文件大小不能超过 100MB');
        return false;
      }

      return false; // 阻止自动上传，手动控制
    },
    onChange: (info) => {
      setFileList(info.fileList);
    },
    onDrop: (e) => {
      console.log('文件拖拽:', e.dataTransfer.files);
    },
  };

  const handleUpload = async () => {
    if (fileList.length === 0) {
      message.warning('请先选择要上传的文件');
      return;
    }

    setIsUploading(true);

    try {
      for (const file of fileList) {
        const formData = new FormData();
        formData.append('file', file.originFileObj as File);
        formData.append('category', selectedCategory);
        formData.append('tags', customTags);

        const uploadedFile: UploadedFile = {
          id: `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          name: file.name,
          size: file.size || 0,
          type: file.type || '',
          category: selectedCategory,
          tags: customTags.split(',').map(tag => tag.trim()).filter(Boolean),
          uploadTime: new Date().toLocaleString('zh-CN'),
          status: 'uploading',
          progress: 0
        };

        setUploadedFiles(prev => [...prev, uploadedFile]);

        // 模拟上传进度
        const progressInterval = setInterval(() => {
          setUploadedFiles(prev => prev.map(f => 
            f.id === uploadedFile.id 
              ? { ...f, progress: Math.min(f.progress + 10, 90) }
              : f
          ));
        }, 200);

        try {
          const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
          });

          clearInterval(progressInterval);

          if (response.ok) {
            const result = await response.json();
            setUploadedFiles(prev => prev.map(f => 
              f.id === uploadedFile.id 
                ? { 
                    ...f, 
                    status: 'success', 
                    progress: 100,
                    url: result.url,
                    analysis: result.analysis
                  }
                : f
            ));
            message.success(`${file.name} 上传成功`);
          } else {
            throw new Error('上传失败');
          }
        } catch (error) {
          clearInterval(progressInterval);
          setUploadedFiles(prev => prev.map(f => 
            f.id === uploadedFile.id 
              ? { ...f, status: 'error', progress: 0 }
              : f
          ));
          message.error(`${file.name} 上传失败`);
        }
      }

      setFileList([]);
      setCustomTags('');
    } finally {
      setIsUploading(false);
    }
  };

  const deleteUploadedFile = async (fileId: string) => {
    try {
      const response = await fetch(`/api/files/${fileId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
        message.success('文件删除成功');
      } else {
        throw new Error('删除失败');
      }
    } catch (error) {
      message.error('文件删除失败');
    }
  };

  const viewFile = (file: UploadedFile) => {
    if (file.url) {
      window.open(file.url, '_blank');
    } else {
      message.info('文件正在处理中，请稍后查看');
    }
  };

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploading':
      case 'processing':
        return <LoadingOutlined spin />;
      case 'success':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'error':
        return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return null;
    }
  };

  const getCategoryInfo = (categoryKey: string) => {
    return categories.find(cat => cat.key === categoryKey) || categories[0];
  };

  return (
    <div className="fade-in-up">
      <Title level={2} style={{ textAlign: 'center', marginBottom: 24 }}>
        📁 智能文件上传中心
      </Title>

      <Row gutter={[24, 24]}>
        <Col xs={24} lg={12}>
          <Card 
            title={
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <CloudUploadOutlined />
                文件上传
              </div>
            }
            className="chinese-card"
          >
            <Alert
              message="支持的文件格式"
              description={`${allowedTypes.join(', ')} | 最大 100MB`}
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />

            <Dragger {...uploadProps} className="chinese-upload-dragger">
              <p className="ant-upload-drag-icon">
                <InboxOutlined style={{ fontSize: 48, color: '#d4af37' }} />
              </p>
              <p className="ant-upload-text">
                点击或拖拽文件到此区域上传
              </p>
              <p className="ant-upload-hint">
                支持单个或批量上传。严格禁止上传敏感信息。
              </p>
            </Dragger>

            <Divider />

            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>文件分类：</Text>
                <Select
                  value={selectedCategory}
                  onChange={setSelectedCategory}
                  style={{ width: '100%', marginTop: 8 }}
                  className="chinese-input"
                >
                  {categories.map(cat => (
                    <Option key={cat.key} value={cat.key}>
                      <Space>
                        {cat.icon}
                        {cat.label}
                      </Space>
                    </Option>
                  ))}
                </Select>
              </div>

              <div>
                <Text strong>自定义标签：</Text>
                <Input
                  value={customTags}
                  onChange={(e) => setCustomTags(e.target.value)}
                  placeholder="输入标签，用逗号分隔 (如: 重要,测试,EMC)"
                  style={{ marginTop: 8 }}
                  className="chinese-input"
                />
              </div>

              <Button
                type="primary"
                block
                size="large"
                loading={isUploading}
                onClick={handleUpload}
                disabled={fileList.length === 0}
                className="chinese-btn-primary"
                style={{ marginTop: 16 }}
              >
                <CloudUploadOutlined />
                开始上传 ({fileList.length} 个文件)
              </Button>
            </Space>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card 
            title={
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <FileTextOutlined />
                已上传文件 ({uploadedFiles.length})
              </div>
            }
            className="chinese-card"
          >
            <List
              dataSource={uploadedFiles}
              renderItem={(file) => {
                const categoryInfo = getCategoryInfo(file.category);
                return (
                  <List.Item
                    actions={[
                      <Button
                        type="text"
                        size="small"
                        icon={<EyeOutlined />}
                        onClick={() => viewFile(file)}
                        disabled={file.status !== 'success'}
                      >
                        查看
                      </Button>,
                      <Popconfirm
                        title="确定要删除这个文件吗？"
                        onConfirm={() => deleteUploadedFile(file.id)}
                        okText="确定"
                        cancelText="取消"
                      >
                        <Button
                          type="text"
                          size="small"
                          icon={<DeleteOutlined />}
                          danger
                        >
                          删除
                        </Button>
                      </Popconfirm>
                    ]}
                    style={{
                      padding: '12px 0',
                      borderBottom: '1px solid #f0f0f0'
                    }}
                  >
                    <List.Item.Meta
                      avatar={getStatusIcon(file.status)}
                      title={
                        <div>
                          <Text strong>{file.name}</Text>
                          <div style={{ marginTop: 4 }}>
                            <Tag color={categoryInfo.color} icon={categoryInfo.icon}>
                              {categoryInfo.label}
                            </Tag>
                            {file.tags.map(tag => (
                              <Tag key={tag} color="default">{tag}</Tag>
                            ))}
                          </div>
                        </div>
                      }
                      description={
                        <div>
                          <Text type="secondary">
                            {(file.size / 1024 / 1024).toFixed(2)} MB • {file.uploadTime}
                          </Text>
                          {file.status === 'uploading' && (
                            <Progress 
                              percent={file.progress} 
                              size="small" 
                              style={{ marginTop: 4 }}
                            />
                          )}
                        </div>
                      }
                    />
                  </List.Item>
                );
              }}
              locale={{ emptyText: '暂无上传文件' }}
              style={{ maxHeight: 400, overflowY: 'auto' }}
            />
          </Card>
        </Col>
      </Row>

      <Card 
        title="📊 文件分类统计"
        style={{ marginTop: 24 }}
        className="chinese-card"
      >
        <Row gutter={[16, 16]}>
          {categories.map(category => {
            const count = uploadedFiles.filter(f => f.category === category.key).length;
            return (
              <Col xs={12} sm={8} md={6} key={category.key}>
                <Card size="small" className="chinese-card">
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: 24, marginBottom: 8 }}>
                      {category.icon}
                    </div>
                    <Text strong>{category.label}</Text>
                    <div style={{ fontSize: 20, color: '#d4af37', fontWeight: 'bold' }}>
                      {count}
                    </div>
                  </div>
                </Card>
              </Col>
            );
          })}
        </Row>
      </Card>
    </div>
  );
};

export default FileUploadArea;