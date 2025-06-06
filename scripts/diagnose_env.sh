#!/bin/bash

echo "=== EMC知识图谱环境诊断报告 ==="
echo "当前时间: $(date '+%Y年%m月%d日 %H:%M:%S')"

# 检查.env文件
if [ -f ".env" ]; then
    echo "✓ .env文件存在"
    echo "文件路径: $(pwd)/.env"
    echo "文件权限: $(ls -la .env)"
else
    echo "✗ .env文件不存在"
    exit 1
fi

echo "=== .env文件内容检查 ==="

# 必需的EMC配置变量
required_vars=(
    "EMC_ENVIRONMENT"
    "EMC_SECRET_KEY"
    "EMC_DEEPSEEK_API_KEY"
    "EMC_NEO4J_PASSWORD"
    "EMC_POSTGRES_PASSWORD"
    "EMC_REDIS_PASSWORD"
)

missing_vars=()
weak_passwords=()

# 检查每个必需变量
for var in "${required_vars[@]}"; do
    if grep -q "^${var}=" .env; then
        value=$(grep "^${var}=" .env | cut -d'=' -f2)
        echo "✓ $var: 已配置"
        
        # 检查密码强度
        if [[ $var == *"PASSWORD"* ]] && [[ ${#value} -lt 8 ]]; then
            weak_passwords+=("$var")
        fi
    else
        echo "✗ $var: 未配置"
        missing_vars+=("$var")
    fi
done

# 检查DeepSeek API密钥格式
deepseek_key=$(grep "^EMC_DEEPSEEK_API_KEY=" .env | cut -d'=' -f2)
if [[ $deepseek_key =~ ^sk-[a-f0-9]{32}$ ]]; then
    echo "✓ DeepSeek API密钥格式正确"
else
    echo "⚠ DeepSeek API密钥格式可能不正确"
fi

# 检查Docker服务
echo "=== Docker服务检查 ==="
if command -v docker &> /dev/null; then
    echo "✓ Docker已安装"
    if docker info &> /dev/null; then
        echo "✓ Docker服务运行中"
    else
        echo "✗ Docker服务未运行"
    fi
else
    echo "✗ Docker未安装"
fi

# 输出修复建议
if [ ${#missing_vars[@]} -gt 0 ]; then
    echo "=== 缺失变量修复建议 ==="
    for var in "${missing_vars[@]}"; do
        echo "请在.env文件中添加: $var=your_value_here"
    done
fi

if [ ${#weak_passwords[@]} -gt 0 ]; then
    echo "=== 密码强度建议 ==="
    for var in "${weak_passwords[@]}"; do
        echo "建议加强密码: $var (至少8位，包含字母数字)"
    done
fi

echo "=== 下一步操作 ==="
if [ ${#missing_vars[@]} -eq 0 ] && [ ${#weak_passwords[@]} -eq 0 ]; then
    echo "✓ 环境配置检查通过，可以启动服务"
    echo "运行: docker-compose up --build"
else
    echo "请修复上述问题后重新检查"
fi