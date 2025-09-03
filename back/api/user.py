"""
护工资源管理系统 - 用户业务API
====================================

用户端的核心业务功能，包括护工搜索、预约、聘用、聊天等
"""

from flask import Blueprint, request, jsonify, g
from services.user_service import UserService
from services.caregiver_service import CaregiverService
from services.appointment_service import AppointmentService
from services.employment_service import EmploymentService
from services.message_service import MessageService
from utils.auth import require_auth
from functools import wraps
import logging

logger = logging.getLogger(__name__)
user_bp = Blueprint('user', __name__)

def require_user_auth(f):
    """用户认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未提供认证令牌'}), 401
        
        token = token.split(' ')[1]
        user_id = require_auth(token, 'user')
        if not user_id:
            return jsonify({'success': False, 'message': '无效的认证令牌'}), 401
        
        request.user_id = user_id
        return f(*args, **kwargs)
    
    return decorated_function

# ==================== 护工搜索和浏览 ====================

@user_bp.route('/api/user/caregivers', methods=['GET'])
def search_caregivers():
    """搜索护工接口"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        service_type = request.args.get('service_type', '')
        city = request.args.get('city', '')
        min_rate = request.args.get('min_rate', type=float)
        max_rate = request.args.get('max_rate', type=float)
        experience = request.args.get('experience', '')
        gender = request.args.get('gender', '')
        
        # 调用服务层搜索护工
        result = CaregiverService.search_caregivers(
            page=page,
            per_page=per_page,
            service_type=service_type,
            city=city,
            min_rate=min_rate,
            max_rate=max_rate,
            experience=experience,
            gender=gender
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '搜索成功'
        })
        
    except Exception as e:
        logger.error(f"搜索护工失败: {str(e)}")
        return jsonify({'success': False, 'message': '搜索失败，请稍后重试'}), 500

@user_bp.route('/api/user/caregivers/<int:caregiver_id>', methods=['GET'])
def get_caregiver_detail(caregiver_id):
    """获取护工详细信息"""
    try:
        caregiver = CaregiverService.get_caregiver_by_id(caregiver_id)
        if not caregiver:
            return jsonify({'success': False, 'message': '护工不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': caregiver,
            'message': '获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取护工详情失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取失败，请稍后重试'}), 500

# ==================== 预约管理 ====================

