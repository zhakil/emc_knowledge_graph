import React, { useState, useCallback } from 'react';
import { 
  Card, 
  Steps, 
  Button, 
  Progress, 
  Alert, 
  Collapse, 
  Typography, 
  Space, 
  Table, 
  Tag, 
  Modal,
  Tabs,
  Row,
  Col,
  Statistic,
  Timeline,
  Divider,
  Switch,
  Slider,
  Select,
  message
} from 'antd';
import { 
  RobotOutlined, 
  ShareAltOutlined, 
  FileTextOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  BulbOutlined,
  DatabaseOutlined,
  EyeOutlined,
  SettingOutlined
} from '@ant-design/icons';

import './IntelligentKGPipeline.css';
import FileSelector from '../FileSelector/FileSelector';

const { Step } = Steps;
const { Panel } = Collapse;
const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;

interface ProcessingProgress {
  currentFile: string;
  currentStep: string;
  progressPercentage: number;
  estimatedRemainingTime: number;
  totalEntitiesExtracted: number;
  totalRelationshipsExtracted: number;
}

interface KGBuildResult {
  success: boolean;
  totalFiles: number;
  processedFiles: number;
  totalEntities: number;
  totalRelationships: number;
  yamlPath?: string;
  neo4jStats?: any;
  processingTime: number;
  errors: string[];
  warnings: string[];
  fileResults: any[];
}

interface ExtractionParams {
  entityTypes: string[];
  relationDepth: number;
  temporalParsing: boolean;
  coreferenceResolution: string;
  confidenceThreshold: number;
  chunkSize: number;
  maxConcurrentExtractions: number;
  enableKagIntegration: boolean;
  kagFusionStrategy: string;
  kagWeight: number;
  deepseekWeight: number;
}

