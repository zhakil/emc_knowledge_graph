import React, { useState, useEffect } from 'react';
import {
  Box,
  CssBaseline,
  ThemeProvider,
  createTheme,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Container,
  Grid,
  Paper,
  Alert,
  Snackbar,
  Badge,
  Menu,
  MenuItem,
  Avatar,
  Tooltip,
  TextField,
  ListItemSecondaryAction,
  CircularProgress
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  Chat,
  AccountTree,
  Upload,
  Analytics,
  Settings,
  Brightness4,
  Brightness7,
  Notifications,
  AccountCircle,
  ExitToApp,
  Help,
  Delete as DeleteIcon
} from '@mui/icons-material';

// 组件导入
import DeepSeekPromptEditor from './components/Editor/DeepSeekPromptEditor';
import KnowledgeGraphViewer from './components/Display/KnowledgeGraphViewer';
import FileUploadZone from './components/Input/FileUploadZone';
import ResponseViewer from './components/Display/ResponseViewer';
import QueryResultViewer from './components/Display/QueryResultViewer';
import FileContentViewer from './components/Display/FileContentViewer';

// Store hooks
import { useDeepSeekStore } from './stores/deepSeekStore';
import { useGraphStore } from './stores/graphStore';
import { useFileStore } from './stores/fileStore'; // Added for FileUploadView

// 主题配置
const createAppTheme = (darkMode: boolean) => createTheme({
  palette: {
    mode: darkMode ? 'dark' : 'light',
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
      light: '#ff5983',
      dark: '#9a0036',
    },
    background: {
      default: darkMode ? '#121212' : '#f5f5f5',
      paper: darkMode ? '#1e1e1e' : '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
  },
  components: {
    MuiDrawer: {
      styleOverrides: {
        paper: {
          width: 240,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          zIndex: 1201,
        },
      },
    },
  },
});

// 应用视图枚举
enum AppView {
  DASHBOARD = 'dashboard',
  AI_CHAT = 'ai_chat',
  KNOWLEDGE_GRAPH = 'knowledge_graph',
  FILE_UPLOAD = 'file_upload',
  ANALYTICS = 'analytics',
  SETTINGS = 'settings'
}

// 菜单项配置
const menuItems = [
  { id: AppView.DASHBOARD, label: '控制台', icon: Dashboard },
  { id: AppView.AI_CHAT, label: 'AI 对话', icon: Chat },
  { id: AppView.KNOWLEDGE_GRAPH, label: '知识图谱', icon: AccountTree },
  { id: AppView.FILE_UPLOAD, label: '文件处理', icon: Upload },
  { id: AppView.ANALYTICS, label: '数据分析', icon: Analytics },
  { id: AppView.SETTINGS, label: '系统设置', icon: Settings },
];

