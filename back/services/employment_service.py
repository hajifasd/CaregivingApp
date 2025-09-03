"""
护工资源管理系统 - 聘用服务
====================================

处理长期聘用相关的业务逻辑，包括创建、查询、更新聘用状态等
"""

from models.business import Employment
from extensions import db
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class EmploymentService:
    """聘用服务类"""
    
    @staticmethod
    def create_employment(user_id, caregiver_id, service_type, start_date, end_date=None, 
                         frequency='', duration_per_session='', notes=''):
        """创建长期聘用关系"""
        try:
            # 获取聘用模型
            EmploymentModel = Employment.get_model(db)
            
            # 创建新聘用关系
            employment = EmploymentModel(
                user_id=user_id,
                caregiver_id=caregiver_id,
                service_type=service_type,
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                duration_per_session=duration_per_session,
                notes=notes,
                status='pending'
            )
            
            # 保存到数据库
            db.session.add(employment)
            db.session.commit()
            
            # 返回聘用信息
            return {
                'id': employment.id,
                'user_id': employment.user_id,
                'caregiver_id': employment.caregiver_id,
                'service_type': employment.service_type,
                'start_date': employment.start_date.isoformat() if employment.start_date else None,
                'end_date': employment.end_date.isoformat() if employment.end_date else None,
                'frequency': employment.frequency,
                'duration_per_session': employment.duration_per_session,
                'notes': employment.notes,
                'status': employment.status,
                'created_at': employment.created_at.isoformat() if employment.created_at else None
            }
            
        except Exception as e:
            logger.error(f"创建聘用关系失败: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_user_employments(user_id, page=1, per_page=10, status=''):
        """获取用户的聘用列表"""
        try:
            EmploymentModel = Employment.get_model(db)
            
            # 构建查询
            query = EmploymentModel.query.filter_by(user_id=user_id)
            
            # 按状态筛选
            if status:
                query = query.filter_by(status=status)
            
            # 分页
            pagination = query.order_by(EmploymentModel.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            # 格式化结果
            employments = []
            for employment in pagination.items:
                employments.append({
                    'id': employment.id,
                    'caregiver_id': employment.caregiver_id,
                    'service_type': employment.service_type,
                    'start_date': employment.start_date.isoformat() if employment.start_date else None,
                    'end_date': employment.end_date.isoformat() if employment.end_date else None,
                    'frequency': employment.frequency,
                    'duration_per_session': employment.duration_per_session,
                    'notes': employment.notes,
                    'status': employment.status,
                    'created_at': employment.created_at.isoformat() if employment.created_at else None
                })
            
            return {
                'employments': employments,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page
            }
            
        except Exception as e:
            logger.error(f"获取用户聘用列表失败: {str(e)}")
            return None
    
    @staticmethod
    def get_caregiver_employments(caregiver_id, page=1, per_page=10, status=''):
        """获取护工的聘用列表"""
        try:
            EmploymentModel = Employment.get_model(db)
            
            # 构建查询
            query = EmploymentModel.query.filter_by(caregiver_id=caregiver_id)
            
            # 按状态筛选
            if status:
                query = query.filter_by(status=status)
            
            # 分页
            pagination = query.order_by(EmploymentModel.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            # 格式化结果
            employments = []
            for employment in pagination.items:
                employments.append({
                    'id': employment.id,
                    'user_id': employment.user_id,
                    'service_type': employment.service_type,
                    'start_date': employment.start_date.isoformat() if employment.start_date else None,
                    'end_date': employment.end_date.isoformat() if employment.end_date else None,
                    'frequency': employment.frequency,
                    'duration_per_session': employment.duration_per_session,
                    'notes': employment.notes,
                    'status': employment.status,
                    'created_at': employment.created_at.isoformat() if employment.created_at else None
                })
            
            return {
                'employments': employments,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page
            }
            
        except Exception as e:
            logger.error(f"获取护工聘用列表失败: {str(e)}")
            return None
    
    @staticmethod
    def accept_employment(employment_id, caregiver_id):
        """护工接受聘用"""
        try:
            EmploymentModel = Employment.get_model(db)
            
            employment = EmploymentModel.query.get(employment_id)
            if not employment:
                return False
            
            # 验证护工权限
            if employment.caregiver_id != caregiver_id:
                return False
            
            # 检查聘用状态
            if employment.status != 'pending':
                return False
            
            # 更新状态
            employment.status = 'active'
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"接受聘用失败: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def reject_employment(employment_id, caregiver_id, reason=''):
        """护工拒绝聘用"""
        try:
            EmploymentModel = Employment.get_model(db)
            
            employment = EmploymentModel.query.get(employment_id)
            if not employment:
                return False
            
            # 验证护工权限
            if employment.caregiver_id != caregiver_id:
                return False
            
            # 检查聘用状态
            if employment.status != 'pending':
                return False
            
            # 更新状态
            employment.status = 'rejected'
            employment.notes = f"{employment.notes or ''}\n拒绝原因: {reason}".strip()
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"拒绝聘用失败: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def terminate_employment(employment_id, user_id, reason=''):
        """终止聘用关系"""
        try:
            EmploymentModel = Employment.get_model(db)
            
            employment = EmploymentModel.query.get(employment_id)
            if not employment:
                return False
            
            # 验证用户权限
            if employment.user_id != user_id:
                return False
            
            # 检查聘用状态
            if employment.status not in ['active', 'pending']:
                return False
            
            # 更新状态
            employment.status = 'terminated'
            employment.notes = f"{employment.notes or ''}\n终止原因: {reason}".strip()
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"终止聘用失败: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def extend_employment(employment_id, user_id, end_date):
        """延长聘用期限"""
        try:
            EmploymentModel = Employment.get_model(db)
            
            employment = EmploymentModel.query.get(employment_id)
            if not employment:
                return False
            
            # 验证用户权限
            if employment.user_id != user_id:
                return False
            
            # 检查聘用状态
            if employment.status != 'active':
                return False
            
            # 更新结束日期
            employment.end_date = end_date
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"延长聘用失败: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def complete_employment(employment_id, user_id):
        """完成聘用关系"""
        try:
            EmploymentModel = Employment.get_model(db)
            
            employment = EmploymentModel.query.get(employment_id)
            if not employment:
                return False
            
            # 验证用户权限
            if employment.user_id != user_id:
                return False
            
            # 检查聘用状态
            if employment.status != 'active':
                return False
            
            # 更新状态
            employment.status = 'completed'
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"完成聘用失败: {str(e)}")
            db.session.rollback()
            return False
