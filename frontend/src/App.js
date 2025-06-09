import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// 配置API基础URL
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [systemStatus, setSystemStatus] = useState('checking');
  const [graphData, setGraphData] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);

  // 检查系统状态
  useEffect(() => {
    checkSystemStatus();
  }, []);

  const checkSystemStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE}/health`, { timeout: 5000 });
      setSystemStatus('online');
      loadInitialData();
    } catch (error) {
      console.error('系统连接失败:', error);
      setSystemStatus('offline');
    }
  };

  // 加载初始数据
  const loadInitialData = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/graph/overview`);
      setGraphData(response.data);
    } catch (error) {
      console.error('数据加载失败:', error);
      // 使用模拟数据
      setGraphData({
        nodes: 156,
        relationships: 423,
        entities: ['Person', 'Organization', 'Technology', 'Project']
      });
    }
  };

  // 搜索功能
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/api/search`, {
        params: { q: searchQuery }
      });
      setSearchResults(response.data.results || []);
    } catch (error) {
      console.error('搜索失败:', error);
      // 模拟搜索结果
      setSearchResults([
        { id: 1, type: 'Person', name: '张三', description: 'AI研究员' },
        { id: 2, type: 'Technology', name: 'Machine Learning', description: '机器学习技术' },
        { id: 3, type: 'Project', name: 'EMC项目', description: '知识图谱项目' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // 创建新实体
  const createEntity = async () => {
    const name = prompt('输入实体名称:');
    if (!name) return;

    try {
      await axios.post(`${API_BASE}/api/entities`, {
        name: name,
        type: 'Custom',
        properties: {}
      });
      alert('实体创建成功!');
      loadInitialData();
    } catch (error) {
      console.error('创建失败:', error);
      alert('创建失败，请检查后端连接');
    }
  };

  return (
    <div className="app">
      {/* 头部导航 */}
      <header className="app-header">
        <h1>🧠 EMC知识图谱系统</h1>
        <div className="status-indicator">
          <span className={`status ${systemStatus}`}>
            {systemStatus === 'online' ? '🟢 在线' : 
             systemStatus === 'offline' ? '🔴 离线' : '🟡 检查中...'}
          </span>
        </div>
      </header>

      {/* 主要功能区 */}
      <main className="main-content">
        
        {/* 系统概览 */}
        <section className="overview-section">
          <h2>📊 系统概览</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-number">{graphData?.nodes || 0}</div>
              <div className="stat-label">实体节点</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{graphData?.relationships || 0}</div>
              <div className="stat-label">关系边</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{graphData?.entities?.length || 0}</div>
              <div className="stat-label">实体类型</div>
            </div>
          </div>
        </section>

        {/* 搜索功能 */}
        <section className="search-section">
          <h2>🔍 知识搜索</h2>
          <div className="search-bar">
            <input
              type="text"
              placeholder="搜索实体、关系或概念..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button onClick={handleSearch} disabled={loading}>
              {loading ? '搜索中...' : '搜索'}
            </button>
          </div>
          
          {/* 搜索结果 */}
          {searchResults.length > 0 && (
            <div className="search-results">
              <h3>搜索结果</h3>
              {searchResults.map(item => (
                <div key={item.id} className="result-item">
                  <span className="result-type">{item.type}</span>
                  <span className="result-name">{item.name}</span>
                  <span className="result-desc">{item.description}</span>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* 快速操作 */}
        <section className="actions-section">
          <h2>⚡ 快速操作</h2>
          <div className="action-buttons">
            <button onClick={createEntity} className="action-btn primary">
              ➕ 创建实体
            </button>
            <button onClick={() => window.open(`${API_BASE}/docs`, '_blank')} className="action-btn">
              📚 API文档
            </button>
            <button onClick={() => window.open('http://localhost:7474', '_blank')} className="action-btn">
              🎯 Neo4j管理
            </button>
            <button onClick={checkSystemStatus} className="action-btn">
              🔄 刷新状态
            </button>
          </div>
        </section>

        {/* 实体类型展示 */}
        {graphData?.entities && (
          <section className="entities-section">
            <h2>📋 实体类型</h2>
            <div className="entity-types">
              {graphData.entities.map((entity, index) => (
                <span key={index} className="entity-tag">
                  {entity}
                </span>
              ))}
            </div>
          </section>
        )}

      </main>

      {/* 底部信息 */}
      <footer className="app-footer">
        <p>EMC知识图谱系统 | 后端: {API_BASE}</p>
      </footer>
    </div>
  );
}

export default App;