const EMCKnowledgeGraphApp: React.FC = () => {
  // 状态管理
  const [currentView, setCurrentView] = useState<AppView>(AppView.DASHBOARD);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);
  const [notifications, setNotifications] = useState<string[]>([]);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  // Store状态
  const { error: deepSeekError, clearError: clearDeepSeekError } = useDeepSeekStore();
  const { error: graphError, clearError: clearGraphError } = useGraphStore();

  // 主题
  const theme = createAppTheme(darkMode);

  // 用户信息 (实际应用中从认证状态获取)
  const user = {
    name: 'EMC 工程师',
    email: 'engineer@emc.com',
    avatar: '/api/placeholder/40/40'
  };

  // 错误处理
  useEffect(() => {
    if (deepSeekError) {
      setSnackbarMessage(`DeepSeek 错误: ${deepSeekError}`);
      setSnackbarOpen(true);
      clearDeepSeekError();
    }
  }, [deepSeekError, clearDeepSeekError]);

  useEffect(() => {
    if (graphError) {
      setSnackbarMessage(`知识图谱错误: ${graphError}`);
      setSnackbarOpen(true);
      clearGraphError();
    }
  }, [graphError, clearGraphError]);

  // 切换侧边栏
  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // 切换主题
  const handleThemeToggle = () => {
    setDarkMode(!darkMode);
  };

  // 用户菜单处理
  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  // 注销处理
  const handleLogout = () => {
    // 实际应用中执行注销逻辑
    console.log('User logout');
    handleUserMenuClose();
  };

  // 渲染主内容区域
  const renderMainContent = () => {
    switch (currentView) {
      case AppView.DASHBOARD:
        return <DashboardView />;
      case AppView.AI_CHAT:
        return <AIChatView />;
      case AppView.KNOWLEDGE_GRAPH:
        return <KnowledgeGraphView />;
      case AppView.FILE_UPLOAD:
        return <FileUploadView />;
      case AppView.ANALYTICS:
        return <AnalyticsView />;
      case AppView.SETTINGS:
        return <SettingsView />;
      default:
        return <DashboardView />;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', height: '100vh' }}>
        {/* 应用栏 */}
        <AppBar position="fixed" sx={{ zIndex: theme.zIndex.drawer + 1 }}>
          <Toolbar>
            <IconButton
              color="inherit"
              edge="start"
              onClick={handleSidebarToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              EMC 知识图谱系统
            </Typography>

            {/* 通知图标 */}
            <Tooltip title="通知">
              <IconButton color="inherit">
                <Badge badgeContent={notifications.length} color="error">
                  <Notifications />
                </Badge>
              </IconButton>
            </Tooltip>

            {/* 主题切换 */}
            <Tooltip title="切换主题">
              <IconButton color="inherit" onClick={handleThemeToggle}>
                {darkMode ? <Brightness7 /> : <Brightness4 />}
              </IconButton>
            </Tooltip>

            {/* 帮助 */}
            <Tooltip title="帮助">
              <IconButton color="inherit">
                <Help />
              </IconButton>
            </Tooltip>

            {/* 用户菜单 */}
            <Tooltip title="用户菜单">
              <IconButton color="inherit" onClick={handleUserMenuOpen}>
                <Avatar 
                  src={user.avatar} 
                  alt={user.name}
                  sx={{ width: 32, height: 32 }}
                >
                  <AccountCircle />
                </Avatar>
              </IconButton>
            </Tooltip>
          </Toolbar>
        </AppBar>

        {/* 侧边栏 */}
        <Drawer
          variant="persistent"
          open={sidebarOpen}
          sx={{
            width: 240,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: 240,
              boxSizing: 'border-box',
            },
          }}
        >
          <Toolbar />
          <Box sx={{ overflow: 'auto' }}>
            <List>
              {menuItems.map((item) => {
                const Icon = item.icon;
                return (
                  <ListItem
                    button
                    key={item.id}
                    selected={currentView === item.id}
                    onClick={() => setCurrentView(item.id)}
                  >
                    <ListItemIcon>
                      <Icon />
                    </ListItemIcon>
                    <ListItemText primary={item.label} />
                  </ListItem>
                );
              })}
            </List>
            <Divider />
            {/* 系统状态指示器 */}
            <Box sx={{ p: 2 }}>
              <Typography variant="caption" color="textSecondary">
                系统状态
              </Typography>
              <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box
                  sx={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    backgroundColor: 'success.main'
                  }}
                />
                <Typography variant="caption">
                  在线
                </Typography>
              </Box>
            </Box>
          </Box>
        </Drawer>

        {/* 主内容区域 */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            transition: theme.transitions.create('margin', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.leavingScreen,
            }),
            marginLeft: sidebarOpen ? 0 : `-240px`,
          }}
        >
          <Toolbar />
          <Box sx={{ p: 3, height: 'calc(100vh - 64px)', overflow: 'auto' }}>
            {renderMainContent()}
          </Box>
        </Box>

        {/* 用户菜单 */}
        <Menu
          anchorEl={userMenuAnchor}
          open={Boolean(userMenuAnchor)}
          onClose={handleUserMenuClose}
        >
          <Box sx={{ p: 2, minWidth: 200 }}>
            <Typography variant="subtitle1">{user.name}</Typography>
            <Typography variant="body2" color="textSecondary">
              {user.email}
            </Typography>
          </Box>
          <Divider />
          <MenuItem onClick={handleUserMenuClose}>
            <ListItemIcon>
              <Settings fontSize="small" />
            </ListItemIcon>
            设置
          </MenuItem>
          <MenuItem onClick={handleLogout}>
            <ListItemIcon>
              <ExitToApp fontSize="small" />
            </ListItemIcon>
            注销
          </MenuItem>
        </Menu>

        {/* 全局通知 */}
        <Snackbar
          open={snackbarOpen}
          autoHideDuration={6000}
          onClose={() => setSnackbarOpen(false)}
          anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        >
          <Alert 
            onClose={() => setSnackbarOpen(false)} 
            severity="error"
            variant="filled"
          >
            {snackbarMessage}
          </Alert>
        </Snackbar>
      </Box>
    </ThemeProvider>
  );
};

