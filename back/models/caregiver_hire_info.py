"""
护工资源管理系统 - 护工聘用信息模型
====================================

护工聘用信息数据模型定义，包含护工可被聘用的详细信息
"""

from datetime import datetime, timezone
from typing import Dict, Any

class CaregiverHireInfo:
    """护工聘用信息数据模型包装器"""
    
    _model_class = None
    
    def __init__(self):
        pass
    
    @classmethod
    def get_model(cls, db):
        """获取实际的SQLAlchemy模型"""
        # 如果模型已经存在，直接返回
        if cls._model_class is not None:
            return cls._model_class
        
        class CaregiverHireInfoModel(db.Model):
            __tablename__ = 'caregiver_hire_info'
            __table_args__ = {'extend_existing': True}  # 允许表重新定义
            
            # 主键
            id = db.Column(db.Integer, primary_key=True)
            
            # 关联护工ID
            caregiver_id = db.Column(db.Integer, db.ForeignKey('caregiver.id'), nullable=False, unique=True)
            
            # 服务类型
            service_type = db.Column(db.String(50), nullable=False)  # elderly, maternal, medical, rehabilitation, psychological, other
            
            # 工作状态
            status = db.Column(db.String(20), nullable=False, default='available')  # available, busy, unavailable
            
            # 期望时薪
            hourly_rate = db.Column(db.Numeric(10, 2), nullable=False)
            
            # 可工作时间
            work_time = db.Column(db.String(20), nullable=False)  # full-time, part-time, flexible, night-shift
            
            # 服务区域
            service_area = db.Column(db.String(200))
            
            # 可服务时间
            available_time = db.Column(db.String(200))
            
            # 专业技能
            skills = db.Column(db.Text)
            
            # 服务承诺
            commitment = db.Column(db.Text)
            
            # 时间戳
            created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
            updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
            
            # 关联关系 - 暂时注释掉，避免循环引用问题
            # caregiver = db.relationship('caregiver', backref='hire_info')
            
            def to_dict(self) -> Dict[str, Any]:
                """转换为字典格式"""
                return {
                    "id": self.id,
                    "caregiver_id": self.caregiver_id,
                    "service_type": self.service_type,
                    "status": self.status,
                    "hourly_rate": float(self.hourly_rate) if self.hourly_rate else None,
                    "work_time": self.work_time,
                    "service_area": self.service_area,
                    "available_time": self.available_time,
                    "skills": self.skills,
                    "commitment": self.commitment,
                    "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None,
                    "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M") if self.updated_at else None
                }
            
            def to_public_dict(self) -> Dict[str, Any]:
                """转换为公开的字典格式（用于用户端显示）"""
                return {
                    "caregiver_id": self.caregiver_id,
                    "service_type": self.service_type,
                    "status": self.status,
                    "hourly_rate": float(self.hourly_rate) if self.hourly_rate else None,
                    "work_time": self.work_time,
                    "service_area": self.service_area,
                    "available_time": self.available_time,
                    "skills": self.skills,
                    "commitment": self.commitment
                }
        
        cls._model_class = CaregiverHireInfoModel
        return CaregiverHireInfoModel
