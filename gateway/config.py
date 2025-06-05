"""
系统配置管理
使用Pydantic进行配置验证和类型检查
"""

import os
from typing import List, Optional
from functools import lru_cache
from pydantic import BaseSettings, validator, Field


class Settings(BaseSettings):
    """应用配置类"""
    
    # 基础配置
    app_name: str = "EMC知识图谱系统"
    environment: str = Field(default="development", description="运行环境")
    debug: bool = Field(default=False, description="调试模式")
    host: str = Field(default="0.0.0.0", description="服务器主机")
    port: int = Field(default=8000, description="服务器端口")
    workers: int = Field(default=4, description="工作进程数")
    log_level: str = Field(default="INFO", description="日志级别")
    
    # 安全配置
    secret_key: str = Field(..., description="JWT密钥")
    jwt_algorithm: str = Field(default="HS256", description="JWT算法")
    jwt_expire_minutes: int = Field(default=1440, description="JWT过期时间(分钟)")
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="允许的CORS源"
    )
    
    # DeepSeek API配置
    deepseek_api_key: str = Field(..., description="DeepSeek API密钥")
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com/v1",
        description="DeepSeek API基础URL"
    )
    deepseek_model: str = Field(default="deepseek-chat", description="默认模型")
    deepseek_max_tokens: int = Field(default=4000, description="最大token数")
    deepseek_temperature: float = Field(default=0.7, description="温度参数")
    deepseek_timeout: int = Field(default=30, description="请求超时时间")
    deepseek_max_retries: int = Field(default=3, description="最大重试次数")
    
    # Neo4j配置
    neo4j_uri: str = Field(default="bolt://localhost:7687", description="Neo4j URI")
    neo4j_username: str = Field(default="neo4j", description="Neo4j用户名")
    neo4j_password: str = Field(..., description="Neo4j密码")
    neo4j_database: str = Field(default="neo4j", description="数据库名称")
    neo4j_max_pool_size: int = Field(default=20, description="连接池大小")
    neo4j_connection_timeout: int = Field(default=30, description="连接超时")
    
    # PostgreSQL配置
    postgres_host: str = Field(default="localhost", description="PostgreSQL主机")
    postgres_port: int = Field(default=5432, description="PostgreSQL端口")
    postgres_db: str = Field(default="emc_knowledge", description="数据库名")
    postgres_user: str = Field(default="postgres", description="数据库用户")
    postgres_password: str = Field(..., description="数据库密码")
    postgres_pool_size: int = Field(default=10, description="连接池大小")
    postgres_max_overflow: int = Field(default=5, description="连接池溢出")
    
    # Redis配置
    redis_host: str = Field(default="localhost", description="Redis主机")
    redis_port: int = Field(default=6379, description="Redis端口")
    redis_db: int = Field(default=0, description="Redis数据库")
    redis_password: Optional[str] = Field(default=None, description="Redis密码")
    redis_max_connections: int = Field(default=20, description="最大连接数")
    redis_timeout: int = Field(default=5, description="连接超时")
    
    # 文件处理配置
    upload_directory: str = Field(default="./uploads", description="上传目录")
    max_file_size: int = Field(default=100 * 1024 * 1024, description="最大文件大小(字节)")
    allowed_file_types: List[str] = Field(
        default=[".pdf", ".docx", ".xlsx", ".csv", ".json", ".xml", ".txt"],
        description="允许的文件类型"
    )
    file_processing_timeout: int = Field(default=300, description="文件处理超时")
    max_concurrent_processing: int = Field(default=3, description="最大并发处理数")
    
    # 速率限制配置
    rate_limit_requests_per_minute: int = Field(default=60, description="每分钟请求限制")
    rate_limit_requests_per_hour: int = Field(default=1000, description="每小时请求限制")
    rate_limit_burst_size: int = Field(default=10, description="突发请求大小")
    
    # 监控配置
    enable_metrics: bool = Field(default=True, description="启用指标收集")
    metrics_path: str = Field(default="/metrics", description="指标路径")
    health_check_interval: int = Field(default=30, description="健康检查间隔")
    
    # 缓存配置
    cache_ttl_short: int = Field(default=300, description="短期缓存TTL(秒)")
    cache_ttl_medium: int = Field(default=3600, description="中期缓存TTL(秒)")
    cache_ttl_long: int = Field(default=86400, description="长期缓存TTL(秒)")
    enable_response_cache: bool = Field(default=True, description="启用响应缓存")
    
    # 分析配置
    analysis_max_nodes: int = Field(default=1000, description="分析最大节点数")
    analysis_timeout: int = Field(default=120, description="分析超时时间")
    enable_background_analysis: bool = Field(default=True, description="启用后台分析")
    
    # WebSocket配置
    websocket_heartbeat_interval: int = Field(default=30, description="心跳间隔")
    websocket_max_connections: int = Field(default=100, description="最大连接数")
    websocket_message_size_limit: int = Field(default=1024 * 1024, description="消息大小限制")
    
    @validator('environment')
    def validate_environment(cls, v):
        """验证环境配置"""
        allowed = ['development', 'testing', 'staging', 'production']
        if v not in allowed:
            raise ValueError(f'环境必须是以下之一: {allowed}')
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """验证日志级别"""
        allowed = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed:
            raise ValueError(f'日志级别必须是以下之一: {allowed}')
        return v.upper()
    
    @validator('deepseek_temperature')
    def validate_temperature(cls, v):
        """验证温度参数"""
        if not 0 <= v <= 2:
            raise ValueError('温度参数必须在0-2之间')
        return v
    
    @validator('upload_directory')
    def validate_upload_directory(cls, v):
        """验证上传目录"""
        # 确保目录存在
        os.makedirs(v, exist_ok=True)
        return v
    
    @property
    def database_url_sync(self) -> str:
        """同步数据库URL"""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def database_url_async(self) -> str:
        """异步数据库URL"""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def redis_url(self) -> str:
        """Redis连接URL"""
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment == "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # 环境变量前缀
        env_prefix = "EMC_"
        
        # 字段别名，支持不同的环境变量命名
        fields = {
            'secret_key': {'env': ['EMC_SECRET_KEY', 'SECRET_KEY']},
            'deepseek_api_key': {'env': ['EMC_DEEPSEEK_API_KEY', 'DEEPSEEK_API_KEY']},
            'neo4j_password': {'env': ['EMC_NEO4J_PASSWORD', 'NEO4J_PASSWORD']},
            'postgres_password': {'env': ['EMC_POSTGRES_PASSWORD', 'POSTGRES_PASSWORD']},
        }


