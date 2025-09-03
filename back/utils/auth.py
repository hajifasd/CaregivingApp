"""
护工资源管理系统 - 认证工具
====================================

处理JWT token的生成、验证等认证相关功能
"""

import jwt
import logging
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, g
from config.settings import FLASK_SECRET_KEY

logger = logging.getLogger(__name__)

def generate_token(user_id, user_type, expires_in=24*60*60):
    """生成JWT token
    
    Args:
        user_id: 用户ID
        user_type: 用户类型 ('user', 'caregiver', 'admin')
        expires_in: 过期时间（秒），默认24小时
    
    Returns:
        str: JWT token
    """
    try:
        payload = {
            'user_id': user_id,
            'user_type': user_type,
            'exp': datetime.now(timezone.utc) + timedelta(seconds=expires_in),
            'iat': datetime.now(timezone.utc)
        }
        
        token = jwt.encode(payload, FLASK_SECRET_KEY, algorithm='HS256')
        return token
        
    except Exception as e:
        logger.error(f"生成token失败: {str(e)}")
        return None

def verify_token(token):
    """验证JWT token
    
    Args:
        token: JWT token字符串
    
    Returns:
        dict: token载荷信息，验证失败返回None
    """
    try:
        payload = jwt.decode(token, FLASK_SECRET_KEY, algorithms=['HS256'])
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token已过期")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"无效的token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"验证token失败: {str(e)}")
        return None

def require_auth(token, expected_user_type=None):
    """验证认证token
    
    Args:
        token: JWT token字符串
        expected_user_type: 期望的用户类型，如果为None则不检查用户类型
    
    Returns:
        int: 用户ID，验证失败返回None
    """
    try:
        payload = verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get('user_id')
        user_type = payload.get('user_type')
        
        if not user_id or not user_type:
            return None
        
        # 如果指定了期望的用户类型，则验证
        if expected_user_type and user_type != expected_user_type:
            logger.warning(f"用户类型不匹配: 期望 {expected_user_type}, 实际 {user_type}")
            return None
        
        return user_id
        
    except Exception as e:
        logger.error(f"认证验证失败: {str(e)}")
        return None

def auth_required(expected_user_type=None):
    """认证装饰器
    
    Args:
        expected_user_type: 期望的用户类型，如果为None则不检查用户类型
    
    Returns:
        function: 装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 获取token
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'success': False, 'message': '未提供认证令牌'}), 401
            
            token = auth_header.split(' ')[1]
            
            # 验证token
            user_id = require_auth(token, expected_user_type)
            if not user_id:
                return jsonify({'success': False, 'message': '无效的认证令牌'}), 401
            
            # 将用户信息存储到g对象中
            g.user_id = user_id
            g.user_type = expected_user_type or 'unknown'
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def get_current_user():
    """获取当前认证用户信息
    
    Returns:
        dict: 包含user_id和user_type的字典
    """
    return {
        'user_id': getattr(g, 'user_id', None),
        'user_type': getattr(g, 'user_type', None)
    }

def is_authenticated():
    """检查用户是否已认证
    
    Returns:
        bool: 是否已认证
    """
    return hasattr(g, 'user_id') and g.user_id is not None

def require_user_auth():
    """要求用户认证的装饰器"""
    return auth_required('user')

def require_caregiver_auth():
    """要求护工认证的装饰器"""
    return auth_required('caregiver')

def require_admin_auth():
    """要求管理员认证的装饰器"""
    return auth_required('admin')

def optional_auth():
    """可选的认证装饰器，不强制要求认证"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 获取token
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                user_id = require_auth(token)
                if user_id:
                    g.user_id = user_id
                    g.user_type = 'authenticated'
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator 