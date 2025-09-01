"""
护工资源管理系统 - 用户数据模型
====================================

用户数据模型定义，包含所有用户相关字段和方法
"""

from datetime import datetime, timezone
from typing import Dict, Any

class User:
    """用户数据模型包装器"""
    
    _model_class = None
    
    def __init__(self):
        pass
    
    @classmethod
    def get_model(cls, db):
        """获取实际的SQLAlchemy模型"""
        if cls._model_class is not None:
            return cls._model_class
        
        class UserModel(db.Model):
            __tablename__ = 'user'
            
            # 基础字段
            id = db.Column(db.Integer, primary_key=True)
            email = db.Column(db.String(120), unique=True, nullable=False)
            password_hash = db.Column(db.String(256), nullable=False)
            id_file = db.Column(db.String(200))
            
            # 审核状态字段
            is_approved = db.Column(db.Boolean, default=False)
            created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
            approved_at = db.Column(db.DateTime, index=True)
            
            # 用户信息字段
            name = db.Column(db.String(100))
            gender = db.Column(db.String(10))
            birth_date = db.Column(db.Date)
            address = db.Column(db.String(200))
            emergency_contact = db.Column(db.String(100))
            phone = db.Column(db.String(20))
            emergency_contact_phone = db.Column(db.String(20))
            special_needs = db.Column(db.Text)
            avatar_url = db.Column(db.String(200))
            is_verified = db.Column(db.Boolean, default=False)

            def to_dict(self) -> Dict[str, Any]:
                """转换为字典格式"""
                return {
                    "id": self.id,
                    "email": self.email,
                    "id_file": self.id_file,
                    "id_file_url": f"/uploads/{self.id_file}" if (self.id_file and self.id_file.strip()) else None,
                    "is_approved": self.is_approved,
                    "created_at": self.created_at.strftime("%Y-%m-%d %H:%M"),
                    "approved_at": self.approved_at.strftime("%Y-%m-%d %H:%M") if self.approved_at else None,
                    # 扩展字段
                    "name": self.name,
                    "gender": self.gender,
                    "birth_date": self.birth_date.strftime("%Y-%m-%d") if self.birth_date else None,
                    "address": self.address,
                    "emergency_contact": self.emergency_contact,
                    "phone": self.phone,
                    "emergency_contact_phone": self.emergency_contact_phone,
                    "special_needs": self.special_needs,
                    "avatar_url": self.avatar_url,
                    "is_verified": self.is_verified
                }

            def set_password(self, password: str):
                """设置密码"""
                import bcrypt
                self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        cls._model_class = UserModel
        return UserModel 