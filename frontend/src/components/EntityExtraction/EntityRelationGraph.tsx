import React, { useEffect, useRef, useState } from 'react';
import { Card, Button, Select, Slider, Switch, Tooltip, Tag } from 'antd';
import { FullscreenOutlined, DownloadOutlined, ReloadOutlined, SettingOutlined } from '@ant-design/icons';
import * as d3 from 'd3';
import './EntityRelationGraph.css';

const { Option } = Select;

interface GraphNode {
  id: string;
  name: string;
  type: string;
  confidence: number;
  properties: Record<string, any>;
  x?: number;
  y?: number;
  fx?: number;
  fy?: number;
}

interface GraphLink {
  source: string | GraphNode;
  target: string | GraphNode;
  type: string;
  confidence: number;
  properties: Record<string, any>;
}

interface EntityRelationGraphProps {
  entities: Array<{
    id: string;
    name: string;
    type: string;
    confidence: number;
    properties: Record<string, any>;
  }>;
  relationships: Array<{
    source: string;
    target: string;
    type: string;
    confidence: number;
    properties: Record<string, any>;
  }>;
  width?: number;
  height?: number;
}

const EntityRelationGraph: React.FC<EntityRelationGraphProps> = ({
  entities,
  relationships,
  width = 800,
  height = 600
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [simulation, setSimulation] = useState<d3.Simulation<GraphNode, GraphLink> | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [layoutType, setLayoutType] = useState<'force' | 'circular' | 'hierarchical'>('force');
  const [nodeSize, setNodeSize] = useState(20);
  const [linkDistance, setLinkDistance] = useState(100);
  const [showLabels, setShowLabels] = useState(true);
  const [showConfidence, setShowConfidence] = useState(true);
  const [filterByType, setFilterByType] = useState<string[]>([]);

  const nodeColors = {
    'Product': '#1890ff',
    'EMCStandard': '#52c41a',
    'Equipment': '#fa8c16',
    'FrequencyRange': '#eb2f96',
    'TestMethod': '#722ed1',
    'Manufacturer': '#13c2c2',
    'Document': '#faad14'
  };

  const linkColors = {
    'HAS_STANDARD': '#ff7875',
    'USES_EQUIPMENT': '#40a9ff',
    'TESTS_WITH': '#73d13d',
    'APPLIES_TO': '#ffadd2',
    'MANUFACTURED_BY': '#b37feb',
    'CONTAINS': '#5cdbd3'
  };

  // 处理数据
  const processData = () => {
    const nodes: GraphNode[] = entities
      .filter(entity => filterByType.length === 0 || filterByType.includes(entity.type))
      .map(entity => ({
        id: entity.id,
        name: entity.name,
        type: entity.type,
        confidence: entity.confidence,
        properties: entity.properties
      }));

    const nodeIds = new Set(nodes.map(n => n.id));
    const links: GraphLink[] = relationships
      .filter(rel => nodeIds.has(rel.source) && nodeIds.has(rel.target))
      .map(rel => ({
        source: rel.source,
        target: rel.target,
        type: rel.type,
        confidence: rel.confidence,
        properties: rel.properties
      }));

    return { nodes, links };
  };

  // 创建力导向图
  const createForceLayout = (nodes: GraphNode[], links: GraphLink[]) => {
    return d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id((d: any) => d.id).distance(linkDistance))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(nodeSize + 5));
  };

  // 创建圆形布局
  const createCircularLayout = (nodes: GraphNode[]) => {
    const radius = Math.min(width, height) * 0.3;
    const centerX = width / 2;
    const centerY = height / 2;

    nodes.forEach((node, i) => {
      const angle = (2 * Math.PI * i) / nodes.length;
      node.fx = centerX + radius * Math.cos(angle);
      node.fy = centerY + radius * Math.sin(angle);
    });

    return d3.forceSimulation(nodes)
      .force('link', d3.forceLink([]).id((d: any) => d.id))
      .force('charge', d3.forceManyBody().strength(0))
      .alphaTarget(0)
      .stop();
  };

  // 创建分层布局
  const createHierarchicalLayout = (nodes: GraphNode[], links: GraphLink[]) => {
    const typeGroups: { [key: string]: GraphNode[] } = {};
    nodes.forEach(node => {
      if (!typeGroups[node.type]) {
        typeGroups[node.type] = [];
      }
      typeGroups[node.type].push(node);
    });

    const types = Object.keys(typeGroups);
    const layerHeight = height / (types.length + 1);

    types.forEach((type, typeIndex) => {
      const nodesInType = typeGroups[type];
      const layerY = layerHeight * (typeIndex + 1);
      const nodeWidth = width / (nodesInType.length + 1);

      nodesInType.forEach((node, nodeIndex) => {
        node.fx = nodeWidth * (nodeIndex + 1);
        node.fy = layerY;
      });
    });

    return d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id((d: any) => d.id).distance(linkDistance))
      .force('charge', d3.forceManyBody().strength(-100))
      .alphaTarget(0)
      .stop();
  };

  // 渲染图形
  const renderGraph = () => {
    if (!svgRef.current) return;

    const { nodes, links } = processData();
    if (nodes.length === 0) return;

    // 清除之前的内容
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current);
    const g = svg.append('g');

    // 添加缩放功能
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

    // 创建模拟器
    let sim: d3.Simulation<GraphNode, GraphLink>;
    
    switch (layoutType) {
      case 'circular':
        sim = createCircularLayout(nodes);
        break;
      case 'hierarchical':
        sim = createHierarchicalLayout(nodes, links);
        break;
      default:
        sim = createForceLayout(nodes, links);
    }

    setSimulation(sim);

    // 添加定义（用于箭头标记）
    const defs = svg.append('defs');
    
    Object.keys(linkColors).forEach(linkType => {
      defs.append('marker')
        .attr('id', `arrow-${linkType}`)
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 15)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', linkColors[linkType as keyof typeof linkColors]);
    });

    // 绘制连线
    const link = g.append('g')
      .selectAll('line')
      .data(links)
      .enter().append('line')
      .attr('class', 'link')
      .attr('stroke', (d: GraphLink) => linkColors[d.type as keyof typeof linkColors] || '#999')
      .attr('stroke-width', (d: GraphLink) => showConfidence ? d.confidence * 4 + 1 : 2)
      .attr('stroke-opacity', 0.8)
      .attr('marker-end', (d: GraphLink) => `url(#arrow-${d.type})`);

    // 绘制节点
    const node = g.append('g')
      .selectAll('circle')
      .data(nodes)
      .enter().append('circle')
      .attr('class', 'node')
      .attr('r', (d: GraphNode) => {
        const baseSize = nodeSize;
        return showConfidence ? baseSize * (0.5 + d.confidence * 0.5) : baseSize;
      })
      .attr('fill', (d: GraphNode) => nodeColors[d.type as keyof typeof nodeColors] || '#999')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .call(d3.drag<SVGCircleElement, GraphNode>()
        .on('start', (event, d) => {
          if (!event.active) sim.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) sim.alphaTarget(0);
          d.fx = undefined;
          d.fy = undefined;
        }))
      .on('click', (event, d) => {
        setSelectedNode(d);
      })
      .on('mouseover', function(event, d) {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('r', (d.confidence ? nodeSize * (0.5 + d.confidence * 0.5) : nodeSize) * 1.2)
          .attr('stroke-width', 3);
      })
      .on('mouseout', function(event, d) {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('r', d.confidence ? nodeSize * (0.5 + d.confidence * 0.5) : nodeSize)
          .attr('stroke-width', 2);
      });

    // 添加节点标签
    if (showLabels) {
      const labels = g.append('g')
        .selectAll('text')
        .data(nodes)
        .enter().append('text')
        .attr('class', 'label')
        .attr('text-anchor', 'middle')
        .attr('dy', -nodeSize - 5)
        .style('font-size', '12px')
        .style('font-weight', 'bold')
        .style('fill', '#333')
        .style('pointer-events', 'none')
        .text((d: GraphNode) => d.name.length > 20 ? d.name.substring(0, 20) + '...' : d.name);

      // 添加置信度标签
      if (showConfidence) {
        g.append('g')
          .selectAll('text')
          .data(nodes)
          .enter().append('text')
          .attr('class', 'confidence-label')
          .attr('text-anchor', 'middle')
          .attr('dy', nodeSize + 15)
          .style('font-size', '10px')
          .style('fill', '#666')
          .style('pointer-events', 'none')
          .text((d: GraphNode) => `${(d.confidence * 100).toFixed(0)}%`);
      }
    }

    // 添加关系标签
    const linkLabels = g.append('g')
      .selectAll('text')
      .data(links)
      .enter().append('text')
      .attr('class', 'link-label')
      .attr('text-anchor', 'middle')
      .style('font-size', '10px')
      .style('fill', '#666')
      .style('pointer-events', 'none')
      .text((d: GraphLink) => d.type);

    // 更新位置
    sim.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node
        .attr('cx', (d: GraphNode) => d.x!)
        .attr('cy', (d: GraphNode) => d.y!);

      if (showLabels) {
        g.selectAll('.label')
          .attr('x', (d: any) => d.x)
          .attr('y', (d: any) => d.y);

        if (showConfidence) {
          g.selectAll('.confidence-label')
            .attr('x', (d: any) => d.x)
            .attr('y', (d: any) => d.y);
        }
      }

      linkLabels
        .attr('x', (d: any) => (d.source.x + d.target.x) / 2)
        .attr('y', (d: any) => (d.source.y + d.target.y) / 2);
    });
  };

  // 导出为PNG
  const exportToPNG = () => {
    if (!svgRef.current) return;

    const svgElement = svgRef.current;
    const serializer = new XMLSerializer();
    const svgString = serializer.serializeToString(svgElement);
    
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    
    const img = new Image();
    img.onload = () => {
      ctx?.drawImage(img, 0, 0);
      const link = document.createElement('a');
      link.download = 'entity-relation-graph.png';
      link.href = canvas.toDataURL();
      link.click();
    };
    
    img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgString)));
  };

  // 重置视图
  const resetView = () => {
    if (!svgRef.current) return;
    
    const svg = d3.select(svgRef.current);
    svg.transition()
      .duration(750)
      .call(
        (d3.zoom() as any).transform,
        d3.zoomIdentity
      );
  };

  // 获取所有实体类型
  const getAllEntityTypes = () => {
    return Array.from(new Set(entities.map(e => e.type)));
  };

  useEffect(() => {
    renderGraph();
  }, [entities, relationships, layoutType, nodeSize, linkDistance, showLabels, showConfidence, filterByType]);

  return (
    <div className="entity-relation-graph">
      <Card
        title="实体关系图谱"
        extra={
          <div className="graph-controls">
            <Select
              value={layoutType}
              onChange={setLayoutType}
              style={{ width: 120, marginRight: 8 }}
            >
              <Option value="force">力导向</Option>
              <Option value="circular">圆形</Option>
              <Option value="hierarchical">分层</Option>
            </Select>
            
            <Select
              mode="multiple"
              placeholder="过滤实体类型"
              value={filterByType}
              onChange={setFilterByType}
              style={{ width: 200, marginRight: 8 }}
            >
              {getAllEntityTypes().map(type => (
                <Option key={type} value={type}>{type}</Option>
              ))}
            </Select>
            
            <Tooltip title="重置视图">
              <Button icon={<ReloadOutlined />} onClick={resetView} style={{ marginRight: 8 }} />
            </Tooltip>
            
            <Tooltip title="导出图片">
              <Button icon={<DownloadOutlined />} onClick={exportToPNG} style={{ marginRight: 8 }} />
            </Tooltip>
            
            <Tooltip title="全屏">
              <Button icon={<FullscreenOutlined />} />
            </Tooltip>
          </div>
        }
      >
        <div className="graph-content">
          <div className="graph-sidebar">
            <div className="control-group">
              <label>节点大小</label>
              <Slider
                min={10}
                max={40}
                value={nodeSize}
                onChange={setNodeSize}
                style={{ marginBottom: 16 }}
              />
            </div>
            
            <div className="control-group">
              <label>连线距离</label>
              <Slider
                min={50}
                max={200}
                value={linkDistance}
                onChange={setLinkDistance}
                style={{ marginBottom: 16 }}
              />
            </div>
            
            <div className="control-group">
              <label>显示标签</label>
              <Switch
                checked={showLabels}
                onChange={setShowLabels}
                style={{ marginBottom: 16 }}
              />
            </div>
            
            <div className="control-group">
              <label>显示置信度</label>
              <Switch
                checked={showConfidence}
                onChange={setShowConfidence}
                style={{ marginBottom: 16 }}
              />
            </div>
            
            {/* 图例 */}
            <div className="legend">
              <h4>实体类型</h4>
              {Object.entries(nodeColors).map(([type, color]) => (
                <div key={type} className="legend-item">
                  <div 
                    className="legend-color" 
                    style={{ backgroundColor: color }}
                  />
                  <span>{type}</span>
                </div>
              ))}
              
              <h4 style={{ marginTop: 16 }}>关系类型</h4>
              {Object.entries(linkColors).map(([type, color]) => (
                <div key={type} className="legend-item">
                  <div 
                    className="legend-line" 
                    style={{ backgroundColor: color }}
                  />
                  <span>{type}</span>
                </div>
              ))}
            </div>
          </div>
          
          <div className="graph-main">
            <svg
              ref={svgRef}
              width={width}
              height={height}
              style={{ border: '1px solid #e8e8e8', borderRadius: 6, background: '#fafafa' }}
            />
          </div>
        </div>
        
        {selectedNode && (
          <div className="node-details">
            <Card size="small" title={`实体详情: ${selectedNode.name}`}>
              <div>
                <Tag color={nodeColors[selectedNode.type as keyof typeof nodeColors]}>
                  {selectedNode.type}
                </Tag>
                <span style={{ marginLeft: 8 }}>
                  置信度: {(selectedNode.confidence * 100).toFixed(1)}%
                </span>
              </div>
              
              {Object.keys(selectedNode.properties).length > 0 && (
                <div style={{ marginTop: 12 }}>
                  <h5>属性</h5>
                  {Object.entries(selectedNode.properties).map(([key, value]) => (
                    <div key={key} style={{ marginBottom: 4 }}>
                      <strong>{key}:</strong> {value}
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>
        )}
      </Card>
    </div>
  );
};

export default EntityRelationGraph;