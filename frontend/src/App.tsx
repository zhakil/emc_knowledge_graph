import React, { useState } from 'react';
import { ConfigProvider, Layout, Menu, theme, FloatButton } from 'antd';
import {
  CloudUploadOutlined,
  FileTextOutlined,
  SettingOutlined,
  HomeOutlined,
  BranchesOutlined,
  BookOutlined
} from '@ant-design/icons';
import './styles/ChineseTheme.css';

// Import our new components
import APISettingsModal from './components/Settings/APISettingsModal';
import FileManager from './components/FileManager/FileManager';
import KnowledgeGraphViewer from './components/Graph/KnowledgeGraphViewer';
import ObsidianMarkdownEditor from './components/editor/ObsidianMarkdownEditor';
import FileUploadArea from './components/Upload/FileUploadArea';
import Dashboard from './components/Dashboard/Dashboard';

const { Header, Content, Sider } = Layout;

interface AppProps {}

const App: React.FC<AppProps> = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [selectedKey, setSelectedKey] = useState('dashboard');
  const [showAPISettings, setShowAPISettings] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);

  const menuItems = [
    {
      key: 'dashboard',
      icon: <HomeOutlined />,
      label: '系统概览',
    },
    {
      key: 'upload',
      icon: <CloudUploadOutlined />,
      label: '文件上传',
    },
    {
      key: 'files',
      icon: <FileTextOutlined />,
      label: '文件管理',
    },
    {
      key: 'knowledge-graph',
      icon: <BranchesOutlined />,
      label: '知识图谱',
    },
    {
      key: 'obsidian-editor',
      icon: <BookOutlined />,
      label: '知识库编辑器',
    },
  ];

  const renderContent = () => {
    switch (selectedKey) {
      case 'dashboard':
        return <Dashboard />;
      case 'upload':
        return <FileUploadArea />;
      case 'files':
        return <FileManager />;
      case 'knowledge-graph':
        return <KnowledgeGraphViewer />;
      case 'obsidian-editor':
        return <ObsidianMarkdownEditor />;
      default:
        return <Dashboard />;
    }
  };

  const chineseTheme = {
    algorithm: isDarkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
    token: {
      colorPrimary: '#d4af37', // 金黄色主色调
      colorBgContainer: isDarkMode ? '#1a1a1a' : '#fafafa',
      colorText: isDarkMode ? '#e8e8e8' : '#2c3e50',
      borderRadius: 8,
      fontFamily: '"Ma Shan Zheng", "SimSun", serif',
    },
    components: {
      Layout: {
        headerBg: isDarkMode ? '#2c3e50' : '#34495e',
        siderBg: isDarkMode ? '#2c3e50' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      },
      Menu: {
        itemBg: 'transparent',
        itemSelectedBg: 'rgba(212, 175, 55, 0.15)',
        itemHoverBg: 'rgba(212, 175, 55, 0.1)',
        itemSelectedColor: '#d4af37',
      },
    },
  };

  return (
    <ConfigProvider theme={chineseTheme}>
      <Layout className="chinese-layout" style={{ minHeight: '100vh' }}>
        {/* 侧边栏 */}
        <Sider 
          collapsible 
          collapsed={collapsed} 
          onCollapse={setCollapsed}
          width={240}
          className="chinese-sider"
        >
          <div className="logo-section">
            <div className="logo-text">
              {!collapsed ? '墨韵知识图谱' : '墨'}
            </div>
            <div className="logo-subtitle">
              {!collapsed && 'EMC Knowledge Graph'}
            </div>
          </div>
          
          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={[selectedKey]}
            items={menuItems}
            onSelect={({ key }) => setSelectedKey(key)}
            className="chinese-menu"
          />
        </Sider>

        <Layout>
          {/* 顶部导航 */}
          <Header className="chinese-header">
            <div className="header-title">
              <span className="title-main">电磁兼容知识图谱系统</span>
              <span className="title-sub">Electromagnetic Compatibility Knowledge Graph</span>
            </div>
            
            <div className="header-actions">
              <span 
                className="theme-switch"
                onClick={() => setIsDarkMode(!isDarkMode)}
              >
                {isDarkMode ? '☀️' : '🌙'}
              </span>
            </div>
          </Header>

          {/* 主要内容区 */}
          <Content className="chinese-content">
            <div className="content-container">
              {renderContent()}
            </div>
          </Content>
        </Layout>

        {/* 悬浮按钮 - 设置 */}
        <FloatButton
          icon={<SettingOutlined />}
          tooltip="系统设置"
          onClick={() => setShowAPISettings(true)}
          className="settings-float-btn"
        />

        {/* API设置模态框 */}
        <APISettingsModal
          visible={showAPISettings}
          onCancel={() => setShowAPISettings(false)}
        />
      </Layout>
    </ConfigProvider>
  );
};

export default App;