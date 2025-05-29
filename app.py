import streamlit as st
import asyncio
from pathlib import Path
import sys

sys.path.append('src')
from document_processor import DocumentProcessor
from graph_manager import RealTimeGraphManager
from visualization import GraphVisualizer

class EMCKnowledgeGraphApp:
    def __init__(self):
        self.graph_manager = RealTimeGraphManager()
        self.doc_processor = DocumentProcessor()
        self.visualizer = GraphVisualizer()
        
    def run(self):
        st.set_page_config(
            page_title="EMC知识图谱管理平台",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # 侧边栏配置
        with st.sidebar:
            self._render_control_panel()
            
        # 主界面
        col1, col2 = st.columns([3, 1])
        
        with col1:
            self._render_graph_view()
            
        with col2:
            self._render_knowledge_panel()
    
    def _render_control_panel(self):
        st.header("📄 文档导入")
        uploaded_file = st.file_uploader(
            "选择文档", 
            type=['pdf', 'docx', 'doc']
        )
        
        standard_name = st.text_input("标准名称", placeholder="如：CISPR 25")
        
        if uploaded_file and standard_name:
            if st.button("🚀 处理文档"):
                self._process_document(uploaded_file, standard_name)
        
        st.header("⚙️ 图谱配置")
        self._render_graph_config()
    
    def _process_document(self, file, standard_name):
        with st.spinner("正在处理文档..."):
            # 异步处理文档
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            knowledge = loop.run_until_complete(
                self.doc_processor.process_document(file, standard_name)
            )
            
            # 更新知识图谱
            self.graph_manager.update_graph(knowledge)
            st.success(f"✅ {standard_name} 已成功导入")

if __name__ == "__main__":
    app = EMCKnowledgeGraphApp()
    app.run()