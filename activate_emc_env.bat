@echo off
echo 🐍 激活EMC知识图谱Conda环境...
call conda activate emc-kg-311
echo ✅ 环境已激活: emc-kg-311
echo 📋 可用命令:
echo   python start_gateway.py  # 启动API服务
echo   jupyter lab              # 启动Jupyter
echo   pytest tests/            # 运行测试
cmd /k
