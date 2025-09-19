"""
护工资源管理系统 - 认证API
====================================

用户登录、注册等认证相关接口
"""

from flask import Blueprint, request, jsonify
from services.user_service import UserService
from utils.auth import generate_token
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/user/login', methods=['POST'])
def user_login():
    """用户登录接口"""
    data = request.json
    account = data.get('email')  # 前端可能发送email字段，但实际是手机号
    password = data.get('password')

    if not account or not password:
        return jsonify({'success': False, 'message': '请输入账号和密码'}), 400

    # 验证用户
    user = UserService.verify_user(account, password)
    
    if user:
        token = generate_token(user.id, 'user', user.fullname)
        return jsonify({
            'success': True,
            'data': {'token': token, 'user': user.to_dict()},
            'message': '登录成功'
        })
    elif (UserService.get_user_by_email(account) or UserService.get_user_by_phone(account)):
        return jsonify({'success': False, 'message': '您的申请尚未通过审核'}), 403
    else:
        return jsonify({'success': False, 'message': '账号或密码错误'}), 401

@auth_bp.route('/api/register', methods=['POST'])
def user_register():
    """用户注册接口"""
    data = request.json
    fullname = data.get('fullname')
    phone = data.get('phone')
    password = data.get('password')

    if not fullname or not fullname.strip():
        return jsonify({'code': 400, 'message': '请输入您的真实姓名'}), 400

    if not phone or not phone.strip():
        return jsonify({'code': 400, 'message': '请输入手机号码'}), 400

    if not password or len(password) < 6:
        return jsonify({'code': 400, 'message': '密码长度不能少于6位'}), 400

    # 检查手机号是否已被注册
    if UserService.get_user_by_phone(phone):
        return jsonify({'code': 400, 'message': '该手机号已被注册'}), 400

    try:
        # 生成临时邮箱
        import time
        temp_email = f"user_{phone}_{int(time.time())}@temp.com"
        
        user = UserService.create_user(temp_email, password, fullname, phone)
        return jsonify({
            'code': 200,
            'data': user.to_dict(),
            'message': '注册成功，等待管理员审核'
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'注册失败：{str(e)}'}), 500

@auth_bp.route('/api/login/admin', methods=['POST'])
def admin_login():
    """管理员登录接口"""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': '请输入用户名和密码'}), 400

    # 从配置文件获取管理员凭据
    from config.settings import ADMIN_USERNAME, ADMIN_PASSWORD
    
    # 验证管理员凭据
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        token = generate_token(0, 'admin')
        return jsonify({
            'success': True,
            'data': {'token': token},
            'message': '登录成功'
        })
    return jsonify({'success': False, 'message': '用户名或密码错误'}), 401 