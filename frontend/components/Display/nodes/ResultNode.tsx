import React from 'react';
import { NodeProps } from 'reactflow';

const ResultNode: React.FC<NodeProps> = ({ data }) => {
  const statusColor = data.status === 'Pass' ? '#4caf50' : 
                     data.status === 'Fail' ? '#f44336' : '#ff9800';
                     
  return (
    <div className="result-node" style={{ border: `2px solid ${statusColor}` }}>
      <div 
        className="node-header" 
        style={{ 
          backgroundColor: statusColor, 
          color: 'white',
          padding: '8px',
          borderRadius: '4px 4px 0 0'
        }}
      >
        <strong>{data.label}</strong>
      </div>
      <div 
        className="node-body" 
        style={{ 
          backgroundColor: '#fff', 
          padding: '12px',
          borderRadius: '0 0 4px 4px'
        }}
      >
        <div>Test: {data.testName}</div>
        <div>Date: {data.date}</div>
        {data.issues && <div>Issues: {data.issues}</div>}
      </div>
    </div>
  );
};

export default ResultNode;