// 各个视图组件
const DashboardView: React.FC = () => {
  const { usageStats } = useDeepSeekStore();
  const { statistics } = useGraphStore();

  return (
    <Container maxWidth="xl">
      <Typography variant="h4" gutterBottom>
        控制台
      </Typography>
      
      <Grid container spacing={3}>
        {/* 统计卡片 */}
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" color="primary">
              {statistics?.totalNodes || 0}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              知识节点
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" color="primary">
              {statistics?.totalEdges || 0}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              关系连接
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" color="primary">
              {usageStats?.requestsToday || 0}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              今日AI调用
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" color="primary">
              {usageStats?.tokensToday || 0}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              今日Token消耗
            </Typography>
          </Paper>
        </Grid>

        {/* 快速操作区域 */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              快速开始
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Box
                  sx={{
                    p: 2,
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    textAlign: 'center',
                    cursor: 'pointer',
                    '&:hover': { backgroundColor: 'action.hover' }
                  }}
                >
                  <Chat sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                  <Typography variant="subtitle2">AI 对话分析</Typography>
                  <Typography variant="body2" color="textSecondary">
                    使用DeepSeek分析EMC文档
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Box
                  sx={{
                    p: 2,
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    textAlign: 'center',
                    cursor: 'pointer',
                    '&:hover': { backgroundColor: 'action.hover' }
                  }}
                >
                  <Upload sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                  <Typography variant="subtitle2">文档上传</Typography>
                  <Typography variant="body2" color="textSecondary">
                    上传EMC标准或测试报告
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* 最近活动 */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              最近活动
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText
                  primary="处理了 EMC测试报告.pdf"
                  secondary="2分钟前"
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="创建了新的知识节点"
                  secondary="10分钟前"
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="AI分析了设备合规性"
                  secondary="1小时前"
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

const AIChatView: React.FC = () => (
  <Container maxWidth="xl">
    <Typography variant="h4" gutterBottom>
      AI 对话助手
    </Typography>
    <Grid container spacing={3} sx={{ height: 'calc(100vh - 160px)' }}>
      <Grid item xs={12} md={6}>
        <DeepSeekPromptEditor />
      </Grid>
      <Grid item xs={12} md={6}>
        <ResponseViewer result={null} />
      </Grid>
    </Grid>
  </Container>
);

const KnowledgeGraphView: React.FC = () => (
  <Container maxWidth="xl">
    <Typography variant="h4" gutterBottom>
      知识图谱
    </Typography>
    <KnowledgeGraphViewer height={window.innerHeight - 200} />
  </Container>
);

const FileUploadView: React.FC = () => {
  // This onFilesSelected is from the original FileUploadZone,
  // ensure it's still relevant or integrate its logic if needed.
  const handleFilesSelectedForUpload = (selectedFiles: File[]) => {
    console.log('Selected files for upload:', selectedFiles);
    // This is where you would typically trigger an upload to the backend.
    // After successful upload, you might want to call fetchFiles() from useFileStore
    // to refresh the list, or optimistically add to the store.
  };

  const {
    files,
    isLoading,
    error,
    fetchFiles,
    deleteFile,
    clearError, // Added for dismissing errors
  } = useFileStore();

  useEffect(() => {
    fetchFiles();
    // Cleanup function to clear any errors when the component unmounts or before re-fetching
    return () => {
      clearError();
    };
  }, [fetchFiles, clearError]);

  const handleDeleteFile = async (filename: string) => {
    // Basic confirmation, can be replaced with a modal dialog
    if (window.confirm(`Are you sure you want to delete ${filename}?`)) {
      await deleteFile(filename);
      // The file list will auto-refresh due to deleteFile calling fetchFiles in the store.
    }
  };

  // Function to format bytes into a readable string
  const formatBytes = (bytes: number, decimals = 2) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };

  return (
    <Container maxWidth="xl"> {/* Assuming Container is imported */}
      <Typography variant="h4" gutterBottom> {/* Assuming Typography is imported */}
        文件处理
      </Typography>
      <Grid container spacing={3}> {/* Assuming Grid is imported */}
        <Grid item xs={12} md={6}>
          {/* FileUploadZone is an existing component, ensure its props are correct */}
          <FileUploadZone onFilesSelected={handleFilesSelectedForUpload} />
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, minHeight: 400 }}> {/* Assuming Paper is imported */}
            <Typography variant="h6" gutterBottom>
              已上传文件
            </Typography>
            <Divider sx={{ mb: 2 }} /> {/* Assuming Divider is imported */}

            {isLoading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', p: 2 }}>
                <CircularProgress /> {/* Assuming CircularProgress is imported */}
                <Typography sx={{ ml: 2 }}>正在加载文件列表...</Typography>
              </Box>
            )}

            {error && (
              <Alert severity="error" onClose={() => clearError()}> {/* Assuming Alert is imported */}
                {error}
              </Alert>
            )}

            {!isLoading && !error && files.length === 0 && (
              <Typography variant="body2" color="textSecondary" sx={{ textAlign: 'center', mt: 2 }}>
                尚未上传任何文件。
              </Typography>
            )}

            {!isLoading && !error && files.length > 0 && (
              <List dense> {/* Assuming List is imported */}
                {files.map((file) => (
                  <ListItem key={file.name} divider> {/* Assuming ListItem is imported */}
                    <ListItemText {/* Assuming ListItemText is imported */}
                      primary={file.name}
                      secondary={`大小: ${formatBytes(file.size)} - 类型: ${file.type} - 修改日期: ${new Date(file.last_modified || 0).toLocaleDateString()}`}
                    />
                    <ListItemSecondaryAction> {/* Assuming ListItemSecondaryAction is imported */}
                      <IconButton edge="end" aria-label="delete" onClick={() => handleDeleteFile(file.name)}>
                        <DeleteIcon /> {/* Assuming DeleteIcon is imported from @mui/icons-material */}
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

const AnalyticsView: React.FC = () => (
  <Container maxWidth="xl">
    <Typography variant="h4" gutterBottom>
      数据分析
    </Typography>
    <QueryResultViewer 
      data={[]} 
      loading={false}
      error={null}
    />
  </Container>
);

const SettingsView: React.FC = () => {
  const {
    apiKey,
    baseUrl,
    config,
    setApiKey,
    setBaseUrl,
    updateConfig,
  } = useDeepSeekStore(); // Assuming useDeepSeekStore is already imported in App.tsx

  const handleConfigChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    let processedValue: string | number = value;
    if (name === 'maxTokens' || name === 'temperature') {
      processedValue = name === 'temperature' ? parseFloat(value) : parseInt(value, 10);
      if (isNaN(processedValue as number)) {
        // Handle invalid number input if necessary, or let the browser/store handle it
        // Revert to current store value if input is not a valid number
        processedValue = name === 'temperature' ? config.temperature : config.maxTokens;
      }
    }
    updateConfig({ ...config, [name]: processedValue });
  };

  const handleBaseUrlChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setBaseUrl(event.target.value);
  };

  const handleApiKeyChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setApiKey(event.target.value);
  };

  return (
    <Container maxWidth="xl"> {/* Assuming Container is imported */}
      <Typography variant="h4" gutterBottom> {/* Assuming Typography is imported */}
        系统设置
      </Typography>
      <Grid container spacing={3}> {/* Assuming Grid is imported */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}> {/* Assuming Paper is imported */}
            <Typography variant="h6" gutterBottom>
              DeepSeek API 配置
            </Typography>
            <TextField // Assuming TextField is imported
              label="API Key"
              value={apiKey}
              onChange={handleApiKeyChange}
              fullWidth
              margin="normal"
              type="password"
            />
            <TextField
              label="Base URL"
              value={baseUrl}
              onChange={handleBaseUrlChange}
              fullWidth
              margin="normal"
            />
            <TextField
              label="Model"
              name="model" // Name attribute for handleConfigChange
              value={config.model}
              onChange={handleConfigChange}
              fullWidth
              margin="normal"
            />
            <TextField
              label="Max Tokens"
              name="maxTokens" // Name attribute for handleConfigChange
              type="number"
              value={config.maxTokens}
              onChange={handleConfigChange}
              fullWidth
              margin="normal"
            />
            <TextField
              label="Temperature"
              name="temperature" // Name attribute for handleConfigChange
              type="number"
              value={config.temperature}
              onChange={handleConfigChange}
              inputProps={{ step: "0.1", min: "0", max: "2" }}
              fullWidth
              margin="normal"
            />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              图数据库设置
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Neo4j连接和知识图谱配置 (此处暂时为占位符)
            </Typography>
            {/* Future Neo4j settings can go here */}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default EMCKnowledgeGraphApp;