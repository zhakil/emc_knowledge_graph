"""
认证授权中间件
提供JWT认证、RBAC权限控制和会话管理
"""

import jwt
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from functools import wraps

from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from data_access.connections.redis_connection import redis_conn
from data_access.repositories.user_repository import UserRepository
from data_access.connections.database_connection import db_connection
from ..config import get_settings


logger = logging.getLogger(__name__)
security = HTTPBearer()


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        self.settings = get_settings()
        
        # 不需要认证的路径
        self.public_paths = {
            "/docs", "/redoc", "/openapi.json",
            "/health", "/", "/static"
        }
        
        # 需要认证但不需要特殊权限的路径
        self.protected_paths = {
            "/api/deepseek", "/api/graph", "/api/files"
        }
        
        # 需要管理员权限的路径
        self.admin_paths = {
            "/api/admin", "/api/system"
        }
    
    async def dispatch(self, request: Request, call_next):
        """中间件主要逻辑"""
        path = request.url.path
        
        # 检查是否是公共路径
        if any(path.startswith(public_path) for public_path in self.public_paths):
            return await call_next(request)
        
        # 检查是否需要认证
        if any(path.startswith(protected_path) for protected_path in self.protected_paths):
            try:
                # 验证JWT token
                token = self._extract_token(request)
                if not token:
                    return self._unauthorized_response("缺少认证token")
                
                user_info = await self._verify_token(token)
                if not user_info:
                    return self._unauthorized_response("无效的认证token")
                
                # 将用户信息添加到请求中
                request.state.user = user_info
                
                # 检查管理员权限
                if any(path.startswith(admin_path) for admin_path in self.admin_paths):
                    if user_info.get("role") != "admin":
                        return self._forbidden_response("需要管理员权限")
                
                # 记录用户活动
                await self._log_user_activity(user_info, request)
                
            except Exception as e:
                logger.error(f"认证中间件错误: {str(e)}")
                return self._unauthorized_response("认证失败")
        
        response = await call_next(request)
        return response
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """从请求中提取JWT token"""
        # 从Authorization header提取
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]
        
        # 从cookie提取（如果需要）
        token_cookie = request.cookies.get("access_token")
        if token_cookie:
            return token_cookie
        
        return None
    
    async def _verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证JWT token"""
        try:
            # 解码JWT
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=[self.settings.jwt_algorithm]
            )
            
            # 检查过期时间
            if payload.get("exp", 0) < time.time():
                return None
            
            # 检查token是否在黑名单中
            if await self._is_token_blacklisted(token):
                return None
            
            # 从数据库获取用户信息
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            user_info = await self._get_user_info(user_id)
            if not user_info or not user_info.get("is_active"):
                return None
            
            return user_info
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"无效的JWT token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Token验证错误: {str(e)}")
            return None
    
    async def _is_token_blacklisted(self, token: str) -> bool:
        """检查token是否在黑名单中"""
        try:
            with redis_conn.sync_client() as client:
                return bool(client.get(f"blacklist:{token}"))
        except Exception:
            return False
    
    async def _get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """从数据库获取用户信息"""
        try:
            with db_connection.sync_session() as session:
                user_repo = UserRepository(session)
                user = user_repo.get_user_by_id(int(user_id))
                
                return {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "is_active": user.is_active
                }
        except Exception as e:
            logger.error(f"获取用户信息错误: {str(e)}")
            return None
    
    async def _log_user_activity(self, user_info: Dict[str, Any], request: Request):
        """记录用户活动"""
        try:
            activity_data = {
                "user_id": user_info["id"],
                "username": user_info["username"],
                "path": request.url.path,
                "method": request.method,
                "ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", ""),
                "timestamp": datetime.now().isoformat()
            }
            
            # 使用Redis记录最近活动
            with redis_conn.sync_client() as client:
                key = f"user_activity:{user_info['id']}"
                client.lpush(key, str(activity_data))
                client.ltrim(key, 0, 99)  # 保留最近100条活动
                client.expire(key, 86400 * 7)  # 7天过期
                
        except Exception as e:
            logger.error(f"记录用户活动失败: {str(e)}")
    
    def _unauthorized_response(self, message: str) -> Response:
        """返回401未授权响应"""
        return Response(
            content=f'{{"detail": "{message}"}}',
            status_code=401,
            headers={"content-type": "application/json"}
        )
    
    def _forbidden_response(self, message: str) -> Response:
        """返回403禁止访问响应"""
        return Response(
            content=f'{{"detail": "{message}"}}',
            status_code=403,
            headers={"content-type": "application/json"}
        )


class JWTManager:
    """JWT管理器"""
    
    def __init__(self):
        self.settings = get_settings()
    
    def create_access_token(
        self,
        user_id: int,
        username: str,
        role: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """创建访问token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.settings.jwt_expire_minutes
            )
        
        payload = {
            "sub": str(user_id),
            "username": username,
            "role": role,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        return jwt.encode(
            payload,
            self.settings.secret_key,
            algorithm=self.settings.jwt_algorithm
        )
    
    def create_refresh_token(self, user_id: int) -> str:
        """创建刷新token"""
        expire = datetime.utcnow() + timedelta(days=30)  # 刷新token有效期30天
        
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        return jwt.encode(
            payload,
            self.settings.secret_key,
            algorithm=self.settings.jwt_algorithm
        )
    
    def verify_refresh_token(self, token: str) -> Optional[int]:
        """验证刷新token"""
        try:
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=[self.settings.jwt_algorithm]
            )
            
            if payload.get("type") != "refresh":
                return None
            
            return int(payload.get("sub"))
            
        except jwt.InvalidTokenError:
            return None
    
    async def blacklist_token(self, token: str):
        """将token加入黑名单"""
        try:
            # 解码token获取过期时间
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=[self.settings.jwt_algorithm],
                options={"verify_exp": False}
            )
            
            exp_timestamp = payload.get("exp", 0)
            current_timestamp = time.time()
            
            # 只有未过期的token才需要加入黑名单
            if exp_timestamp > current_timestamp:
                ttl = int(exp_timestamp - current_timestamp)
                
                with redis_conn.sync_client() as client:
                    client.setex(f"blacklist:{token}", ttl, "1")
                    
        except Exception as e:
            logger.error(f"Token黑名单操作失败: {str(e)}")


