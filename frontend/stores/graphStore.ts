import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

// 图数据结构类型定义
interface GraphNode {
    id: string;
    label: string;
    type: 'emc_standard' | 'equipment' | 'test_method' | 'regulation' | 'frequency_range';
    properties: Record<string, any>;
    x?: number;
    y?: number;
    fx?: number | null;
    fy?: number | null;
}

interface GraphEdge {
    id: string;
    source: string;
    target: string;
    type: 'applies_to' | 'requires' | 'tests' | 'complies_with' | 'related_to';
    properties: Record<string, any>;
}

interface GraphData {
    nodes: GraphNode[];
    edges: GraphEdge[];
}

interface GraphQuery {
    id: string;
    name: string;
    description: string;
    cypher: string;
    parameters: Record<string, any>;
    createdAt: string;
    lastExecuted?: string;
    resultCount?: number;
}

interface GraphStatistics {
    totalNodes: number;
    totalEdges: number;
    nodeTypes: Record<string, number>;
    edgeTypes: Record<string, number>;
    lastUpdated: string;
}

interface AnalysisResult {
    id: string;
    type: 'compliance_check' | 'similarity_analysis' | 'path_finding' | 'centrality_analysis';
    title: string;
    description: string;
    data: any;
    visualization?: GraphData;
    createdAt: string;
}

interface GraphState {
    // 图数据
    graphData: GraphData | null;
    isLoading: boolean;
    error: string | null;

    // 查询管理
    savedQueries: GraphQuery[];
    queryHistory: GraphQuery[];
    currentQuery: string;
    queryResults: any[];

    // 选择状态
    selectedNodes: Set<string>;
    selectedEdges: Set<string>;
    highlightedNodes: Set<string>;

    // 过滤器
    nodeTypeFilter: Set<string>;
    edgeTypeFilter: Set<string>;
    searchFilter: string;

    // 可视化设置
    layoutType: 'force' | 'hierarchical' | 'circular' | 'grid';
    showLabels: boolean;
    showEdgeLabels: boolean;
    nodeSize: number;
    edgeWidth: number;

    // 统计信息
    statistics: GraphStatistics | null;

    // 分析结果
    analysisResults: AnalysisResult[];
    currentAnalysis: AnalysisResult | null;

    // 导入导出状态
    importProgress: number;
    exportProgress: number;
}

interface GraphActions {
    // 数据管理
    fetchGraphData: (query?: string) => Promise<void>;
    updateGraphData: (data: GraphData) => void;
    addNode: (node: GraphNode) => void;
    addEdge: (edge: GraphEdge) => void;
    removeNode: (nodeId: string) => void;
    removeEdge: (edgeId: string) => void;
    updateNode: (nodeId: string, updates: Partial<GraphNode>) => void;
    updateEdge: (edgeId: string, updates: Partial<GraphEdge>) => void;

    // 查询管理
    executeQuery: (query: string, parameters?: Record<string, any>) => Promise<any[]>;
    saveQuery: (query: Omit<GraphQuery, 'id' | 'createdAt'>) => void;
    deleteQuery: (queryId: string) => void;
    loadSavedQueries: () => Promise<void>;
    setCurrentQuery: (query: string) => void;

    // 选择管理
    selectNode: (nodeId: string, multiSelect?: boolean) => void;
    selectEdge: (edgeId: string, multiSelect?: boolean) => void;
    clearSelection: () => void;
    highlightNodes: (nodeIds: string[]) => void;
    clearHighlight: () => void;

    // 过滤器
    setNodeTypeFilter: (types: Set<string>) => void;
    setEdgeTypeFilter: (types: Set<string>) => void;
    setSearchFilter: (search: string) => void;
    clearFilters: () => void;

    // 可视化设置
    setLayoutType: (layout: GraphState['layoutType']) => void;
    toggleLabels: () => void;
    toggleEdgeLabels: () => void;
    setNodeSize: (size: number) => void;
    setEdgeWidth: (width: number) => void;

    // 统计信息
    fetchStatistics: () => Promise<void>;

