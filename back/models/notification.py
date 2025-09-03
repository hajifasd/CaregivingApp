"""
护工资源管理系统 - 通知系统数据模型
====================================

用于管理用户和护工之间的各种通知，包括工作机会、申请回复、合同状态变更等
"""

from datetime import datetime, timezone
from typing import Dict, Any

class Notification:
    """通知模型包装器"""
    
    _model_class = None
    
    def __init__(self):
        pass
    
    @classmethod
    def get_model(cls, db):
        """获取实际的SQLAlchemy模型"""
        if cls._model_class is not None:
            return cls._model_class
        
        class NotificationModel(db.Model):
            """通知模型 - 存储系统内的各种通知信息
            
            字段说明：
            - id: 通知唯一标识
            - recipient_id: 接收者ID
            - recipient_type: 接收者类型（user, caregiver, admin）
            - sender_id: 发送者ID
            - sender_type: 发送者类型（user, caregiver, admin, system）
            - notification_type: 通知类型（job_opportunity工作机会, application_response申请回复, contract_update合同更新, system_message系统消息）
            - title: 通知标题
            - content: 通知内容
            - related_id: 相关业务ID（如申请ID、合同ID等）
            - related_type: 相关业务类型
            - is_read: 是否已读
            - read_at: 阅读时间
            - priority: 优先级（low, normal, high, urgent）
            - created_at: 创建时间
            """
            __tablename__ = 'notification'
            __table_args__ = {'extend_existing': True}
            
            id = db.Column(db.Integer, primary_key=True)
            recipient_id = db.Column(db.Integer, nullable=False, index=True)
            recipient_type = db.Column(db.String(20), nullable=False)
            sender_id = db.Column(db.Integer)
            sender_type = db.Column(db.String(20))
            notification_type = db.Column(db.String(50), nullable=False)
            title = db.Column(db.String(200), nullable=False)
            content = db.Column(db.Text, nullable=False)
            related_id = db.Column(db.Integer)
            related_type = db.Column(db.String(50))
            is_read = db.Column(db.Boolean, default=False)
            read_at = db.Column(db.DateTime)
            priority = db.Column(db.String(20), default='normal')
            created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
            
            def to_dict(self) -> Dict[str, Any]:
                """转换为字典格式"""
                return {
                    "id": self.id,
                    "recipient_id": self.recipient_id,
                    "recipient_type": self.recipient_type,
                    "sender_id": self.sender_id,
                    "sender_type": self.sender_type,
                    "notification_type": self.notification_type,
                    "title": self.title,
                    "content": self.content,
                    "related_id": self.related_id,
                    "related_type": self.related_type,
                    "is_read": self.is_read,
                    "read_at": self.read_at.isoformat() if self.read_at else None,
                    "priority": self.priority,
                    "created_at": self.created_at.isoformat() if self.created_at else None
                }
            
            def mark_as_read(self):
                """标记为已读"""
                self.is_read = True
                self.read_at = datetime.now(timezone.utc)
            
            def __repr__(self):
                return f"<Notification(id={self.id}, type='{self.notification_type}', recipient={self.recipient_type}:{self.recipient_id})>"
        
        cls._model_class = NotificationModel
        return NotificationModel
