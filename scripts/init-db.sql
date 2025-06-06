-- EMC知识图谱数据库初始化
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建基础表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入测试数据
INSERT INTO users (username, email) VALUES 
    ('admin', 'admin@emc-kg.com'),
    ('engineer', 'engineer@emc-kg.com')
ON CONFLICT (username) DO NOTHING;

-- 显示初始化完成
SELECT 'EMC知识图谱数据库初始化完成' as status;