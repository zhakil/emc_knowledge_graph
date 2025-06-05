#!/bin/bash

# EMC知识图谱项目重构脚本
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}开始EMC知识图谱项目重构...${NC}"

# 1. 删除冗余文件
echo -e "\n${YELLOW}步骤1: 清理冗余文件${NC}"

# 删除监控系统
[ -d "monitoring" ] && rm -rf monitoring/ && echo "✅ 已删除 monitoring/"

# 删除CI/CD
[ -d ".github/workflows" ] && rm -rf .github/workflows/ && echo "✅ 已删除 .github/workflows/"

# 删除过度设计的服务
files_to_delete=(
    "services/ai_integration/chain_orchestrator.py"
    "services/ai_integration/context_manager.py"
    "services/ai_integration/response_processor.py"
    "services/emc_domain/regulation_tracker.py"
    "services/emc_domain/test_report_analyzer.py"
    "services/file_processing/format_converter.py"
    "services/file_processing/metadata_manager.py"
    "services/file_processing/version_controller.py"
    "sync.bat"
)

for file in "${files_to_delete[@]}"; do
    [ -f "$file" ] && rm -f "$file" && echo "✅ 已删除 $file"
done

# 删除integration目录
[ -d "services/integration" ] && rm -rf services/integration/ && echo "✅ 已删除 services/integration/"

# 2. 创建新目录结构
echo -e "\n${YELLOW}步骤2: 创建新目录结构${NC}"

directories=(
    "frontend/src/components/graph-editor"
    "frontend/src/components/prompt-editor"
    "frontend/src/components/display-panel"
    "frontend/src/layouts"
    "frontend/src/hooks"
    "frontend/src/stores"
    "gateway/websocket"
    "services/graph_editing"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir" && echo "✅ 创建目录 $dir"
done

echo -e "\n${GREEN}重构完成！${NC}"
