import React, { useState } from 'react';
import { Card, Form, Input, Button, Select, Switch, Progress, Alert, Typography, Space, Table, Tag, Row, Col } from 'antd';
import { ApiOutlined, BranchesOutlined } from '@ant-design/icons';
import FileSelector from '../FileSelector/FileSelector';

const { TextArea } = Input;
const { Option } = Select;
const { Title, Text } = Typography;

interface ExtractionParams {
  entity_types: string[];
  relation_depth: number;
  temporal_parsing: boolean;
  coreference_resolution: string;
  confidence_threshold: number;
}

interface ExtractionResult {
  entities: Array<{
    id: string;
    text: string;
    type: string;
    confidence: number;
    start: number;
    end: number;
  }>;
  relations: Array<{
    id: string;
    subject: string;
    predicate: string;
    object: string;
    confidence: number;
    evidence: string;
  }>;
  temporal_contexts: Array<{
    text: string;
    normalized: string;
    confidence: number;
  }>;
}

const DeepSeekExtractor: React.FC = () => {
  const [form] = Form.useForm();
  const [isExtracting, setIsExtracting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedFileIds, setSelectedFileIds] = useState<string[]>([]);

  const defaultParams: ExtractionParams = {
    entity_types: ['PERSON', 'ORG', 'EVENT', 'PRODUCT'],
    relation_depth: 2,
    temporal_parsing: true,
    coreference_resolution: 'enhanced',
    confidence_threshold: 0.75
  };

  const performExtraction = async (values: any) => {
    setIsExtracting(true);
    setProgress(0);
    setError(null);
    setResult(null);

    try {
      // 构建API调用参数
      const apiParams = {
        text: values.text,
        params: {
          entity_types: values.entity_types || defaultParams.entity_types,
          relation_depth: values.relation_depth || defaultParams.relation_depth,
          temporal_parsing: values.temporal_parsing ?? defaultParams.temporal_parsing,
          coreference_resolution: values.coreference_resolution || defaultParams.coreference_resolution,
          confidence_threshold: values.confidence_threshold || defaultParams.confidence_threshold
        },
        context: values.context || ''
      };

      // 模拟API调用过程
      console.log('DeepSeek API 调用参数:', JSON.stringify(apiParams, null, 2));
      
      // 进度模拟
      const progressSteps = ['分析文本结构', '实体识别', '关系抽取', '置信度计算', '结果整合'];
      for (let i = 0; i < progressSteps.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        setProgress(((i + 1) / progressSteps.length) * 100);
      }

      // 模拟提取结果
      const mockResult: ExtractionResult = {
        entities: [
          {
            id: 'ent_1',
            text: 'SuperCharger Model SC-5000',
            type: 'PRODUCT',
            confidence: 0.95,
            start: 0,
            end: 25
          },
          {
            id: 'ent_2',
            text: 'ChargeCorp Technologies',
            type: 'ORG',
            confidence: 0.92,
            start: 29,
            end: 52
          },
          {
            id: 'ent_3',
            text: 'EN 55011:2016',
            type: 'STANDARD',
            confidence: 0.98,
            start: 65,
            end: 79
          },
          {
            id: 'ent_4',
            text: '2024年3月',
            type: 'DATE',
            confidence: 0.88,
            start: 95,
            end: 102
          }
        ],
        relations: [
          {
            id: 'rel_1',
            subject: 'ent_1',
            predicate: 'manufactured_by',
            object: 'ent_2',
            confidence: 0.94,
            evidence: 'SuperCharger Model SC-5000 由 ChargeCorp Technologies 制造'
          },
          {
            id: 'rel_2',
            subject: 'ent_1',
            predicate: 'complies_with',
            object: 'ent_3',
            confidence: 0.91,
            evidence: '符合 EN 55011:2016 标准'
          },
          {
            id: 'rel_3',
            subject: 'ent_1',
            predicate: 'tested_on',
            object: 'ent_4',
            confidence: 0.85,
            evidence: '在 2024年3月 通过了EMC测试'
          }
        ],
        temporal_contexts: [
          {
            text: '2024年3月',
            normalized: '2024-03',
            confidence: 0.95
          }
        ]
      };

      setResult(mockResult);
      
    } catch (err) {
      setError('提取过程中发生错误: ' + (err as Error).message);
    } finally {
      setIsExtracting(false);
    }
  };

  const entityColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80
    },
    {
      title: '文本',
      dataIndex: 'text',
      key: 'text'
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => <Tag color="blue">{type}</Tag>
    },
    {
      title: '置信度',
      dataIndex: 'confidence',
      key: 'confidence',
      render: (confidence: number) => (
        <Progress 
          percent={Math.round(confidence * 100)} 
          size="small"
          status={confidence > 0.9 ? 'success' : confidence > 0.7 ? 'normal' : 'exception'}
        />
      )
    },
    {
      title: '位置',
      key: 'position',
      render: (record: any) => `${record.start}-${record.end}`
    }
  ];

  const relationColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80
    },
    {
      title: '主体',
      dataIndex: 'subject',
      key: 'subject'
    },
    {
      title: '关系',
      dataIndex: 'predicate',
      key: 'predicate',
      render: (predicate: string) => <Tag color="green">{predicate}</Tag>
    },
    {
      title: '客体',
      dataIndex: 'object',
      key: 'object'
    },
    {
      title: '置信度',
      dataIndex: 'confidence',
      key: 'confidence',
      render: (confidence: number) => `${Math.round(confidence * 100)}%`
    },
    {
      title: '证据',
      dataIndex: 'evidence',
      key: 'evidence',
      ellipsis: true
    }
  ];

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: '0 auto' }}>
      <Card>
        <Title level={2}>
          <Space>
            <ApiOutlined />
            DeepSeek 深度关系提取
          </Space>
        </Title>
        
        {/* 文件选择器 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col span={24}>
            <FileSelector
              value={selectedFileIds}
              onChange={setSelectedFileIds}
              multiple={false}
              title="选择分析文件（可选）"
              placeholder="选择文件自动填充分析内容，或手动输入文本"
              allowedTypes={['pdf', 'docx', 'txt', 'md', 'html']}
              maxCount={1}
            />
          </Col>
        </Row>

        <Form
          form={form}
          layout="vertical"
          onFinish={performExtraction}
          initialValues={defaultParams}
        >
          <Form.Item
            label="输入文本"
            name="text"
            rules={[{ required: true, message: '请输入要分析的文本' }]}
          >
            <TextArea
              rows={6}
              placeholder="请输入要进行实体关系提取的文本内容..."
              style={{ fontFamily: 'monospace' }}
            />
          </Form.Item>

          <Form.Item
            label="上下文文本（可选）"
            name="context"
          >
            <TextArea
              rows={3}
              placeholder="提供相邻文本块以增强上下文连贯性..."
              style={{ fontFamily: 'monospace' }}
            />
          </Form.Item>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 16 }}>
            <Form.Item
              label="实体类型"
              name="entity_types"
            >
              <Select
                mode="multiple"
                placeholder="选择要识别的实体类型"
                style={{ width: '100%' }}
              >
                <Option value="PERSON">人物</Option>
                <Option value="ORG">组织机构</Option>
                <Option value="EVENT">事件</Option>
                <Option value="PRODUCT">产品</Option>
                <Option value="LOCATION">地点</Option>
                <Option value="DATE">日期</Option>
                <Option value="STANDARD">标准</Option>
                <Option value="EQUIPMENT">设备</Option>
              </Select>
            </Form.Item>

            <Form.Item
              label="关系深度"
              name="relation_depth"
            >
              <Select>
                <Option value={1}>1层关系</Option>
                <Option value={2}>2层关系（推荐）</Option>
                <Option value={3}>3层关系</Option>
              </Select>
            </Form.Item>

            <Form.Item
              label="置信度阈值"
              name="confidence_threshold"
            >
              <Select>
                <Option value={0.5}>0.5 (宽松)</Option>
                <Option value={0.75}>0.75 (推荐)</Option>
                <Option value={0.9}>0.9 (严格)</Option>
              </Select>
            </Form.Item>

            <Form.Item
              label="指代消解"
              name="coreference_resolution"
            >
              <Select>
                <Option value="basic">基础</Option>
                <Option value="enhanced">增强（推荐）</Option>
                <Option value="advanced">高级</Option>
              </Select>
            </Form.Item>
          </div>

          <Form.Item name="temporal_parsing" valuePropName="checked">
            <Switch /> 启用时间上下文解析
          </Form.Item>

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={isExtracting}
              icon={<BranchesOutlined />}
              size="large"
            >
              开始提取
            </Button>
          </Form.Item>
        </Form>

        {isExtracting && (
          <Card size="small" style={{ marginTop: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text>正在进行深度关系提取...</Text>
              <Progress percent={progress} status="active" />
            </Space>
          </Card>
        )}

        {error && (
          <Alert
            message="提取失败"
            description={error}
            type="error"
            style={{ marginTop: 16 }}
          />
        )}

        {result && (
          <div style={{ marginTop: 24 }}>
            <Card title="提取结果" size="small">
              <div style={{ marginBottom: 16 }}>
                <Space size="large">
                  <div>
                    <Text type="secondary">识别实体: </Text>
                    <Text strong>{result.entities.length}</Text>
                  </div>
                  <div>
                    <Text type="secondary">提取关系: </Text>
                    <Text strong>{result.relations.length}</Text>
                  </div>
                  <div>
                    <Text type="secondary">时间上下文: </Text>
                    <Text strong>{result.temporal_contexts.length}</Text>
                  </div>
                </Space>
              </div>

              <Card title="识别的实体" size="small" style={{ marginBottom: 16 }}>
                <Table
                  dataSource={result.entities}
                  columns={entityColumns}
                  size="small"
                  pagination={false}
                />
              </Card>

              <Card title="提取的关系" size="small" style={{ marginBottom: 16 }}>
                <Table
                  dataSource={result.relations}
                  columns={relationColumns}
                  size="small"
                  pagination={false}
                />
              </Card>

              {result.temporal_contexts.length > 0 && (
                <Card title="时间上下文" size="small">
                  {result.temporal_contexts.map((context, index) => (
                    <div key={index} style={{ marginBottom: 8 }}>
                      <Space>
                        <Tag color="purple">{context.text}</Tag>
                        <Text code>{context.normalized}</Text>
                        <Text type="secondary">({Math.round(context.confidence * 100)}%)</Text>
                      </Space>
                    </div>
                  ))}
                </Card>
              )}
            </Card>
          </div>
        )}
      </Card>
    </div>
  );
};

export default DeepSeekExtractor;