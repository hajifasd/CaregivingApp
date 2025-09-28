"""
护工资源管理系统 - 用户服务
====================================

用户相关的业务逻辑服务
"""

from models.user import User
from utils.auth import generate_token, verify_token
from extensions import db
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

class UserService:
    """用户服务类"""
    
    @staticmethod
    def create_user(email: str, password: str, name: str = None, phone: str = None):
        """创建新用户"""
        UserModel = User.get_model(db)
        user = UserModel(
            email=email,
            name=name,
            phone=phone,
            is_approved=False
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def get_user_by_email(email: str):
        """通过邮箱获取用户"""
        UserModel = User.get_model(db)
        return UserModel.query.filter_by(email=email).first()
    
    @staticmethod
    def get_user_by_phone(phone: str):
        """通过手机号获取用户"""
        UserModel = User.get_model(db)
        return UserModel.query.filter_by(phone=phone).first()
    
    @staticmethod
    def verify_user(account: str, password: str):
        """验证用户登录"""
        UserModel = User.get_model(db)
        
        # 尝试通过邮箱查找
        user = UserModel.query.filter_by(email=account).first()
        if user and user.is_approved and user.check_password(password):
            return user
        
        # 尝试通过手机号查找
        user = UserModel.query.filter_by(phone=account).first()
        if user and user.is_approved and user.check_password(password):
            return user
        
        return None
    
    @staticmethod
    def get_pending_users():
        """获取待审核用户"""
        UserModel = User.get_model(db)
        return UserModel.query.filter_by(is_approved=False).all()
    
    @staticmethod
    def get_approved_users():
        """获取已审核用户"""
        UserModel = User.get_model(db)
        return UserModel.query.filter_by(is_approved=True).all()
    
    @staticmethod
    def get_user_by_id(user_id: int):
        """根据ID获取用户"""
        UserModel = User.get_model(db)
        return UserModel.query.get(user_id)
    
    @staticmethod
    def approve_user(user_id: int) -> bool:
        """审核通过用户"""
        UserModel = User.get_model(db)
        user = UserModel.query.get(user_id)
        if user and not user.is_approved:
            user.is_approved = True
            user.approved_at = datetime.now(timezone.utc)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def update_user_profile(user_id: int, profile_data: Dict[str, Any]) -> bool:
        """更新用户个人资料"""
        try:
            UserModel = User.get_model(db)
            user = UserModel.query.get(user_id)
            
            if not user:
                return False
            
            # 更新允许的字段，映射前端字段到数据库字段
            field_mapping = {
                'name': 'name',
                'phone': 'phone', 
                'email': 'email',
                'gender': 'gender',
                'birth_date': 'birth_date',
                'address': 'address',
                'emergency_contact': 'emergency_contact',
                'emergency_phone': 'emergency_contact_phone',  # 数据库字段名不同
                'special_needs': 'special_needs'
            }
            
            for frontend_field, value in profile_data.items():
                if frontend_field in field_mapping:
                    db_field = field_mapping[frontend_field]
                    if hasattr(user, db_field):
                        setattr(user, db_field, value)
            
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"更新用户资料失败: {str(e)}")
            db.session.rollback()
            return False 