@user_bp.route('/api/user/appointments', methods=['POST'])
@require_user_auth
def create_appointment():
    """创建预约"""
    try:
        data = request.json
        user_id = request.user_id
        
        # 验证必要字段
        required_fields = ['caregiver_id', 'service_type', 'date', 'start_time', 'end_time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'缺少必要字段: {field}'}), 400
        
        # 创建预约
        appointment = AppointmentService.create_appointment(
            user_id=user_id,
            caregiver_id=data['caregiver_id'],
            service_type=data['service_type'],
            date=data['date'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            notes=data.get('notes', '')
        )
        
        if appointment:
            return jsonify({
                'success': True,
                'data': appointment,
                'message': '预约创建成功，等待护工确认'
            })
        else:
            return jsonify({'success': False, 'message': '预约创建失败'}), 500
            
    except Exception as e:
        logger.error(f"创建预约失败: {str(e)}")
        return jsonify({'success': False, 'message': '预约创建失败，请稍后重试'}), 500

@user_bp.route('/api/user/appointments', methods=['GET'])
@require_user_auth
def get_user_appointments():
    """获取用户的预约列表"""
    try:
        user_id = request.user_id
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', '')
        
        appointments = AppointmentService.get_user_appointments(
            user_id=user_id,
            page=page,
            per_page=per_page,
            status=status
        )
        
        return jsonify({
            'success': True,
            'data': appointments,
            'message': '获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取预约列表失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取失败，请稍后重试'}), 500

@user_bp.route('/api/user/appointments/<int:appointment_id>', methods=['PUT'])
@require_user_auth
def update_appointment(appointment_id):
    """更新预约状态"""
    try:
        user_id = request.user_id
        data = request.json
        action = data.get('action')  # cancel, confirm, complete
        
        if action == 'cancel':
            result = AppointmentService.cancel_appointment(appointment_id, user_id)
        elif action == 'confirm':
            result = AppointmentService.confirm_appointment(appointment_id, user_id)
        elif action == 'complete':
            result = AppointmentService.complete_appointment(appointment_id, user_id)
        else:
            return jsonify({'success': False, 'message': '无效的操作'}), 400
        
        if result:
            return jsonify({
                'success': True,
                'message': '操作成功'
            })
        else:
            return jsonify({'success': False, 'message': '操作失败'}), 500
            
    except Exception as e:
        logger.error(f"更新预约失败: {str(e)}")
        return jsonify({'success': False, 'message': '操作失败，请稍后重试'}), 500

# ==================== 长期聘用 ====================

@user_bp.route('/api/user/employments', methods=['POST'])
@require_user_auth
def create_employment():
    """创建长期聘用"""
    try:
        data = request.json
        user_id = request.user_id
        
        # 验证必要字段
        required_fields = ['caregiver_id', 'service_type', 'start_date', 'frequency', 'duration_per_session']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'缺少必要字段: {field}'}), 400
        
        # 创建聘用关系
        employment = EmploymentService.create_employment(
            user_id=user_id,
            caregiver_id=data['caregiver_id'],
            service_type=data['service_type'],
            start_date=data['start_date'],
            end_date=data.get('end_date'),
            frequency=data['frequency'],
            duration_per_session=data['duration_per_session'],
            notes=data.get('notes', '')
        )
        
        if employment:
            return jsonify({
                'success': True,
                'data': employment,
                'message': '聘用关系创建成功'
            })
        else:
            return jsonify({'success': False, 'message': '聘用关系创建失败'}), 500
            
    except Exception as e:
        logger.error(f"创建聘用关系失败: {str(e)}")
        return jsonify({'success': False, 'message': '创建失败，请稍后重试'}), 500

@user_bp.route('/api/user/employments', methods=['GET'])
@require_user_auth
def get_user_employments():
    """获取用户的聘用列表"""
    try:
        user_id = request.user_id
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', '')
        
        employments = EmploymentService.get_user_employments(
            user_id=user_id,
            page=page,
            per_page=per_page,
            status=status
        )
        
        return jsonify({
            'success': True,
            'data': employments,
            'message': '获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取聘用列表失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取失败，请稍后重试'}), 500

@user_bp.route('/api/user/employments/<int:employment_id>', methods=['PUT'])
@require_user_auth
def update_employment(employment_id):
    """更新聘用状态"""
    try:
        user_id = request.user_id
        data = request.json
        action = data.get('action')  # terminate, extend
        
        if action == 'terminate':
            result = EmploymentService.terminate_employment(employment_id, user_id)
        elif action == 'extend':
            end_date = data.get('end_date')
            if not end_date:
                return jsonify({'success': False, 'message': '缺少结束日期'}), 400
            result = EmploymentService.extend_employment(employment_id, user_id, end_date)
        else:
            return jsonify({'success': False, 'message': '无效的操作'}), 400
        
        if result:
            return jsonify({
                'success': True,
                'message': '操作成功'
            })
        else:
            return jsonify({'success': False, 'message': '操作失败'}), 500
            
    except Exception as e:
        logger.error(f"更新聘用关系失败: {str(e)}")
        return jsonify({'success': False, 'message': '操作失败，请稍后重试'}), 500

# ==================== 消息和聊天 ====================

@user_bp.route('/api/user/messages', methods=['GET'])
@require_user_auth
def get_user_messages():
    """获取用户的消息列表"""
    try:
        user_id = request.user_id
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        contact_id = request.args.get('contact_id', type=int)  # 特定联系人的消息
        
        messages = MessageService.get_user_messages(
            user_id=user_id,
            contact_id=contact_id,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'success': True,
            'data': messages,
            'message': '获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取消息失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取失败，请稍后重试'}), 500

