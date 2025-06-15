import React, { useState } from 'react';
import { ConfigProvider, Layout, Menu, theme, FloatButton, Button } from 'antd';
import {
  CloudUploadOutlined,
  FileTextOutlined,
  SettingOutlined,
  BranchesOutlined,
  BookOutlined,
  RobotOutlined
} from '@ant-design/icons';

// Import our new components
import APISettingsModal from './components/Settings/APISettingsModal';
import FileManager from './components/FileManager/FileManager';
import KnowledgeGraphViewer from './components/Graph/KnowledgeGraphViewer';
import ObsidianMarkdownEditor from './components/editor/ObsidianMarkdownEditor';
import FileUploadArea from './components/Upload/FileUploadArea';
import ExtractionDashboard from './components/EntityExtraction/ExtractionDashboard';

const { Header, Content, Sider } = Layout;

interface AppProps {}

const App: React.FC<AppProps> = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [selectedKey, setSelectedKey] = useState('upload');
  const [showAPISettings, setShowAPISettings] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);

  const menuItems = [
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
      key: 'extraction',
      icon: <RobotOutlined />,
      label: '实体关系提取',
    },
    {
      key: 'editor',
      icon: <BookOutlined />,
      label: 'Markdown编辑器',
    },
    {
      key: 'knowledge-graph',
      icon: <BranchesOutlined />,
      label: '知识图谱',
    },
  ];

  const renderContent = () => {
    switch (selectedKey) {
      case 'upload':
        return <FileUploadArea />;
      case 'files':
        return <FileManager />;
      case 'extraction':
        return <ExtractionDashboard />;
      case 'editor':
        return <ObsidianMarkdownEditor />;
      case 'knowledge-graph':
        return <KnowledgeGraphViewer />;
      default:
        return <FileUploadArea />;
    }
  };

  const professionalTheme = {
    algorithm: isDarkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
    token: {
      colorPrimary: '#1890ff',
      colorBgContainer: isDarkMode ? '#1a1a1a' : '#ffffff',
      colorText: isDarkMode ? '#e8e8e8' : '#333333',
      borderRadius: 4,
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    },
    components: {
      Layout: {
        headerBg: isDarkMode ? '#1f1f1f' : '#ffffff',
        siderBg: isDarkMode ? '#262626' : '#f5f5f5',
        bodyBg: isDarkMode ? '#000000' : '#f0f2f5',
      },
      Menu: {
        itemBg: 'transparent',
        itemSelectedBg: '#e6f7ff',
        itemHoverBg: '#f0f0f0',
        itemSelectedColor: '#1890ff',
      },
    },
  };

  return (
    <ConfigProvider theme={professionalTheme}>
      <Layout style={{ minHeight: '100vh' }}>
        {/* 侧边栏 */}
        <Sider 
          collapsible 
          collapsed={collapsed} 
          onCollapse={setCollapsed}
          width={240}
          style={{
            background: isDarkMode ? '#262626' : '#f5f5f5',
            borderRight: `1px solid ${isDarkMode ? '#434343' : '#d9d9d9'}`
          }}
        >
          <div className="logo-section">
            <div style={{
              color: isDarkMode ? '#fff' : '#333',
              fontSize: collapsed ? 16 : 18,
              fontWeight: 600,
              textAlign: 'center',
              fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
            }}>
              {!collapsed ? 'EMC知识图谱' : 'EMC'}
            </div>
          </div>
          
          <Menu
            mode="inline"
            selectedKeys={[selectedKey]}
            items={menuItems}
            onSelect={({ key }) => setSelectedKey(key)}
            style={{
              background: 'transparent',
              border: 'none',
              marginTop: 16
            }}
          />
        </Sider>

        <Layout>
          {/* 顶部导航 */}
          <Header style={{
            background: isDarkMode ? '#1f1f1f' : '#ffffff',
            borderBottom: `1px solid ${isDarkMode ? '#434343' : '#d9d9d9'}`,
            padding: '0 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{
              fontSize: 20,
              fontWeight: 600,
              color: isDarkMode ? '#fff' : '#333',
              fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
            }}>
              EMC知识图谱系统
            </div>
            
            <div>
              <Button
                type="text"
                onClick={() => setIsDarkMode(!isDarkMode)}
                style={{
                  color: isDarkMode ? '#fff' : '#333',
                  border: 'none',
                  background: 'transparent'
                }}
              >
                {isDarkMode ? '☀️' : '🌙'}
              </Button>
            </div>
          </Header>

          {/* 主要内容区 */}
          <Content style={{
            background: isDarkMode ? '#000000' : '#f0f2f5',
            padding: 24,
            minHeight: 'calc(100vh - 64px)'
          }}>
            {renderContent()}
          </Content>
        </Layout>

        {/* 悬浮按钮 - 设置 */}
        <FloatButton
          icon={<SettingOutlined />}
          tooltip="系统设置"
          onClick={() => setShowAPISettings(true)}
          style={{
            right: 24,
            bottom: 24
          }}
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