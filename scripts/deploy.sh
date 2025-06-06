#!/usr/bin/bash

# EMC知识图谱系统部署脚本
# 用于自动化部署和环境配置

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查必需的命令
check_dependencies() {
    log_info "检查系统依赖..."
    
    local deps=("docker" "docker-compose" "curl" "jq")
    local missing_deps=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "缺少以下依赖: ${missing_deps[*]}"
        log_info "请安装缺少的依赖后重试"
        exit 1
    fi
    
    log_success "系统依赖检查完成"
}

# 检查Docker是否运行
check_docker() {
    log_info "检查Docker状态..."
    
    if ! docker info &> /dev/null; then
        log_error "Docker未运行或当前用户无权限访问Docker"
        log_info "请确保Docker正在运行且当前用户在docker组中"
        exit 1
    fi
    
    log_success "Docker状态正常"
}

# 创建环境配置文件
create_env_file() {
    log_info "创建环境配置文件..."
    
    if [ ! -f ".env" ]; then
        log_info "未找到.env文件，创建新的配置文件..."
        
        # 生成随机密码
        SECRET_KEY=$(openssl rand -base64 32)
        POSTGRES_PASSWORD=$(openssl rand -base64 16)
        NEO4J_PASSWORD=$(openssl rand -base64 16)
        REDIS_PASSWORD=$(openssl rand -base64 16)
        GRAFANA_PASSWORD=$(openssl rand -base64 16)
        
        cat > .env << EOF
# EMC知识图谱系统环境配置

# 基础安全配置
SECRET_KEY=${SECRET_KEY}

# DeepSeek API配置（请填写实际的API密钥）
DEEPSEEK_API_KEY=your-deepseek-api-key-here

# 数据库密码
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
NEO4J_PASSWORD=${NEO4J_PASSWORD}
REDIS_PASSWORD=${REDIS_PASSWORD}

# 监控系统密码
GRAFANA_PASSWORD=${GRAFANA_PASSWORD}

# 部署环境
ENVIRONMENT=production
DEBUG=false
EOF
        
        log_warning "请编辑.env文件并填写DeepSeek API密钥等必要配置"
        log_info "生成的.env文件位置: $(pwd)/.env"
    else
        log_success "找到现有的.env文件"
    fi
}

# 验证环境配置
validate_env() {
    log_info "验证环境配置..."
    
    if [ ! -f ".env" ]; then
        log_error "未找到.env文件"
        return 1
    fi
    
    source .env
    
    # 检查必需的配置项
    local required_vars=("SECRET_KEY" "DEEPSEEK_API_KEY" "POSTGRES_PASSWORD" "NEO4J_PASSWORD" "REDIS_PASSWORD")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ] || [ "${!var}" = "your-deepseek-api-key-here" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_error "以下环境变量未正确配置: ${missing_vars[*]}"
        log_info "请编辑.env文件并填写正确的值"
        return 1
    fi
    
    log_success "环境配置验证通过"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    local dirs=("uploads" "logs" "data/postgres" "data/neo4j" "data/redis" "static")
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        log_info "创建目录: $dir"
    done
    
    # 设置权限
    chmod 755 uploads logs static
    chmod 700 data/postgres data/neo4j data/redis
    
    log_success "目录创建完成"
}

# 拉取Docker镜像
pull_images() {
    log_info "拉取Docker镜像..."
    
    docker-compose pull
    
    log_success "Docker镜像拉取完成"
}

# 构建自定义镜像
build_images() {
    log_info "构建自定义镜像..."
    
    docker-compose build --no-cache
    
    log_success "自定义镜像构建完成"
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    
    # 启动数据库服务
    docker-compose up -d postgres redis neo4j
    
    # 等待数据库启动
    log_info "等待PostgreSQL启动..."
    until docker-compose exec postgres pg_isready -U postgres > /dev/null 2>&1; do
        sleep 2
    done
    
    log_info "等待Neo4j启动..."
    until docker-compose exec neo4j cypher-shell -u neo4j -p "${NEO4J_PASSWORD}" "RETURN 1" > /dev/null 2>&1; do
        sleep 2
    done
    
    log_info "等待Redis启动..."
    until docker-compose exec redis redis-cli --no-auth-warning -a "${REDIS_PASSWORD}" ping | grep PONG > /dev/null 2>&1; do
        sleep 2
    done
    
    # 运行数据库迁移
    log_info "运行数据库迁移..."
    docker-compose run --rm gateway python -m alembic upgrade head
    
    log_success "数据库初始化完成"
}

# 启动所有服务
start_services() {
    log_info "启动所有服务..."
    
    docker-compose up -d
    
    log_success "所有服务已启动"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    local services=("gateway:8000/health" "frontend:3000" "prometheus:9090" "grafana:3001")
    local max_attempts=30
    local attempt=1
    
    for service in "${services[@]}"; do
        local service_name=$(echo "$service" | cut -d':' -f1)
        local endpoint="http://localhost:$(echo "$service" | cut -d':' -f2-)"
        
        log_info "检查 $service_name 服务状态..."
        
        while [ $attempt -le $max_attempts ]; do
            if curl -f -s "$endpoint" > /dev/null 2>&1; then
                log_success "$service_name 服务正常"
                break
            fi
            
            if [ $attempt -eq $max_attempts ]; then
                log_warning "$service_name 服务可能未正常启动"
                break
            fi
            
            sleep 5
            ((attempt++))
        done
        attempt=1
    done
}