    // 分析功能
    runComplianceCheck: (equipmentId: string, standardId: string) => Promise<void>;
    runSimilarityAnalysis: (nodeId: string) => Promise<void>;
    findShortestPath: (sourceId: string, targetId: string) => Promise<void>;
    runCentralityAnalysis: () => Promise<void>;
    setCurrentAnalysis: (analysis: AnalysisResult | null) => void;

    // 导入导出
    exportGraph: (format: 'json' | 'csv' | 'gexf') => Promise<string>;
    importGraph: (data: string, format: 'json' | 'csv') => Promise<void>;
    exportSubgraph: (nodeIds: string[]) => Promise<string>;

    // 错误处理
    setError: (error: string | null) => void;
    clearError: () => void;
}

type GraphStore = GraphState & GraphActions;

export const useGraphStore = create<GraphStore>()(
    devtools(
        persist(
            (set, get) => ({
                // 初始状态
                graphData: null,
                isLoading: false,
                error: null,
                savedQueries: [],
                queryHistory: [],
                currentQuery: '',
                queryResults: [],
                selectedNodes: new Set(),
                selectedEdges: new Set(),
                highlightedNodes: new Set(),
                nodeTypeFilter: new Set(),
                edgeTypeFilter: new Set(),
                searchFilter: '',
                layoutType: 'force',
                showLabels: true,
                showEdgeLabels: false,
                nodeSize: 10,
                edgeWidth: 2,
                statistics: null,
                analysisResults: [],
                currentAnalysis: null,
                importProgress: 0,
                exportProgress: 0,

                // 数据管理
                fetchGraphData: async (query?: string) => {
                    set({ isLoading: true, error: null });

                    try {
                        const url = query
                            ? `/api/graph/query?q=${encodeURIComponent(query)}`
                            : '/api/graph/data';

                        const response = await fetch(url);

                        if (!response.ok) {
                            throw new Error(`获取图数据失败: ${response.status}`);
                        }

                        const data = await response.json();
                        set({ graphData: data, isLoading: false });

                        // 同时更新统计信息
                        get().fetchStatistics();

                    } catch (error: any) {
                        set({ error: error.message, isLoading: false });
                    }
                },

                updateGraphData: (data: GraphData) => {
                    set({ graphData: data });
                },

                addNode: (node: GraphNode) => {
                    set((state) => {
                        if (!state.graphData) return state;

                        return {
                            graphData: {
                                ...state.graphData,
                                nodes: [...state.graphData.nodes, node],
                            },
                        };
                    });
                },

                addEdge: (edge: GraphEdge) => {
                    set((state) => {
                        if (!state.graphData) return state;

                        return {
                            graphData: {
                                ...state.graphData,
                                edges: [...state.graphData.edges, edge],
                            },
                        };
                    });
                },

                removeNode: (nodeId: string) => {
                    set((state) => {
                        if (!state.graphData) return state;

                        return {
                            graphData: {
                                nodes: state.graphData.nodes.filter(n => n.id !== nodeId),
                                edges: state.graphData.edges.filter(e => e.source !== nodeId && e.target !== nodeId),
                            },
                        };
                    });
                },

                removeEdge: (edgeId: string) => {
                    set((state) => {
                        if (!state.graphData) return state;

                        return {
                            graphData: {
                                ...state.graphData,
                                edges: state.graphData.edges.filter(e => e.id !== edgeId),
                            },
                        };
                    });
                },

                updateNode: (nodeId: string, updates: Partial<GraphNode>) => {
                    set((state) => {
                        if (!state.graphData) return state;

                        return {
                            graphData: {
                                ...state.graphData,
                                nodes: state.graphData.nodes.map(node =>
                                    node.id === nodeId ? { ...node, ...updates } : node
                                ),
                            },
                        };
                    });
                },

                updateEdge: (edgeId: string, updates: Partial<GraphEdge>) => {
                    set((state) => {
                        if (!state.graphData) return state;

                        return {
                            graphData: {
                                ...state.graphData,
                                edges: state.graphData.edges.map(edge =>
                                    edge.id === edgeId ? { ...edge, ...updates } : edge
                                ),
                            },
                        };
                    });
                },

                // 查询管理
                executeQuery: async (query: string, parameters?: Record<string, any>) => {
                    set({ isLoading: true, error: null });

                    try {
                        const response = await fetch('/api/graph/execute', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ query, parameters: parameters || {} }),
                        });

                        if (!response.ok) {
                            throw new Error(`查询执行失败: ${response.status}`);
                        }

                        const results = await response.json();

                        // 添加到历史记录
                        const historyQuery: GraphQuery = {
                            id: Date.now().toString(),
                            name: `查询 ${new Date().toLocaleString()}`,
                            description: query.substring(0, 100) + '...',
                            cypher: query,
                            parameters: parameters || {},
                            createdAt: new Date().toISOString(),
                            lastExecuted: new Date().toISOString(),
                            resultCount: results.length,
                        };

                        set((state) => ({
                            queryResults: results,
                            queryHistory: [historyQuery, ...state.queryHistory.slice(0, 19)], // 保留最近20条
                            isLoading: false,
                        }));

                        return results;

                    } catch (error: any) {
                        set({ error: error.message, isLoading: false });
                        return [];
                    }
                },

                saveQuery: (query: Omit<GraphQuery, 'id' | 'createdAt'>) => {
                    const fullQuery: GraphQuery = {
                        ...query,
                        id: Date.now().toString(),
                        createdAt: new Date().toISOString(),
                    };

                    set((state) => ({
                        savedQueries: [...state.savedQueries, fullQuery],
                    }));
                },

                deleteQuery: (queryId: string) => {
                    set((state) => ({
                        savedQueries: state.savedQueries.filter(q => q.id !== queryId),
                    }));
                },

                loadSavedQueries: async () => {
                    try {
                        const response = await fetch('/api/graph/queries');
                        if (response.ok) {
                            const queries = await response.json();
                            set({ savedQueries: queries });
                        }
                    } catch (error) {
                        console.error('加载保存的查询失败:', error);
                    }
                },

                setCurrentQuery: (query: string) => {
                    set({ currentQuery: query });
                },

                // 选择管理
                selectNode: (nodeId: string, multiSelect = false) => {
                    set((state) => {
                        const newSelection = new Set(multiSelect ? state.selectedNodes : []);

                        if (newSelection.has(nodeId)) {
                            newSelection.delete(nodeId);
                        } else {
                            newSelection.add(nodeId);
                        }

                        return { selectedNodes: newSelection };
                    });
                },

                selectEdge: (edgeId: string, multiSelect = false) => {
                    set((state) => {
                        const newSelection = new Set(multiSelect ? state.selectedEdges : []);

                        if (newSelection.has(edgeId)) {
                            newSelection.delete(edgeId);
                        } else {
                            newSelection.add(edgeId);
                        }

                        return { selectedEdges: newSelection };
                    });
                },

                clearSelection: () => {
                    set({ selectedNodes: new Set(), selectedEdges: new Set() });
                },

                highlightNodes: (nodeIds: string[]) => {
                    set({ highlightedNodes: new Set(nodeIds) });
                },

                clearHighlight: () => {
                    set({ highlightedNodes: new Set() });
                },

                // 过滤器
                setNodeTypeFilter: (types: Set<string>) => {
                    set({ nodeTypeFilter: types });
                },

                setEdgeTypeFilter: (types: Set<string>) => {
                    set({ edgeTypeFilter: types });
                },

                setSearchFilter: (search: string) => {
                    set({ searchFilter: search });
                },

                clearFilters: () => {
                    set({
                        nodeTypeFilter: new Set(),
                        edgeTypeFilter: new Set(),
                        searchFilter: '',
                    });
                },

                // 可视化设置
                setLayoutType: (layout: GraphState['layoutType']) => {
                    set({ layoutType: layout });
                },

                toggleLabels: () => {
                    set((state) => ({ showLabels: !state.showLabels }));
                },

                toggleEdgeLabels: () => {
                    set((state) => ({ showEdgeLabels: !state.showEdgeLabels }));
                },

                setNodeSize: (size: number) => {
                    set({ nodeSize: size });
                },

                setEdgeWidth: (width: number) => {
                    set({ edgeWidth: width });
                },

                // 统计信息
                fetchStatistics: async () => {
                    try {
                        const response = await fetch('/api/graph/statistics');
                        if (response.ok) {
                            const statistics = await response.json();
                            set({ statistics });
                        }
                    } catch (error) {
                        console.error('获取统计信息失败:', error);
                    }
                },

                // 分析功能
                runComplianceCheck: async (equipmentId: string, standardId: string) => {
                    set({ isLoading: true });

                    try {
                        const response = await fetch('/api/graph/analysis/compliance', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ equipmentId, standardId }),
                        });

                        if (!response.ok) {
                            throw new Error('合规性检查失败');
                        }

                        const result = await response.json();

                        const analysis: AnalysisResult = {
                            id: Date.now().toString(),
                            type: 'compliance_check',
                            title: `合规性检查: ${equipmentId} vs ${standardId}`,
                            description: `检查设备 ${equipmentId} 是否符合标准 ${standardId}`,
                            data: result,
                            visualization: result.graph,
                            createdAt: new Date().toISOString(),
                        };

                        set((state) => ({
                            analysisResults: [analysis, ...state.analysisResults],
                            currentAnalysis: analysis,
                            isLoading: false,
                        }));

                    } catch (error: any) {
                        set({ error: error.message, isLoading: false });
                    }
                },

                runSimilarityAnalysis: async (nodeId: string) => {
                    set({ isLoading: true });

                    try {
                        const response = await fetch('/api/graph/analysis/similarity', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ nodeId }),
                        });

                        if (!response.ok) {
                            throw new Error('相似性分析失败');
                        }

                        const result = await response.json();

                        const analysis: AnalysisResult = {
                            id: Date.now().toString(),
                            type: 'similarity_analysis',
                            title: `相似性分析: ${nodeId}`,
                            description: `查找与节点 ${nodeId} 相似的其他节点`,
                            data: result,
                            createdAt: new Date().toISOString(),
                        };

                        set((state) => ({
                            analysisResults: [analysis, ...state.analysisResults],
                            currentAnalysis: analysis,
                            isLoading: false,
                        }));

                    } catch (error: any) {
                        set({ error: error.message, isLoading: false });
                    }
                },

                findShortestPath: async (sourceId: string, targetId: string) => {
                    set({ isLoading: true });

                    try {
                        const response = await fetch('/api/graph/analysis/path', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ sourceId, targetId }),
                        });

                        if (!response.ok) {
                            throw new Error('路径查找失败');
                        }

                        const result = await response.json();

                        const analysis: AnalysisResult = {
                            id: Date.now().toString(),
                            type: 'path_finding',
                            title: `路径查找: ${sourceId} → ${targetId}`,
                            description: `查找从 ${sourceId} 到 ${targetId} 的最短路径`,
                            data: result,
                            visualization: result.graph,
                            createdAt: new Date().toISOString(),
                        };

                        set((state) => ({
                            analysisResults: [analysis, ...state.analysisResults],
                            currentAnalysis: analysis,
                            isLoading: false,
                        }));

                    } catch (error: any) {
                        set({ error: error.message, isLoading: false });
                    }
                },

                runCentralityAnalysis: async () => {
                    set({ isLoading: true });

                    try {
                        const response = await fetch('/api/graph/analysis/centrality', {
                            method: 'POST',
                        });

                        if (!response.ok) {
                            throw new Error('中心性分析失败');
                        }

                        const result = await response.json();

                        const analysis: AnalysisResult = {
                            id: Date.now().toString(),
                            type: 'centrality_analysis',
                            title: '中心性分析',
                            description: '计算图中各节点的中心性指标',
                            data: result,
                            createdAt: new Date().toISOString(),
                        };

                        set((state) => ({
                            analysisResults: [analysis, ...state.analysisResults],
                            currentAnalysis: analysis,
                            isLoading: false,
                        }));

                    } catch (error: any) {
                        set({ error: error.message, isLoading: false });
                    }
                },

                setCurrentAnalysis: (analysis: AnalysisResult | null) => {
                    set({ currentAnalysis: analysis });
                },

                // 导入导出
                exportGraph: async (format: 'json' | 'csv' | 'gexf') => {
                    const state = get();
                    if (!state.graphData) {
                        throw new Error('没有可导出的图数据');
                    }

                    set({ exportProgress: 0 });

                    try {
                        const response = await fetch('/api/graph/export', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                data: state.graphData,
                                format,
                            }),
                        });

                        if (!response.ok) {
                            throw new Error('导出失败');
                        }

                        const exportData = await response.text();
                        set({ exportProgress: 100 });

                        // 重置进度
                        setTimeout(() => set({ exportProgress: 0 }), 1000);

                        return exportData;

                    } catch (error: any) {
                        set({ error: error.message, exportProgress: 0 });
                        throw error;
                    }
                },

                importGraph: async (data: string, format: 'json' | 'csv') => {
                    set({ importProgress: 0, isLoading: true });

                    try {
                        const response = await fetch('/api/graph/import', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ data, format }),
                        });

                        if (!response.ok) {
                            throw new Error('导入失败');
                        }

                        const importedData = await response.json();

                        set({
                            graphData: importedData,
                            importProgress: 100,
                            isLoading: false,
                        });

                        // 重置进度
                        setTimeout(() => set({ importProgress: 0 }), 1000);

                        // 更新统计信息
                        get().fetchStatistics();

                    } catch (error: any) {
                        set({
                            error: error.message,
                            importProgress: 0,
                            isLoading: false,
                        });
                    }
                },

                exportSubgraph: async (nodeIds: string[]) => {
                    const state = get();
                    if (!state.graphData) {
                        throw new Error('没有可导出的图数据');
                    }

                    try {
                        const response = await fetch('/api/graph/export/subgraph', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ nodeIds }),
                        });

                        if (!response.ok) {
                            throw new Error('子图导出失败');
                        }

                        return await response.text();

                    } catch (error: any) {
                        set({ error: error.message });
                        throw error;
                    }
                },

                // 错误处理
                setError: (error: string | null) => {
                    set({ error });
                },

                clearError: () => {
                    set({ error: null });
                },
            }),
            {
                name: 'graph-store',
                partialize: (state) => ({
                    savedQueries: state.savedQueries,
                    layoutType: state.layoutType,
                    showLabels: state.showLabels,
                    showEdgeLabels: state.showEdgeLabels,
                    nodeSize: state.nodeSize,
                    edgeWidth: state.edgeWidth,
                }),
            }
        ),
        {
            name: 'graph-store',
        }
    )
);

