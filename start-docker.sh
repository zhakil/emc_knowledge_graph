#!/bin/bash

# EMC知识图谱系统 - Docker启动脚本
# 作者: EMC团队
# 版本: 1.0.0

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数定义
print_header() {
    echo -e "${BLUE}"
    echo "=================================="
    echo " EMC知识图谱系统 Docker部署工具"
    echo "=================================="
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 检查依赖
check_dependencies() {
    print_info "检查系统依赖..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装或未在PATH中"
        echo "请访问 https://docs.docker.com/get-docker/ 安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose未安装"
        echo "请安装Docker Compose或使用新版Docker"
        exit 1
    fi
    
    print_success "依赖检查通过"
}

# 检查端口占用
check_ports() {
    print_info "检查端口占用..."
    
    ports=(80 3000 6379 7474 7687 8000)
    occupied_ports=()
    
    for port in "${ports[@]}"; do
        if lsof -i:$port &> /dev/null || netstat -tuln 2>/dev/null | grep :$port &> /dev/null; then
            occupied_ports+=($port)
        fi
    done
    
    if [ ${#occupied_ports[@]} -gt 0 ]; then
        print_warning "以下端口被占用: ${occupied_ports[*]}"
        echo "请停止占用这些端口的服务或修改docker-compose.community.yml中的端口映射"
        read -p "是否继续部署? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_success "端口检查通过"
    fi
}

# 检查系统资源
check_resources() {
    print_info "检查系统资源..."
    
    # 检查内存
    total_mem=$(free -m | awk '/^Mem:/{print $2}')
    if [ $total_mem -lt 4096 ]; then
        print_warning "系统内存不足4GB，可能影响性能"
    fi
    
    # 检查磁盘空间
    available_space=$(df . | awk 'NR==2{print $4}')
    if [ $available_space -lt 10485760 ]; then  # 10GB in KB
        print_warning "可用磁盘空间不足10GB"
    fi
    
    print_success "资源检查完成"
}

# 创建必要目录
create_directories() {
    print_info "创建必要目录..."
    
    directories=("data" "logs" "nginx/ssl")
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "创建目录: $dir"
        fi
    done
}

# 启动服务
start_services() {
    print_info "启动Docker服务..."
    
    # 检查是否使用新版docker compose
    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
    
    # 构建并启动服务
    $COMPOSE_CMD -f docker-compose.community.yml build
    $COMPOSE_CMD -f docker-compose.community.yml up -d
    
    print_success "服务启动完成"
}

# 等待服务就绪
wait_for_services() {
    print_info "等待服务启动..."
    
    services=(
        "http://localhost:8000/health:后端API"
        "http://localhost:7474:Neo4j数据库"
        "http://localhost:3000:前端应用"
    )
    
    for service in "${services[@]}"; do
        url=$(echo $service | cut -d: -f1-2)
        name=$(echo $service | cut -d: -f3)
        
        echo -n "等待 $name 启动..."
        for i in {1..30}; do
            if curl -s $url > /dev/null 2>&1; then
                echo -e " ${GREEN}✅${NC}"
                break
            fi
            sleep 2
            echo -n "."
        done
        
        if [ $i -eq 30 ]; then
            echo -e " ${YELLOW}⚠️ 超时${NC}"
        fi
    done
}

# 显示访问信息
show_access_info() {
    print_header
    print_success "🎉 EMC知识图谱系统部署成功！"
    echo
    echo "📱 访问地址:"
    echo "   🌐 前端应用:    http://localhost:3000"
    echo "   📊 API文档:     http://localhost:8000/docs"
    echo "   🗄️  Neo4j浏览器: http://localhost:7474"
    echo "   ⚡ 系统健康:    http://localhost:8000/health"
    echo "   🔄 Nginx代理:   http://localhost:80"
    echo
    echo "🔐 默认账号:"
    echo "   Neo4j: neo4j / emc_password_123"
    echo
    echo "🛠️ 管理命令:"
    echo "   查看状态: docker compose -f docker-compose.community.yml ps"
    echo "   查看日志: docker compose -f docker-compose.community.yml logs -f"
    echo "   停止服务: docker compose -f docker-compose.community.yml down"
    echo
    echo "📚 更多信息请查看: DOCKER_DEPLOYMENT.md"
    echo
}

# 主函数
main() {
    print_header
    
    # 检查是否在项目根目录
    if [ ! -f "docker-compose.community.yml" ]; then
        print_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    # 执行检查和部署
    check_dependencies
    check_ports
    check_resources
    create_directories
    start_services
    wait_for_services
    show_access_info
    
    print_success "部署完成！系统正在运行中..."
}

# 错误处理
trap 'print_error "脚本执行过程中发生错误"' ERR

# 执行主函数
main "$@"