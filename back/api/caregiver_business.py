"""
护工资源管理系统 - 护工业务API
====================================

护工端的核心业务功能，包括预约处理、聘用管理、聊天等
"""

from flask import Blueprint, request, jsonify, g
from services.caregiver_service import CaregiverService
from services.appointment_service import AppointmentService
from datetime import datetime
from services.employment_service import EmploymentService
from services.message_service import MessageService
from utils.auth import require_auth
from functools import wraps
import logging
from extensions import db

logger = logging.getLogger(__name__)
caregiver_business_bp = Blueprint('caregiver_business', __name__)

# 使用统一的认证装饰器
from utils.auth import require_caregiver_auth

# ==================== 护工个人资料管理 ====================

@caregiver_business_bp.route('/api/caregiver/profile', methods=['GET'])
@require_caregiver_auth()
def get_caregiver_profile():
    """获取护工个人资料"""
    try:
        caregiver_id = g.current_user['user_id']
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

# 护工资料更新API已移至 caregiver.py 中，避免重复定义

@caregiver_business_bp.route('/api/caregiver/availability', methods=['PUT'])
@require_caregiver_auth()
def update_availability():
    """更新护工可用时间"""
    try:
        caregiver_id = g.current_user['user_id']
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
@require_caregiver_auth()
def get_caregiver_appointments():
    """获取护工的预约列表"""
    try:
        caregiver_id = g.current_user['user_id']
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
@require_caregiver_auth()
def update_appointment_status(appointment_id):
    """更新预约状态（护工端）"""
    try:
        caregiver_id = g.current_user['user_id']
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

# ==================== 工作申请管理 ====================

@caregiver_business_bp.route('/api/caregiver/applications', methods=['GET'])
@require_caregiver_auth()
def get_caregiver_applications():
    """获取护工的工作申请列表"""
    try:
        caregiver_id = g.current_user['user_id']
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', '')
        
        # 获取真实的工作申请数据
        from services.job_service import JobService
        job_service = JobService()
        job_service.set_db(db)
        
        result = job_service.get_caregiver_applications(
            caregiver_id=caregiver_id,
            page=page,
            per_page=per_page
        )
        
        if result['success']:
            applications = result['data'] or []
        else:
            # 如果获取失败，返回空列表
            applications = []
        
        # 根据状态筛选
        if status:
            applications = [app for app in applications if app['status'] == status]
        
        return jsonify({
            'success': True,
            'applications': applications,
            'total': len(applications),
            'message': '获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取工作申请失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取失败，请稍后重试'}), 500

@caregiver_business_bp.route('/api/caregiver/applications/<int:application_id>', methods=['GET'])
@require_caregiver_auth()
def get_application_detail(application_id):
    """获取工作申请详情"""
    try:
        # 获取真实的工作申请详情数据
        from services.job_service import JobService
        job_service = JobService()
        job_service.set_db(db)
        
        # 这里需要实现获取申请详情的逻辑
        # 暂时返回基本申请信息
        application = {
            'id': application_id,
            'job_title': '工作申请详情',
            'job_description': '申请详情描述',
            'job_location': '工作地点',
            'job_salary': '薪资面议',
            'job_type': '工作类型',
            'job_schedule': '工作时间',
            'status': 'pending',
            'applied_date': datetime.now().strftime('%Y-%m-%d'),
            'review_notes': ''
        }
        
        return jsonify({
            'success': True,
            'application': application,
            'message': '获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取申请详情失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取失败，请稍后重试'}), 500

@caregiver_business_bp.route('/api/caregiver/applications/<int:application_id>/cancel', methods=['POST'])
@require_caregiver_auth()
def cancel_application(application_id):
    """取消工作申请"""
    try:
        caregiver_id = g.current_user['user_id']
        
        # 调用服务层取消申请
        from services.job_service import JobService
        job_service = JobService()
        job_service.set_db(db)
        
        result = job_service.cancel_application(
            application_id=application_id,
            caregiver_id=caregiver_id
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': '申请已取消'
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message'] or '取消失败'
            }), 400
        
    except Exception as e:
        logger.error(f"取消申请失败: {str(e)}")
        return jsonify({'success': False, 'message': '取消失败，请稍后重试'}), 500

# ==================== 工作机会管理 ====================

