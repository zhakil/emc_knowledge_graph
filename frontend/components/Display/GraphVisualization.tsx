import React, { useState, useCallback, useEffect, useMemo } from 'react';
import ReactFlow, {
    Controls,
    Background,
    MiniMap,
    Node,
    Edge,
    NodeTypes,
    Connection,
    addEdge,
    applyEdgeChanges,
    applyNodeChanges,
    NodeChange,
    EdgeChange,
    ReactFlowProvider,
    useReactFlow,
    Panel
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
    Box,
    Typography,
    Chip,
    IconButton,
    Tooltip,
    Paper,
    FormControl,
    Select,
    MenuItem,
    InputLabel,
    Switch,
    FormControlLabel,
    Slider,
    Button,
    Alert
} from '@mui/material';
import {
    ZoomIn,
    ZoomOut,
    CenterFocusStrong,
    FilterList,
    Save,
    Download,
    Refresh
} from '@mui/icons-material';

// 自定义节点组件
import EMCStandardNode from './nodes/EMCStandardNode';
import EquipmentNode from './nodes/EquipmentNode';
import TestResultNode from './nodes/TestResultNode';
import RequirementNode from './nodes/RequirementNode';
import ComplianceNode from './nodes/ComplianceNode';

// 类型定义
interface GraphData {
    nodes: Node[];
    edges: Edge[];
    metadata?: {
        totalNodes: number;
        totalEdges: number;
        categories: string[];
        lastUpdated: string;
    };
}

interface GraphVisualizationProps {
    data: GraphData;
    loading?: boolean;
    error?: string | null;
    onNodeClick?: (node: Node) => void;
    onEdgeClick?: (edge: Edge) => void;
    onSelectionChange?: (selectedNodes: Node[], selectedEdges: Edge[]) => void;
    onGraphUpdate?: (nodes: Node[], edges: Edge[]) => void;
    height?: string | number;
    showMiniMap?: boolean;
    showControls?: boolean;
    interactive?: boolean;
    theme?: 'light' | 'dark';
}

// 节点类型映射
const nodeTypes: NodeTypes = {
    emcStandard: EMCStandardNode,
    equipment: EquipmentNode,
    testResult: TestResultNode,
    requirement: RequirementNode,
    compliance: ComplianceNode
};

// 边样式配置
const edgeStyles = {
    default: { stroke: '#64748b', strokeWidth: 2 },
    highlighted: { stroke: '#3b82f6', strokeWidth: 3 },
    compliance: { stroke: '#10b981', strokeWidth: 2, strokeDasharray: '5,5' },
    violation: { stroke: '#ef4444', strokeWidth: 2, strokeDasharray: '5,5' },
    dependency: { stroke: '#f59e0b', strokeWidth: 2 }
};

// 节点类型颜色映射
const nodeColors = {
    emcStandard: '#8b5cf6',
    equipment: '#10b981',
    testResult: '#f59e0b',
    requirement: '#3b82f6',
    compliance: '#ef4444'
};

