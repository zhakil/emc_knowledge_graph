import React, { useState, useCallback } from 'react';
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
  ReactFlowProvider
} from 'reactflow';
import 'reactflow/dist/style.css';
import { TestDependency } from '../../types/TestTypes';

// Custom node types
import TestNode from './nodes/TestNode';
import EquipmentNode from './nodes/EquipmentNode';
import RequirementNode from './nodes/RequirementNode';

// Node type definitions
const nodeTypes: NodeTypes = {
  test: TestNode,
  equipment: EquipmentNode,
  requirement: RequirementNode
};

interface EntityRelationViewerProps {
  initialNodes?: Node[];
  initialEdges?: Edge[];
  onSelectionChange?: (selectedNodes: Node[], selectedEdges: Edge[]) => void;
}

const EntityRelationViewer: React.FC<EntityRelationViewerProps> = ({
  initialNodes = [],
  initialEdges = [],
  onSelectionChange
}) => {
  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>(initialEdges);

  // Handle node changes (drag, position updates)
  const onNodesChange = useCallback(
    (changes: NodeChange[]) => 
      setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );

  // Handle edge changes
  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => 
      setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );

  // Create connections between nodes
  const onConnect = useCallback(
    (connection: Connection) => 
      setEdges((eds) => addEdge({ ...connection, animated: true }, eds)),
    []
  );

  // Track selection changes
  const onSelectionChangeHandler = useCallback(
    ({ nodes: selectedNodes, edges: selectedEdges }) => {
      if (onSelectionChange) {
        onSelectionChange(selectedNodes, selectedEdges);
      }
    },
    [onSelectionChange]
  );

  return (
    <div className="entity-relation-viewer" style={{ height: '600px', width: '100%' }}>
      <ReactFlowProvider>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onSelectionChange={onSelectionChangeHandler}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-left"
        >
          <Controls />
          <MiniMap position="bottom-right" zoomable pannable />
          <Background color="#f0f2f5" gap={16} />
        </ReactFlow>
      </ReactFlowProvider>
    </div>
  );
};

export default EntityRelationViewer;