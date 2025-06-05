import React from 'react';
import { NodeProps } from 'reactflow';

const EquipmentNode: React.FC<NodeProps> = ({ data }) => (
  <div className="equipment-node border-2 border-green-500 rounded-lg">
    <div className="node-header bg-green-500 text-white p-2 rounded-t">
      <strong>{data.label}</strong>
    </div>
    <div className="node-body bg-white p-3 rounded-b">
      <div>Model: {data.model}</div>
      <div>Calibration: {data.calibrationDate}</div>
    </div>
  </div>
);

export default EquipmentNode;