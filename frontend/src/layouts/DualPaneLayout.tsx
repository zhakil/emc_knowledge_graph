import React, { useState, useEffect } from 'react';
import { Box, AppBar, Toolbar, Typography, IconButton } from '@mui/material';
import { Split } from '@geoffcox/react-splitter';
import { Settings, Help } from '@mui/icons-material';
import { UnifiedEditor } from '../components/editor/UnifiedEditor';
import { UnifiedDisplay } from '../components/display/UnifiedDisplay';
import { useDeepSeekStore } from '../stores/deepSeekStore';
import { useGraphStore } from '../stores/graphStore';

export const DualPaneLayout: React.FC = () => {
  const [splitSize, setSplitSize] = useState(50);
  const [aiResponse, setAiResponse] = useState(null);
  const [fileContent, setFileContent] = useState('');

  const { sendPrompt } = useDeepSeekStore();
  const { graphData, fetchGraphData } = useGraphStore();

  // 处理AI提示词执行
  const handlePromptExecute = async (prompt: string, config: any) => {
    try {
      const response = await sendPrompt(prompt, config);
      setAiResponse(response);
    } catch (error) {
      console.error('AI响应失败:', error);
    }
  };

  // 处理文件上传
  const handleFileUpload = async (files: File[]) => {
    try {
      const formData = new FormData();
      files.forEach(file => formData.append('files', file));
      
      const response = await fetch('/api/files/upload/batch', {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      
      // 显示文件内容或处理结果
      setFileContent(JSON.stringify(result, null, 2));
      
      // 刷新图数据
      await fetchGraphData();
    } catch (error) {
      console.error('文件上传失败:', error);
    }
  };

  // 处理配置保存
  const handleConfigSave = async (config: any) => {
    try {
      localStorage.setItem('emc_config', JSON.stringify(config));
      console.log('配置已保存');
    } catch (error) {
      console.error('配置保存失败:', error);
    }
  };

  useEffect(() => {
    // 初始化加载图数据
    fetchGraphData();
  }, [fetchGraphData]);

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* 顶部应用栏 */}
      <AppBar position="static" elevation={1}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            EMC知识图谱系统
          </Typography>
          <IconButton color="inherit">
            <Settings />
          </IconButton>
          <IconButton color="inherit">
            <Help />
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* 双窗格布局 */}
      <Box sx={{ flexGrow: 1, overflow: 'hidden' }}>
        <Split
          split="vertical"
          defaultSize={splitSize}
          onChange={setSplitSize}
          resizerStyle={{
            background: '#e0e0e0',
            width: '4px',
            cursor: 'col-resize'
          }}
        >
          {/* 左侧编辑窗口 */}
          <Box sx={{ height: '100%', p: 1 }}>
            <UnifiedEditor
              onPromptExecute={handlePromptExecute}
              onFileUpload={handleFileUpload}
              onConfigSave={handleConfigSave}
            />
          </Box>

          {/* 右侧显示窗口 */}
          <Box sx={{ height: '100%', p: 1 }}>
            <UnifiedDisplay
              aiResponse={aiResponse}
              graphData={graphData}
              fileContent={fileContent}
            />
          </Box>
        </Split>
      </Box>
    </Box>
  );
};