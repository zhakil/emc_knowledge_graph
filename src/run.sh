#!/bin/bash
export DEEPSEEK_API_KEY="your_api_key_here"
export PYTHONPATH="${PYTHONPATH}:./src"

# 安装依赖
pip install -r requirements.txt

# 启动应用
streamlit run app.py --server.port=8501 --server.address=0.0.0.0