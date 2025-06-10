"""
实用高效的数据库连接检查工具
直接解决Neo4j、PostgreSQL、Redis的连接验证问题
"""

import os
import sys
import time
import subprocess
from typing import Dict, Tuple, List
import json


class DatabaseChecker:
    """高效的数据库状态检查器 - 注重实用性"""
    
    def __init__(self):
        self.config = self._load_env_config()
        self.results = {}
    
    def _load_env_config(self) -> Dict[str, str]:
        """从.env文件加载配置 - 实用导向"""
        config = {
            'postgres_password': 'Zqz112233',
            'neo4j_password': 'Zqz112233', 
            'redis_password': 'Zqz112233'
        }
        
        # 尝试从.env读取
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        if 'POSTGRES_PASSWORD' in key:
                            config['postgres_password'] = value
                        elif 'NEO4J_PASSWORD' in key:
                            config['neo4j_password'] = value
                        elif 'REDIS_PASSWORD' in key:
                            config['redis_password'] = value
        except FileNotFoundError:
            print("⚠️  .env文件未找到，使用默认配置")
        
        return config
    
    def check_docker_containers(self) -> Dict[str, bool]:
        """快速检查Docker容器状态"""
        containers = ['emc_postgres', 'emc_neo4j', 'emc_redis']
        status = {}
        
        try:
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            running_containers = result.stdout
            
            for container in containers:
                status[container] = container in running_containers
                
        except Exception as e:
            print(f"Docker检查失败: {e}")
            return {container: False for container in containers}
        
        return status
    
    def test_postgres_connection(self) -> Tuple[bool, str]:
        """PostgreSQL连接测试 - 高效实用"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="emc_knowledge", 
                user="postgres",
                password=self.config['postgres_password'],
                connect_timeout=5
            )
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT current_database(), version()")
                row = cursor.fetchone()
                if row is None:
                    conn.close()
                    return False, "未能获取数据库信息"
                db_name, version = row
                
            conn.close()
            return True, f"连接成功 - 数据库: {db_name}"
            
        except ImportError:
            return False, "psycopg2模块未安装: pip install psycopg2-binary"
        except Exception as e:
            return False, f"连接失败: {str(e)}"
    
    def test_neo4j_connection(self) -> Tuple[bool, str]:
        """Neo4j连接测试 - 实用优先"""
        try:
            from neo4j import GraphDatabase
            
            driver = GraphDatabase.driver(
                "bolt://localhost:7687",
                auth=("neo4j", self.config['neo4j_password'])
            )
            
            with driver.session() as session:
                result = session.run("CALL dbms.components() YIELD name, versions RETURN name, versions[0] as version")
                info = result.single()
                
            driver.close()
            return True, f"连接成功 - {info['name']} {info['version']}"
            
        except ImportError:
            return False, "neo4j模块未安装: pip install neo4j"
        except Exception as e:
            return False, f"连接失败: {str(e)}"
    
    def test_redis_connection(self) -> Tuple[bool, str]:
        """Redis连接测试 - 简洁高效"""
        try:
            import redis
            
            r = redis.Redis(
                host='localhost',
                port=6379,
                password=self.config['redis_password'],
                decode_responses=True,
                socket_timeout=5
            )
            
            # 测试基本操作
            r.set('emc_test', 'connection_ok', ex=10)
            value = r.get('emc_test')
            r.delete('emc_test')
            
            info = r.info('server')
            version = info['redis_version']
            
            return True, f"连接成功 - Redis {version}"
            
        except ImportError:
            return False, "redis模块未安装: pip install redis"
        except Exception as e:
            return False, f"连接失败: {str(e)}"
    
    def run_comprehensive_check(self) -> Dict[str, Dict[str, object]]:
        """运行完整检查 - 实用报告生成"""
        print("🔍 EMC数据库连接检查")
        print("=" * 40)
        
        # Docker容器检查
        container_status = self.check_docker_containers()
        
        # 数据库连接测试
        tests = [
            ("PostgreSQL", self.test_postgres_connection),
            ("Neo4j", self.test_neo4j_connection),
            ("Redis", self.test_redis_connection)
        ]
        
        results = {}
        success_count = 0
        
        for name, test_func in tests:
            success, message = test_func()
            container_name = f"emc_{name.lower()}"
            container_running = container_status.get(container_name, False)
            
            status_icon = "✅" if success else "❌"
            container_icon = "🟢" if container_running else "🔴"
            
            print(f"{status_icon} {name}: {message}")
            print(f"   {container_icon} 容器状态: {'运行中' if container_running else '未运行'}")
            
            results[name] = {
                'connection_success': success,
                'container_running': container_running, 
                'message': message
            }
            
            if success:
                success_count += 1
        
        # 生成实用建议
        if success_count == len(tests):
            print("\n🎉 所有数据库连接正常！")
            print("📍 可以启动EMC应用服务")
        else:
            print(f"\n⚠️  {success_count}/{len(tests)} 服务正常")
            self._print_fix_suggestions(results)
        
        return results
    
    def _print_fix_suggestions(self, results: Dict) -> None:
        """生成实用的修复建议"""
        print("\n🔧 修复建议:")
        
        # 检查是否有容器未运行
        containers_down = [name for name, info in results.items() 
                          if not info['container_running']]
        
        if containers_down:
            print("   启动服务: docker-compose up -d")
        
        # 检查连接失败的具体建议
        for name, info in results.items():
            if not info['connection_success']:
                if "模块未安装" in info['message']:
                    print(f"   安装{name}依赖: pip install -r requirements.txt")
                elif "密码" in info['message']:
                    print(f"   检查{name}密码配置")


def main():
    """主函数 - 直接运行检查"""
    checker = DatabaseChecker()
    results = checker.run_comprehensive_check()
    
    # 返回状态码，便于脚本集成
    all_success = all(isinstance(info, dict) and info.get('connection_success', False) for info in results.values())
    sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    main()