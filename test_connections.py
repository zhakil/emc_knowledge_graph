#!/usr/bin/env python3
"""
测试数据库连接状态
"""
import os
import sys
import asyncio
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

async def test_neo4j_connection():
    """测试Neo4j连接"""
    try:
        from neo4j import AsyncGraphDatabase
        
        uri = os.getenv('EMC_NEO4J_URI', 'bolt://localhost:7687')
        user = os.getenv('EMC_NEO4J_USER', 'neo4j')
        password = os.getenv('EMC_NEO4J_PASSWORD', 'Zqz112233')
        
        print(f"🔍 测试Neo4j连接: {uri}")
        
        driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
        
        async with driver.session() as session:
            result = await session.run("RETURN 'Neo4j连接成功!' as message")
            record = await result.single()
            if record:
                print(f"✅ Neo4j: {record['message']}")
                return True
            else:
                print("❌ Neo4j: 无返回结果")
                return False
                
    except ImportError:
        print("⚠️  Neo4j: neo4j驱动未安装")
        return False
    except Exception as e:
        print(f"❌ Neo4j连接失败: {e}")
        return False
    finally:
        try:
            await driver.close()
        except:
            pass

def test_redis_connection():
    """测试Redis连接"""
    try:
        import redis
        
        host = os.getenv('EMC_REDIS_HOST', 'localhost')
        port = int(os.getenv('EMC_REDIS_PORT', '6379'))
        db = int(os.getenv('EMC_REDIS_DB', '0'))
        password = os.getenv('EMC_REDIS_PASSWORD', 'Zqz112233')
        
        print(f"🔍 测试Redis连接: {host}:{port}")
        
        r = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True,
            socket_timeout=5
        )
        
        # 测试连接
        r.ping()
        print("✅ Redis: 连接成功!")
        return True
        
    except ImportError:
        print("⚠️  Redis: redis驱动未安装")
        return False
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        return False

def test_postgres_connection():
    """测试PostgreSQL连接"""
    try:
        import psycopg2
        
        host = os.getenv('EMC_POSTGRES_HOST', 'localhost')
        port = int(os.getenv('EMC_POSTGRES_PORT', '5432'))
        database = os.getenv('EMC_POSTGRES_DATABASE', 'emc_knowledge_graph')
        user = os.getenv('EMC_POSTGRES_USER', 'emc_user')
        password = os.getenv('EMC_POSTGRES_PASSWORD', 'Zqz112233')
        
        print(f"🔍 测试PostgreSQL连接: {host}:{port}/{database}")
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=5
        )
        
        with conn.cursor() as cur:
            cur.execute("SELECT 'PostgreSQL连接成功!' as message")
            result = cur.fetchone()
            if result:
                print(f"✅ PostgreSQL: {result[0]}")
                return True
            else:
                print("❌ PostgreSQL: 无返回结果")
                return False
                
    except ImportError:
        print("⚠️  PostgreSQL: psycopg2驱动未安装")
        return False
    except Exception as e:
        print(f"❌ PostgreSQL连接失败: {e}")
        return False
    finally:
        try:
            conn.close()
        except:
            pass

async def main():
    """主测试函数"""
    print("=" * 50)
    print("🚀 EMC知识图谱系统 - 数据库连接测试")
    print("=" * 50)
    
    # 加载环境变量
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print("✅ 已加载.env配置文件")
    else:
        print("⚠️  .env文件不存在，使用默认配置")
    
    print()
    
    # 测试各个数据库连接
    results = {
        'neo4j': await test_neo4j_connection(),
        'redis': test_redis_connection(), 
        'postgres': test_postgres_connection()
    }
    
    print()
    print("=" * 50)
    print("📊 连接测试结果汇总")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for service, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {service.upper()}: {'连接正常' if status else '连接失败'}")
    
    print()
    print(f"通过: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 所有数据库连接测试通过！")
        return True
    elif passed_tests > 0:
        print("⚠️  部分数据库连接成功，请检查失败的服务")
        return False
    else:
        print("❌ 所有数据库连接失败，请检查配置和服务状态")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)