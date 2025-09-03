"""
护工资源管理系统 - 预约服务
====================================

处理预约相关的业务逻辑，包括创建、查询、更新预约状态等
"""

from models.business import Appointment
from extensions import db
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class AppointmentService:
    """预约服务类"""
    
    @staticmethod
    def create_appointment(user_id, caregiver_id, service_type, date, start_time, end_time, notes=''):
        """创建预约"""
        try:
            # 获取预约模型
            AppointmentModel = Appointment.get_model(db)
            
            # 创建新预约
            appointment = AppointmentModel(
                user_id=user_id,
                caregiver_id=caregiver_id,
                service_type=service_type,
                date=date,
                start_time=start_time,
                end_time=end_time,
                notes=notes,
                status='pending'
            )
            
            # 保存到数据库
            db.session.add(appointment)
            db.session.commit()
            
            # 返回预约信息
            return {
                'id': appointment.id,
                'user_id': appointment.user_id,
                'caregiver_id': appointment.caregiver_id,
                'service_type': appointment.service_type,
                'date': appointment.date.isoformat() if appointment.date else None,
                'start_time': appointment.start_time.isoformat() if appointment.start_time else None,
                'end_time': appointment.end_time.isoformat() if appointment.end_time else None,
                'notes': appointment.notes,
                'status': appointment.status,
                'created_at': appointment.created_at.isoformat() if appointment.created_at else None
            }
            
        except Exception as e:
            logger.error(f"创建预约失败: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_user_appointments(user_id, page=1, per_page=10, status=''):
        """获取用户的预约列表"""
        try:
            AppointmentModel = Appointment.get_model(db)
            
            # 构建查询
            query = AppointmentModel.query.filter_by(user_id=user_id)
            
            # 按状态筛选
            if status:
                query = query.filter_by(status=status)
            
            # 分页
            pagination = query.order_by(AppointmentModel.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            # 格式化结果
            appointments = []
            for appointment in pagination.items:
                appointments.append({
                    'id': appointment.id,
                    'caregiver_id': appointment.caregiver_id,
                    'service_type': appointment.service_type,
                    'date': appointment.date.isoformat() if appointment.date else None,
                    'start_time': appointment.start_time.isoformat() if appointment.start_time else None,
                    'end_time': appointment.end_time.isoformat() if appointment.end_time else None,
                    'notes': appointment.notes,
                    'status': appointment.status,
                    'created_at': appointment.created_at.isoformat() if appointment.created_at else None
                })
            
            return {
                'appointments': appointments,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page
            }
            
        except Exception as e:
            logger.error(f"获取用户预约列表失败: {str(e)}")
            return None
    
    @staticmethod
    def get_caregiver_appointments(caregiver_id, page=1, per_page=10, status=''):
        """获取护工的预约列表"""
        try:
            AppointmentModel = Appointment.get_model(db)
            
            # 构建查询
            query = AppointmentModel.query.filter_by(caregiver_id=caregiver_id)
            
            # 按状态筛选
            if status:
                query = query.filter_by(status=status)
            
            # 分页
            pagination = query.order_by(AppointmentModel.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            # 格式化结果
            appointments = []
            for appointment in pagination.items:
                appointments.append({
                    'id': appointment.id,
                    'user_id': appointment.user_id,
                    'service_type': appointment.service_type,
                    'date': appointment.date.isoformat() if appointment.date else None,
                    'start_time': appointment.start_time.isoformat() if appointment.start_time else None,
                    'end_time': appointment.end_time.isoformat() if appointment.end_time else None,
                    'notes': appointment.notes,
                    'status': appointment.status,
                    'created_at': appointment.created_at.isoformat() if appointment.created_at else None
                })
            
            return {
                'appointments': appointments,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page
            }
            
        except Exception as e:
            logger.error(f"获取护工预约列表失败: {str(e)}")
            return None
    
    @staticmethod
    def accept_appointment(appointment_id, caregiver_id):
        """护工接受预约"""
        try:
            AppointmentModel = Appointment.get_model(db)
            
            appointment = AppointmentModel.query.get(appointment_id)
            if not appointment:
                return False
            
            # 验证护工权限
            if appointment.caregiver_id != caregiver_id:
                return False
            
            # 更新状态
            appointment.status = 'confirmed'
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"接受预约失败: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def reject_appointment(appointment_id, caregiver_id, reason=''):
        """护工拒绝预约"""
        try:
            AppointmentModel = Appointment.get_model(db)
            
            appointment = AppointmentModel.query.get(appointment_id)
            if not appointment:
                return False
            
            # 验证护工权限
            if appointment.caregiver_id != caregiver_id:
                return False
            
            # 更新状态
            appointment.status = 'rejected'
            appointment.notes = f"{appointment.notes or ''}\n拒绝原因: {reason}".strip()
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"拒绝预约失败: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def start_appointment(appointment_id, caregiver_id):
        """开始预约服务"""
        try:
            AppointmentModel = Appointment.get_model(db)
            
            appointment = AppointmentModel.query.get(appointment_id)
            if not appointment:
                return False
            
            # 验证护工权限
            if appointment.caregiver_id != caregiver_id:
                return False
            
            # 检查预约状态
            if appointment.status != 'confirmed':
                return False
            
            # 更新状态
            appointment.status = 'in_progress'
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"开始预约失败: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def complete_appointment(appointment_id, caregiver_id):
        """完成预约服务"""
        try:
            AppointmentModel = Appointment.get_model(db)
            
            appointment = AppointmentModel.query.get(appointment_id)
            if not appointment:
                return False
            
            # 验证护工权限
            if appointment.caregiver_id != caregiver_id:
                return False
            
            # 检查预约状态
            if appointment.status != 'in_progress':
                return False
            
            # 更新状态
            appointment.status = 'completed'
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"完成预约失败: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def cancel_appointment(appointment_id, user_id):
        """用户取消预约"""
        try:
            AppointmentModel = Appointment.get_model(db)
            
            appointment = AppointmentModel.query.get(appointment_id)
            if not appointment:
                return False
            
            # 验证用户权限
            if appointment.user_id != user_id:
                return False
            
            # 检查预约状态
            if appointment.status not in ['pending', 'confirmed']:
                return False
            
            # 更新状态
            appointment.status = 'cancelled'
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"取消预约失败: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def confirm_appointment(appointment_id, user_id):
        """用户确认预约"""
        try:
            AppointmentModel = Appointment.get_model(db)
            
            appointment = AppointmentModel.query.get(appointment_id)
            if not appointment:
                return False
            
            # 验证用户权限
            if appointment.user_id != user_id:
                return False
            
            # 检查预约状态
            if appointment.status != 'pending':
                return False
            
            # 更新状态
            appointment.status = 'confirmed'
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"确认预约失败: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def submit_review(appointment_id, user_id, rating, content):
        """提交服务评价"""
        try:
            AppointmentModel = Appointment.get_model(db)
            
            appointment = AppointmentModel.query.get(appointment_id)
            if not appointment:
                return None
            
            # 验证用户权限
            if appointment.user_id != user_id:
                return None
            
            # 检查预约状态
            if appointment.status != 'completed':
                return None
            
            # 这里可以创建评价记录
            # 暂时返回成功
            return {
                'appointment_id': appointment_id,
                'rating': rating,
                'content': content,
                'submitted_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"提交评价失败: {str(e)}")
            return None
