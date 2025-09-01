"""
护工资源管理系统 - 认证工具函数
====================================

包含密码加密、JWT令牌生成和验证等认证相关功能
"""

import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import sys
import os

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from back.config.settings import APP_SECRET, JWT_EXPIRATION_HOURS

def hash_password(password: str) -> str:
    """使用bcrypt加密密码
    
    Args:
        password: 明文密码
        
    Returns:
        str: 加密后的密码哈希
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(hashed_password: str, input_password: str) -> bool:
    """验证密码是否正确
    
    Args:
        hashed_password: 存储的密码哈希
        input_password: 输入的密码
        
    Returns:
        bool: 密码是否正确
    """
    return bcrypt.checkpw(input_password.encode(), hashed_password.encode())

def generate_token(user_id: int, user_type: str = 'user') -> str:
    """生成JWT认证令牌
    
    Args:
        user_id: 用户ID
        user_type: 用户类型（user, caregiver, admin）
        
    Returns:
        str: JWT令牌字符串
    """
    payload = {
        "user_id": user_id,
        "user_type": user_type,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, APP_SECRET, algorithm="HS256")

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """验证JWT令牌
    
    Args:
        token: JWT令牌字符串
        
    Returns:
        Optional[Dict]: 解码后的载荷信息，验证失败返回None
    """
    try:
        return jwt.decode(token, APP_SECRET, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None 