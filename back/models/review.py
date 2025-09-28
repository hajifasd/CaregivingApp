"""
护工资源管理系统 - 评价数据模型
====================================

用户对护工的评价数据模型
"""

from datetime import datetime, timezone
from typing import Dict, Any

class Review:
    """评价数据模型包装器"""
    
    _model_class = None
    
    def __init__(self):
        pass
    
    @classmethod
    def get_model(cls, db):
        """获取实际的SQLAlchemy模型"""
        if cls._model_class is not None:
            return cls._model_class
        
        class ReviewModel(db.Model):
            """评价模型 - 存储用户对护工的评价
            
            字段说明：
            - id: 评价唯一标识
            - user_id: 用户ID（外键关联）
            - caregiver_id: 护工ID（外键关联）
            - rating: 评分（1-5星）
            - comment: 评价内容
            - service_type: 服务类型
            - created_at: 评价时间
            """
            __tablename__ = 'review'
            __table_args__ = {'extend_existing': True}
            
            id = db.Column(db.Integer, primary_key=True)
            user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
            caregiver_id = db.Column(db.Integer, db.ForeignKey('caregiver.id'), nullable=False)
            appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=True)
            rating = db.Column(db.Integer, nullable=False)
            comment = db.Column(db.Text)
            service_type = db.Column(db.String(50))
            reply = db.Column(db.Text)  # 护工回复
            created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
            
            def to_dict(self):
                return {
                    'id': self.id,
                    'user_id': self.user_id,
                    'caregiver_id': self.caregiver_id,
                    'appointment_id': self.appointment_id,
                    'rating': self.rating,
                    'comment': self.comment,
                    'service_type': self.service_type,
                    'reply': self.reply,
                    'created_at': self.created_at.isoformat() if self.created_at else None
                }
        
        cls._model_class = ReviewModel
        return ReviewModel
