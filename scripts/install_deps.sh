#!/usr/bin/env bash

# 智能依赖安装脚本
install_jq() {
    echo "安装 jq..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get >/dev/null; then
            sudo apt-get update && sudo apt-get install -y jq
        elif command -v yum >/dev/null; then
            sudo yum install -y jq
        elif command -v dnf >/dev/null; then
            sudo dnf install -y jq
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew >/dev/null; then
            brew install jq
        else
            echo "请先安装 Homebrew"
            exit 1
        fi
    else
        echo "请手动安装 jq: https://stedolan.github.io/jq/download/"
        exit 1
    fi
}

# 检查并安装
if ! command -v jq >/dev/null; then
    install_jq
else
    echo "jq 已安装"
fi

echo "依赖检查完成"