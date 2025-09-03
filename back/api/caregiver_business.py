"""
护工资源管理系统 - 护工业务API
====================================

护工端的核心业务功能，包括预约处理、聘用管理、聊天等
"""

from flask import Blueprint, request, jsonify, g
from services.caregiver_service import CaregiverService
from services.appointment_service import AppointmentService
from services.employment_service import EmploymentService
from services.message_service import MessageService
from utils.auth import require_auth
from functools import wraps
import logging

logger = logging.getLogger(__name__)
caregiver_business_bp = Blueprint('caregiver_business', __name__)

def require_caregiver_auth(f):
    """护工认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未提供认证令牌'}), 401
        
        token = token.split(' ')[1]
        caregiver_id = require_auth(token, 'caregiver')
        if not caregiver_id:
            return jsonify({'success': False, 'message': '无效的认证令牌'}), 401
        
        request.caregiver_id = caregiver_id
        return f(*args, **kwargs)
    
    return decorated_function

# ==================== 护工个人资料管理 ====================

@caregiver_business_bp.route('/api/caregiver/profile', methods=['GET'])
@require_caregiver_auth
def get_caregiver_profile():
    """获取护工个人资料"""
    try:
        caregiver_id = request.caregiver_id
        profile = CaregiverService.get_caregiver_profile(caregiver_id)
        
        if profile:
            return jsonify({
                'success': True,
                'data': profile,
                'message': '获取成功'
            })
        else:
            return jsonify({'success': False, 'message': '护工不存在'}), 404
            
    except Exception as e:
        logger.error(f"获取护工资料失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取失败，请稍后重试'}), 500

@caregiver_business_bp.route('/api/caregiver/profile', methods=['PUT'])
@require_caregiver_auth
def update_caregiver_profile():
    """更新护工个人资料"""
    try:
        caregiver_id = request.caregiver_id
        data = request.json
        
        # 更新护工资料
        result = CaregiverService.update_caregiver_profile(caregiver_id, data)
        
        if result:
            return jsonify({
                'success': True,
                'message': '更新成功'
            })
        else:
            return jsonify({'success': False, 'message': '更新失败'}), 500
            
    except Exception as e:
        logger.error(f"更新护工资料失败: {str(e)}")
        return jsonify({'success': False, 'message': '更新失败，请稍后重试'}), 500

@caregiver_business_bp.route('/api/caregiver/availability', methods=['PUT'])
@require_caregiver_auth
def update_availability():
    """更新护工可用时间"""
    try:
        caregiver_id = request.caregiver_id
        data = request.json
        
        # 更新可用时间
        result = CaregiverService.update_availability(caregiver_id, data)
        
        if result:
            return jsonify({
                'success': True,
                'message': '可用时间更新成功'
            })
        else:
            return jsonify({'success': False, 'message': '更新失败'}), 500
            
    except Exception as e:
        logger.error(f"更新可用时间失败: {str(e)}")
        return jsonify({'success': False, 'message': '更新失败，请稍后重试'}), 500

# ==================== 预约管理 ====================

@caregiver_business_bp.route('/api/caregiver/appointments', methods=['GET'])
@require_caregiver_auth
def get_caregiver_appointments():
    """获取护工的预约列表"""
    try:
        caregiver_id = request.caregiver_id
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', '')
        
        appointments = AppointmentService.get_caregiver_appointments(
            caregiver_id=caregiver_id,
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

@caregiver_business_bp.route('/api/caregiver/appointments/<int:appointment_id>', methods=['PUT'])
@require_caregiver_auth
def update_appointment_status(appointment_id):
    """更新预约状态（护工端）"""
    try:
        caregiver_id = request.caregiver_id
        data = request.json
        action = data.get('action')  # accept, reject, start, complete
        
        if action == 'accept':
            result = AppointmentService.accept_appointment(appointment_id, caregiver_id)
        elif action == 'reject':
            reason = data.get('reason', '')
            result = AppointmentService.reject_appointment(appointment_id, caregiver_id, reason)
        elif action == 'start':
            result = AppointmentService.start_appointment(appointment_id, caregiver_id)
        elif action == 'complete':
            result = AppointmentService.complete_appointment(appointment_id, caregiver_id)
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
        logger.error(f"更新预约状态失败: {str(e)}")
        return jsonify({'success': False, 'message': '操作失败，请稍后重试'}), 500

# ==================== 长期聘用管理 ====================

@caregiver_business_bp.route('/api/caregiver/employments', methods=['GET'])
@require_caregiver_auth
def get_caregiver_employments():
    """获取护工的聘用列表"""
    try:
        caregiver_id = request.caregiver_id
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', '')
        
        employments = EmploymentService.get_caregiver_employments(
            caregiver_id=caregiver_id,
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

@caregiver_business_bp.route('/api/caregiver/employments/<int:employment_id>', methods=['PUT'])
@require_caregiver_auth
def update_employment_status(employment_id):
    """更新聘用状态（护工端）"""
    try:
        caregiver_id = request.caregiver_id
        data = request.json
        action = data.get('action')  # accept, reject, terminate
        
        if action == 'accept':
            result = EmploymentService.accept_employment(employment_id, caregiver_id)
        elif action == 'reject':
            reason = data.get('reason', '')
            result = EmploymentService.reject_employment(employment_id, caregiver_id, reason)
        elif action == 'terminate':
            reason = data.get('reason', '')
            result = EmploymentService.terminate_employment(employment_id, caregiver_id, reason)
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
        logger.error(f"更新聘用状态失败: {str(e)}")
        return jsonify({'success': False, 'message': '操作失败，请稍后重试'}), 500

# ==================== 消息和聊天 ====================

@caregiver_business_bp.route('/api/caregiver/messages', methods=['GET'])
@require_caregiver_auth
def get_caregiver_messages():
    """获取护工的消息列表"""
    try:
        caregiver_id = request.caregiver_id
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        contact_id = request.args.get('contact_id', type=int)  # 特定联系人的消息
        
        messages = MessageService.get_caregiver_messages(
            caregiver_id=caregiver_id,
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

@caregiver_business_bp.route('/api/caregiver/messages', methods=['POST'])
@require_caregiver_auth
def send_message():
    """发送消息（护工端）"""
    try:
        data = request.json
        caregiver_id = request.caregiver_id
        
        # 验证必要字段
        if not data.get('recipient_id') or not data.get('content'):
            return jsonify({'success': False, 'message': '缺少必要字段'}), 400
        
        # 发送消息
        message = MessageService.send_message(
            sender_id=caregiver_id,
            sender_type='caregiver',
            recipient_id=data['recipient_id'],
            recipient_type='user',
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

@caregiver_business_bp.route('/api/caregiver/messages/<int:message_id>/read', methods=['PUT'])
@require_caregiver_auth
def mark_message_read(message_id):
    """标记消息为已读（护工端）"""
    try:
        caregiver_id = request.caregiver_id
        
        result = MessageService.mark_message_read(message_id, caregiver_id, 'caregiver')
        
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

# ==================== 工作记录和报告 ====================

@caregiver_business_bp.route('/api/caregiver/work-records', methods=['POST'])
@require_caregiver_auth
def create_work_record():
    """创建工作记录"""
    try:
        data = request.json
        caregiver_id = request.caregiver_id
        
        # 验证必要字段
        if not data.get('appointment_id') or not data.get('work_summary'):
            return jsonify({'success': False, 'message': '缺少必要字段'}), 400
        
        # 创建工作记录
        work_record = CaregiverService.create_work_record(
            caregiver_id=caregiver_id,
            appointment_id=data['appointment_id'],
            work_summary=data['work_summary'],
            health_status=data.get('health_status', ''),
            recommendations=data.get('recommendations', ''),
            next_steps=data.get('next_steps', '')
        )
        
        if work_record:
            return jsonify({
                'success': True,
                'data': work_record,
                'message': '工作记录创建成功'
            })
        else:
            return jsonify({'success': False, 'message': '工作记录创建失败'}), 500
            
    except Exception as e:
        logger.error(f"创建工作记录失败: {str(e)}")
        return jsonify({'success': False, 'message': '创建失败，请稍后重试'}), 500

@caregiver_business_bp.route('/api/caregiver/work-records', methods=['GET'])
@require_caregiver_auth
def get_work_records():
    """获取护工的工作记录"""
    try:
        caregiver_id = request.caregiver_id
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        work_records = CaregiverService.get_work_records(
            caregiver_id=caregiver_id,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'success': True,
            'data': work_records,
            'message': '获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取工作记录失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取失败，请稍后重试'}), 500

# ==================== 收入统计 ====================

@caregiver_business_bp.route('/api/caregiver/income-stats', methods=['GET'])
@require_caregiver_auth
def get_income_stats():
    """获取护工的收入统计"""
    try:
        caregiver_id = request.caregiver_id
        period = request.args.get('period', 'month')  # day, week, month, year
        
        income_stats = CaregiverService.get_income_stats(caregiver_id, period)
        
        return jsonify({
            'success': True,
            'data': income_stats,
            'message': '获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取收入统计失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取失败，请稍后重试'}), 500

# ==================== 服务评价查看 ====================

@caregiver_business_bp.route('/api/caregiver/reviews', methods=['GET'])
@require_caregiver_auth
def get_caregiver_reviews():
    """获取护工收到的评价"""
    try:
        caregiver_id = request.caregiver_id
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        reviews = CaregiverService.get_caregiver_reviews(
            caregiver_id=caregiver_id,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'success': True,
            'data': reviews,
            'message': '获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取评价失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取失败，请稍后重试'}), 500