class DevelopmentSettings(Settings):
    """开发环境配置"""
    environment: str = "development"
    debug: bool = True
    log_level: str = "DEBUG"
    
    # 开发环境允许更多CORS源
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]
    
    # 开发环境较宽松的限制
    rate_limit_requests_per_minute: int = 120
    rate_limit_requests_per_hour: int = 2000


class TestingSettings(Settings):
    """测试环境配置"""
    environment: str = "testing"
    debug: bool = True
    log_level: str = "DEBUG"
    
    # 测试数据库
    postgres_db: str = "emc_knowledge_test"
    redis_db: int = 1
    
    # 测试环境快速处理
    file_processing_timeout: int = 60
    analysis_timeout: int = 30


class ProductionSettings(Settings):
    """生产环境配置"""
    environment: str = "production"
    debug: bool = False
    log_level: str = "INFO"
    workers: int = 8
    
    # 生产环境严格的安全设置
    jwt_expire_minutes: int = 60  # 更短的token有效期
    
    # 生产环境更保守的限制
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    rate_limit_requests_per_minute: int = 30
    
    # 生产环境优化的缓存设置
    cache_ttl_short: int = 600
    cache_ttl_medium: int = 7200
    cache_ttl_long: int = 172800


@lru_cache()
def get_settings() -> Settings:
    """获取设置实例（带缓存）"""
    environment = os.getenv("EMC_ENVIRONMENT", "development").lower()
    
    if environment == "testing":
        return TestingSettings()
    elif environment == "production":
        return ProductionSettings()
    else:
        return DevelopmentSettings()


# 配置验证
def validate_settings():
    """验证配置完整性"""
    settings = get_settings()
    
    required_fields = [
        'secret_key', 'deepseek_api_key', 'neo4j_password', 'postgres_password'
    ]
    
    missing_fields = []
    for field in required_fields:
        value = getattr(settings, field, None)
        if not value:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"缺少必需的配置字段: {', '.join(missing_fields)}")
    
    return True


# 配置示例生成器
def generate_env_example():
    """生成.env.example文件"""
    example_content = """# EMC知识图谱系统配置文件示例
# 复制此文件为.env并填入实际配置值

# 基础配置
EMC_ENVIRONMENT=development
EMC_DEBUG=true
EMC_HOST=0.0.0.0
EMC_PORT=8000
EMC_LOG_LEVEL=INFO

# 安全配置
EMC_SECRET_KEY=your-secret-key-here
EMC_JWT_EXPIRE_MINUTES=1440

# DeepSeek API配置
EMC_DEEPSEEK_API_KEY=your-deepseek-api-key
EMC_DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
EMC_DEEPSEEK_MODEL=deepseek-chat
EMC_DEEPSEEK_MAX_TOKENS=4000
EMC_DEEPSEEK_TEMPERATURE=0.7

# Neo4j配置
EMC_NEO4J_URI=bolt://localhost:7687
EMC_NEO4J_USERNAME=neo4j
EMC_NEO4J_PASSWORD=your-neo4j-password
EMC_NEO4J_DATABASE=neo4j

# PostgreSQL配置
EMC_POSTGRES_HOST=localhost
EMC_POSTGRES_PORT=5432
EMC_POSTGRES_DB=emc_knowledge
EMC_POSTGRES_USER=postgres
EMC_POSTGRES_PASSWORD=your-postgres-password

# Redis配置
EMC_REDIS_HOST=localhost
EMC_REDIS_PORT=6379
EMC_REDIS_DB=0
EMC_REDIS_PASSWORD=

# 文件处理配置
EMC_UPLOAD_DIRECTORY=./uploads
EMC_MAX_FILE_SIZE=104857600
EMC_FILE_PROCESSING_TIMEOUT=300

# 速率限制配置
EMC_RATE_LIMIT_REQUESTS_PER_MINUTE=60
EMC_RATE_LIMIT_REQUESTS_PER_HOUR=1000

# 监控配置
EMC_ENABLE_METRICS=true
EMC_HEALTH_CHECK_INTERVAL=30

# 缓存配置
EMC_CACHE_TTL_SHORT=300
EMC_CACHE_TTL_MEDIUM=3600
EMC_CACHE_TTL_LONG=86400
"""
    
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(example_content)
    
    print("已生成 .env.example 文件")


if __name__ == "__main__":
    # 生成配置示例文件
    generate_env_example()
    
    # 验证当前配置
    try:
        validate_settings()
        settings = get_settings()
        print(f"配置验证成功 - 环境: {settings.environment}")
        print(f"数据库URL: {settings.database_url_sync}")
        print(f"Redis URL: {settings.redis_url}")
    except Exception as e:
        print(f"配置验证失败: {e}")