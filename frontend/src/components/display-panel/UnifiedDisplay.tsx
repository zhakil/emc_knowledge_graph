import React, { useState } from 'react';
import { Box, Tabs, Tab, Paper } from '@mui/material';
import { KnowledgeGraphViewer } from './KnowledgeGraphViewer';
import { ResponseViewer } from './ResponseViewer';
import { QueryResultViewer } from './QueryResultViewer';
import { FileContentViewer } from './FileContentViewer';

interface UnifiedDisplayProps {
  aiResponse?: any;
  graphData?: any;
  queryResults?: any[];
  fileContent?: string;
}

export const UnifiedDisplay: React.FC<UnifiedDisplayProps> = ({
  aiResponse,
  graphData,
  queryResults,
  fileContent
}) => {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <Paper elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Tabs 
        value={activeTab} 
        onChange={(_, newValue) => setActiveTab(newValue)}
        sx={{ borderBottom: 1, borderColor: 'divider' }}
      >
        <Tab label="知识图谱" />
        <Tab label="AI响应" />
        <Tab label="查询结果" />
        <Tab label="文件内容" />
      </Tabs>

      <Box sx={{ flexGrow: 1, overflow: 'hidden' }}>
        {activeTab === 0 && (
          <KnowledgeGraphViewer 
            data={graphData} 
            height="100%" 
            interactive={true}
          />
        )}
        {activeTab === 1 && (
          <ResponseViewer result={aiResponse} />
        )}
        {activeTab === 2 && (
          <QueryResultViewer data={queryResults || []} />
        )}
        {activeTab === 3 && fileContent && (
          <FileContentViewer 
            content={fileContent}
            language="json"
            filename="imported_file"
          />
        )}
      </Box>
    </Paper>
  );
};