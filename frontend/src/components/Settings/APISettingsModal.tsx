import React, { useState, useEffect } from 'react';
import {
  Modal,
  Form,
  Input,
  Select,
  Switch,
  Button,
  Tabs,
  Card,
  Space,
  message,
  Divider,
  Tag,
  InputNumber,
  Alert
} from 'antd';
import {
  ApiOutlined,
  DatabaseOutlined,
  SettingOutlined,
  SaveOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';

interface APISettingsModalProps {
  visible: boolean;
  onCancel: () => void;
}

interface APIConfig {
  deepseek: {
    apiKey: string;
    baseUrl: string;
    model: string;
    timeout: number;
    maxRetries: number;
  };
  neo4j: {
    uri: string;
    username: string;
    password: string;
    database: string;
    maxConnections: number;
  };
  system: {
    environment: string;
    debug: boolean;
    logLevel: string;
    uploadMaxSize: number;
  };
}

const APISettingsModal: React.FC<APISettingsModalProps> = ({ visible, onCancel }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [testingConnection, setTestingConnection] = useState<string>('');
  const [connectionStatus, setConnectionStatus] = useState<Record<string, 'success' | 'error' | 'testing'>>({});

  const defaultConfig: APIConfig = {
    deepseek: {
      apiKey: '',
      baseUrl: 'https://api.deepseek.com/v1',
      model: 'deepseek-reasoner',
      timeout: 30,
      maxRetries: 3,
    },
    neo4j: {
      uri: 'bolt://localhost:7687',
      username: 'neo4j',
      password: '',
      database: 'neo4j',
      maxConnections: 100,
    },
    system: {
      environment: 'development',
      debug: true,
      logLevel: 'INFO',
      uploadMaxSize: 100,
    },
  };

  useEffect(() => {
    if (visible) {
      loadSettings();
    }
  }, [visible]);

  const loadSettings = async () => {
    try {
      setLoading(true);
      // 从后端加载配置
      const response = await fetch('/api/settings');
      if (response.ok) {
        const config = await response.json();
        form.setFieldsValue(config);
      } else {
        form.setFieldsValue(defaultConfig);
      }
    } catch (error) {
      console.error('加载设置失败:', error);
      form.setFieldsValue(defaultConfig);
      message.warning('使用默认配置');
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async (type: 'deepseek' | 'neo4j') => {
    const values = form.getFieldsValue();
    setTestingConnection(type);
    setConnectionStatus({ ...connectionStatus, [type]: 'testing' });

    try {
      const response = await fetch(`/api/test-connection/${type}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values[type]),
      });

      if (response.ok) {
        setConnectionStatus({ ...connectionStatus, [type]: 'success' });
        message.success(`${type.toUpperCase()} 连接测试成功`);
      } else {
        throw new Error('连接失败');
      }
    } catch (error) {
      setConnectionStatus({ ...connectionStatus, [type]: 'error' });
      message.error(`${type.toUpperCase()} 连接测试失败`);
    } finally {
      setTestingConnection('');
    }
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      const response = await fetch('/api/settings', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        message.success('设置保存成功');
        onCancel();
      } else {
        throw new Error('保存失败');
      }
    } catch (error) {
      console.error('保存设置失败:', error);
      message.error('保存设置失败');
    } finally {
      setLoading(false);
    }
  };

  const resetToDefault = () => {
    Modal.confirm({
      title: '重置设置',
      content: '确定要重置为默认设置吗？这将清除所有自定义配置。',
      okText: '确定',
      cancelText: '取消',
      onOk: () => {
        form.setFieldsValue(defaultConfig);
        setConnectionStatus({});
        message.info('已重置为默认设置');
      },
    });
  };

  const renderConnectionStatus = (type: string) => {
    const status = connectionStatus[type];
    if (!status) return null;

    const statusConfig = {
      success: { icon: <CheckCircleOutlined />, color: 'success', text: '连接正常' },
      error: { icon: <ExclamationCircleOutlined />, color: 'error', text: '连接失败' },
      testing: { icon: <ReloadOutlined spin />, color: 'processing', text: '测试中...' },
    };

    const config = statusConfig[status];
    return (
      <Tag color={config.color} icon={config.icon}>
        {config.text}
      </Tag>
    );
  };

  const deepseekPanel = (
    <div className="chinese-card-body">
      <Alert
        message="DeepSeek API 配置"
        description="配置 DeepSeek 大语言模型 API，用于智能文档分析和实体提取"
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />
      
      <Form.Item
        name={['deepseek', 'apiKey']}
        label="API 密钥"
        rules={[{ required: true, message: '请输入 DeepSeek API 密钥' }]}
      >
        <Input.Password 
          placeholder="sk-xxxxxxxxxxxxxxxx"
          className="chinese-input"
        />
      </Form.Item>

      <Form.Item
        name={['deepseek', 'baseUrl']}
        label="API 端点"
      >
        <Input 
          placeholder="https://api.deepseek.com/v1"
          className="chinese-input"
        />
      </Form.Item>

      <Form.Item
        name={['deepseek', 'model']}
        label="模型"
      >
        <Select className="chinese-input">
          <Select.Option value="deepseek-reasoner">DeepSeek Reasoner</Select.Option>
          <Select.Option value="deepseek-chat">DeepSeek Chat</Select.Option>
          <Select.Option value="deepseek-coder">DeepSeek Coder</Select.Option>
        </Select>
      </Form.Item>

      <Space>
        <Form.Item
          name={['deepseek', 'timeout']}
          label="超时时间(秒)"
        >
          <InputNumber min={10} max={300} className="chinese-input" />
        </Form.Item>

        <Form.Item
          name={['deepseek', 'maxRetries']}
          label="最大重试次数"
        >
          <InputNumber min={1} max={10} className="chinese-input" />
        </Form.Item>
      </Space>

      <Divider />
      
      <Space>
        <Button
          type="primary"
          loading={testingConnection === 'deepseek'}
          onClick={() => testConnection('deepseek')}
          className="chinese-btn-primary"
        >
          测试连接
        </Button>
        {renderConnectionStatus('deepseek')}
      </Space>
    </div>
  );

  const neo4jPanel = (
    <div className="chinese-card-body">
      <Alert
        message="Neo4j 图数据库配置"
        description="配置 Neo4j 图数据库连接，用于知识图谱存储和查询"
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />

      <Form.Item
        name={['neo4j', 'uri']}
        label="连接 URI"
        rules={[{ required: true, message: '请输入 Neo4j 连接 URI' }]}
      >
        <Input 
          placeholder="bolt://localhost:7687"
          className="chinese-input"
        />
      </Form.Item>

      <Space>
        <Form.Item
          name={['neo4j', 'username']}
          label="用户名"
          rules={[{ required: true, message: '请输入用户名' }]}
        >
          <Input 
            placeholder="neo4j"
            className="chinese-input"
          />
        </Form.Item>

        <Form.Item
          name={['neo4j', 'password']}
          label="密码"
          rules={[{ required: true, message: '请输入密码' }]}
        >
          <Input.Password 
            placeholder="数据库密码"
            className="chinese-input"
          />
        </Form.Item>
      </Space>

      <Space>
        <Form.Item
          name={['neo4j', 'database']}
          label="数据库名"
        >
          <Input 
            placeholder="neo4j"
            className="chinese-input"
          />
        </Form.Item>

        <Form.Item
          name={['neo4j', 'maxConnections']}
          label="最大连接数"
        >
          <InputNumber min={10} max={1000} className="chinese-input" />
        </Form.Item>
      </Space>

      <Divider />
      
      <Space>
        <Button
          type="primary"
          loading={testingConnection === 'neo4j'}
          onClick={() => testConnection('neo4j')}
          className="chinese-btn-primary"
        >
          测试连接
        </Button>
        {renderConnectionStatus('neo4j')}
      </Space>
    </div>
  );

  const systemPanel = (
    <div className="chinese-card-body">
      <Alert
        message="系统配置"
        description="配置系统运行环境和基础设置"
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />

      <Form.Item
        name={['system', 'environment']}
        label="运行环境"
      >
        <Select className="chinese-input">
          <Select.Option value="development">开发环境</Select.Option>
          <Select.Option value="production">生产环境</Select.Option>
          <Select.Option value="testing">测试环境</Select.Option>
        </Select>
      </Form.Item>

      <Form.Item
        name={['system', 'debug']}
        label="调试模式"
        valuePropName="checked"
      >
        <Switch />
      </Form.Item>

      <Form.Item
        name={['system', 'logLevel']}
        label="日志级别"
      >
        <Select className="chinese-input">
          <Select.Option value="DEBUG">调试</Select.Option>
          <Select.Option value="INFO">信息</Select.Option>
          <Select.Option value="WARNING">警告</Select.Option>
          <Select.Option value="ERROR">错误</Select.Option>
        </Select>
      </Form.Item>

      <Form.Item
        name={['system', 'uploadMaxSize']}
        label="文件上传大小限制(MB)"
      >
        <InputNumber min={1} max={1000} className="chinese-input" />
      </Form.Item>
    </div>
  );

  const tabItems = [
    {
      key: 'deepseek',
      label: (
        <span>
          <ApiOutlined />
          DeepSeek API
        </span>
      ),
      children: deepseekPanel,
    },
    {
      key: 'neo4j',
      label: (
        <span>
          <DatabaseOutlined />
          Neo4j 数据库
        </span>
      ),
      children: neo4jPanel,
    },
    {
      key: 'system',
      label: (
        <span>
          <SettingOutlined />
          系统设置
        </span>
      ),
      children: systemPanel,
    },
  ];

  return (
    <Modal
      title={
        <div style={{ textAlign: 'center', fontSize: '18px', fontWeight: 'bold' }}>
          🔧 系统配置设置
        </div>
      }
      open={visible}
      onCancel={onCancel}
      width={800}
      footer={[
        <Button key="reset" onClick={resetToDefault}>
          <ReloadOutlined /> 重置默认
        </Button>,
        <Button key="cancel" onClick={onCancel}>
          取消
        </Button>,
        <Button
          key="save"
          type="primary"
          loading={loading}
          onClick={handleSave}
          className="chinese-btn-primary"
        >
          <SaveOutlined /> 保存配置
        </Button>,
      ]}
      className="chinese-card"
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={defaultConfig}
      >
        <Tabs
          items={tabItems}
          type="card"
          className="chinese-tabs"
        />
      </Form>
    </Modal>
  );
};

export default APISettingsModal;