@caregiver_business_bp.route('/api/caregiver/jobs', methods=['GET'])
@require_caregiver_auth()
def get_caregiver_jobs():
    """获取护工可申请的工作机会列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        location = request.args.get('location', '')
        job_type = request.args.get('job_type', '')
        
        # 获取真实的工作机会数据
        from services.job_service import JobService
        job_service = JobService()
        job_service.set_db(db)
        
        result = job_service.get_available_jobs(
            page=page,
            per_page=per_page,
            location=location,
            job_type=job_type
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'jobs': result['data'],
                'total': result['total'],
                'message': '获取成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message'] or '获取工作机会失败'
            }), 400
        
    except Exception as e:
        logger.error(f"获取工作机会失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取失败，请稍后重试'}), 500

@caregiver_business_bp.route('/api/caregiver/jobs/<int:job_id>', methods=['GET'])
@require_caregiver_auth()
def get_job_detail(job_id):
    """获取工作机会详情"""
    try:
        # 获取真实的工作详情数据
        from services.job_service import JobService
        job_service = JobService()
        job_service.set_db(db)
        
        result = job_service.get_job_detail(job_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'job': result['data'],
                'message': '获取成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message'] or '获取工作详情失败'
            }), 400
        
    except Exception as e:
        logger.error(f"获取工作详情失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取失败，请稍后重试'}), 500

@caregiver_business_bp.route('/api/caregiver/jobs/<int:job_id>/apply', methods=['POST'])
@require_caregiver_auth()
def apply_for_job(job_id):
    """申请工作机会"""
    try:
        caregiver_id = g.current_user['user_id']
        data = request.json
        application_message = data.get('message', '')
        
        # 调用服务层创建申请
        from services.job_service import JobService
        job_service = JobService()
        job_service.set_db(db)
        
        result = job_service.apply_for_job(
            job_id=job_id,
            caregiver_id=caregiver_id,
            application_message=application_message
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': '申请已提交，请等待审核'
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message'] or '申请失败'
            }), 400
        
    except Exception as e:
        logger.error(f"申请工作失败: {str(e)}")
        return jsonify({'success': False, 'message': '申请失败，请稍后重试'}), 500

# ==================== 长期聘用管理 ====================

@caregiver_business_bp.route('/api/caregiver/employments', methods=['GET'])
@require_caregiver_auth()
def get_caregiver_employments():
    """获取护工的聘用列表"""
    try:
        caregiver_id = g.current_user['user_id']
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
@require_caregiver_auth()
def update_employment_status(employment_id):
    """更新聘用状态（护工端）"""
    try:
        caregiver_id = g.current_user['user_id']
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
@require_caregiver_auth()
def get_caregiver_messages():
    """获取护工的消息列表"""
    try:
        caregiver_id = g.current_user['user_id']
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        contact_id = request.args.get('contact_id', type=int)  # 特定联系人的消息
        
        # 获取护工的消息列表
        from services.message_service import message_service
        message_service.set_db(db)
        
        # 获取护工的所有对话
        from models.chat import ChatConversation
        ChatConversationModel = ChatConversation.get_model(db)
        
        conversations = ChatConversationModel.query.filter(
            ChatConversationModel.caregiver_id == caregiver_id,
            ChatConversationModel.is_active == True
        ).order_by(ChatConversationModel.updated_at.desc()).all()
        
        # 转换为前端需要的格式
        messages = []
        for conv in conversations:
            messages.append({
                'contactId': f'user_{conv.user_id}',
                'type': 'user',
                'sender': f'用户{conv.user_id}',
                'avatar': '/uploads/avatars/default-user.png',
                'content': conv.last_message_content or '暂无消息',
                'time': conv.last_message_time.strftime('%H:%M') if conv.last_message_time else '00:00',
                'date': conv.last_message_time.strftime('%Y-%m-%d') if conv.last_message_time else '',
                'unread': conv.unread_count > 0
            })
        
        result = {
            'success': True,
            'data': messages,
            'total': len(messages),
            'message': '获取成功'
        }
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"获取消息失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取失败，请稍后重试'}), 500

@caregiver_business_bp.route('/api/caregiver/messages/history', methods=['GET'])
@require_caregiver_auth()
def get_caregiver_message_history():
        """获取护工与特定用户的消息历史"""
        try:
            caregiver_id = g.current_user['user_id']
            contact_id = request.args.get('contact_id', type=int)
            contact_type = request.args.get('contact_type', 'user')
            limit = request.args.get('limit', 50, type=int)
            offset = request.args.get('offset', 0, type=int)
            
            if not contact_id:
                return jsonify({'success': False, 'message': '缺少联系人ID'}), 400
            
            from services.message_service import message_service
            message_service.set_db(db)
            
            messages = message_service.get_message_history(
                caregiver_id, 'caregiver', contact_id, contact_type, limit, offset
            )
            
            return jsonify({
                'success': True,
                'data': {
                    'messages': messages,
                    'contact_id': contact_id,
                    'contact_type': contact_type,
                    'has_more': len(messages) == limit
                },
                'message': '获取成功'
            })
            
        except Exception as e:
            logger.error(f"获取消息历史失败: {str(e)}")
            return jsonify({'success': False, 'message': '获取失败，请稍后重试'}), 500

@caregiver_business_bp.route('/api/caregiver/contacts', methods=['GET'])
@require_caregiver_auth()
def get_caregiver_contacts():
    """获取护工可联系的用户列表（所有用户）"""
    try:
        keyword = request.args.get('keyword', '').strip()
        limit = request.args.get('limit', 50, type=int)
        
        # 获取所有用户信息
        from models.user import User
        UserModel = User.get_model(db)
        
        # 确保模型存在
        if not UserModel:
            return jsonify({'success': False, 'message': '用户模型未找到'}), 500
        
        # 构建查询
        query = UserModel.query
        
        # 如果有关键词，进行模糊搜索
        if keyword:
            query = query.filter(
                db.or_(
                    UserModel.name.contains(keyword),
                    UserModel.phone.contains(keyword)
                )
            )
        
        # 限制数量
        users = query.limit(limit).all()
        
        contacts = []
        for user in users:
                contacts.append({
                    'id': user.id,
                    'name': user.name,
                    'phone': user.phone,
                    'avatar': user.avatar_url or '/uploads/avatars/default-user.png',
                    'type': 'user',
                    'contactId': f'user_{user.id}',
                    'lastMessage': '暂无消息',
                    'time': '',
                    'online': True  # 默认在线状态
                })
        
        return jsonify({
            'success': True,
            'data': contacts,
            'message': '获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取联系人失败: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'}), 500

@caregiver_business_bp.route('/api/caregiver/messages', methods=['POST'])
@require_caregiver_auth()
def send_message():
    """发送消息（护工端）"""
    try:
        data = request.json
        caregiver_id = g.current_user['user_id']
        
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
@require_caregiver_auth()
def mark_message_read(message_id):
    """标记消息为已读（护工端）"""
    try:
        caregiver_id = g.current_user['user_id']
        
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
@require_caregiver_auth()
def create_work_record():
    """创建工作记录"""
    try:
        data = request.json
        caregiver_id = g.current_user['user_id']
        
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
@require_caregiver_auth()
def get_work_records():
    """获取护工的工作记录"""
    try:
        caregiver_id = g.current_user['user_id']
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
@require_caregiver_auth()
def get_income_stats():
    """获取护工的收入统计"""
    try:
        caregiver_id = g.current_user['user_id']
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
@require_caregiver_auth()
def get_caregiver_reviews():
    """获取护工收到的评价"""
    try:
        caregiver_id = g.current_user['user_id']
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

@caregiver_business_bp.route('/api/caregiver/reviews/<int:review_id>/reply', methods=['POST'])
@require_caregiver_auth()
def reply_to_review(review_id):
    """护工回复评价"""
    try:
        caregiver_id = g.current_user['user_id']
        data = request.json
        
        if not data.get('reply'):
            return jsonify({'success': False, 'message': '请输入回复内容'}), 400
        
        # 导入评价模型
        from models.review import Review
        from extensions import db
        
        ReviewModel = Review.get_model(db)
        
        # 查找评价记录
        review = ReviewModel.query.filter_by(
            id=review_id,
            caregiver_id=caregiver_id
        ).first()
        
        if not review:
            return jsonify({'success': False, 'message': '评价不存在'}), 404
        
        # 更新回复内容
        review.reply = data['reply']
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '回复提交成功',
            'data': {
                'review_id': review_id,
                'reply': review.reply
            }
        })
        
    except Exception as e:
        logger.error(f"回复评价失败: {str(e)}")
        return jsonify({'success': False, 'message': '回复失败，请稍后重试'}), 500


# 护工资料更新API已移至 caregiver.py 中，避免重复定义

# 添加其他缺失的API端点
@caregiver_business_bp.route('/api/caregiver/earnings', methods=['GET'])
@require_caregiver_auth()
def get_caregiver_earnings():
    """获取护工收入统计"""
    try:
        caregiver_id = g.current_user['user_id']
        period = request.args.get('period', 'month')  # day, week, month, year
        
        # 这里应该调用CaregiverService的相应方法
        # 暂时返回模拟数据
        earnings_data = {
            'total_earnings': 0,
            'period_earnings': 0,
            'period': period,
            'chart_data': []
        }
        
        return jsonify({
            'success': True,
            'data': earnings_data,
            'message': '获取收入统计成功'
        })
        
    except Exception as e:
        logger.error(f"获取收入统计失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取失败，请稍后重试'}), 500

@caregiver_business_bp.route('/api/caregiver/settings', methods=['GET', 'POST'])
@require_caregiver_auth()
def caregiver_settings():
    """护工设置"""
    try:
        caregiver_id = g.current_user['user_id']
        
        if request.method == 'GET':
            # 获取设置
            settings = {
                'notifications': True,
                'email_notifications': True,
                'sms_notifications': False,
                'privacy_level': 'normal'
            }
            
            return jsonify({
                'success': True,
                'data': settings,
                'message': '获取设置成功'
            })
            
        elif request.method == 'POST':
            # 更新设置
            data = request.json
            # 这里应该更新数据库中的设置
            return jsonify({
                'success': True,
                'message': '设置更新成功'
            })
            
    except Exception as e:
        logger.error(f"设置操作失败: {str(e)}")
        return jsonify({'success': False, 'message': '操作失败，请稍后重试'}), 500

@caregiver_business_bp.route('/api/caregiver/change-password', methods=['POST'])
@require_caregiver_auth()
def change_caregiver_password():
    """修改护工密码"""
    try:
        caregiver_id = g.current_user['user_id']
        data = request.json
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'success': False, 'message': '请输入当前密码和新密码'}), 400
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': '新密码长度不能少于6位'}), 400
        
        # 调用服务层修改密码
        success = CaregiverService.update_caregiver_password(caregiver_id, current_password, new_password)
        
        if success:
            return jsonify({
                'success': True,
                'message': '密码修改成功'
            })
        else:
            return jsonify({'success': False, 'message': '当前密码错误'}), 400
            
    except Exception as e:
        logger.error(f"修改密码失败: {str(e)}")
        return jsonify({'success': False, 'message': '修改失败，请稍后重试'}), 500

@caregiver_business_bp.route('/api/caregiver/schedule', methods=['GET', 'POST'])
@require_caregiver_auth()
def caregiver_schedule():
    """护工工作安排"""
    try:
        caregiver_id = g.current_user['user_id']
        
        if request.method == 'GET':
            # 获取工作安排
            schedule = {
                'monday': {'available': True, 'start_time': '09:00', 'end_time': '17:00'},
                'tuesday': {'available': True, 'start_time': '09:00', 'end_time': '17:00'},
                'wednesday': {'available': True, 'start_time': '09:00', 'end_time': '17:00'},
                'thursday': {'available': True, 'start_time': '09:00', 'end_time': '17:00'},
                'friday': {'available': True, 'start_time': '09:00', 'end_time': '17:00'},
                'saturday': {'available': False, 'start_time': '', 'end_time': ''},
                'sunday': {'available': False, 'start_time': '', 'end_time': ''}
            }
            
            return jsonify({
                'success': True,
                'data': schedule,
                'message': '获取工作安排成功'
            })
            
        elif request.method == 'POST':
            # 更新工作安排
            data = request.json
            # 这里应该更新数据库中的工作安排
            return jsonify({
                'success': True,
                'message': '工作安排更新成功'
            })
            
    except Exception as e:
        logger.error(f"工作安排操作失败: {str(e)}")
        return jsonify({'success': False, 'message': '操作失败，请稍后重试'}), 500
