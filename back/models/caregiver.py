"""
护工资源管理系统 - 护工数据模型
====================================

护工数据模型定义，包含所有护工相关字段和方法
"""

from datetime import datetime, timezone
from typing import Dict, Any

class Caregiver:
    """护工数据模型包装器"""
    
    _model_class = None
    
    def __init__(self):
        pass
    
    @classmethod
    def get_model(cls, db):
        """获取实际的SQLAlchemy模型"""
        # 如果模型已经存在，直接返回
        if cls._model_class is not None:
            return cls._model_class
        
        class CaregiverModel(db.Model):
            __tablename__ = 'caregiver'
            __table_args__ = {'extend_existing': True}  # 允许表重新定义
            
            # 基础字段
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(100), nullable=False)
            phone = db.Column(db.String(20), unique=True, nullable=False)
            password_hash = db.Column(db.String(256), nullable=False)
            
            # 审核状态字段
            is_approved = db.Column(db.Boolean, default=False)
            created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
            approved_at = db.Column(db.DateTime, index=True)
            
            # 护工信息字段
            gender = db.Column(db.String(10))
            age = db.Column(db.Integer)
            avatar_url = db.Column(db.String(200))
            qualification = db.Column(db.String(100))
            introduction = db.Column(db.Text)
            experience_years = db.Column(db.Integer)
            hourly_rate = db.Column(db.Float)
            rating = db.Column(db.Float, default=0)
            review_count = db.Column(db.Integer, default=0)
            status = db.Column(db.String(20), default="pending")
            available = db.Column(db.Boolean, default=True)

            def to_dict(self) -> Dict[str, Any]:
                """转换为字典格式"""
                return {
                    "id": self.id,
                    "name": self.name,
                    "phone": self.phone,
                    "is_approved": self.is_approved,
                    "created_at": self.created_at.strftime("%Y-%m-%d %H:%M"),
                    "approved_at": self.approved_at.strftime("%Y-%m-%d %H:%M") if self.approved_at else None,
                    # 扩展字段
                    "gender": self.gender,
                    "age": self.age,
                    "avatar_url": self.avatar_url,
                    "qualification": self.qualification,
                    "introduction": self.introduction,
                    "experience_years": self.experience_years,
                    "hourly_rate": self.hourly_rate,
                    "rating": self.rating,
                    "review_count": self.review_count,
                    "status": self.status,
                    "available": self.available
                }

            def set_password(self, password: str):
                """设置密码"""
                import bcrypt
                self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            
            def check_password(self, password: str) -> bool:
                """验证密码"""
                import bcrypt
                try:
                    return bcrypt.checkpw(password.encode(), self.password_hash.encode())
                except Exception:
                    return False
        
        cls._model_class = CaregiverModel
        return CaregiverModel 