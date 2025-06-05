import React, { useState, useCallback } from 'react';
import { Box, Grid, Paper, Tabs, Tab } from '@mui/material';
import { DeepSeekPromptEditor } from './DeepSeekPromptEditor';
import { FileUploadZone } from './FileUploadZone';
import { ConfigEditor } from './ConfigEditor';

interface UnifiedEditorProps {
  onPromptExecute: (prompt: string, config: any) => Promise<void>;
  onFileUpload: (files: File[]) => Promise<void>;
  onConfigSave: (config: any) => Promise<void>;
}

export const UnifiedEditor: React.FC<UnifiedEditorProps> = ({
  onPromptExecute,
  onFileUpload,
  onConfigSave
}) => {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <Paper elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Tabs 
        value={activeTab} 
        onChange={(_, newValue) => setActiveTab(newValue)}
        sx={{ borderBottom: 1, borderColor: 'divider' }}
      >
        <Tab label="AI提示词编辑" />
        <Tab label="文件导入" />
        <Tab label="系统配置" />
      </Tabs>

      <Box sx={{ flexGrow: 1, p: 2 }}>
        {activeTab === 0 && (
          <DeepSeekPromptEditor onExecute={onPromptExecute} />
        )}
        {activeTab === 1 && (
          <FileUploadZone 
            onFilesSelected={onFileUpload}
            acceptedFormats={['.pdf', '.csv', '.xlsx', '.json', '.xml']}
            maxSizeMB={100}
          />
        )}
        {activeTab === 2 && (
          <ConfigEditor onSave={onConfigSave} />
        )}
      </Box>
    </Paper>
  );
};