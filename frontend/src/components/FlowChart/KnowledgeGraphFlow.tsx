import React, { useEffect, useRef, useState } from 'react';
import { Card, Button, Space, Tooltip, Tag, Progress, Typography } from 'antd';
import { 
  PlayCircleOutlined, 
  PauseCircleOutlined, 
  ReloadOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined,
  SyncOutlined
} from '@ant-design/icons';
import * as d3 from 'd3';
import './KnowledgeGraphFlow.css';

const { Title, Text } = Typography;

interface FlowNode {
  id: string;
  label: string;
  description: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress: number;
  x: number;
  y: number;
}

interface FlowEdge {
  source: string;
  target: string;
  label?: string;
}

const KnowledgeGraphFlow: React.FC = () => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [isAnimating, setIsAnimating] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [nodes, setNodes] = useState<FlowNode[]>([
    {
      id: 'A',
      label: '文件上传',
      description: '支持PDF、Word、图片、文本等多种格式文件上传',
      status: 'pending',
      progress: 0,
      x: 150,
      y: 100
    },
    {
      id: 'B',
      label: '多格式预处理',
      description: 'OCR识别、文本提取、格式标准化处理',
      status: 'pending',
      progress: 0,
      x: 150,
      y: 200
    },
    {
      id: 'C',
      label: '实体关系提取',
      description: '使用AI模型识别文本中的实体和关系',
      status: 'pending',
      progress: 0,
      x: 150,
      y: 300
    },
    {
      id: 'D',
      label: '动态知识校验',
      description: '基于领域知识库进行实体关系验证和优化',
      status: 'pending',
      progress: 0,
      x: 150,
      y: 400
    },
    {
      id: 'E',
      label: '智能YAML生成',
      description: '生成结构化的知识表示文件',
      status: 'pending',
      progress: 0,
      x: 400,
      y: 400
    },
    {
      id: 'F',
      label: '图谱构建优化',
      description: '构建知识图谱并进行拓扑优化',
      status: 'pending',
      progress: 0,
      x: 400,
      y: 300
    },
    {
      id: 'G',
      label: '反馈增强闭环',
      description: '基于用户反馈持续优化知识图谱质量',
      status: 'pending',
      progress: 0,
      x: 400,
      y: 200
    }
  ]);

  const edges: FlowEdge[] = [
    { source: 'A', target: 'B' },
    { source: 'B', target: 'C' },
    { source: 'C', target: 'D' },
    { source: 'D', target: 'E' },
    { source: 'E', target: 'F' },
    { source: 'F', target: 'G' },
    { source: 'G', target: 'A', label: '反馈优化' }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return '#d9d9d9';
      case 'processing': return '#1890ff';
      case 'completed': return '#52c41a';
      case 'error': return '#ff4d4f';
      default: return '#d9d9d9';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return '⏳';
      case 'processing': return '🔄';
      case 'completed': return '✅';
      case 'error': return '❌';
      default: return '⏳';
    }
  };

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    const width = 600;
    const height = 500;

    // 清空之前的内容
    svg.selectAll('*').remove();

    // 创建箭头标记
    const defs = svg.append('defs');
    
    defs.append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 8)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#666');

    // 绘制连线
    edges.forEach(edge => {
      const sourceNode = nodes.find(n => n.id === edge.source)!;
      const targetNode = nodes.find(n => n.id === edge.target)!;
      
      // 计算连线路径
      let path = `M ${sourceNode.x} ${sourceNode.y + 30}`;
      
      if (edge.label === '反馈优化') {
        // 反馈闭环的弧形路径
        const midX = (sourceNode.x + targetNode.x) / 2 + 100;
        const midY = (sourceNode.y + targetNode.y) / 2;
        path += ` Q ${midX} ${midY} ${targetNode.x + 50} ${targetNode.y}`;
      } else {
        // 直线连接
        path += ` L ${targetNode.x} ${targetNode.y - 30}`;
      }

      svg.append('path')
        .attr('d', path)
        .attr('stroke', '#666')
        .attr('stroke-width', 2)
        .attr('fill', 'none')
        .attr('marker-end', 'url(#arrowhead)')
        .style('opacity', 0.7);

      // 添加连线标签
      if (edge.label) {
        const midX = sourceNode.x + 80;
        const midY = sourceNode.y - 20;
        
        svg.append('text')
          .attr('x', midX)
          .attr('y', midY)
          .attr('text-anchor', 'middle')
          .attr('font-size', '12px')
          .attr('fill', '#666')
          .text(edge.label);
      }
    });

    // 绘制节点
    const nodeGroups = svg.selectAll('.node')
      .data(nodes)
      .enter()
      .append('g')
      .attr('class', 'node')
      .attr('transform', d => `translate(${d.x - 60}, ${d.y - 30})`);

    // 节点背景
    nodeGroups.append('rect')
      .attr('width', 120)
      .attr('height', 60)
      .attr('rx', 8)
      .attr('fill', d => getStatusColor(d.status))
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('filter', 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))');

    // 节点文本
    nodeGroups.append('text')
      .attr('x', 60)
      .attr('y', 25)
      .attr('text-anchor', 'middle')
      .attr('font-size', '12px')
      .attr('font-weight', 'bold')
      .attr('fill', '#333')
      .text(d => d.label);

    // 状态图标
    nodeGroups.append('text')
      .attr('x', 100)
      .attr('y', 15)
      .attr('text-anchor', 'middle')
      .attr('font-size', '16px')
      .text(d => getStatusIcon(d.status));

    // 进度条（仅在处理中时显示）
    nodeGroups.filter(d => d.status === 'processing')
      .append('rect')
      .attr('x', 10)
      .attr('y', 45)
      .attr('width', 100)
      .attr('height', 4)
      .attr('fill', '#f0f0f0')
      .attr('rx', 2);

    nodeGroups.filter(d => d.status === 'processing')
      .append('rect')
      .attr('x', 10)
      .attr('y', 45)
      .attr('width', d => d.progress)
      .attr('height', 4)
      .attr('fill', '#1890ff')
      .attr('rx', 2);

  }, [nodes]);

  const startAnimation = async () => {
    setIsAnimating(true);
    setCurrentStep(0);

    // 重置所有节点状态
    setNodes(prev => prev.map(node => ({
      ...node,
      status: 'pending' as const,
      progress: 0
    })));

    // 逐步处理每个节点
    for (let i = 0; i < nodes.length; i++) {
      setCurrentStep(i);
      
      // 设置当前节点为处理中
      setNodes(prev => prev.map((node, index) => 
        index === i ? { ...node, status: 'processing' as const } : node
      ));

      // 模拟进度
      for (let progress = 0; progress <= 100; progress += 10) {
        await new Promise(resolve => setTimeout(resolve, 100));
        setNodes(prev => prev.map((node, index) => 
          index === i ? { ...node, progress } : node
        ));
      }

      // 设置为完成状态
      setNodes(prev => prev.map((node, index) => 
        index === i ? { ...node, status: 'completed' as const, progress: 100 } : node
      ));

      await new Promise(resolve => setTimeout(resolve, 500));
    }

    setIsAnimating(false);
  };

  const stopAnimation = () => {
    setIsAnimating(false);
  };

  const resetAnimation = () => {
    setIsAnimating(false);
    setCurrentStep(0);
    setNodes(prev => prev.map(node => ({
      ...node,
      status: 'pending' as const,
      progress: 0
    })));
  };

  const getCurrentNode = () => {
    return nodes[currentStep];
  };

  return (
    <div className="knowledge-graph-flow">
      <Card 
        title={
          <Space>
            <Title level={4} style={{ margin: 0 }}>🧠 知识图谱构建流程</Title>
          </Space>
        }
        extra={
          <Space>
            <Button 
              type="primary" 
              icon={<PlayCircleOutlined />}
              onClick={startAnimation}
              disabled={isAnimating}
              loading={isAnimating}
            >
              开始演示
            </Button>
            <Button 
              icon={<PauseCircleOutlined />}
              onClick={stopAnimation}
              disabled={!isAnimating}
            >
              暂停
            </Button>
            <Button 
              icon={<ReloadOutlined />}
              onClick={resetAnimation}
            >
              重置
            </Button>
          </Space>
        }
      >
        <div style={{ display: 'flex', gap: 24 }}>
          {/* 流程图 */}
          <div style={{ flex: 1 }}>
            <svg 
              ref={svgRef} 
              width="600" 
              height="500" 
              style={{ 
                border: '1px solid #f0f0f0', 
                borderRadius: 8,
                background: '#fafafa'
              }}
            />
          </div>

          {/* 详情面板 */}
          <div style={{ width: 300 }}>
            <Card size="small" title="流程详情">
              {isAnimating && (
                <div style={{ marginBottom: 16 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                    <SyncOutlined spin />
                    <Text strong>当前步骤: {currentStep + 1}/{nodes.length}</Text>
                  </div>
                  <Progress 
                    percent={Math.round(((currentStep + 1) / nodes.length) * 100)} 
                    size="small"
                    status="active"
                  />
                </div>
              )}

              {nodes.map((node, index) => (
                <div 
                  key={node.id}
                  style={{ 
                    padding: 12,
                    margin: '8px 0',
                    background: index === currentStep && isAnimating ? '#e6f7ff' : '#fff',
                    border: '1px solid #f0f0f0',
                    borderRadius: 6,
                    borderLeft: `4px solid ${getStatusColor(node.status)}`
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                    <span style={{ fontSize: 16 }}>{getStatusIcon(node.status)}</span>
                    <Text strong>{node.label}</Text>
                    <Tag color={node.status === 'completed' ? 'success' : node.status === 'processing' ? 'processing' : 'default'}>
                      {node.status === 'pending' ? '等待' : 
                       node.status === 'processing' ? '处理中' :
                       node.status === 'completed' ? '完成' : '错误'}
                    </Tag>
                  </div>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {node.description}
                  </Text>
                  
                  {node.status === 'processing' && (
                    <div style={{ marginTop: 8 }}>
                      <Progress 
                        percent={node.progress} 
                        size="small" 
                        status="active"
                        showInfo={false}
                      />
                    </div>
                  )}
                </div>
              ))}
            </Card>

            <Card size="small" title="流程说明" style={{ marginTop: 16 }}>
              <Space direction="vertical" size="small">
                <div>
                  <InfoCircleOutlined style={{ color: '#1890ff', marginRight: 8 }} />
                  <Text>完整的知识图谱构建闭环流程</Text>
                </div>
                <div>
                  <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                  <Text>支持多种文件格式输入</Text>
                </div>
                <div>
                  <SyncOutlined style={{ color: '#722ed1', marginRight: 8 }} />
                  <Text>AI驱动的智能处理</Text>
                </div>
                <div>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    通过反馈机制持续优化知识图谱质量，形成自我完善的智能系统。
                  </Text>
                </div>
              </Space>
            </Card>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default KnowledgeGraphFlow;