# 显示服务信息
show_service_info() {
    log_info "系统部署完成！"
    echo ""
    echo "==================================="
    echo "     EMC知识图谱系统服务信息"
    echo "==================================="
    echo ""
    echo "🌐 前端应用:      http://localhost:3000"
    echo "🚀 API网关:       http://localhost:8000"
    echo "📊 API文档:       http://localhost:8000/docs"
    echo "💾 Neo4j浏览器:   http://localhost:7474"
    echo "📈 Prometheus:    http://localhost:9090"
    echo "📊 Grafana:       http://localhost:3001"
    echo "🔍 Kibana:        http://localhost:5601"
    echo ""
    echo "默认登录信息:"
    echo "- Grafana: admin / $(grep GRAFANA_PASSWORD .env | cut -d'=' -f2)"
    echo "- Neo4j: neo4j / $(grep NEO4J_PASSWORD .env | cut -d'=' -f2)"
    echo ""
    echo "==================================="
    echo ""
    log_success "部署完成！请访问 http://localhost:3000 开始使用系统"
}

# 停止服务
stop_services() {
    log_info "停止所有服务..."
    docker-compose down
    log_success "所有服务已停止"
}

# 清理数据
clean_data() {
    log_warning "这将删除所有数据，包括数据库、文件上传等"
    read -p "确定要继续吗？(y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "清理数据..."
        docker-compose down -v
        docker system prune -f
        rm -rf data/ uploads/ logs/
        log_success "数据清理完成"
    else
        log_info "操作已取消"
    fi
}

# 显示日志
show_logs() {
    local service=${1:-}
    
    if [ -n "$service" ]; then
        docker-compose logs -f "$service"
    else
        docker-compose logs -f
    fi
}

# 备份数据
backup_data() {
    log_info "创建数据备份..."
    
    local backup_dir="backup/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # 备份PostgreSQL
    log_info "备份PostgreSQL数据..."
    docker-compose exec postgres pg_dump -U postgres emc_knowledge > "$backup_dir/postgres_backup.sql"
    
    # 备份Neo4j
    log_info "备份Neo4j数据..."
    docker-compose exec neo4j neo4j-admin dump --database=neo4j --to=/tmp/neo4j_backup.dump
    docker cp "$(docker-compose ps -q neo4j):/tmp/neo4j_backup.dump" "$backup_dir/"
    
    # 备份上传文件
    log_info "备份上传文件..."
    if [ -d "uploads" ]; then
        cp -r uploads "$backup_dir/"
    fi
    
    # 备份配置文件
    cp .env "$backup_dir/" 2>/dev/null || true
    cp docker-compose.yml "$backup_dir/"
    
    log_success "备份完成: $backup_dir"
}

# 恢复数据
restore_data() {
    local backup_dir=$1
    
    if [ -z "$backup_dir" ] || [ ! -d "$backup_dir" ]; then
        log_error "请指定有效的备份目录"
        return 1
    fi
    
    log_warning "这将覆盖现有数据"
    read -p "确定要继续吗？(y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "操作已取消"
        return 1
    fi
    
    log_info "恢复数据中..."
    
    # 停止服务
    docker-compose down
    
    # 恢复PostgreSQL
    if [ -f "$backup_dir/postgres_backup.sql" ]; then
        log_info "恢复PostgreSQL数据..."
        docker-compose up -d postgres
        until docker-compose exec postgres pg_isready -U postgres > /dev/null 2>&1; do
            sleep 2
        done
        docker-compose exec -T postgres psql -U postgres -d emc_knowledge < "$backup_dir/postgres_backup.sql"
    fi
    
    # 恢复Neo4j
    if [ -f "$backup_dir/neo4j_backup.dump" ]; then
        log_info "恢复Neo4j数据..."
        docker cp "$backup_dir/neo4j_backup.dump" "$(docker-compose ps -q neo4j):/tmp/"
        docker-compose exec neo4j neo4j-admin load --database=neo4j --from=/tmp/neo4j_backup.dump --force
    fi
    
    # 恢复上传文件
    if [ -d "$backup_dir/uploads" ]; then
        log_info "恢复上传文件..."
        rm -rf uploads
        cp -r "$backup_dir/uploads" .
    fi
    
    # 恢复配置文件
    if [ -f "$backup_dir/.env" ]; then
        cp "$backup_dir/.env" .
    fi
    
    # 重启服务
    docker-compose up -d
    
    log_success "数据恢复完成"
}

# 显示帮助信息
show_help() {
    echo "EMC知识图谱系统部署脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  deploy       完整部署系统（默认）"
    echo "  start        启动所有服务"
    echo "  stop         停止所有服务"
    echo "  restart      重启所有服务"
    echo "  status       显示服务状态"
    echo "  logs [服务]  显示日志"
    echo "  backup       备份数据"
    echo "  restore      恢复数据"
    echo "  clean        清理所有数据"
    echo "  update       更新系统"
    echo "  help         显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 deploy                    # 完整部署"
    echo "  $0 logs gateway              # 查看网关日志"
    echo "  $0 restore backup/20240101_120000  # 恢复指定备份"
}

# 主函数
main() {
    local command=${1:-deploy}
    
    case "$command" in
        "deploy")
            check_dependencies
            check_docker
            create_env_file
            validate_env
            create_directories
            pull_images
            build_images
            init_database
            start_services
            health_check
            show_service_info
            ;;
        "start")
            docker-compose up -d
            log_success "所有服务已启动"
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            docker-compose restart
            log_success "所有服务已重启"
            ;;
        "status")
            docker-compose ps
            ;;
        "logs")
            show_logs "$2"
            ;;
        "backup")
            backup_data
            ;;
        "restore")
            restore_data "$2"
            ;;
        "clean")
            clean_data
            ;;
        "update")
            log_info "更新系统..."
            git pull
            build_images
            docker-compose up -d
            log_success "系统更新完成"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"