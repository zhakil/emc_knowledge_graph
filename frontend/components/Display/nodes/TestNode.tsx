import React from 'react';
import { NodeProps } from 'reactflow';

const TestNode: React.FC<NodeProps> = ({ data }) => (
  <div className="test-node">
    <div className="node-header bg-blue-500 text-white p-2 rounded-t">
      <strong>{data.label}</strong>
    </div>
    <div className="node-body bg-white p-3 rounded-b border">
      <div>Standard: {data.standard}</div>
      <div>Frequency: {data.frequencyRange}</div>
      <div>Status: {data.status}</div>
    </div>
  </div>
);

export default TestNode;