@user_bp.route('/api/user/messages', methods=['POST'])
@require_user_auth
def send_message():
    """发送消息"""
    try:
        data = request.json
        user_id = request.user_id
        
        # 验证必要字段
        if not data.get('recipient_id') or not data.get('content'):
            return jsonify({'success': False, 'message': '缺少必要字段'}), 400
        
        # 发送消息
        message = MessageService.send_message(
            sender_id=user_id,
            sender_type='user',
            recipient_id=data['recipient_id'],
            recipient_type='caregiver',
            content=data['content']
        )
        
        if message:
            return jsonify({
                'success': True,
                'data': message,
                'message': '消息发送成功'
            })
        else:
            return jsonify({'success': False, 'message': '消息发送失败'}), 500
            
    except Exception as e:
        logger.error(f"发送消息失败: {str(e)}")
        return jsonify({'success': False, 'message': '发送失败，请稍后重试'}), 500

@user_bp.route('/api/user/messages/<int:message_id>/read', methods=['PUT'])
@require_user_auth
def mark_message_read(message_id):
    """标记消息为已读"""
    try:
        user_id = request.user_id
        
        result = MessageService.mark_message_read(message_id, user_id, 'user')
        
        if result:
            return jsonify({
                'success': True,
                'message': '标记成功'
            })
        else:
            return jsonify({'success': False, 'message': '标记失败'}), 500
            
    except Exception as e:
        logger.error(f"标记消息已读失败: {str(e)}")
        return jsonify({'success': False, 'message': '操作失败，请稍后重试'}), 500

# ==================== 用户个人资料 ====================

@user_bp.route('/api/user/profile', methods=['GET'])
@require_user_auth
def get_user_profile():
    """获取用户个人资料"""
    try:
        user_id = request.user_id
        profile = UserService.get_user_profile(user_id)
        
        if profile:
            return jsonify({
                'success': True,
                'data': profile,
                'message': '获取成功'
            })
        else:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
            
    except Exception as e:
        logger.error(f"获取用户资料失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取失败，请稍后重试'}), 500

@user_bp.route('/api/user/profile', methods=['PUT'])
@require_user_auth
def update_user_profile():
    """更新用户个人资料"""
    try:
        user_id = request.user_id
        data = request.json
        
        # 更新用户资料
        result = UserService.update_user_profile(user_id, data)
        
        if result:
            return jsonify({
                'success': True,
                'message': '更新成功'
            })
        else:
            return jsonify({'success': False, 'message': '更新失败'}), 500
            
    except Exception as e:
        logger.error(f"更新用户资料失败: {str(e)}")
        return jsonify({'success': False, 'message': '更新失败，请稍后重试'}), 500

# ==================== 评价和反馈 ====================

@user_bp.route('/api/user/appointments/<int:appointment_id>/review', methods=['POST'])
@require_user_auth
def submit_review(appointment_id):
    """提交服务评价"""
    try:
        user_id = request.user_id
        data = request.json
        
        # 验证必要字段
        if not data.get('rating') or not data.get('content'):
            return jsonify({'success': False, 'message': '请提供评分和评价内容'}), 400
        
        # 提交评价
        review = AppointmentService.submit_review(
            appointment_id=appointment_id,
            user_id=user_id,
            rating=data['rating'],
            content=data['content']
        )
        
        if review:
            return jsonify({
                'success': True,
                'data': review,
                'message': '评价提交成功'
            })
        else:
            return jsonify({'success': False, 'message': '评价提交失败'}), 500
            
    except Exception as e:
        logger.error(f"提交评价失败: {str(e)}")
        return jsonify({'success': False, 'message': '提交失败，请稍后重试'}), 500
