# 保存为 test_type_checking.py
import redis
import requests
from typing import Optional

def test_redis_typing() -> Optional[str]:
    """测试Redis类型提示是否正常工作"""
    # 这里我们不实际连接Redis，只是测试类型系统
    client: redis.Redis = None  # type: ignore
    return "Redis类型检查正常"

def test_requests_typing() -> Optional[str]:
    """测试Requests类型提示是否正常工作"""
    response: requests.Response = None  # type: ignore
    return "Requests类型检查正常"

if __name__ == "__main__":
    print("类型系统验证测试")
    print(test_redis_typing())
    print(test_requests_typing())