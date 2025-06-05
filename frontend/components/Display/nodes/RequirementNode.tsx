import React from 'react';
import { NodeProps } from 'reactflow';

const RequirementNode: React.FC<NodeProps> = ({ data }) => (
  <div className="requirement-node border-2 border-purple-500 rounded-lg">
    <div className="node-header bg-purple-500 text-white p-2 rounded-t">
      <strong>{data.label}</strong>
    </div>
    <div className="node-body bg-white p-3 rounded-b">
      <div>Standard: {data.standard}</div>
      <div>Section: {data.section}</div>
    </div>
  </div>
);

export default RequirementNode;