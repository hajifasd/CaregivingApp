"""
护工资源管理系统 - 护工API
====================================

护工相关的API接口，包括登录、个人信息管理等
"""

from flask import Blueprint, request, jsonify
from services.caregiver_service import CaregiverService
from utils.auth import generate_token, verify_token
from functools import wraps

caregiver_bp = Blueprint('caregiver', __name__)

def require_caregiver_auth(f):
    """护工认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未提供认证令牌'}), 401
        
        token = token.split(' ')[1]
        payload = verify_token(token)
        
        if not payload or payload.get('user_type') != 'caregiver':
            return jsonify({'success': False, 'message': '无效的认证令牌或用户类型不匹配'}), 401
        
        caregiver_id = payload.get('user_id')
        
        # 验证护工是否存在且已审核通过
        caregiver = CaregiverService.get_caregiver_by_id(caregiver_id)
        if not caregiver or not caregiver.get('is_approved'):
            return jsonify({'success': False, 'message': '护工不存在或未通过审核'}), 403
        
        request.caregiver_id = caregiver_id
        return f(*args, **kwargs)
    
    return decorated_function

@caregiver_bp.route('/api/caregiver/login', methods=['POST'])
def caregiver_login():
    """护工登录接口"""
    data = request.json
    phone = data.get('phone')
    password = data.get('password')

    if not phone or not password:
        return jsonify({'success': False, 'message': '请输入手机号码和密码'}), 400

    # 验证护工
    caregiver = CaregiverService.verify_caregiver(phone, password)
    
    if caregiver:
        token = generate_token(caregiver['id'], 'caregiver', caregiver.get('name'))
        return jsonify({
            'success': True,
            'data': {'token': token, 'caregiver': caregiver},
            'message': '登录成功'
        })
    elif CaregiverService.get_caregiver_by_phone(phone):
        return jsonify({'success': False, 'message': '您的申请尚未通过审核'}), 403
    else:
        return jsonify({'success': False, 'message': '手机号码或密码错误'}), 401

@caregiver_bp.route('/api/caregiver/register', methods=['POST'])
def caregiver_register():
    """护工注册接口"""
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    password = data.get('password')
    gender = data.get('gender')
    age = data.get('age')
    experience_years = data.get('experience_years', 0)
    hourly_rate = data.get('hourly_rate')
    qualification = data.get('qualification', '')
    introduction = data.get('introduction', '')

    if not name or not name.strip():
        return jsonify({'success': False, 'message': '请输入您的真实姓名'}), 400

    if not phone or not phone.strip():
        return jsonify({'success': False, 'message': '请输入手机号码'}), 400

    if not password or len(password) < 6:
        return jsonify({'success': False, 'message': '密码长度不能少于6位'}), 400

    try:
        # 创建护工，传递所有可选字段
        caregiver = CaregiverService.create_caregiver(
            name=name,
            phone=phone,
            password=password,
            gender=gender,
            age=age,
            experience_years=experience_years,
            hourly_rate=hourly_rate,
            qualification=qualification,
            introduction=introduction
        )
        
        if caregiver:
            return jsonify({
                'success': True,
                'data': caregiver,
                'message': '注册成功，等待管理员审核'
            })
        else:
            return jsonify({'success': False, 'message': '注册失败'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'注册失败：{str(e)}'}), 500

@caregiver_bp.route('/api/caregiver/verify', methods=['GET'])
def verify_caregiver_token():
    """验证护工token"""
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({'success': False, 'message': '未提供认证令牌'}), 401
    
    token = token.split(' ')[1]
    payload = verify_token(token)
    
    if not payload or payload.get('user_type') != 'caregiver':
        return jsonify({'success': False, 'message': '无效的认证令牌'}), 401
    
    caregiver_id = payload.get('user_id')
    caregiver = CaregiverService.get_caregiver_by_id(caregiver_id)
    
    if not caregiver:
        return jsonify({'success': False, 'message': '护工不存在'}), 404
    
    return jsonify({
        'success': True,
        'data': caregiver,
        'message': 'token验证成功'
    })

@caregiver_bp.route('/api/caregiver/profile', methods=['GET'])
@require_caregiver_auth
def get_caregiver_profile():
    """获取护工个人信息"""
    caregiver_id = request.caregiver_id
    caregiver = CaregiverService.get_caregiver_by_id(caregiver_id)
    
    if not caregiver:
        return jsonify({'success': False, 'message': '护工不存在'}), 404
    
    return jsonify({
        'success': True,
        'data': caregiver,
        'message': '获取个人信息成功'
    })

@caregiver_bp.route('/api/caregiver/profile', methods=['PUT'])
@require_caregiver_auth
def update_caregiver_profile():
    """更新护工个人信息"""
    caregiver_id = request.caregiver_id
    data = request.json
    
    # 验证必填字段
    if not data.get('name'):
        return jsonify({'success': False, 'message': '姓名不能为空'}), 400
    
    try:
        caregiver = CaregiverService.update_caregiver_profile(caregiver_id, data)
        if caregiver:
            return jsonify({
                'success': True,
                'data': caregiver,
                'message': '个人信息更新成功'
            })
        else:
            return jsonify({'success': False, 'message': '更新失败'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新失败：{str(e)}'}), 500

@caregiver_bp.route('/api/caregiver/dashboard', methods=['GET'])
@require_caregiver_auth
def get_caregiver_dashboard():
    """获取护工仪表盘数据"""
    caregiver_id = request.caregiver_id
    
    try:
        dashboard_data = CaregiverService.get_caregiver_dashboard_data(caregiver_id)
        return jsonify({
            'success': True,
            'data': dashboard_data,
            'message': '获取仪表盘数据成功'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取数据失败：{str(e)}'}), 500

@caregiver_bp.route('/api/caregiver/availability', methods=['PUT'])
@require_caregiver_auth
def update_caregiver_availability():
    """更新护工可用状态"""
    caregiver_id = request.caregiver_id
    data = request.json
    available = data.get('available', True)
    
    try:
        success = CaregiverService.update_caregiver_availability(caregiver_id, available)
        if success:
            return jsonify({
                'success': True,
                'message': '状态更新成功'
            })
        else:
            return jsonify({'success': False, 'message': '更新失败'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新失败：{str(e)}'}), 500

@caregiver_bp.route('/api/caregiver/password', methods=['PUT'])
@require_caregiver_auth
def update_caregiver_password():
    """修改护工密码"""
    caregiver_id = request.caregiver_id
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'success': False, 'message': '请输入当前密码和新密码'}), 400
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': '新密码长度不能少于6位'}), 400
    
    try:
        success = CaregiverService.update_caregiver_password(caregiver_id, current_password, new_password)
        if success:
            return jsonify({
                'success': True,
                'message': '密码修改成功'
            })
        else:
            return jsonify({'success': False, 'message': '当前密码错误'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'密码修改失败：{str(e)}'}), 500

# 管理员相关接口
@caregiver_bp.route('/api/caregiver/approve/<int:caregiver_id>', methods=['POST'])
def approve_caregiver(caregiver_id):
    """审核通过护工（管理员接口）"""
    # 这里应该添加管理员权限验证
    try:
        success = CaregiverService.approve_caregiver(caregiver_id)
        if success:
            return jsonify({
                'success': True,
                'message': '护工审核通过'
            })
        else:
            return jsonify({'success': False, 'message': '审核失败'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'审核失败：{str(e)}'}), 500

@caregiver_bp.route('/api/caregiver/reject/<int:caregiver_id>', methods=['POST'])
def reject_caregiver(caregiver_id):
    """拒绝护工申请（管理员接口）"""
    # 这里应该添加管理员权限验证
    try:
        success = CaregiverService.reject_caregiver(caregiver_id)
        if success:
            return jsonify({
                'success': True,
                'message': '护工申请已拒绝'
            })
        else:
            return jsonify({'success': False, 'message': '操作失败'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'操作失败：{str(e)}'}), 500

@caregiver_bp.route('/api/caregiver/pending', methods=['GET'])
def get_pending_caregivers():
    """获取待审核护工列表（管理员接口）"""
    # 这里应该添加管理员权限验证
    try:
        caregivers = CaregiverService.get_pending_caregivers()
        return jsonify({
            'success': True,
            'data': caregivers,
            'message': '获取待审核护工列表成功'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取失败：{str(e)}'}), 500

@caregiver_bp.route('/api/caregiver/approved', methods=['GET'])
def get_approved_caregivers():
    """获取已审核护工列表（管理员接口）"""
    # 这里应该添加管理员权限验证
    try:
        caregivers = CaregiverService.get_approved_caregivers()
        return jsonify({
            'success': True,
            'data': caregivers,
            'message': '获取已审核护工列表成功'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取失败：{str(e)}'}), 500

@caregiver_bp.route('/api/caregiver/search', methods=['GET'])
def search_caregivers():
    """搜索护工接口
    
    支持按姓名、手机号等关键词搜索已审核通过的护工
    """
    try:
        keyword = request.args.get('keyword', '').strip()
        limit = request.args.get('limit', 20, type=int)
        
        # 限制最大返回数量
        if limit > 50:
            limit = 50
        
        caregivers = CaregiverService.search_caregivers(keyword, limit)
        
        return jsonify({
            'success': True,
            'data': caregivers,
            'message': f'搜索到 {len(caregivers)} 位护工',
            'total': len(caregivers)
        })
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'搜索失败：{str(e)}'
        }), 500