class RBACManager:
    """基于角色的访问控制管理器"""
    
    # 权限定义
    PERMISSIONS = {
        "admin": [
            "system:read", "system:write", "system:delete",
            "user:read", "user:write", "user:delete",
            "graph:read", "graph:write", "graph:delete",
            "file:read", "file:write", "file:delete",
            "ai:read", "ai:write"
        ],
        "engineer": [
            "graph:read", "graph:write",
            "file:read", "file:write",
            "ai:read", "ai:write"
        ],
        "technician": [
            "graph:read",
            "file:read", "file:write",
            "ai:read"
        ],
        "viewer": [
            "graph:read",
            "file:read",
            "ai:read"
        ],
        "guest": [
            "graph:read"
        ]
    }
    
    @classmethod
    def has_permission(cls, user_role: str, required_permission: str) -> bool:
        """检查用户角色是否有指定权限"""
        user_permissions = cls.PERMISSIONS.get(user_role, [])
        return required_permission in user_permissions
    
    @classmethod
    def check_permissions(cls, user_role: str, required_permissions: List[str]) -> bool:
        """检查用户角色是否有所有指定权限"""
        user_permissions = cls.PERMISSIONS.get(user_role, [])
        return all(perm in user_permissions for perm in required_permissions)


# 依赖注入函数
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """获取当前认证用户"""
    if not credentials:
        raise HTTPException(status_code=401, detail="缺少认证凭据")
    
    token = credentials.credentials
    settings = get_settings()
    
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="无效的token")
        
        # 从数据库获取用户信息
        with db_connection.sync_session() as session:
            user_repo = UserRepository(session)
            user = user_repo.get_user_by_id(int(user_id))
            
            if not user.is_active:
                raise HTTPException(status_code=401, detail="用户账户已禁用")
            
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active
            }
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的token")
    except Exception as e:
        logger.error(f"用户认证错误: {str(e)}")
        raise HTTPException(status_code=401, detail="认证失败")


async def get_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取管理员用户（需要管理员权限）"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user


def require_permissions(*required_permissions: str):
    """权限装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取current_user
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(status_code=401, detail="未认证用户")
            
            user_role = current_user.get("role")
            if not RBACManager.check_permissions(user_role, list(required_permissions)):
                raise HTTPException(
                    status_code=403,
                    detail=f"需要权限: {', '.join(required_permissions)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class SessionManager:
    """会话管理器"""
    
    @staticmethod
    async def create_session(user_id: int, device_info: Dict[str, Any]) -> str:
        """创建用户会话"""
        session_id = f"session:{user_id}:{int(time.time())}"
        
        session_data = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "device_info": device_info,
            "is_active": True
        }
        
        try:
            with redis_conn.sync_client() as client:
                client.hset(session_id, mapping=session_data)
                client.expire(session_id, 86400)  # 24小时过期
                
                # 记录用户的活跃会话
                user_sessions_key = f"user_sessions:{user_id}"
                client.sadd(user_sessions_key, session_id)
                client.expire(user_sessions_key, 86400)
                
            return session_id
            
        except Exception as e:
            logger.error(f"创建会话失败: {str(e)}")
            raise
    
    @staticmethod
    async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        try:
            with redis_conn.sync_client() as client:
                session_data = client.hgetall(session_id)
                return session_data if session_data else None
        except Exception as e:
            logger.error(f"获取会话失败: {str(e)}")
            return None
    
    @staticmethod
    async def update_session_activity(session_id: str):
        """更新会话活动时间"""
        try:
            with redis_conn.sync_client() as client:
                client.hset(session_id, "last_activity", datetime.now().isoformat())
                client.expire(session_id, 86400)
        except Exception as e:
            logger.error(f"更新会话活动时间失败: {str(e)}")
    
    @staticmethod
    async def terminate_session(session_id: str):
        """终止会话"""
        try:
            with redis_conn.sync_client() as client:
                session_data = client.hgetall(session_id)
                if session_data:
                    user_id = session_data.get("user_id")
                    if user_id:
                        client.srem(f"user_sessions:{user_id}", session_id)
                
                client.delete(session_id)
                
        except Exception as e:
            logger.error(f"终止会话失败: {str(e)}")
    
    @staticmethod
    async def get_user_sessions(user_id: int) -> List[str]:
        """获取用户的所有活跃会话"""
        try:
            with redis_conn.sync_client() as client:
                return list(client.smembers(f"user_sessions:{user_id}"))
        except Exception as e:
            logger.error(f"获取用户会话失败: {str(e)}")
            return []


# 全局实例
jwt_manager = JWTManager()
rbac_manager = RBACManager()
session_manager = SessionManager()