const GraphVisualization: React.FC<GraphVisualizationProps> = ({
    data,
    loading = false,
    error = null,
    onNodeClick,
    onEdgeClick,
    onSelectionChange,
    onGraphUpdate,
    height = '70vh',
    showMiniMap = true,
    showControls = true,
    interactive = true,
    theme = 'light'
}) => {
    // 状态管理
    const [nodes, setNodes] = useState<Node[]>([]);
    const [edges, setEdges] = useState<Edge[]>([]);
    const [selectedNodes, setSelectedNodes] = useState<Node[]>([]);
    const [selectedEdges, setSelectedEdges] = useState<Edge[]>([]);

    // 过滤和显示选项
    const [nodeTypeFilter, setNodeTypeFilter] = useState<string>('all');
    const [showLabels, setShowLabels] = useState(true);
    const [nodeSize, setNodeSize] = useState(50);
    const [layoutDirection, setLayoutDirection] = useState<'horizontal' | 'vertical'>('horizontal');

    // 初始化图数据
    useEffect(() => {
        if (data?.nodes && data?.edges) {
            // 应用节点大小设置
            const processedNodes = data.nodes.map(node => ({
                ...node,
                style: {
                    ...node.style,
                    width: nodeSize,
                    height: nodeSize,
                    backgroundColor: nodeColors[node.type as keyof typeof nodeColors] || '#94a3b8'
                }
            }));

            // 应用边样式
            const processedEdges = data.edges.map(edge => ({
                ...edge,
                style: edgeStyles[edge.type as keyof typeof edgeStyles] || edgeStyles.default,
                labelBgStyle: { fill: theme === 'dark' ? '#1f2937' : '#ffffff' }
            }));

            setNodes(processedNodes);
            setEdges(processedEdges);
        }
    }, [data, nodeSize, theme]);

    // 过滤节点
    const filteredNodes = useMemo(() => {
        if (nodeTypeFilter === 'all') return nodes;
        return nodes.filter(node => node.type === nodeTypeFilter);
    }, [nodes, nodeTypeFilter]);

    // 过滤对应的边
    const filteredEdges = useMemo(() => {
        const filteredNodeIds = new Set(filteredNodes.map(node => node.id));
        return edges.filter(edge =>
            filteredNodeIds.has(edge.source) && filteredNodeIds.has(edge.target)
        );
    }, [edges, filteredNodes]);

    // 节点变更处理
    const onNodesChange = useCallback(
        (changes: NodeChange[]) => {
            const updatedNodes = applyNodeChanges(changes, nodes);
            setNodes(updatedNodes);

            if (onGraphUpdate && interactive) {
                onGraphUpdate(updatedNodes, edges);
            }
        },
        [nodes, edges, onGraphUpdate, interactive]
    );

    // 边变更处理
    const onEdgesChange = useCallback(
        (changes: EdgeChange[]) => {
            const updatedEdges = applyEdgeChanges(changes, edges);
            setEdges(updatedEdges);

            if (onGraphUpdate && interactive) {
                onGraphUpdate(nodes, updatedEdges);
            }
        },
        [nodes, edges, onGraphUpdate, interactive]
    );

    // 连接处理
    const onConnect = useCallback(
        (connection: Connection) => {
            if (!interactive) return;

            const newEdge = {
                ...connection,
                id: `edge-${connection.source}-${connection.target}-${Date.now()}`,
                type: 'default',
                animated: true
            };

            const updatedEdges = addEdge(newEdge, edges);
            setEdges(updatedEdges);

            if (onGraphUpdate) {
                onGraphUpdate(nodes, updatedEdges);
            }
        },
        [edges, nodes, onGraphUpdate, interactive]
    );

    // 选择变更处理
    const handleSelectionChange = useCallback(
        ({ nodes: selectedNodes, edges: selectedEdges }) => {
            setSelectedNodes(selectedNodes);
            setSelectedEdges(selectedEdges);

            if (onSelectionChange) {
                onSelectionChange(selectedNodes, selectedEdges);
            }
        },
        [onSelectionChange]
    );

    // 节点点击处理
    const handleNodeClick = useCallback(
        (event: React.MouseEvent, node: Node) => {
            if (onNodeClick) {
                onNodeClick(node);
            }
        },
        [onNodeClick]
    );

    // 边点击处理
    const handleEdgeClick = useCallback(
        (event: React.MouseEvent, edge: Edge) => {
            if (onEdgeClick) {
                onEdgeClick(edge);
            }
        },
        [onEdgeClick]
    );

    // 自动布局
    const autoLayout = useCallback(() => {
        // 使用简单的力导向布局算法
        const layoutNodes = nodes.map((node, index) => {
            const angle = (index / nodes.length) * 2 * Math.PI;
            const radius = Math.min(300, nodes.length * 20);

            return {
                ...node,
                position: {
                    x: Math.cos(angle) * radius + 400,
                    y: Math.sin(angle) * radius + 300
                }
            };
        });

        setNodes(layoutNodes);
    }, [nodes]);

    // 重置视图
    const resetView = useCallback(() => {
        // ReactFlow实例方法，需要在组件内部调用
    }, []);

    // 导出图数据
    const exportGraph = useCallback(() => {
        const graphData = {
            nodes: nodes,
            edges: edges,
            metadata: {
                exportTime: new Date().toISOString(),
                nodeCount: nodes.length,
                edgeCount: edges.length
            }
        };

        const blob = new Blob([JSON.stringify(graphData, null, 2)], {
            type: 'application/json'
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `emc-knowledge-graph-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }, [nodes, edges]);

    // 获取统计信息
    const statistics = useMemo(() => {
        const nodeTypeCount = nodes.reduce((acc, node) => {
            acc[node.type || 'unknown'] = (acc[node.type || 'unknown'] || 0) + 1;
            return acc;
        }, {} as Record<string, number>);

        return {
            totalNodes: nodes.length,
            totalEdges: edges.length,
            selectedCount: selectedNodes.length + selectedEdges.length,
            nodeTypes: nodeTypeCount
        };
    }, [nodes, edges, selectedNodes, selectedEdges]);

    if (error) {
        return (
            <Alert severity="error" sx={{ m: 2 }}>
                {error}
            </Alert>
        );
    }

    return (
        <Box sx={{
            height,
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 2,
            overflow: 'hidden',
            position: 'relative',
            backgroundColor: theme === 'dark' ? '#1f2937' : '#ffffff'
        }}>
            {/* 控制面板 */}
            <Paper
                elevation={2}
                sx={{
                    position: 'absolute',
                    top: 10,
                    left: 10,
                    p: 2,
                    zIndex: 1000,
                    minWidth: 300,
                    maxWidth: 400
                }}
            >
                {/* 统计信息 */}
                <Box sx={{ mb: 2 }}>
                    <Typography variant="h6" gutterBottom>
                        知识图谱概览
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        <Chip label={`节点: ${statistics.totalNodes}`} size="small" />
                        <Chip label={`边: ${statistics.totalEdges}`} size="small" />
                        {statistics.selectedCount > 0 && (
                            <Chip
                                label={`已选: ${statistics.selectedCount}`}
                                size="small"
                                color="primary"
                            />
                        )}
                    </Box>
                </Box>

                {/* 过滤控制 */}
                <Box sx={{ mb: 2 }}>
                    <FormControl fullWidth size="small" sx={{ mb: 1 }}>
                        <InputLabel>节点类型过滤</InputLabel>
                        <Select
                            value={nodeTypeFilter}
                            label="节点类型过滤"
                            onChange={(e) => setNodeTypeFilter(e.target.value)}
                        >
                            <MenuItem value="all">全部类型</MenuItem>
                            <MenuItem value="emcStandard">EMC标准</MenuItem>
                            <MenuItem value="equipment">设备</MenuItem>
                            <MenuItem value="testResult">测试结果</MenuItem>
                            <MenuItem value="requirement">要求</MenuItem>
                            <MenuItem value="compliance">合规性</MenuItem>
                        </Select>
                    </FormControl>

                    <FormControlLabel
                        control={
                            <Switch
                                checked={showLabels}
                                onChange={(e) => setShowLabels(e.target.checked)}
                                size="small"
                            />
                        }
                        label="显示标签"
                    />
                </Box>

                {/* 节点大小控制 */}
                <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                        节点大小: {nodeSize}px
                    </Typography>
                    <Slider
                        value={nodeSize}
                        onChange={(_, value) => setNodeSize(value as number)}
                        min={30}
                        max={100}
                        step={10}
                        marks
                        size="small"
                    />
                </Box>

                {/* 操作按钮 */}
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Tooltip title="自动布局">
                        <IconButton size="small" onClick={autoLayout}>
                            <CenterFocusStrong />
                        </IconButton>
                    </Tooltip>
                    <Tooltip title="导出图数据">
                        <IconButton size="small" onClick={exportGraph}>
                            <Download />
                        </IconButton>
                    </Tooltip>
                    <Tooltip title="刷新">
                        <IconButton size="small" onClick={() => window.location.reload()}>
                            <Refresh />
                        </IconButton>
                    </Tooltip>
                </Box>
            </Paper>

            {/* ReactFlow图表 */}
            <ReactFlowProvider>
                <ReactFlow
                    nodes={filteredNodes}
                    edges={filteredEdges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    onSelectionChange={handleSelectionChange}
                    onNodeClick={handleNodeClick}
                    onEdgeClick={handleEdgeClick}
                    nodeTypes={nodeTypes}
                    fitView
                    attributionPosition="bottom-left"
                    nodesDraggable={interactive}
                    nodesConnectable={interactive}
                    elementsSelectable={interactive}
                    selectNodesOnDrag={interactive}
                    panOnDrag={true}
                    zoomOnScroll={true}
                    zoomOnPinch={true}
                    deleteKeyCode="Delete"
                    selectionKeyCode="Shift"
                    multiSelectionKeyCode="Ctrl"
                >
                    {showControls && <Controls />}
                    {showMiniMap && (
                        <MiniMap
                            position="bottom-right"
                            nodeColor={(node) => nodeColors[node.type as keyof typeof nodeColors] || '#94a3b8'}
                            nodeStrokeWidth={2}
                            zoomable
                            pannable
                        />
                    )}
                    <Background
                        color={theme === 'dark' ? '#374151' : '#e5e7eb'}
                        gap={16}
                    />

                    {/* 右上角信息面板 */}
                    <Panel position="top-right">
                        <Paper sx={{ p: 1, backgroundColor: 'rgba(255,255,255,0.9)' }}>
                            <Typography variant="caption" display="block">
                                显示: {filteredNodes.length}/{nodes.length} 节点
                            </Typography>
                            <Typography variant="caption" display="block">
                                连接: {filteredEdges.length}/{edges.length} 边
                            </Typography>
                        </Paper>
                    </Panel>
                </ReactFlow>
            </ReactFlowProvider>

            {/* 加载状态 */}
            {loading && (
                <Box
                    sx={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        backgroundColor: 'rgba(255,255,255,0.8)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 2000
                    }}
                >
                    <Typography>加载知识图谱中...</Typography>
                </Box>
            )}
        </Box>
    );
};

export default GraphVisualization;