// 选择器hooks
export const useFilteredGraphData = () => {
    return useGraphStore((state) => {
        if (!state.graphData) return null;

        let nodes = state.graphData.nodes;
        let edges = state.graphData.edges;

        // 应用节点类型过滤
        if (state.nodeTypeFilter.size > 0) {
            nodes = nodes.filter(node => state.nodeTypeFilter.has(node.type));
        }

        // 应用边类型过滤
        if (state.edgeTypeFilter.size > 0) {
            edges = edges.filter(edge => state.edgeTypeFilter.has(edge.type));
        }

        // 应用搜索过滤
        if (state.searchFilter) {
            const searchLower = state.searchFilter.toLowerCase();
            nodes = nodes.filter(node =>
                node.label.toLowerCase().includes(searchLower) ||
                Object.values(node.properties).some(value =>
                    String(value).toLowerCase().includes(searchLower)
                )
            );
        }

        // 过滤相关边
        const nodeIds = new Set(nodes.map(n => n.id));
        edges = edges.filter(edge =>
            nodeIds.has(edge.source) && nodeIds.has(edge.target)
        );

        return { nodes, edges };
    });
};

export const useGraphStatistics = () => {
    return useGraphStore((state) => state.statistics);
};

export const useSelectedElements = () => {
    return useGraphStore((state) => ({
        selectedNodes: state.selectedNodes,
        selectedEdges: state.selectedEdges,
        highlightedNodes: state.highlightedNodes,
    }));
};