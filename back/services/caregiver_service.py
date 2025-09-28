"""
护工资源管理系统 - 护工服务类
====================================

护工相关的业务逻辑处理，包括登录验证、信息管理等
"""

import bcrypt
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from models.caregiver import Caregiver

class CaregiverService:
    """护工服务类"""
    
    @staticmethod
    def verify_caregiver(phone: str, password: str) -> Optional[Dict[str, Any]]:
        """验证护工登录"""
        try:
            from extensions import db
            
            # 获取护工模型
            CaregiverModel = Caregiver.get_model(db)
            
            # 查找护工
            caregiver = CaregiverModel.query.filter_by(phone=phone).first()
            
            if not caregiver:
                return None
            
            # 验证密码
            if bcrypt.checkpw(password.encode(), caregiver.password_hash.encode()):
                # 检查是否已审核通过
                if caregiver.is_approved:
                    return caregiver.to_dict()
                else:
                    return None  # 未审核通过
            else:
                return None
                
        except Exception as e:
            print(f"护工验证失败: {e}")
            return None
    
    @staticmethod
    def get_caregiver_by_phone(phone: str) -> Optional[Dict[str, Any]]:
        """根据手机号获取护工信息"""
        try:
            from extensions import db
            
            CaregiverModel = Caregiver.get_model(db)
            caregiver = CaregiverModel.query.filter_by(phone=phone).first()
            
            return caregiver.to_dict() if caregiver else None
            
        except Exception as e:
            print(f"获取护工信息失败: {e}")
            return None
    
    @staticmethod
    def get_caregiver_by_id(caregiver_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取护工信息"""
        try:
            from extensions import db
            
            CaregiverModel = Caregiver.get_model(db)
            caregiver = CaregiverModel.query.get(caregiver_id)
            
            return caregiver.to_dict() if caregiver else None
            
        except Exception as e:
            print(f"获取护工信息失败: {e}")
            return None
    
    @staticmethod
    def create_caregiver(name: str, phone: str, password: str, **kwargs) -> Optional[Dict[str, Any]]:
        """创建护工账号"""
        try:
            from extensions import db
            
            CaregiverModel = Caregiver.get_model(db)
            
            # 检查手机号是否已存在
            existing_caregiver = CaregiverModel.query.filter_by(phone=phone).first()
            if existing_caregiver:
                raise Exception("该手机号已被注册")
            
            # 创建新护工
            caregiver = CaregiverModel()
            caregiver.name = name
            caregiver.phone = phone
            caregiver.set_password(password)
            
            # 设置可选字段
            if 'gender' in kwargs:
                caregiver.gender = kwargs['gender']
            if 'age' in kwargs:
                caregiver.age = kwargs['age']
            if 'qualification' in kwargs:
                caregiver.qualification = kwargs['qualification']
            if 'introduction' in kwargs:
                caregiver.introduction = kwargs['introduction']
            if 'experience_years' in kwargs:
                caregiver.experience_years = kwargs['experience_years']
            if 'hourly_rate' in kwargs:
                caregiver.hourly_rate = kwargs['hourly_rate']
            
            db.session.add(caregiver)
            db.session.commit()
            
            return caregiver.to_dict()
            
        except Exception as e:
            print(f"创建护工失败: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def update_caregiver_profile(caregiver_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新护工个人信息"""
        try:
            from extensions import db
            
            CaregiverModel = Caregiver.get_model(db)
            caregiver = CaregiverModel.query.get(caregiver_id)
            
            if not caregiver:
                return None
            
            # 更新字段
            if 'gender' in data:
                caregiver.gender = data['gender']
            if 'age' in data:
                caregiver.age = data['age']
            if 'qualification' in data:
                caregiver.qualification = data['qualification']
            if 'introduction' in data:
                caregiver.introduction = data['introduction']
            if 'experience_years' in data:
                caregiver.experience_years = data['experience_years']
            if 'hourly_rate' in data:
                caregiver.hourly_rate = data['hourly_rate']
            if 'id_card' in data:
                caregiver.id_card = data['id_card']
            if 'emergency_contact' in data:
                caregiver.emergency_contact = data['emergency_contact']
            if 'email' in data:
                caregiver.email = data['email']
            if 'id_file' in data:
                caregiver.id_file = data['id_file']
            if 'cert_file' in data:
                caregiver.cert_file = data['cert_file']
            
            db.session.commit()
            return caregiver.to_dict()
            
        except Exception as e:
            print(f"更新护工信息失败: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_caregiver_dashboard_data(caregiver_id: int) -> Dict[str, Any]:
        """获取护工仪表盘数据"""
        try:
            from extensions import db
            from models.business import Appointment, Employment
            from datetime import datetime, timedelta
            
            CaregiverModel = Caregiver.get_model(db)
            AppointmentModel = Appointment.get_model(db)
            EmploymentModel = Employment.get_model(db)
            
            caregiver = CaregiverModel.query.get(caregiver_id)
            
            if not caregiver:
                return {}
            
            # 计算真实统计数据
            now = datetime.now()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # 总工作机会（所有预约）
            total_jobs = AppointmentModel.query.filter_by(caregiver_id=caregiver_id).count()
            
            # 进行中的预约
            active_appointments = AppointmentModel.query.filter(
                AppointmentModel.caregiver_id == caregiver_id,
                AppointmentModel.status.in_(['confirmed', 'in_progress'])
            ).count()
            
            # 本月收入计算（基于预约和聘用）
            monthly_appointments = AppointmentModel.query.filter(
                AppointmentModel.caregiver_id == caregiver_id,
                AppointmentModel.status == 'completed',
                AppointmentModel.completed_at >= start_of_month
            ).all()
            
            monthly_employments = EmploymentModel.query.filter(
                EmploymentModel.caregiver_id == caregiver_id,
                EmploymentModel.status == 'active',
                EmploymentModel.start_date <= now,
                EmploymentModel.end_date >= start_of_month
            ).all()
            
            # 计算本月收入
            monthly_earnings = 0
            for appointment in monthly_appointments:
                if appointment.hourly_rate and appointment.duration_hours:
                    monthly_earnings += appointment.hourly_rate * appointment.duration_hours
            
            for employment in monthly_employments:
                if employment.hourly_rate and employment.frequency:
                    # 估算本月收入（基于频率和时薪）
                    days_in_month = (now - start_of_month).days
                    estimated_sessions = (days_in_month / 7) * employment.frequency
                    monthly_earnings += employment.hourly_rate * employment.duration_per_session * estimated_sessions
            
            # 计算平均评分
            avg_rating = caregiver.rating or 0
            
            # 本月完成的服务数量
            completed_this_month = AppointmentModel.query.filter(
                AppointmentModel.caregiver_id == caregiver_id,
                AppointmentModel.status == 'completed',
                AppointmentModel.completed_at >= start_of_month
            ).count()
            
            # 总评价数量
            total_reviews = caregiver.review_count or 0
            
            # 计算更多统计指标
            # 本周收入
            start_of_week = now - timedelta(days=now.weekday())
            weekly_appointments = AppointmentModel.query.filter(
                AppointmentModel.caregiver_id == caregiver_id,
                AppointmentModel.status == 'completed',
                AppointmentModel.completed_at >= start_of_week
            ).all()
            
            weekly_earnings = 0
            for appointment in weekly_appointments:
                if appointment.hourly_rate and appointment.duration_hours:
                    weekly_earnings += appointment.hourly_rate * appointment.duration_hours
            
            # 今日收入
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_appointments = AppointmentModel.query.filter(
                AppointmentModel.caregiver_id == caregiver_id,
                AppointmentModel.status == 'completed',
                AppointmentModel.completed_at >= start_of_day
            ).all()
            
            today_earnings = 0
            for appointment in today_appointments:
                if appointment.hourly_rate and appointment.duration_hours:
                    today_earnings += appointment.hourly_rate * appointment.duration_hours
            
            # 待处理预约
            pending_appointments = AppointmentModel.query.filter(
                AppointmentModel.caregiver_id == caregiver_id,
                AppointmentModel.status == 'pending'
            ).count()
            
            # 本月工作时长
            monthly_hours = 0
            for appointment in monthly_appointments:
                if appointment.duration_hours:
                    monthly_hours += appointment.duration_hours
            
            # 平均每次服务时长
            avg_service_duration = monthly_hours / len(monthly_appointments) if monthly_appointments else 0
            
            # 客户满意度（基于评分）
            satisfaction_rate = (avg_rating / 5.0) * 100 if avg_rating > 0 else 0
            
            # 工作完成率
            total_appointments_this_month = AppointmentModel.query.filter(
                AppointmentModel.caregiver_id == caregiver_id,
                AppointmentModel.created_at >= start_of_month
            ).count()
            completion_rate = (completed_this_month / total_appointments_this_month * 100) if total_appointments_this_month > 0 else 0
            
            # 收入趋势（最近7天）
            daily_earnings = []
            for i in range(7):
                day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timedelta(days=1)
                
                day_appointments = AppointmentModel.query.filter(
                    AppointmentModel.caregiver_id == caregiver_id,
                    AppointmentModel.status == 'completed',
                    AppointmentModel.completed_at >= day_start,
                    AppointmentModel.completed_at < day_end
                ).all()
                
                day_earnings = 0
                for appointment in day_appointments:
                    if appointment.hourly_rate and appointment.duration_hours:
                        day_earnings += appointment.hourly_rate * appointment.duration_hours
                
                daily_earnings.append({
                    'date': day_start.strftime('%Y-%m-%d'),
                    'earnings': round(day_earnings, 2)
                })
            
            daily_earnings.reverse()  # 按时间正序排列
            
            return {
                'total_jobs': total_jobs,
                'active_appointments': active_appointments,
                'pending_appointments': pending_appointments,
                'monthly_earnings': round(monthly_earnings, 2),
                'weekly_earnings': round(weekly_earnings, 2),
                'today_earnings': round(today_earnings, 2),
                'rating': round(avg_rating, 1),
                'completed_this_month': completed_this_month,
                'total_reviews': total_reviews,
                'monthly_hours': round(monthly_hours, 1),
                'avg_service_duration': round(avg_service_duration, 1),
                'satisfaction_rate': round(satisfaction_rate, 1),
                'completion_rate': round(completion_rate, 1),
                'daily_earnings_trend': daily_earnings,
                'caregiver_info': caregiver.to_dict()
            }
            
        except Exception as e:
            print(f"获取护工仪表盘数据失败: {e}")
            return {
                'total_jobs': 0,
                'active_appointments': 0,
                'monthly_earnings': 0,
                'rating': 0,
                'completed_this_month': 0,
                'total_reviews': 0,
                'caregiver_info': {}
            }
    
    @staticmethod
    def approve_caregiver(caregiver_id: int) -> bool:
        """审核通过护工"""
        try:
            from extensions import db
            
            CaregiverModel = Caregiver.get_model(db)
            caregiver = CaregiverModel.query.get(caregiver_id)
            
            if not caregiver:
                return False
            
            caregiver.is_approved = True
            caregiver.approved_at = datetime.now(timezone.utc)
            caregiver.status = "approved"
            
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"审核护工失败: {e}")
            return False
    
    @staticmethod
    def reject_caregiver(caregiver_id: int) -> bool:
        """拒绝护工申请"""
        try:
            from extensions import db
            
            CaregiverModel = Caregiver.get_model(db)
            caregiver = CaregiverModel.query.get(caregiver_id)
            
            if not caregiver:
                return False
            
            caregiver.is_approved = False
            caregiver.status = "rejected"
            
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"拒绝护工失败: {e}")
            return False
    
    @staticmethod
    def get_pending_caregivers() -> list:
        """获取待审核护工列表"""
        try:
            from extensions import db
            
            CaregiverModel = Caregiver.get_model(db)
            caregivers = CaregiverModel.query.filter_by(is_approved=False).order_by(CaregiverModel.created_at.desc()).all()
            
            return [caregiver.to_dict() for caregiver in caregivers]
            
        except Exception as e:
            print(f"获取待审核护工失败: {e}")
            return []
    
    @staticmethod
    def get_approved_caregivers() -> list:
        """获取已审核护工列表"""
        try:
            from extensions import db
            
            CaregiverModel = Caregiver.get_model(db)
            caregivers = CaregiverModel.query.filter_by(is_approved=True).order_by(CaregiverModel.approved_at.desc()).all()
            
            return [caregiver.to_dict() for caregiver in caregivers]
            
        except Exception as e:
            print(f"获取已审核护工失败: {e}")
            return []
    
    @staticmethod
    def update_caregiver_availability(caregiver_id: int, available: bool) -> bool:
        """更新护工可用状态"""
        try:
            from extensions import db
            
            CaregiverModel = Caregiver.get_model(db)
            caregiver = CaregiverModel.query.get(caregiver_id)
            
            if not caregiver:
                return False
            
            caregiver.available = available
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"更新护工状态失败: {e}")
            return False
    
    @staticmethod
    def update_caregiver_password(caregiver_id: int, current_password: str, new_password: str) -> bool:
        """修改护工密码"""
        try:
            from extensions import db
            
            CaregiverModel = Caregiver.get_model(db)
            caregiver = CaregiverModel.query.get(caregiver_id)
            
            if not caregiver:
                return False
            
            # 验证当前密码
            if not bcrypt.checkpw(current_password.encode(), caregiver.password_hash.encode()):
                return False
            
            # 设置新密码
            caregiver.set_password(new_password)
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"修改护工密码失败: {e}")
            db.session.rollback()
            return False

    @staticmethod
    def search_caregivers(keyword: str, limit: int = 20) -> list:
        """搜索护工
        
        Args:
            keyword: 搜索关键词（姓名、手机号等）
            limit: 返回结果数量限制
            
        Returns:
            护工列表
        """
        try:
            from extensions import db
            
            CaregiverModel = Caregiver.get_model(db)
            
            # 构建搜索查询
            query = CaregiverModel.query.filter(
                CaregiverModel.is_approved == True,  # 只搜索已审核通过的护工
                CaregiverModel.status != "rejected"   # 排除被拒绝的护工
            )
            
            # 如果有关键词，添加搜索条件
            if keyword and keyword.strip():
                keyword = keyword.strip()
                # 支持按姓名、手机号搜索
                query = query.filter(
                    (CaregiverModel.name.like(f'%{keyword}%')) |
                    (CaregiverModel.phone.like(f'%{keyword}%'))
                )
            
            # 按创建时间排序，限制结果数量
            caregivers = query.order_by(CaregiverModel.created_at.desc()).limit(limit).all()
            
            # 转换为字典格式，只返回必要的信息
            result = []
            for caregiver in caregivers:
                caregiver_dict = caregiver.to_dict()
                # 为了安全，不返回敏感信息
                if 'password_hash' in caregiver_dict:
                    del caregiver_dict['password_hash']
                result.append(caregiver_dict)
            
            return result
            
        except Exception as e:
            print(f"搜索护工失败: {e}")
            return []
    
    def get_caregiver_reviews(self, caregiver_id: int, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        获取护工的评价列表
        
        Args:
            caregiver_id: 护工ID
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            评价列表和统计信息
        """
        try:
            if not self.db:
                return {
                    "success": False,
                    "data": [],
                    "total": 0,
                    "message": "数据库未设置"
                }
            
            # 导入评价模型
            from models.review import Review
            ReviewModel = Review.get_model(self.db)
            
            # 获取护工的评价
            query = ReviewModel.query.filter_by(caregiver_id=caregiver_id)
            total = query.count()
            reviews = query.order_by(ReviewModel.created_at.desc()).offset(offset).limit(limit).all()
            
            # 转换为前端需要的格式
            result = []
            for review in reviews:
                # 获取用户信息
                user = self.user_model.query.get(review.user_id)
                user_name = user.name if user else '匿名用户'
                
                result.append({
                    'id': review.id,
                    'user_name': user_name,
                    'rating': review.rating,
                    'comment': review.comment,
                    'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S') if review.created_at else '未知',
                    'service_type': review.service_type
                })
            
            return {
                "success": True,
                "data": result,
                "total": total,
                "message": "获取成功"
            }
            
        except Exception as e:
            print(f"获取护工评价失败: {e}")
            return {
                "success": False,
                "data": [],
                "total": 0,
                "message": f"获取失败: {str(e)}"
            }
