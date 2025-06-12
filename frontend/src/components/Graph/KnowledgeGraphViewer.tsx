import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Select,
  Input,
  Space,
  Tooltip,
  Drawer,
  Descriptions,
  Tag,
  Alert,
  Spin,
  message,
  Modal,
  Form,
  InputNumber,
  Switch,
  Typography,
  Divider
} from 'antd';
import {
  BranchesOutlined,
  SearchOutlined,
  FullscreenOutlined,
  SettingOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  NodeIndexOutlined,
  ShareAltOutlined,
  ZoomInOutlined,
  ZoomOutOutlined,
  ReloadOutlined,
  DownloadOutlined,
  SaveOutlined
} from '@ant-design/icons';
import * as d3 from 'd3';

const { Option } = Select;
const { Search } = Input;
const { Title, Text } = Typography;

interface GraphNode {
  id: string;
  label: string;
  type: 'Equipment' | 'Standard' | 'Test' | 'Requirement' | 'Result';
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
  properties: Record<string, any>;
  color?: string;
}

interface GraphLink {
  source: string;
  target: string;
  type: string;
  properties: Record<string, any>;
}

interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

const KnowledgeGraphViewer: React.FC = () => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [nodeType, setNodeType] = useState<string>('all');
  const [showAddNodeModal, setShowAddNodeModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [graphSettings, setGraphSettings] = useState({
    nodeSize: 8,
    linkDistance: 100,
    chargeStrength: -300,
    showLabels: true,
    enablePhysics: true
  });

  const nodeTypes = [
    { key: 'all', label: '全部节点', color: '#d4af37' },
    { key: 'Equipment', label: 'EMC设备', color: '#1890ff' },
    { key: 'Standard', label: 'EMC标准', color: '#52c41a' },
    { key: 'Test', label: 'EMC测试', color: '#faad14' },
    { key: 'Requirement', label: '技术要求', color: '#722ed1' },
    { key: 'Result', label: '测试结果', color: '#eb2f96' }
  ];

  const linkTypes = [
    { key: 'COMPLIES_WITH', label: '符合标准', color: '#52c41a' },
    { key: 'TESTED_BY', label: '测试于', color: '#1890ff' },
    { key: 'REQUIRES', label: '要求', color: '#faad14' },
    { key: 'PRODUCES', label: '产生', color: '#eb2f96' },
    { key: 'RELATED_TO', label: '相关', color: '#722ed1' }
  ];

  useEffect(() => {
    loadGraphData();
  }, []);

  useEffect(() => {
    if (graphData.nodes.length > 0) {
      renderGraph();
    }
  }, [graphData, graphSettings]);

  const loadGraphData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/knowledge-graph/nodes');
      if (response.ok) {
        const data = await response.json();
        setGraphData(data);
      } else {
        // 使用模拟数据
        const mockData: GraphData = {
          nodes: [
            {
              id: 'emc_device_1',
              label: 'EMC测试设备',
              type: 'Equipment',
              properties: { manufacturer: 'TestCorp', model: 'EMC-2000' }
            },
            {
              id: 'iec_61000_4_3',
              label: 'IEC 61000-4-3',
              type: 'Standard',
              properties: { category: 'EMC标准', frequency_range: '80 MHz - 1 GHz' }
            },
            {
              id: 'rf_immunity_test',
              label: '射频电磁场抗扰度测试',
              type: 'Test',
              properties: { test_level: 'Level 3', frequency: '80MHz-1GHz' }
            },
            {
              id: 'test_requirement_1',
              label: '测试要求A',
              type: 'Requirement',
              properties: { severity: 'high', compliance_level: 'mandatory' }
            },
            {
              id: 'test_result_1',
              label: '测试结果A',
              type: 'Result',
              properties: { status: 'pass', confidence: 0.95 }
            }
          ],
          links: [
            {
              source: 'emc_device_1',
              target: 'iec_61000_4_3',
              type: 'COMPLIES_WITH',
              properties: { compliance_level: 'Level 3' }
            },
            {
              source: 'emc_device_1',
              target: 'rf_immunity_test',
              type: 'TESTED_BY',
              properties: { test_date: '2025-06-11' }
            },
            {
              source: 'iec_61000_4_3',
              target: 'test_requirement_1',
              type: 'REQUIRES',
              properties: { section: '4.3.1' }
            },
            {
              source: 'rf_immunity_test',
              target: 'test_result_1',
              type: 'PRODUCES',
              properties: { timestamp: '2025-06-11 14:30:00' }
            }
          ]
        };
        setGraphData(mockData);
        message.info('使用模拟数据展示知识图谱');
      }
    } catch (error) {
      console.error('加载图数据失败:', error);
      message.error('加载图数据失败');
    } finally {
      setLoading(false);
    }
  };

  const renderGraph = useCallback(() => {
    if (!svgRef.current || graphData.nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = 800;
    const height = 600;

    svg.attr('width', width).attr('height', height);

    const g = svg.append('g');

    // 缩放功能
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

    // 力导向图模拟
    const simulation = d3.forceSimulation(graphData.nodes as any)
      .force('link', d3.forceLink(graphData.links)
        .id((d: any) => d.id)
        .distance(graphSettings.linkDistance))
      .force('charge', d3.forceManyBody().strength(graphSettings.chargeStrength))
      .force('center', d3.forceCenter(width / 2, height / 2));

    // 绘制连接线
    const link = g.append('g')
      .selectAll('line')
      .data(graphData.links)
      .enter().append('line')
      .attr('stroke', d => {
        const linkType = linkTypes.find(lt => lt.key === d.type);
        return linkType?.color || '#999';
      })
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', 2);

    // 绘制节点
    const node = g.append('g')
      .selectAll('circle')
      .data(graphData.nodes)
      .enter().append('circle')
      .attr('r', graphSettings.nodeSize)
      .attr('fill', d => {
        const nodeTypeInfo = nodeTypes.find(nt => nt.key === d.type);
        return nodeTypeInfo?.color || '#d4af37';
      })
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .call(d3.drag<SVGCircleElement, GraphNode>()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }));

    // 节点点击事件
    node.on('click', (event, d) => {
      setSelectedNode(d);
      setDrawerVisible(true);
    });

    // 节点标签
    if (graphSettings.showLabels) {
      const labels = g.append('g')
        .selectAll('text')
        .data(graphData.nodes)
        .enter().append('text')
        .text(d => d.label)
        .style('font-size', '12px')
        .style('font-weight', 'bold')
        .style('fill', '#2c3e50')
        .style('text-anchor', 'middle')
        .style('pointer-events', 'none');

      simulation.on('tick', () => {
        link
          .attr('x1', (d: any) => d.source.x)
          .attr('y1', (d: any) => d.source.y)
          .attr('x2', (d: any) => d.target.x)
          .attr('y2', (d: any) => d.target.y);

        node
          .attr('cx', (d: any) => d.x)
          .attr('cy', (d: any) => d.y);

        labels
          .attr('x', (d: any) => d.x)
          .attr('y', (d: any) => d.y + 20);
      });
    } else {
      simulation.on('tick', () => {
        link
          .attr('x1', (d: any) => d.source.x)
          .attr('y1', (d: any) => d.source.y)
          .attr('x2', (d: any) => d.target.x)
          .attr('y2', (d: any) => d.target.y);

        node
          .attr('cx', (d: any) => d.x)
          .attr('cy', (d: any) => d.y);
      });
    }

    if (!graphSettings.enablePhysics) {
      simulation.stop();
    }
  }, [graphData, graphSettings]);

  const handleSearch = (value: string) => {
    setSearchTerm(value);
    if (value) {
      const searchResults = graphData.nodes.filter(node => 
        node.label.toLowerCase().includes(value.toLowerCase()) ||
        node.type.toLowerCase().includes(value.toLowerCase())
      );
      
      if (searchResults.length > 0) {
        setSelectedNode(searchResults[0]);
        setDrawerVisible(true);
      } else {
        message.info('未找到匹配的节点');
      }
    }
  };

  const addNewNode = async (values: any) => {
    try {
      const newNode: GraphNode = {
        id: `node_${Date.now()}`,
        label: values.label,
        type: values.type,
        properties: values.properties || {},
        x: Math.random() * 800,
        y: Math.random() * 600
      };

      const response = await fetch('/api/knowledge-graph/nodes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newNode)
      });

      if (response.ok) {
        setGraphData(prev => ({
          ...prev,
          nodes: [...prev.nodes, newNode]
        }));
        message.success('节点创建成功');
        setShowAddNodeModal(false);
      } else {
        throw new Error('创建失败');
      }
    } catch (error) {
      console.error('创建节点失败:', error);
      message.error('创建节点失败');
    }
  };

  const exportGraph = () => {
    const dataStr = JSON.stringify(graphData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'knowledge_graph_export.json';
    link.click();
    URL.revokeObjectURL(url);
    message.success('图数据导出成功');
  };

  const filteredNodes = nodeType === 'all' 
    ? graphData.nodes 
    : graphData.nodes.filter(node => node.type === nodeType);

  return (
    <div className="fade-in-up">
      <Title level={2} style={{ textAlign: 'center', marginBottom: 24 }}>
        🕸️ EMC知识图谱可视化
      </Title>

      <Row gutter={[24, 24]}>
        <Col xs={24} lg={18}>
          <Card 
            title={
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Space>
                  <BranchesOutlined />
                  知识图谱视图
                  <Tag color="gold">{graphData.nodes.length} 节点</Tag>
                  <Tag color="blue">{graphData.links.length} 关系</Tag>
                </Space>
                <Space>
                  <Tooltip title="设置">
                    <Button 
                      icon={<SettingOutlined />}
                      onClick={() => setShowSettingsModal(true)}
                    />
                  </Tooltip>
                  <Tooltip title="全屏">
                    <Button icon={<FullscreenOutlined />} />
                  </Tooltip>
                  <Tooltip title="导出">
                    <Button 
                      icon={<DownloadOutlined />}
                      onClick={exportGraph}
                    />
                  </Tooltip>
                  <Tooltip title="刷新">
                    <Button 
                      icon={<ReloadOutlined />}
                      onClick={loadGraphData}
                      loading={loading}
                    />
                  </Tooltip>
                </Space>
              </div>
            }
            className="chinese-card"
          >
            {loading ? (
              <div style={{ textAlign: 'center', padding: '100px 0' }}>
                <Spin size="large" />
                <div style={{ marginTop: 16 }}>加载知识图谱中...</div>
              </div>
            ) : (
              <div style={{ position: 'relative' }}>
                <svg 
                  ref={svgRef}
                  style={{ 
                    width: '100%', 
                    height: '600px', 
                    border: '2px solid rgba(212, 175, 55, 0.2)',
                    borderRadius: '8px',
                    background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)'
                  }}
                />
                <div 
                  style={{
                    position: 'absolute',
                    top: 16,
                    left: 16,
                    zIndex: 10
                  }}
                >
                  <Space direction="vertical">
                    <Alert
                      message="使用说明"
                      description="拖拽移动节点，点击查看详情，滚轮缩放视图"
                      type="info"
                      showIcon
                      closable
                    />
                  </Space>
                </div>
              </div>
            )}
          </Card>
        </Col>

        <Col xs={24} lg={6}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Card title="🔍 图谱搜索" className="chinese-card">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Search
                  placeholder="搜索节点..."
                  onSearch={handleSearch}
                  className="chinese-input"
                />
                <Select
                  value={nodeType}
                  onChange={setNodeType}
                  style={{ width: '100%' }}
                  className="chinese-input"
                >
                  {nodeTypes.map(type => (
                    <Option key={type.key} value={type.key}>
                      <Space>
                        <div 
                          style={{
                            width: 12,
                            height: 12,
                            borderRadius: '50%',
                            backgroundColor: type.color
                          }}
                        />
                        {type.label}
                      </Space>
                    </Option>
                  ))}
                </Select>
                <Button 
                  type="primary"
                  block
                  icon={<PlusOutlined />}
                  onClick={() => setShowAddNodeModal(true)}
                  className="chinese-btn-primary"
                >
                  添加节点
                </Button>
              </Space>
            </Card>

            <Card title="📊 图谱统计" className="chinese-card">
              <Space direction="vertical" style={{ width: '100%' }}>
                {nodeTypes.slice(1).map(type => {
                  const count = graphData.nodes.filter(n => n.type === type.key).length;
                  return (
                    <div key={type.key} style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Space>
                        <div 
                          style={{
                            width: 12,
                            height: 12,
                            borderRadius: '50%',
                            backgroundColor: type.color
                          }}
                        />
                        {type.label}
                      </Space>
                      <Text strong>{count}</Text>
                    </div>
                  );
                })}
              </Space>
            </Card>
          </Space>
        </Col>
      </Row>

      {/* 节点详情抽屉 */}
      <Drawer
        title={selectedNode ? `节点详情: ${selectedNode.label}` : '节点详情'}
        placement="right"
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
        width={400}
      >
        {selectedNode && (
          <div>
            <Descriptions bordered column={1}>
              <Descriptions.Item label="节点ID">{selectedNode.id}</Descriptions.Item>
              <Descriptions.Item label="标签">{selectedNode.label}</Descriptions.Item>
              <Descriptions.Item label="类型">
                <Tag color={nodeTypes.find(t => t.key === selectedNode.type)?.color}>
                  {nodeTypes.find(t => t.key === selectedNode.type)?.label}
                </Tag>
              </Descriptions.Item>
            </Descriptions>

            <Divider>属性信息</Divider>
            {Object.entries(selectedNode.properties).map(([key, value]) => (
              <div key={key} style={{ marginBottom: 8 }}>
                <Text strong>{key}: </Text>
                <Text>{String(value)}</Text>
              </div>
            ))}

            <Divider>操作</Divider>
            <Space>
              <Button icon={<EditOutlined />}>编辑</Button>
              <Button icon={<ShareAltOutlined />}>关联</Button>
              <Button icon={<DeleteOutlined />} danger>删除</Button>
            </Space>
          </div>
        )}
      </Drawer>

      {/* 添加节点模态框 */}
      <Modal
        title="添加新节点"
        open={showAddNodeModal}
        onCancel={() => setShowAddNodeModal(false)}
        onOk={() => {
          // 表单提交逻辑
          setShowAddNodeModal(false);
        }}
        className="chinese-card"
      >
        <Form layout="vertical">
          <Form.Item name="label" label="节点标签" rules={[{ required: true }]}>
            <Input className="chinese-input" />
          </Form.Item>
          <Form.Item name="type" label="节点类型" rules={[{ required: true }]}>
            <Select className="chinese-input">
              {nodeTypes.slice(1).map(type => (
                <Option key={type.key} value={type.key}>{type.label}</Option>
              ))}
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* 图谱设置模态框 */}
      <Modal
        title="图谱显示设置"
        open={showSettingsModal}
        onCancel={() => setShowSettingsModal(false)}
        onOk={() => setShowSettingsModal(false)}
        className="chinese-card"
      >
        <Form layout="vertical" initialValues={graphSettings}>
          <Form.Item label="节点大小">
            <InputNumber 
              min={4} 
              max={20} 
              value={graphSettings.nodeSize}
              onChange={(value) => setGraphSettings(prev => ({ ...prev, nodeSize: value || 8 }))}
            />
          </Form.Item>
          <Form.Item label="连接距离">
            <InputNumber 
              min={50} 
              max={300} 
              value={graphSettings.linkDistance}
              onChange={(value) => setGraphSettings(prev => ({ ...prev, linkDistance: value || 100 }))}
            />
          </Form.Item>
          <Form.Item label="显示标签">
            <Switch 
              checked={graphSettings.showLabels}
              onChange={(checked) => setGraphSettings(prev => ({ ...prev, showLabels: checked }))}
            />
          </Form.Item>
          <Form.Item label="启用物理引擎">
            <Switch 
              checked={graphSettings.enablePhysics}
              onChange={(checked) => setGraphSettings(prev => ({ ...prev, enablePhysics: checked }))}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default KnowledgeGraphViewer;