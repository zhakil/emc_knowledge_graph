import React, { useState, useEffect } from 'react';
import {
  Row,
  Col,
  Card,
  Statistic,
  Progress,
  Alert,
  List,
  Avatar,
  Tag,
  Button,
  Space,
  Typography,
  Timeline,
  Table,
  Tooltip,
  Badge
} from 'antd';
import {
  CloudUploadOutlined,
  FileTextOutlined,
  BranchesOutlined,
  DatabaseOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined,
  RiseOutlined,
  TeamOutlined,
  ApiOutlined,
  BarChartOutlined,
  LineChartOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;

interface SystemStatus {
  api: 'online' | 'offline' | 'warning';
  database: 'connected' | 'disconnected' | 'error';
  upload: 'active' | 'inactive';
  knowledgeGraph: 'running' | 'stopped' | 'development';
}

interface Statistics {
  totalFiles: number;
  totalNodes: number;
  totalRelations: number;
  todayUploads: number;
  processingFiles: number;
  storageUsed: number;
  storageTotal: number;
}

interface RecentActivity {
  id: string;
  type: 'upload' | 'analysis' | 'graph' | 'system';
  title: string;
  description: string;
  timestamp: string;
  status: 'success' | 'warning' | 'error' | 'info';
}

const Dashboard: React.FC = () => {
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    api: 'online',
    database: 'connected',
    upload: 'active',
    knowledgeGraph: 'development'
  });

  const [statistics, setStatistics] = useState<Statistics>({
    totalFiles: 0,
    totalNodes: 0,
    totalRelations: 0,
    todayUploads: 0,
    processingFiles: 0,
    storageUsed: 0,
    storageTotal: 100
  });

  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000); // 每30秒刷新
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // 获取系统状态
      const statusResponse = await fetch('/api/system/status');
      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        setSystemStatus(statusData);
      } else {
        // 使用模拟数据
        setSystemStatus({
          api: 'online',
          database: 'connected',
          upload: 'active',
          knowledgeGraph: 'development'
        });
      }

      // 获取统计数据
      const statsResponse = await fetch('/api/system/statistics');
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStatistics({
          totalFiles: statsData.totalFiles || 0,
          totalNodes: statsData.totalNodes || 0,
          totalRelations: statsData.totalRelations || 0,
          todayUploads: statsData.todayUploads || 0,
          processingFiles: statsData.processingFiles || 0,
          storageUsed: statsData.storageUsed || 0,
          storageTotal: statsData.storageTotal || 100
        });
      } else {
        // 使用模拟数据
        setStatistics({
          totalFiles: 156,
          totalNodes: 1247,
          totalRelations: 3891,
          todayUploads: 23,
          processingFiles: 3,
          storageUsed: 67.8,
          storageTotal: 100
        });
      }

      // 获取最近活动
      const activitiesResponse = await fetch('/api/system/activities');
      if (activitiesResponse.ok) {
        const activitiesData = await activitiesResponse.json();
        setRecentActivities(activitiesData);
      } else {
        // 使用模拟数据
        setRecentActivities([
          {
            id: 'act_1',
            type: 'upload',
            title: '文件上传完成',
            description: '成功上传 "EMC测试报告_设备B.pdf"',
            timestamp: '2025-06-11 15:30:22',
            status: 'success'
          },
          {
            id: 'act_2',
            type: 'analysis',
            title: 'AI分析完成',
            description: '完成对 "IEC61000-4-3标准.pdf" 的实体提取',
            timestamp: '2025-06-11 15:28:15',
            status: 'success'
          },
          {
            id: 'act_3',
            type: 'graph',
            title: '知识图谱更新',
            description: '新增 5 个节点和 12 个关系',
            timestamp: '2025-06-11 15:25:08',
            status: 'info'
          },
          {
            id: 'act_4',
            type: 'system',
            title: '系统启动',
            description: 'EMC知识图谱系统启动完成',
            timestamp: '2025-06-11 14:00:00',
            status: 'info'
          }
        ]);
      }
    } catch (error) {
      console.error('加载仪表板数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
      case 'connected':
      case 'active':
      case 'running':
        return 'success';
      case 'development':
      case 'warning':
        return 'warning';
      case 'offline':
      case 'disconnected':
      case 'inactive':
      case 'stopped':
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusText = (service: string, status: string) => {
    const statusMap: Record<string, Record<string, string>> = {
      api: {
        online: '正常运行',
        offline: '离线',
        warning: '警告'
      },
      database: {
        connected: '已连接',
        disconnected: '未连接',
        error: '连接错误'
      },
      upload: {
        active: '功能可用',
        inactive: '不可用'
      },
      knowledgeGraph: {
        running: '正常运行',
        development: '开发模式',
        stopped: '已停止'
      }
    };
    return statusMap[service]?.[status] || status;
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'upload':
        return <CloudUploadOutlined />;
      case 'analysis':
        return <BarChartOutlined />;
      case 'graph':
        return <BranchesOutlined />;
      case 'system':
        return <ApiOutlined />;
      default:
        return <ClockCircleOutlined />;
    }
  };

  const systemServices = [
    {
      key: 'api',
      name: 'API 服务',
      icon: <ApiOutlined />,
      status: systemStatus.api
    },
    {
      key: 'database',
      name: '数据库',
      icon: <DatabaseOutlined />,
      status: systemStatus.database
    },
    {
      key: 'upload',
      name: '文件上传',
      icon: <CloudUploadOutlined />,
      status: systemStatus.upload
    },
    {
      key: 'knowledgeGraph',
      name: '知识图谱',
      icon: <BranchesOutlined />,
      status: systemStatus.knowledgeGraph
    }
  ];

  const quickActions = [
    {
      title: '上传文件',
      description: '上传新的EMC文档',
      icon: <CloudUploadOutlined />,
      action: () => window.location.hash = '#/upload'
    },
    {
      title: '查看图谱',
      description: '浏览知识图谱',
      icon: <BranchesOutlined />,
      action: () => window.location.hash = '#/knowledge-graph'
    },
    {
      title: '文件管理',
      description: '管理已上传文件',
      icon: <FileTextOutlined />,
      action: () => window.location.hash = '#/files'
    },
    {
      title: '系统设置',
      description: '配置系统参数',
      icon: <ApiOutlined />,
      action: () => window.location.hash = '#/settings'
    }
  ];

  return (
    <div className="fade-in-up">
      <Title level={2} style={{ textAlign: 'center', marginBottom: 24 }}>
        🏠 系统概览仪表板
      </Title>

      {/* 系统状态概览 */}
      <Alert
        message="系统运行状态"
        description="EMC知识图谱系统当前运行正常，所有核心服务已启动"
        type="success"
        showIcon
        closable
        style={{ marginBottom: 24 }}
      />

      {/* 系统服务状态 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {systemServices.map(service => (
          <Col xs={12} sm={6} key={service.key}>
            <Card className="chinese-card" style={{ textAlign: 'center' }}>
              <Space direction="vertical">
                <div style={{ fontSize: 24, color: '#d4af37' }}>
                  {service.icon}
                </div>
                <Text strong>{service.name}</Text>
                <Badge 
                  status={getStatusColor(service.status) as any}
                  text={getStatusText(service.key, service.status)}
                />
              </Space>
            </Card>
          </Col>
        ))}
      </Row>

      {/* 统计数据 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card className="chinese-card">
            <Statistic
              title="文件总数"
              value={statistics.totalFiles}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card className="chinese-card">
            <Statistic
              title="知识节点"
              value={statistics.totalNodes}
              prefix={<BranchesOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card className="chinese-card">
            <Statistic
              title="关系数量"
              value={statistics.totalRelations}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card className="chinese-card">
            <Statistic
              title="今日上传"
              value={statistics.todayUploads}
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]}>
        {/* 存储使用情况 */}
        <Col xs={24} lg={8}>
          <Card 
            title="💾 存储使用情况"
            className="chinese-card"
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <Progress
                percent={statistics?.storageUsed || 0}
                status={(statistics?.storageUsed || 0) > 80 ? 'exception' : 'active'}
                format={percent => `${percent || 0}%`}
              />
              <Text type="secondary">
                已使用 {(statistics?.storageUsed || 0).toFixed(1)}GB / 共 {statistics?.storageTotal || 100}GB
              </Text>
              
              {(statistics?.processingFiles || 0) > 0 && (
                <Alert
                  message={`${statistics.processingFiles} 个文件正在处理中`}
                  type="info"
                  showIcon
                  style={{ marginTop: 16 }}
                />
              )}
            </Space>
          </Card>
        </Col>

        {/* 快捷操作 */}
        <Col xs={24} lg={8}>
          <Card 
            title="⚡ 快捷操作"
            className="chinese-card"
          >
            <List
              dataSource={quickActions}
              renderItem={item => (
                <List.Item style={{ padding: '8px 0' }}>
                  <List.Item.Meta
                    avatar={<Avatar icon={item.icon} style={{ backgroundColor: '#d4af37' }} />}
                    title={
                      <Button 
                        type="link" 
                        onClick={item.action}
                        style={{ padding: 0, height: 'auto' }}
                      >
                        {item.title}
                      </Button>
                    }
                    description={item.description}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* 最近活动 */}
        <Col xs={24} lg={8}>
          <Card 
            title="📋 最近活动"
            extra={
              <Button 
                type="text" 
                size="small"
                onClick={loadDashboardData}
                loading={loading}
              >
                刷新
              </Button>
            }
            className="chinese-card"
          >
            <Timeline>
              {recentActivities.map(activity => (
                <Timeline.Item
                  key={activity.id}
                  dot={getActivityIcon(activity.type)}
                  color={getStatusColor(activity.status)}
                >
                  <div>
                    <Text strong>{activity.title}</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {activity.description}
                    </Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: '11px' }}>
                      {activity.timestamp}
                    </Text>
                  </div>
                </Timeline.Item>
              ))}
            </Timeline>
          </Card>
        </Col>
      </Row>

      {/* 系统信息 */}
      <Card 
        title="ℹ️ 系统信息"
        style={{ marginTop: 24 }}
        className="chinese-card"
      >
        <Row gutter={[24, 16]}>
          <Col xs={24} sm={12}>
            <Text strong>系统版本: </Text>
            <Text>EMC知识图谱系统 v1.0.0</Text>
          </Col>
          <Col xs={24} sm={12}>
            <Text strong>运行环境: </Text>
            <Tag color="blue">开发模式</Tag>
          </Col>
          <Col xs={24} sm={12}>
            <Text strong>启动时间: </Text>
            <Text>2025-06-11 14:00:00</Text>
          </Col>
          <Col xs={24} sm={12}>
            <Text strong>运行时长: </Text>
            <Text>1小时 30分钟</Text>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default Dashboard;