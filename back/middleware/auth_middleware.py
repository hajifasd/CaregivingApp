"""
认证中间件
用于保护需要认证的API端点
"""

from flask import request, jsonify, g
from functools import wraps
import jwt
import os
from datetime import datetime

def require_auth_middleware(f):
    """认证中间件装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 获取token
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'success': False, 'message': 'Token格式错误'}), 401
        
        if not token:
            return jsonify({'success': False, 'message': '缺少认证token'}), 401
        
        try:
            # 验证token
            secret_key = os.getenv('APP_SECRET', 'dev-secret-key-change-in-production')
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # 将用户信息存储到g对象中
            g.current_user = {
                'user_id': data['user_id'],
                'user_type': data['user_type'],
                'name': data.get('name', '')
            }
            
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Token无效'}), 401
        except Exception as e:
            return jsonify({'success': False, 'message': f'认证失败: {str(e)}'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_user_auth(f):
    """用户认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 先进行基础认证
        auth_result = require_auth_middleware(f)(*args, **kwargs)
        
        # 如果认证失败，直接返回
        if isinstance(auth_result, tuple) and auth_result[1] != 200:
            return auth_result
        
        # 检查用户类型
        if g.current_user['user_type'] != 'user':
            return jsonify({'success': False, 'message': '权限不足，需要用户权限'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_caregiver_auth(f):
    """护工认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 先进行基础认证
        auth_result = require_auth_middleware(f)(*args, **kwargs)
        
        # 如果认证失败，直接返回
        if isinstance(auth_result, tuple) and auth_result[1] != 200:
            return auth_result
        
        # 检查用户类型
        if g.current_user['user_type'] != 'caregiver':
            return jsonify({'success': False, 'message': '权限不足，需要护工权限'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_admin_auth(f):
    """管理员认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 先进行基础认证
        auth_result = require_auth_middleware(f)(*args, **kwargs)
        
        # 如果认证失败，直接返回
        if isinstance(auth_result, tuple) and auth_result[1] != 200:
            return auth_result
        
        # 检查用户类型
        if g.current_user['user_type'] != 'admin':
            return jsonify({'success': False, 'message': '权限不足，需要管理员权限'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function



