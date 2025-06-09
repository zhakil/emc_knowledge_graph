import React, { useEffect } from 'react';
import { Box, CircularProgress, Alert, Typography } from '@mui/material';
import GraphVisualization from './GraphVisualization'; // Assuming this is the correct path
import { useGraphStore, useFilteredGraphData } from '../../stores/graphStore'; // Assuming this is the correct path

interface KnowledgeGraphViewerProps {
  height?: string | number;
}

const KnowledgeGraphViewer: React.FC<KnowledgeGraphViewerProps> = ({ height = 'calc(100vh - 250px)' }) => {
  const { fetchGraphData, isLoading, error, selectedNodes, selectedEdges, graphData } = useGraphStore();
  const filteredData = useFilteredGraphData(); // This hook provides filtered nodes and edges

  useEffect(() => {
    // Fetch initial graph data if it's not already loaded
    if (!graphData) {
      fetchGraphData();
    }
  }, [graphData, fetchGraphData]);

  if (isLoading && !graphData) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height={height}>
        <CircularProgress />
        <Typography ml={2}>Loading Knowledge Graph...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box height={height} p={2}>
        <Alert severity="error">Error loading graph: {error}</Alert>
      </Box>
    );
  }

  if (!filteredData || !filteredData.nodes || !filteredData.edges) {
    return (
      <Box height={height} p={2}>
        <Alert severity="info">No graph data to display. Try fetching data or adjusting filters.</Alert>
      </Box>
    );
  }

  const handleNodeClick = (node: any) => {
    console.log('Node clicked:', node);
    // Add any specific interaction logic here, e.g., using selectNode from graphStore
  };

  const handleEdgeClick = (edge: any) => {
    console.log('Edge clicked:', edge);
    // Add any specific interaction logic here
  };

  return (
    <Box sx={{ height, width: '100%' }}>
      <GraphVisualization
        data={{ nodes: filteredData.nodes, edges: filteredData.edges }}
        loading={isLoading}
        // error={error} // Error is handled above, but could be passed if GraphVisualization has its own error display
        onNodeClick={handleNodeClick}
        onEdgeClick={handleEdgeClick}
        height="100%"
        showMiniMap={true}
        showControls={true}
        interactive={true}
      />
      {/* Optionally, display information about selected nodes/edges or other controls here */}
      {/* <pre>Selected Nodes: {JSON.stringify(Array.from(selectedNodes), null, 2)}</pre> */}
      {/* <pre>Selected Edges: {JSON.stringify(Array.from(selectedEdges), null, 2)}</pre> */}
    </Box>
  );
};

export default KnowledgeGraphViewer;
