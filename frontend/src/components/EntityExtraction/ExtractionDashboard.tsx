import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Progress, Timeline, Tag, Button, message, Tabs, Alert, Space, Upload } from 'antd';
import { FileTextOutlined, RobotOutlined, ShareAltOutlined, DatabaseOutlined, BarChartOutlined, BulbOutlined, UploadOutlined } from '@ant-design/icons';
import EntityExtractionViewer from './EntityExtractionViewer';
import EntityRelationGraph from './EntityRelationGraph';
import FileSelector from '../FileSelector/FileSelector';
import './ExtractionDashboard.css';

const { TabPane } = Tabs;
const { Dragger } = Upload;

interface ProcessingStats {
  totalDocuments: number;
  processedDocuments: number;
  totalEntities: number;
  totalRelationships: number;
  averageConfidence: number;
  processingTime: number;
  entityTypes: Record<string, number>;
  relationshipTypes: Record<string, number>;
}

interface RealtimeMetrics {
  currentThroughput: number; // 文档/分钟
  avgExtractionTime: number; // 秒/文档
  successRate: number; // 百分比
  errorRate: number; // 百分比
  queueLength: number;
}

const ExtractionDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('extraction');
  const [selectedFileIds, setSelectedFileIds] = useState<string[]>([]);
  const [processingStats, setProcessingStats] = useState<ProcessingStats>({
    totalDocuments: 156,
    processedDocuments: 143,
    totalEntities: 1247,
    totalRelationships: 892,
    averageConfidence: 0.87,
    processingTime: 425.6,
    entityTypes: {
      'Product': 245,
      'EMCStandard': 189,
      'Equipment': 156,
      'FrequencyRange': 134,
      'TestMethod': 98,
      'Manufacturer': 87,
      'Document': 78
    },
    relationshipTypes: {
      'HAS_STANDARD': 234,
      'USES_EQUIPMENT': 198,
      'TESTS_WITH': 156,
      'APPLIES_TO': 123,
      'MANUFACTURED_BY': 98,
      'CONTAINS': 83
    }
  });

  const [realtimeMetrics, setRealtimeMetrics] = useState<RealtimeMetrics>({
    currentThroughput: 12.5,
    avgExtractionTime: 4.8,
    successRate: 94.2,
    errorRate: 5.8,
    queueLength: 8
  });

  const [recentActivities, setRecentActivities] = useState([
    {
      time: '2024-01-15 14:32:15',
      action: '完成实体提取',
      document: 'EMC_Test_Report_SC5000.pdf',
      entities: 15,
      relationships: 12,
      status: 'success'
    },
    {
      time: '2024-01-15 14:31:45',
      action: '开始处理文档',
      document: 'IEC_61000_Standard.pdf',
      entities: 0,
      relationships: 0,
      status: 'processing'
    },
    {
      time: '2024-01-15 14:30:22',
      action: '实体消歧完成',
      document: 'EN55011_Compliance_Report.pdf',
      entities: 23,
      relationships: 18,
      status: 'success'
    },
    {
      time: '2024-01-15 14:29:56',
      action: '处理失败',
      document: 'corrupted_file.pdf',
      entities: 0,
      relationships: 0,
      status: 'error'
    }
  ]);

  // 模拟实时数据更新
  useEffect(() => {
    const interval = setInterval(() => {
      setRealtimeMetrics(prev => ({
        ...prev,
        currentThroughput: Math.max(0, prev.currentThroughput + (Math.random() - 0.5) * 2),
        avgExtractionTime: Math.max(1, prev.avgExtractionTime + (Math.random() - 0.5) * 0.5),
        queueLength: Math.max(0, prev.queueLength + Math.floor((Math.random() - 0.5) * 3))
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleFileUpload = (file: File) => {
    message.success(`开始处理文件: ${file.name}`);
    
    // 模拟添加到处理队列
    setRealtimeMetrics(prev => ({
      ...prev,
      queueLength: prev.queueLength + 1
    }));

    // 模拟处理完成后的活动记录
    setTimeout(() => {
      const newActivity = {
        time: new Date().toLocaleString(),
        action: '完成实体提取',
        document: file.name,
        entities: Math.floor(Math.random() * 20) + 5,
        relationships: Math.floor(Math.random() * 15) + 3,
        status: 'success' as const
      };
      
      setRecentActivities(prev => [newActivity, ...prev.slice(0, 9)]);
      setRealtimeMetrics(prev => ({
        ...prev,
        queueLength: Math.max(0, prev.queueLength - 1)
      }));
    }, 3000);

    return false; // 防止默认上传行为
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'green';
      case 'processing': return 'blue';
      case 'error': return 'red';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return '✅';
      case 'processing': return '⏳';
      case 'error': return '❌';
      default: return '📄';
    }
  };

  const completionRate = (processingStats.processedDocuments / processingStats.totalDocuments) * 100;

  return (
    <div className="extraction-dashboard">
      <div className="dashboard-header">
        <h1>EMC实体关系提取控制台</h1>
        <div className="header-actions">
          <Dragger
            accept=".pdf,.docx,.txt"
            multiple={true}
            beforeUpload={handleFileUpload}
            showUploadList={false}
            className="upload-dragger"
          >
            <Button type="primary" icon={<UploadOutlined />}>
              批量上传文档
            </Button>
          </Dragger>
        </div>
      </div>

      {/* 实时指标概览 */}
      <Row gutter={[16, 16]} className="metrics-overview">
        <Col xs={24} sm={12} md={6}>
          <Card className="metric-card">
            <Statistic
              title="处理进度"
              value={completionRate}
              precision={1}
              suffix="%"
              prefix={<DatabaseOutlined />}
            />
            <Progress 
              percent={completionRate} 
              size="small" 
              strokeColor="#52c41a"
              style={{ marginTop: 8 }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card className="metric-card">
            <Statistic
              title="提取实体"
              value={processingStats.totalEntities}
              prefix={<BulbOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <div className="metric-subtitle">
              平均置信度: {(processingStats.averageConfidence * 100).toFixed(1)}%
            </div>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card className="metric-card">
            <Statistic
              title="识别关系"
              value={processingStats.totalRelationships}
              prefix={<ShareAltOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <div className="metric-subtitle">
              关系类型: {Object.keys(processingStats.relationshipTypes).length}种
            </div>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card className="metric-card">
            <Statistic
              title="处理效率"
              value={realtimeMetrics.currentThroughput}
              precision={1}
              suffix="doc/min"
              prefix={<BarChartOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
            <div className="metric-subtitle">
              队列长度: {realtimeMetrics.queueLength}
            </div>
          </Card>
        </Col>
      </Row>

      {/* 实时状态警报 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={24}>
          <Space direction="vertical" style={{ width: '100%' }}>
            {realtimeMetrics.successRate < 90 && (
              <Alert
                message="系统提醒"
                description={`当前成功率${realtimeMetrics.successRate.toFixed(1)}%，低于正常水平，请检查输入文档质量或系统配置。`}
                type="warning"
                showIcon
                closable
              />
            )}
            
            {realtimeMetrics.queueLength > 20 && (
              <Alert
                message="处理队列拥堵"
                description={`当前队列中有${realtimeMetrics.queueLength}个文档等待处理，建议调整并发参数或稍后再试。`}
                type="info"
                showIcon
                closable
              />
            )}
          </Space>
        </Col>
      </Row>

      {/* 文件选择器 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={24}>
          <FileSelector
            value={selectedFileIds}
            onChange={setSelectedFileIds}
            multiple={true}
            title="选择分析文件"
            placeholder="请选择要进行实体关系提取的文件"
            allowedTypes={['pdf', 'docx', 'txt', 'md', 'html']}
            maxCount={5}
          />
        </Col>
      </Row>

      {/* 主要内容标签页 */}
      <Tabs activeKey={activeTab} onChange={setActiveTab} className="main-tabs">
        <TabPane
          tab={
            <span>
              <RobotOutlined />
              实时提取分析
            </span>
          }
          key="extraction"
        >
          <EntityExtractionViewer />
        </TabPane>

        <TabPane
          tab={
            <span>
              <ShareAltOutlined />
              关系图谱
            </span>
          }
          key="graph"
        >
          <EntityRelationGraph
            entities={[
              {
                id: 'e1',
                name: 'SuperCharger SC-5000',
                type: 'Product',
                confidence: 0.95,
                properties: { manufacturer: 'ChargeCorp' }
              },
              {
                id: 'e2',
                name: 'EN 55011',
                type: 'EMCStandard',
                confidence: 0.98,
                properties: { standardFamily: 'CISPR' }
              },
              {
                id: 'e3',
                name: 'EMI Receiver R3273',
                type: 'Equipment',
                confidence: 0.92,
                properties: { manufacturer: 'Rohde & Schwarz' }
              }
            ]}
            relationships={[
              {
                source: 'e1',
                target: 'e2',
                type: 'HAS_STANDARD',
                confidence: 0.85,
                properties: {}
              },
              {
                source: 'e1',
                target: 'e3',
                type: 'TESTS_WITH',
                confidence: 0.88,
                properties: {}
              }
            ]}
          />
        </TabPane>

        <TabPane
          tab={
            <span>
              <BarChartOutlined />
              统计分析
            </span>
          }
          key="statistics"
        >
          <Row gutter={[16, 16]}>
            <Col xs={24} lg={12}>
              <Card title="实体类型分布" className="chart-card">
                <div className="entity-type-chart">
                  {Object.entries(processingStats.entityTypes).map(([type, count]) => {
                    const percentage = (count / processingStats.totalEntities) * 100;
                    return (
                      <div key={type} className="type-item">
                        <div className="type-header">
                          <span className="type-name">{type}</span>
                          <span className="type-count">{count}</span>
                        </div>
                        <Progress 
                          percent={percentage} 
                          size="small"
                          format={percent => `${percent?.toFixed(1)}%`}
                          strokeColor="#1890ff"
                        />
                      </div>
                    );
                  })}
                </div>
              </Card>
            </Col>

            <Col xs={24} lg={12}>
              <Card title="关系类型分布" className="chart-card">
                <div className="relationship-type-chart">
                  {Object.entries(processingStats.relationshipTypes).map(([type, count]) => {
                    const percentage = (count / processingStats.totalRelationships) * 100;
                    return (
                      <div key={type} className="type-item">
                        <div className="type-header">
                          <span className="type-name">{type}</span>
                          <span className="type-count">{count}</span>
                        </div>
                        <Progress 
                          percent={percentage} 
                          size="small"
                          format={percent => `${percent?.toFixed(1)}%`}
                          strokeColor="#52c41a"
                        />
                      </div>
                    );
                  })}
                </div>
              </Card>
            </Col>

            <Col span={24}>
              <Card title="处理性能指标">
                <Row gutter={[16, 16]}>
                  <Col xs={24} sm={8}>
                    <div className="performance-metric">
                      <div className="metric-value">{realtimeMetrics.avgExtractionTime.toFixed(1)}s</div>
                      <div className="metric-label">平均提取时间</div>
                    </div>
                  </Col>
                  <Col xs={24} sm={8}>
                    <div className="performance-metric">
                      <div className="metric-value">{realtimeMetrics.successRate.toFixed(1)}%</div>
                      <div className="metric-label">成功率</div>
                    </div>
                  </Col>
                  <Col xs={24} sm={8}>
                    <div className="performance-metric">
                      <div className="metric-value">{processingStats.processingTime.toFixed(1)}s</div>
                      <div className="metric-label">总处理时间</div>
                    </div>
                  </Col>
                </Row>
              </Card>
            </Col>
          </Row>
        </TabPane>

        <TabPane
          tab={
            <span>
              <FileTextOutlined />
              处理日志
            </span>
          }
          key="activity"
        >
          <Card title="最近处理活动" className="activity-card">
            <Timeline className="activity-timeline">
              {recentActivities.map((activity, index) => (
                <Timeline.Item
                  key={index}
                  color={getStatusColor(activity.status)}
                  dot={<span style={{ fontSize: 16 }}>{getStatusIcon(activity.status)}</span>}
                >
                  <div className="activity-item">
                    <div className="activity-header">
                      <span className="activity-action">{activity.action}</span>
                      <Tag color={getStatusColor(activity.status)}>
                        {activity.status}
                      </Tag>
                    </div>
                    <div className="activity-document">{activity.document}</div>
                    <div className="activity-details">
                      <span>实体: {activity.entities}</span>
                      <span>关系: {activity.relationships}</span>
                      <span className="activity-time">{activity.time}</span>
                    </div>
                  </div>
                </Timeline.Item>
              ))}
            </Timeline>
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default ExtractionDashboard;