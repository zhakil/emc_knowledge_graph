import React, { useState, useEffect, useRef } from 'react';
import { Card, Typography, Steps, Progress, Tag, Timeline, Spin, Button, Upload, message, Divider, Row, Col, Tooltip, Alert } from 'antd';
import { FileTextOutlined, RobotOutlined, ShareAltOutlined, DatabaseOutlined, EyeOutlined, UploadOutlined, PlayCircleOutlined, StopOutlined } from '@ant-design/icons';
import './EntityExtractionViewer.css';

const { Title, Text, Paragraph } = Typography;
const { Step } = Steps;

interface Entity {
  id: string;
  name: string;
  type: string;
  confidence: number;
  startPos: number;
  endPos: number;
  properties: Record<string, any>;
}

interface Relationship {
  id: string;
  source: string;
  target: string;
  type: string;
  confidence: number;
  properties: Record<string, any>;
}

interface ExtractionResult {
  entities: Entity[];
  relationships: Relationship[];
  processingTime: number;
  confidence: number;
  method: 'ai' | 'rules' | 'hybrid';
}

interface ExtractionStep {
  id: number;
  title: string;
  description: string;
  status: 'wait' | 'process' | 'finish' | 'error';
  duration?: number;
  result?: any;
}

const EntityExtractionViewer: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [currentStep, setCurrentStep] = useState(0);
  const [extractionSteps, setExtractionSteps] = useState<ExtractionStep[]>([
    { id: 0, title: '文本预处理', description: '清理和标准化输入文本', status: 'wait' },
    { id: 1, title: 'AI实体识别', description: '使用DeepSeek API识别实体', status: 'wait' },
    { id: 2, title: '规则增强', description: '应用EMC领域规则进行增强', status: 'wait' },
    { id: 3, title: '关系抽取', description: '识别实体间的语义关系', status: 'wait' },
    { id: 4, title: '结果验证', description: '验证和优化提取结果', status: 'wait' },
    { id: 5, title: '知识图谱存储', description: '将结果存储到Neo4j数据库', status: 'wait' }
  ]);
  
  const [extractionResult, setExtractionResult] = useState<ExtractionResult | null>(null);
  const [highlightedText, setHighlightedText] = useState('');
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [realTimeProgress, setRealTimeProgress] = useState(0);
  const textAreaRef = useRef<HTMLTextAreaElement>(null);
  
  // 示例EMC文本
  const sampleText = `SuperCharger Model SC-5000 was tested according to the EMC Standard EN 55011. 
The radiated emissions test was conducted from 30MHz to 1GHz using the EMI Receiver R3273. 
The product showed compliance with Class A limits. The test was performed at the accredited 
EMC Laboratory using a 3-meter semi-anechoic chamber. The manufacturer ChargeCorp provided 
the technical documentation including the user manual and circuit diagrams.`;

  const entityTypeColors = {
    'Product': '#1890ff',
    'EMCStandard': '#52c41a',
    'Equipment': '#fa8c16',
    'FrequencyRange': '#eb2f96',
    'TestMethod': '#722ed1',
    'Manufacturer': '#13c2c2',
    'Document': '#faad14'
  };

  const relationshipTypes = [
    'HAS_STANDARD',
    'USES_EQUIPMENT', 
    'TESTS_WITH',
    'APPLIES_TO',
    'MANUFACTURED_BY',
    'CONTAINS'
  ];

  // 模拟实体提取过程
  const simulateExtraction = async () => {
    if (!inputText.trim()) {
      message.warning('请输入要分析的文本');
      return;
    }

    setIsProcessing(true);
    setCurrentStep(0);
    setRealTimeProgress(0);
    setExtractionResult(null);

    const steps = [...extractionSteps];
    
    for (let i = 0; i < steps.length; i++) {
      // 更新当前步骤状态
      steps[i].status = 'process';
      setExtractionSteps([...steps]);
      setCurrentStep(i);
      
      // 模拟处理时间
      const processingTime = Math.random() * 2000 + 1000; // 1-3秒
      const startTime = Date.now();
      
      // 实时进度更新
      const progressInterval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min((elapsed / processingTime) * 100, 100);
        setRealTimeProgress(progress);
      }, 100);
      
      await new Promise(resolve => setTimeout(resolve, processingTime));
      clearInterval(progressInterval);
      
      // 完成当前步骤
      steps[i].status = 'finish';
      steps[i].duration = processingTime;
      setExtractionSteps([...steps]);
      setRealTimeProgress(100);
      
      // 模拟步骤结果
      if (i === 1) { // AI实体识别结果
        generateMockEntities();
      } else if (i === 3) { // 关系抽取结果
        generateMockRelationships();
      }
    }
    
    setIsProcessing(false);
    setCurrentStep(steps.length);
    generateFinalResult();
  };

  const generateMockEntities = () => {
    // 模拟识别到的实体（基于输入文本）
    const mockEntities: Entity[] = [
      {
        id: 'e1',
        name: 'SuperCharger Model SC-5000',
        type: 'Product',
        confidence: 0.95,
        startPos: 0,
        endPos: 25,
        properties: { manufacturer: 'ChargeCorp', category: 'Industrial Charger' }
      },
      {
        id: 'e2', 
        name: 'EN 55011',
        type: 'EMCStandard',
        confidence: 0.98,
        startPos: 65,
        endPos: 73,
        properties: { standardFamily: 'CISPR', version: '2016+A11:2020' }
      },
      {
        id: 'e3',
        name: 'EMI Receiver R3273', 
        type: 'Equipment',
        confidence: 0.92,
        startPos: 145,
        endPos: 162,
        properties: { manufacturer: 'Rohde & Schwarz', type: 'EMI Receiver' }
      },
      {
        id: 'e4',
        name: '30MHz to 1GHz',
        type: 'FrequencyRange', 
        confidence: 0.90,
        startPos: 125,
        endPos: 138,
        properties: { startFreq: '30MHz', endFreq: '1GHz', unit: 'Hz' }
      }
    ];
    
    highlightEntitiesInText(mockEntities);
  };

  const generateMockRelationships = () => {
    // 模拟识别到的关系
  };

  const generateFinalResult = () => {
    const mockResult: ExtractionResult = {
      entities: [
        {
          id: 'e1',
          name: 'SuperCharger Model SC-5000',
          type: 'Product',
          confidence: 0.95,
          startPos: 0,
          endPos: 25,
          properties: { manufacturer: 'ChargeCorp', category: 'Industrial Charger' }
        },
        {
          id: 'e2',
          name: 'EN 55011',
          type: 'EMCStandard', 
          confidence: 0.98,
          startPos: 65,
          endPos: 73,
          properties: { standardFamily: 'CISPR', version: '2016+A11:2020' }
        },
        {
          id: 'e3',
          name: 'EMI Receiver R3273',
          type: 'Equipment',
          confidence: 0.92, 
          startPos: 145,
          endPos: 162,
          properties: { manufacturer: 'Rohde & Schwarz', type: 'EMI Receiver' }
        },
        {
          id: 'e4',
          name: '30MHz to 1GHz',
          type: 'FrequencyRange',
          confidence: 0.90,
          startPos: 125, 
          endPos: 138,
          properties: { startFreq: '30MHz', endFreq: '1GHz', unit: 'Hz' }
        }
      ],
      relationships: [
        {
          id: 'r1',
          source: 'e1',
          target: 'e2', 
          type: 'HAS_STANDARD',
          confidence: 0.85,
          properties: { context: 'compliance testing' }
        },
        {
          id: 'r2',
          source: 'e1',
          target: 'e3',
          type: 'TESTS_WITH', 
          confidence: 0.88,
          properties: { testType: 'radiated emissions' }
        },
        {
          id: 'r3',
          source: 'e3',
          target: 'e4',
          type: 'APPLIES_TO',
          confidence: 0.92,
          properties: { measurement: 'frequency range' }
        }
      ],
      processingTime: 8.5,
      confidence: 0.91,
      method: 'hybrid'
    };
    
    setExtractionResult(mockResult);
    highlightEntitiesInText(mockResult.entities);
  };

  const highlightEntitiesInText = (entities: Entity[]) => {
    let highlighted = inputText;
    const sortedEntities = [...entities].sort((a, b) => b.startPos - a.startPos);
    
    sortedEntities.forEach(entity => {
      const entityText = highlighted.substring(entity.startPos, entity.endPos);
      const color = entityTypeColors[entity.type as keyof typeof entityTypeColors] || '#666';
      const highlightedEntity = `<span class="entity-highlight" style="background-color: ${color}20; border-bottom: 2px solid ${color}; cursor: pointer;" data-entity-id="${entity.id}">${entityText}</span>`;
      highlighted = highlighted.substring(0, entity.startPos) + highlightedEntity + highlighted.substring(entity.endPos);
    });
    
    setHighlightedText(highlighted);
  };

  const handleEntityClick = (entityId: string) => {
    if (extractionResult) {
      const entity = extractionResult.entities.find(e => e.id === entityId);
      setSelectedEntity(entity || null);
    }
  };

  const stopExtraction = () => {
    setIsProcessing(false);
    const steps = extractionSteps.map(step => ({ ...step, status: 'wait' as const }));
    setExtractionSteps(steps);
    setCurrentStep(0);
    setRealTimeProgress(0);
  };

  useEffect(() => {
    setInputText(sampleText);
  }, []);

  return (
    <div className="entity-extraction-viewer">
      <Title level={2}>
        <RobotOutlined /> EMC文本实体关系提取分析器
      </Title>
      
      <Row gutter={[24, 24]}>
        {/* 左侧：输入和控制 */}
        <Col span={12}>
          <Card title={<><FileTextOutlined /> 输入文本</>} className="input-card">
            <div style={{ marginBottom: 16 }}>
              <Button 
                type="primary" 
                icon={<PlayCircleOutlined />}
                onClick={simulateExtraction}
                disabled={isProcessing}
                style={{ marginRight: 8 }}
              >
                开始提取分析
              </Button>
              
              {isProcessing && (
                <Button 
                  danger
                  icon={<StopOutlined />}
                  onClick={stopExtraction}
                >
                  停止分析
                </Button>
              )}
              
              <Button 
                style={{ marginLeft: 8 }}
                onClick={() => setInputText(sampleText)}
              >
                加载示例文本
              </Button>
            </div>
            
            <textarea
              ref={textAreaRef}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="请输入EMC相关文本进行实体关系提取分析..."
              style={{ 
                width: '100%', 
                height: 200, 
                border: '1px solid #d9d9d9',
                borderRadius: 6,
                padding: 12,
                fontSize: 14,
                lineHeight: 1.5
              }}
            />
            
            <div style={{ marginTop: 16, fontSize: 12, color: '#666' }}>
              <Text type="secondary">
                支持的实体类型：产品、EMC标准、测试设备、频率范围、测试方法、制造商等
              </Text>
            </div>
          </Card>

          {/* 处理步骤 */}
          <Card title={<><ShareAltOutlined /> 提取处理流程</>} style={{ marginTop: 16 }}>
            <Steps direction="vertical" current={currentStep} size="small">
              {extractionSteps.map((step) => (
                <Step
                  key={step.id}
                  title={step.title}
                  description={
                    <div>
                      <div>{step.description}</div>
                      {step.status === 'process' && (
                        <Progress 
                          percent={Math.round(realTimeProgress)} 
                          size="small" 
                          style={{ marginTop: 4 }}
                        />
                      )}
                      {step.status === 'finish' && step.duration && (
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          耗时: {(step.duration / 1000).toFixed(1)}s
                        </Text>
                      )}
                    </div>
                  }
                  status={step.status}
                  icon={step.status === 'process' ? <Spin size="small" /> : undefined}
                />
              ))}
            </Steps>
          </Card>
        </Col>

        {/* 右侧：结果展示 */}
        <Col span={12}>
          {/* 高亮文本 */}
          <Card title={<><EyeOutlined /> 实体标注结果</>} className="highlight-card">
            {highlightedText ? (
              <div 
                className="highlighted-text"
                dangerouslySetInnerHTML={{ __html: highlightedText }}
                onClick={(e) => {
                  const target = e.target as HTMLElement;
                  if (target.classList.contains('entity-highlight')) {
                    const entityId = target.getAttribute('data-entity-id');
                    if (entityId) handleEntityClick(entityId);
                  }
                }}
              />
            ) : (
              <div style={{ textAlign: 'center', color: '#999', padding: 40 }}>
                等待文本分析...
              </div>
            )}
            
            {/* 实体类型图例 */}
            <Divider />
            <div>
              <Text strong>实体类型图例：</Text>
              <div style={{ marginTop: 8 }}>
                {Object.entries(entityTypeColors).map(([type, color]) => (
                  <Tag 
                    key={type} 
                    color={color} 
                    style={{ marginBottom: 4 }}
                  >
                    {type}
                  </Tag>
                ))}
              </div>
            </div>
          </Card>

          {/* 提取结果统计 */}
          {extractionResult && (
            <Card title={<><DatabaseOutlined /> 提取结果统计</>} style={{ marginTop: 16 }}>
              <Row gutter={16}>
                <Col span={8}>
                  <div className="stat-item">
                    <div className="stat-number">{extractionResult.entities.length}</div>
                    <div className="stat-label">识别实体</div>
                  </div>
                </Col>
                <Col span={8}>
                  <div className="stat-item">
                    <div className="stat-number">{extractionResult.relationships.length}</div>
                    <div className="stat-label">提取关系</div>
                  </div>
                </Col>
                <Col span={8}>
                  <div className="stat-item">
                    <div className="stat-number">{(extractionResult.confidence * 100).toFixed(1)}%</div>
                    <div className="stat-label">整体置信度</div>
                  </div>
                </Col>
              </Row>
              
              <Divider />
              
              <Row gutter={16}>
                <Col span={12}>
                  <Text type="secondary">处理时间: </Text>
                  <Text strong>{extractionResult.processingTime}秒</Text>
                </Col>
                <Col span={12}>
                  <Text type="secondary">提取方法: </Text>
                  <Tag color={extractionResult.method === 'hybrid' ? 'blue' : 'green'}>
                    {extractionResult.method === 'hybrid' ? 'AI+规则混合' : extractionResult.method}
                  </Tag>
                </Col>
              </Row>
            </Card>
          )}
        </Col>
      </Row>

      {/* 详细结果展示 */}
      {extractionResult && (
        <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
          {/* 实体列表 */}
          <Col span={12}>
            <Card title="识别的实体" size="small">
              <div className="entity-list">
                {extractionResult.entities.map((entity) => (
                  <div 
                    key={entity.id} 
                    className={`entity-item ${selectedEntity?.id === entity.id ? 'selected' : ''}`}
                    onClick={() => setSelectedEntity(entity)}
                  >
                    <div className="entity-header">
                      <Tag color={entityTypeColors[entity.type as keyof typeof entityTypeColors]}>
                        {entity.type}
                      </Tag>
                      <Text strong>{entity.name}</Text>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {(entity.confidence * 100).toFixed(1)}%
                      </Text>
                    </div>
                    {Object.keys(entity.properties).length > 0 && (
                      <div className="entity-properties">
                        {Object.entries(entity.properties).map(([key, value]) => (
                          <Text key={key} type="secondary" style={{ fontSize: 12, display: 'block' }}>
                            {key}: {value}
                          </Text>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          </Col>

          {/* 关系列表 */}
          <Col span={12}>
            <Card title="提取的关系" size="small">
              <div className="relationship-list">
                {extractionResult.relationships.map((rel) => {
                  const sourceEntity = extractionResult.entities.find(e => e.id === rel.source);
                  const targetEntity = extractionResult.entities.find(e => e.id === rel.target);
                  
                  return (
                    <div key={rel.id} className="relationship-item">
                      <div className="relationship-header">
                        <Text>{sourceEntity?.name}</Text>
                        <div className="relationship-arrow">
                          <Tag color="blue">{rel.type}</Tag>
                        </div>
                        <Text>{targetEntity?.name}</Text>
                      </div>
                      <div className="relationship-confidence">
                        <Progress 
                          percent={rel.confidence * 100} 
                          size="small" 
                          format={percent => `${percent?.toFixed(1)}%`}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>
          </Col>
        </Row>
      )}

      {/* 实时处理日志 */}
      {isProcessing && (
        <Card title="实时处理日志" style={{ marginTop: 24 }}>
          <Timeline>
            {extractionSteps.map((step) => (
              <Timeline.Item
                key={step.id}
                color={
                  step.status === 'finish' ? 'green' : 
                  step.status === 'process' ? 'blue' : 
                  step.status === 'error' ? 'red' : 'gray'
                }
                dot={step.status === 'process' ? <Spin size="small" /> : undefined}
              >
                <div>
                  <Text strong>{step.title}</Text>
                  <br />
                  <Text type="secondary">{step.description}</Text>
                  {step.status === 'process' && (
                    <div style={{ marginTop: 4 }}>
                      <Progress percent={Math.round(realTimeProgress)} size="small" />
                    </div>
                  )}
                </div>
              </Timeline.Item>
            ))}
          </Timeline>
        </Card>
      )}
    </div>
  );
};

export default EntityExtractionViewer;