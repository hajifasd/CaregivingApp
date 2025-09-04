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
            
            CaregiverModel = Caregiver.get_model(db)
            caregiver = CaregiverModel.query.get(caregiver_id)
            
            if not caregiver:
                return {}
            
            # 这里可以添加更多统计数据，目前返回基础数据
            return {
                'total_jobs': 0,  # 总工作机会
                'active_appointments': 0,  # 进行中预约
                'monthly_earnings': 0,  # 本月收入
                'rating': caregiver.rating or 0,  # 平均评分
                'caregiver_info': caregiver.to_dict()
            }
            
        except Exception as e:
            print(f"获取护工仪表盘数据失败: {e}")
            return {}
    
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