const IntelligentKGPipeline: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedFileIds, setSelectedFileIds] = useState<string[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState<ProcessingProgress>({
    currentFile: '',
    currentStep: '',
    progressPercentage: 0,
    estimatedRemainingTime: 0,
    totalEntitiesExtracted: 0,
    totalRelationshipsExtracted: 0
  });
  const [result, setResult] = useState<KGBuildResult | null>(null);
  const [showAdvancedConfig, setShowAdvancedConfig] = useState(false);
  const [extractionParams, setExtractionParams] = useState<ExtractionParams>({
    entityTypes: ['PERSON', 'ORG', 'EVENT', 'PRODUCT', 'EQUIPMENT', 'STANDARD'],
    relationDepth: 2,
    temporalParsing: true,
    coreferenceResolution: 'enhanced',
    confidenceThreshold: 0.75,
    chunkSize: 1000,
    maxConcurrentExtractions: 3,
    enableKagIntegration: true,
    kagFusionStrategy: 'weighted_ensemble',
    kagWeight: 0.6,
    deepseekWeight: 0.4
  });

  const [processingLog, setProcessingLog] = useState<Array<{
    timestamp: string;
    level: 'info' | 'warning' | 'error' | 'success';
    message: string;
    details?: any;
  }>>([]);

  const addLogEntry = useCallback((level: 'info' | 'warning' | 'error' | 'success', message: string, details?: any) => {
    setProcessingLog(prev => [...prev, {
      timestamp: new Date().toLocaleTimeString(),
      level,
      message,
      details
    }]);
  }, []);

  const handleFileSelect = (fileIds: string[]) => {
    setSelectedFileIds(fileIds);
    addLogEntry('info', `已选择 ${fileIds.length} 个文件进行处理`);
  };

  const startProcessing = async () => {
    if (selectedFileIds.length === 0) {
      message.error('请先选择要处理的文件');
      return;
    }

    setIsProcessing(true);
    setCurrentStep(1);
    addLogEntry('info', '开始智能知识图谱构建流程');

    try {
      // 步骤 1: 文件解析和预处理
      setCurrentStep(1);
      setProgress(prev => ({ 
        ...prev, 
        currentStep: '文件解析和预处理',
        progressPercentage: 20
      }));
      await simulateFileProcessing();

      // 步骤 2: KAG-DeepSeek融合提取
      setCurrentStep(2);
      const extractionMode = extractionParams.enableKagIntegration ? 'KAG-DeepSeek融合提取' : 'DeepSeek关系提取';
      setProgress(prev => ({ 
        ...prev, 
        currentStep: extractionMode,
        progressPercentage: 40
      }));
      addLogEntry('info', `使用${extractionMode}模式进行关系提取`);
      if (extractionParams.enableKagIntegration) {
        addLogEntry('info', `融合策略: ${extractionParams.kagFusionStrategy}, KAG权重: ${extractionParams.kagWeight}`);
      }
      await simulateRelationExtraction();

      // 步骤 3: YAML生成和冲突检测
      setCurrentStep(3);
      setProgress(prev => ({ 
        ...prev, 
        currentStep: 'YAML生成和冲突检测',
        progressPercentage: 70
      }));
      await simulateYamlGeneration();

      // 步骤 4: 图谱构建和验证
      setCurrentStep(4);
      setProgress(prev => ({ 
        ...prev, 
        currentStep: '图谱构建和验证',
        progressPercentage: 90
      }));
      await simulateGraphConstruction();

      // 完成
      setCurrentStep(5);
      setProgress(prev => ({ 
        ...prev, 
        currentStep: '构建完成',
        progressPercentage: 100,
        estimatedRemainingTime: 0
      }));

      // 模拟最终结果
      const mockResult: KGBuildResult = {
        success: true,
        totalFiles: selectedFileIds.length,
        processedFiles: selectedFileIds.length,
        totalEntities: 156,
        totalRelationships: 89,
        yamlPath: 'output/knowledge_graph_20240115.yaml',
        neo4jStats: {
          entitiesCreated: 156,
          relationshipsCreated: 89,
          entitiesUpdated: 12,
          relationshipsUpdated: 5
        },
        processingTime: 125.6,
        errors: [],
        warnings: ['检测到 3 个潜在冲突，已自动解决'],
        fileResults: selectedFileIds.map((fileId, index) => ({
          filePath: `file_${fileId}`,
          success: true,
          entitiesCount: Math.floor(Math.random() * 30) + 10,
          relationshipsCount: Math.floor(Math.random() * 20) + 5,
          conflictsCount: Math.floor(Math.random() * 3)
        }))
      };

      setResult(mockResult);
      addLogEntry('success', '知识图谱构建完成', mockResult);
      
    } catch (error) {
      addLogEntry('error', '构建过程中发生错误', error);
      message.error('构建失败，请查看详细日志');
    } finally {
      setIsProcessing(false);
    }
  };

  // 模拟处理函数
  const simulateFileProcessing = () => new Promise(resolve => {
    let processed = 0;
    const interval = setInterval(() => {
      processed++;
      setProgress(prev => ({
        ...prev,
        currentFile: `文件_${Math.min(processed - 1, selectedFileIds.length - 1) + 1}`,
        progressPercentage: 10 + (processed / selectedFileIds.length) * 20
      }));
      
      if (processed >= selectedFileIds.length) {
        clearInterval(interval);
        addLogEntry('info', `文件解析完成: ${selectedFileIds.length} 个文件`);
        resolve(void 0);
      }
    }, 500);
  });

  const simulateRelationExtraction = () => new Promise(resolve => {
    let entities = 0;
    let relationships = 0;
    const interval = setInterval(() => {
      entities += Math.floor(Math.random() * 10) + 5;
      relationships += Math.floor(Math.random() * 6) + 3;
      
      setProgress(prev => ({
        ...prev,
        totalEntitiesExtracted: entities,
        totalRelationshipsExtracted: relationships,
        progressPercentage: 30 + (entities / 150) * 30
      }));
      
      if (entities >= 150) {
        clearInterval(interval);
        addLogEntry('info', `关系提取完成: ${entities} 实体, ${relationships} 关系`);
        resolve(void 0);
      }
    }, 800);
  });

  const simulateYamlGeneration = () => new Promise(resolve => {
    setTimeout(() => {
      addLogEntry('info', 'YAML知识库生成完成');
      addLogEntry('warning', '检测到 3 个实体冲突，已自动合并');
      resolve(void 0);
    }, 2000);
  });

  const simulateGraphConstruction = () => new Promise(resolve => {
    setTimeout(() => {
      addLogEntry('info', 'Neo4j图数据库更新完成');
      resolve(void 0);
    }, 1500);
  });

  const resetPipeline = () => {
    setCurrentStep(0);
    setSelectedFileIds([]);
    setResult(null);
    setProgress({
      currentFile: '',
      currentStep: '',
      progressPercentage: 0,
      estimatedRemainingTime: 0,
      totalEntitiesExtracted: 0,
      totalRelationshipsExtracted: 0
    });
    setProcessingLog([]);
    addLogEntry('info', '流程已重置');
  };

  const resultColumns = [
    {
      title: '文件',
      dataIndex: 'filePath',
      key: 'filePath'
    },
    {
      title: '状态',
      dataIndex: 'success',
      key: 'success',
      render: (success: boolean) => (
        <Tag color={success ? 'green' : 'red'}>
          {success ? '成功' : '失败'}
        </Tag>
      )
    },
    {
      title: '实体',
      dataIndex: 'entitiesCount',
      key: 'entitiesCount'
    },
    {
      title: '关系',
      dataIndex: 'relationshipsCount',
      key: 'relationshipsCount'
    },
    {
      title: '冲突',
      dataIndex: 'conflictsCount',
      key: 'conflictsCount',
      render: (count: number) => (
        <Tag color={count > 0 ? 'orange' : 'green'}>
          {count}
        </Tag>
      )
    }
  ];

  const steps = [
    {
      title: '智能解析',
      description: '文档解析和语义分块',
      icon: <FileTextOutlined />
    },
    {
      title: 'KAG-DeepSeek融合提取',
      description: '深度关系提取和知识增强',
      icon: <RobotOutlined />
    },
    {
      title: 'YAML生成',
      description: '动态YAML生成和冲突检测',
      icon: <ShareAltOutlined />
    },
    {
      title: '图谱构建',
      description: '知识图谱构建和验证',
      icon: <DatabaseOutlined />
    },
    {
      title: '完成',
      description: '构建完成',
      icon: <CheckCircleOutlined />
    }
  ];

  return (
    <div className="intelligent-kg-pipeline">
      <Card className="header-card">
        <Title level={2}>
          <Space>
            <BulbOutlined />
            智能知识图谱构建流水线
          </Space>
        </Title>
        <Paragraph>
          基于KAG-DeepSeek融合AI的专业级知识图谱构建系统，支持多格式文档解析、
          深度关系提取、动态YAML生成和图谱智能构建。集成KAG知识增强生成框架，
          提供多跳推理和DIKW层次化知识提取能力。
        </Paragraph>
      </Card>

      {/* 进度步骤 */}
      <Card className="steps-card">
        <Steps 
          current={currentStep} 
          status={isProcessing ? "process" : "wait"}
          className="pipeline-steps"
        >
          {steps.map((step, index) => (
            <Step 
              key={index}
              title={step.title}
              description={step.description}
              icon={step.icon}
            />
          ))}
        </Steps>
      </Card>

      {/* 主要内容区域 */}
      <Row gutter={[16, 16]}>
        {/* 左侧：配置和文件管理 */}
        <Col xs={24} lg={12}>
          {/* 文件选择 */}
          <FileSelector
            value={selectedFileIds}
            onChange={handleFileSelect}
            multiple={true}
            title="选择处理文件"
            placeholder="请选择要进行知识图谱构建的文件"
            allowedTypes={['pdf', 'docx', 'txt', 'md', 'html']}
            maxCount={10}
          />

          {/* 高级配置 */}
          <Card 
            title={
              <Space>
                <SettingOutlined />
                高级配置
                <Switch 
                  size="small"
                  checked={showAdvancedConfig}
                  onChange={setShowAdvancedConfig}
                />
              </Space>
            }
            className="config-card"
          >
            {showAdvancedConfig && (
              <Collapse>
                <Panel header="提取参数配置" key="extraction">
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div>
                      <Text>实体类型：</Text>
                      <Select
                        mode="multiple"
                        style={{ width: '100%' }}
                        value={extractionParams.entityTypes}
                        onChange={(value) => setExtractionParams(prev => ({ ...prev, entityTypes: value }))}
                      >
                        <Option value="PERSON">人物</Option>
                        <Option value="ORG">组织</Option>
                        <Option value="EVENT">事件</Option>
                        <Option value="PRODUCT">产品</Option>
                        <Option value="EQUIPMENT">设备</Option>
                        <Option value="STANDARD">标准</Option>
                        <Option value="FREQUENCY">频率</Option>
                        <Option value="MEASUREMENT">测量</Option>
                      </Select>
                    </div>

                    <div>
                      <Text>置信度阈值：{extractionParams.confidenceThreshold}</Text>
                      <Slider
                        min={0.1}
                        max={1.0}
                        step={0.05}
                        value={extractionParams.confidenceThreshold}
                        onChange={(value) => setExtractionParams(prev => ({ ...prev, confidenceThreshold: value }))}
                        marks={{
                          0.1: '0.1',
                          0.5: '0.5',
                          0.75: '0.75',
                          1.0: '1.0'
                        }}
                      />
                    </div>

                    <div>
                      <Text>关系深度：</Text>
                      <Select
                        value={extractionParams.relationDepth}
                        onChange={(value) => setExtractionParams(prev => ({ ...prev, relationDepth: value }))}
                      >
                        <Option value={1}>1层关系</Option>
                        <Option value={2}>2层关系（推荐）</Option>
                        <Option value={3}>3层关系</Option>
                      </Select>
                    </div>

                    <div>
                      <Space>
                        <Switch
                          checked={extractionParams.temporalParsing}
                          onChange={(checked) => setExtractionParams(prev => ({ ...prev, temporalParsing: checked }))}
                        />
                        <Text>时间上下文解析</Text>
                      </Space>
                    </div>
                  </Space>
                </Panel>

                <Panel header="KAG智能增强配置" key="kag">
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div>
                      <Space>
                        <Switch
                          checked={extractionParams.enableKagIntegration}
                          onChange={(checked) => setExtractionParams(prev => ({ ...prev, enableKagIntegration: checked }))}
                        />
                        <Text strong>启用KAG知识增强生成</Text>
                      </Space>
                      <Paragraph type="secondary" style={{ fontSize: '12px', margin: '4px 0 0 0' }}>
                        集成KAG框架进行多跳推理和深度知识提取
                      </Paragraph>
                    </div>

                    {extractionParams.enableKagIntegration && (
                      <>
                        <div>
                          <Text>融合策略：</Text>
                          <Select
                            style={{ width: '100%' }}
                            value={extractionParams.kagFusionStrategy}
                            onChange={(value) => setExtractionParams(prev => ({ ...prev, kagFusionStrategy: value }))}
                          >
                            <Option value="weighted_ensemble">权重集成</Option>
                            <Option value="cascade">级联模式</Option>
                            <Option value="voting">投票机制</Option>
                          </Select>
                        </div>

                        <div>
                          <Text>KAG权重：{extractionParams.kagWeight}</Text>
                          <Slider
                            min={0.1}
                            max={0.9}
                            step={0.1}
                            value={extractionParams.kagWeight}
                            onChange={(value) => {
                              setExtractionParams(prev => ({ 
                                ...prev, 
                                kagWeight: value,
                                deepseekWeight: Math.round((1 - value) * 10) / 10
                              }));
                            }}
                            marks={{
                              0.1: '0.1',
                              0.5: '0.5',
                              0.9: '0.9'
                            }}
                          />
                        </div>

                        <div>
                          <Text>DeepSeek权重：{extractionParams.deepseekWeight}</Text>
                          <Slider
                            min={0.1}
                            max={0.9}
                            step={0.1}
                            value={extractionParams.deepseekWeight}
                            onChange={(value) => {
                              setExtractionParams(prev => ({ 
                                ...prev, 
                                deepseekWeight: value,
                                kagWeight: Math.round((1 - value) * 10) / 10
                              }));
                            }}
                            marks={{
                              0.1: '0.1',
                              0.5: '0.5',
                              0.9: '0.9'
                            }}
                          />
                        </div>
                      </>
                    )}
                  </Space>
                </Panel>

                <Panel header="性能配置" key="performance">
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div>
                      <Text>文本块大小：{extractionParams.chunkSize}</Text>
                      <Slider
                        min={500}
                        max={2000}
                        step={100}
                        value={extractionParams.chunkSize}
                        onChange={(value) => setExtractionParams(prev => ({ ...prev, chunkSize: value }))}
                      />
                    </div>

                    <div>
                      <Text>并发提取数：{extractionParams.maxConcurrentExtractions}</Text>
                      <Slider
                        min={1}
                        max={5}
                        step={1}
                        value={extractionParams.maxConcurrentExtractions}
                        onChange={(value) => setExtractionParams(prev => ({ ...prev, maxConcurrentExtractions: value }))}
                      />
                    </div>
                  </Space>
                </Panel>
              </Collapse>
            )}
          </Card>
        </Col>

        {/* 右侧：进度和结果 */}
        <Col xs={24} lg={12}>
          {/* 实时进度 */}
          {isProcessing && (
            <Card title="处理进度" className="progress-card">
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <Text strong>当前步骤：</Text>
                  <Text>{progress.currentStep}</Text>
                </div>
                
                {progress.currentFile && (
                  <div>
                    <Text strong>当前文件：</Text>
                    <Text>{progress.currentFile}</Text>
                  </div>
                )}

                <Progress 
                  percent={progress.progressPercentage} 
                  status="active"
                  strokeColor={{
                    from: '#108ee9',
                    to: '#87d068',
                  }}
                />

                <Row gutter={16}>
                  <Col span={12}>
                    <Statistic
                      title="已提取实体"
                      value={progress.totalEntitiesExtracted}
                      prefix={<BulbOutlined />}
                    />
                  </Col>
                  <Col span={12}>
                    <Statistic
                      title="已提取关系"
                      value={progress.totalRelationshipsExtracted}
                      prefix={<ShareAltOutlined />}
                    />
                  </Col>
                </Row>

                {progress.estimatedRemainingTime > 0 && (
                  <div>
                    <Text type="secondary">
                      预计剩余时间：{Math.floor(progress.estimatedRemainingTime / 60)}分
                      {progress.estimatedRemainingTime % 60}秒
                    </Text>
                  </div>
                )}
              </Space>
            </Card>
          )}

          {/* 处理日志 */}
          <Card title="处理日志" className="log-card">
            <div className="log-container">
              <Timeline>
                {processingLog.slice(-10).map((log, index) => (
                  <Timeline.Item
                    key={index}
                    color={
                      log.level === 'success' ? 'green' :
                      log.level === 'warning' ? 'orange' :
                      log.level === 'error' ? 'red' : 'blue'
                    }
                    dot={
                      log.level === 'success' ? <CheckCircleOutlined /> :
                      log.level === 'warning' ? <ExclamationCircleOutlined /> :
                      log.level === 'error' ? <ExclamationCircleOutlined /> :
                      <InfoCircleOutlined />
                    }
                  >
                    <div>
                      <Text className="log-timestamp">{log.timestamp}</Text>
                      <div className="log-message">{log.message}</div>
                      {log.details && (
                        <div className="log-details">
                          <Text code>{JSON.stringify(log.details, null, 2)}</Text>
                        </div>
                      )}
                    </div>
                  </Timeline.Item>
                ))}
              </Timeline>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 控制按钮 */}
      <Card className="control-card">
        <Space>
          <Button
            type="primary"
            size="large"
            icon={<RobotOutlined />}
            onClick={startProcessing}
            disabled={isProcessing || selectedFileIds.length === 0}
            loading={isProcessing}
          >
            开始构建知识图谱
          </Button>

          <Button
            size="large"
            onClick={resetPipeline}
            disabled={isProcessing}
          >
            重置流程
          </Button>

          {result && (
            <Button
              size="large"
              icon={<EyeOutlined />}
              onClick={() => {
                Modal.info({
                  title: '构建结果详情',
                  width: 800,
                  content: (
                    <div>
                      <Row gutter={16}>
                        <Col span={8}>
                          <Statistic title="总文件" value={result.totalFiles} />
                        </Col>
                        <Col span={8}>
                          <Statistic title="处理成功" value={result.processedFiles} />
                        </Col>
                        <Col span={8}>
                          <Statistic title="处理时间" value={result.processingTime} suffix="秒" />
                        </Col>
                      </Row>
                      <Divider />
                      <Row gutter={16}>
                        <Col span={12}>
                          <Statistic title="提取实体" value={result.totalEntities} prefix={<BulbOutlined />} />
                        </Col>
                        <Col span={12}>
                          <Statistic title="提取关系" value={result.totalRelationships} prefix={<ShareAltOutlined />} />
                        </Col>
                      </Row>
                      {result.yamlPath && (
                        <>
                          <Divider />
                          <div>
                            <Text strong>YAML输出：</Text>
                            <Text code>{result.yamlPath}</Text>
                          </div>
                        </>
                      )}
                    </div>
                  )
                });
              }}
            >
              查看详细结果
            </Button>
          )}
        </Space>
      </Card>

      {/* 结果展示 */}
      {result && (
        <Card title="构建结果" className="result-card">
          <Tabs>
            <TabPane tab="概览统计" key="overview">
              <Row gutter={[16, 16]}>
                <Col xs={24} sm={12} md={6}>
                  <Card className="stat-card">
                    <Statistic
                      title="处理成功率"
                      value={(result.processedFiles / result.totalFiles * 100).toFixed(1)}
                      suffix="%"
                      valueStyle={{ color: result.success ? '#3f8600' : '#cf1322' }}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Card className="stat-card">
                    <Statistic
                      title="实体密度"
                      value={(result.totalEntities / result.processedFiles).toFixed(1)}
                      suffix="/文件"
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Card className="stat-card">
                    <Statistic
                      title="关系密度"
                      value={(result.totalRelationships / result.totalEntities).toFixed(2)}
                      suffix="/实体"
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Card className="stat-card">
                    <Statistic
                      title="处理效率"
                      value={(result.totalFiles / result.processingTime * 60).toFixed(1)}
                      suffix="文件/分钟"
                    />
                  </Card>
                </Col>
              </Row>

              {result.warnings.length > 0 && (
                <Alert
                  message="处理警告"
                  description={
                    <ul>
                      {result.warnings.map((warning, index) => (
                        <li key={index}>{warning}</li>
                      ))}
                    </ul>
                  }
                  type="warning"
                  style={{ marginTop: 16 }}
                />
              )}

              {result.errors.length > 0 && (
                <Alert
                  message="处理错误"
                  description={
                    <ul>
                      {result.errors.map((error, index) => (
                        <li key={index}>{error}</li>
                      ))}
                    </ul>
                  }
                  type="error"
                  style={{ marginTop: 16 }}
                />
              )}
            </TabPane>

            <TabPane tab="文件详情" key="files">
              <Table
                dataSource={result.fileResults}
                columns={resultColumns}
                pagination={{ pageSize: 10 }}
                size="small"
              />
            </TabPane>

            <TabPane tab="Neo4j统计" key="neo4j">
              {result.neo4jStats ? (
                <Row gutter={[16, 16]}>
                  <Col span={12}>
                    <Statistic
                      title="新增实体"
                      value={result.neo4jStats.entitiesCreated}
                      valueStyle={{ color: '#3f8600' }}
                    />
                  </Col>
                  <Col span={12}>
                    <Statistic
                      title="更新实体"
                      value={result.neo4jStats.entitiesUpdated}
                      valueStyle={{ color: '#1890ff' }}
                    />
                  </Col>
                  <Col span={12}>
                    <Statistic
                      title="新增关系"
                      value={result.neo4jStats.relationshipsCreated}
                      valueStyle={{ color: '#3f8600' }}
                    />
                  </Col>
                  <Col span={12}>
                    <Statistic
                      title="更新关系"
                      value={result.neo4jStats.relationshipsUpdated}
                      valueStyle={{ color: '#1890ff' }}
                    />
                  </Col>
                </Row>
              ) : (
                <Alert
                  message="Neo4j更新未启用"
                  description="请配置Neo4j服务以启用图数据库更新"
                  type="info"
                />
              )}
            </TabPane>
          </Tabs>
        </Card>
      )}
    </div>
  );
};

export default IntelligentKGPipeline;