"""
护工资源管理系统 - 用户服务
====================================

用户相关的业务逻辑服务
"""

from back.models import User
from back.utils.auth import hash_password, verify_password
from back.extensions import db
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

class UserService:
    """用户服务类"""
    
    @staticmethod
    def create_user(email: str, password: str, name: str = None, phone: str = None) -> User:
        """创建新用户"""
        user = User(
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
    def get_user_by_email(email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def get_user_by_phone(phone: str) -> Optional[User]:
        """通过手机号获取用户"""
        return User.query.filter_by(phone=phone).first()
    
    @staticmethod
    def verify_user(account: str, password: str) -> Optional[User]:
        """验证用户登录"""
        # 尝试通过邮箱查找
        user = User.query.filter_by(email=account).first()
        if user and user.is_approved and verify_password(user.password_hash, password):
            return user
        
        # 尝试通过手机号查找
        user = User.query.filter_by(phone=account).first()
        if user and user.is_approved and verify_password(user.password_hash, password):
            return user
        
        return None
    
    @staticmethod
    def get_pending_users() -> List[User]:
        """获取待审核用户"""
        return User.query.filter_by(is_approved=False).all()
    
    @staticmethod
    def get_approved_users() -> List[User]:
        """获取已审核用户"""
        return User.query.filter_by(is_approved=True).all()
    
    @staticmethod
    def approve_user(user_id: int) -> bool:
        """审核通过用户"""
        user = User.query.get(user_id)
        if user and not user.is_approved:
            user.is_approved = True
            user.approved_at = datetime.now(timezone.utc)
            db.session.commit()
            return True
        return False 