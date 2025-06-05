#!/usr/bin/env bash
# 兼容性更好的脚本头，自动查找bash路径

set -euo pipefail  # 严格错误处理

# 颜色定义 - 实用的视觉反馈
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m' 
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

# 日志函数 - 简洁高效
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查系统类型
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos" 
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# 智能依赖安装 - 实际解决问题
install_dependencies() {
    local os_type=$(detect_os)
    
    log_info "检测到系统: $os_type"
    
    case $os_type in
        "linux")
            if command -v apt-get >/dev/null 2>&1; then
                log_info "使用apt-get安装依赖..."
                sudo apt-get update && sudo apt-get install -y jq curl docker.io docker-compose
            elif command -v yum >/dev/null 2>&1; then
                log_info "使用yum安装依赖..."
                sudo yum install -y jq curl docker docker-compose
            elif command -v pacman >/dev/null 2>&1; then
                log_info "使用pacman安装依赖..."
                sudo pacman -S --noconfirm jq curl docker docker-compose
            fi
            ;;
        "macos")
            if command -v brew >/dev/null 2>&1; then
                log_info "使用Homebrew安装依赖..."
                brew install jq curl docker docker-compose
            else
                log_error "请先安装Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                exit 1
            fi
            ;;
        "windows")
            log_warn "Windows系统请手动安装Docker Desktop和Git Bash"
            log_info "下载链接: https://www.docker.com/products/docker-desktop"
            ;;
        *)
            log_error "不支持的操作系统"
            exit 1
            ;;
    esac
}

# 验证依赖 - 高效检查
check_dependencies() {
    local missing_deps=()
    local deps=("docker" "docker-compose" "curl" "jq")
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" >/dev/null 2>&1; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_warn "缺少依赖: ${missing_deps[*]}"
        read -p "是否自动安装? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_dependencies
        else
            log_error "请手动安装依赖后重试"
            exit 1
        fi
    fi
    
    log_info "所有依赖检查通过"
}

# 修复脚本权限和格式
fix_scripts() {
    log_info "修复脚本文件..."
    
    # 确保脚本目录存在
    mkdir -p scripts
    
    # 修复文件权限
    find scripts/ -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
    
    # 转换行尾格式（处理Windows/Mac/Linux兼容性）
    if command -v dos2unix >/dev/null 2>&1; then
        find scripts/ -name "*.sh" -exec dos2unix {} \; 2>/dev/null || true
    fi
    
    log_info "脚本修复完成"
}

# 主函数
main() {
    log_info "开始EMC知识图谱系统环境修复..."
    
    fix_scripts
    check_dependencies
    
    log_info "环境修复完成！现在可以运行部署脚本了"
    echo "执行: ./scripts/deploy.sh deploy"
}

main "$@"