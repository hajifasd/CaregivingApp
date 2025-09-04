"""
护工资源管理系统 - 聊天记录数据模型
====================================

专门用于存储用户和护工之间的聊天记录，支持历史查询和消息管理
"""

from datetime import datetime, timezone
from typing import Dict, Any

class ChatMessage:
    """聊天记录模型包装器"""
    
    _model_class = None
    
    def __init__(self):
        pass
    
    @classmethod
    def get_model(cls, db):
        """获取实际的SQLAlchemy模型"""
        if cls._model_class is not None:
            return cls._model_class
        
        class ChatMessageModel(db.Model):
            """聊天记录模型 - 存储用户和护工之间的所有聊天消息
            
            字段说明：
            - id: 消息唯一标识
            - conversation_id: 对话ID（用户ID_护工ID的组合）
            - sender_id: 发送者ID
            - sender_type: 发送者类型（user用户, caregiver护工）
            - sender_name: 发送者姓名
            - recipient_id: 接收者ID
            - recipient_type: 接收者类型（user用户, caregiver护工）
            - content: 消息内容
            - message_type: 消息类型（text文本, image图片, file文件, system系统消息）
            - is_read: 是否已读
            - created_at: 创建时间
            - updated_at: 更新时间
            """
            __tablename__ = 'chat_message'
            __table_args__ = {'extend_existing': True}  # 允许表重新定义
            
            id = db.Column(db.Integer, primary_key=True)
            conversation_id = db.Column(db.String(100), nullable=False, index=True)  # 用于快速查询对话
            sender_id = db.Column(db.Integer, nullable=False)
            sender_type = db.Column(db.String(20), nullable=False)
            sender_name = db.Column(db.String(100), nullable=False)
            recipient_id = db.Column(db.Integer, nullable=False)
            recipient_type = db.Column(db.String(20), nullable=False)
            content = db.Column(db.Text, nullable=False)
            message_type = db.Column(db.String(20), default='text')
            is_read = db.Column(db.Boolean, default=False)
            created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
            updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

            def to_dict(self) -> Dict[str, Any]:
                """转换为字典格式"""
                return {
                    "id": self.id,
                    "conversation_id": self.conversation_id,
                    "sender_id": self.sender_id,
                    "sender_type": self.sender_type,
                    "sender_name": self.sender_name,
                    "recipient_id": self.recipient_id,
                    "recipient_type": self.recipient_type,
                    "content": self.content,
                    "message_type": self.message_type,
                    "is_read": self.is_read,
                    "created_at": self.created_at.isoformat() if self.created_at else None,
                    "updated_at": self.updated_at.isoformat() if self.updated_at else None
                }

            def __repr__(self):
                return f"<ChatMessage(id={self.id}, conversation_id='{self.conversation_id}', sender='{self.sender_name}', content='{self.content[:50]}...')>"
        
        cls._model_class = ChatMessageModel
        return ChatMessageModel

class ChatConversation:
    """聊天对话模型包装器"""
    
    _model_class = None
    
    def __init__(self):
        pass
    
    @classmethod
    def get_model(cls, db):
        """获取实际的SQLAlchemy模型"""
        if cls._model_class is not None:
            return cls._model_class
        
        class ChatConversationModel(db.Model):
            """聊天对话模型 - 管理用户和护工之间的对话会话
            
            字段说明：
            - id: 对话唯一标识
            - conversation_id: 对话ID（用户ID_护工ID的组合）
            - user_id: 用户ID
            - caregiver_id: 护工ID
            - last_message_id: 最后一条消息的ID
            - last_message_content: 最后一条消息内容
            - last_message_time: 最后一条消息时间
            - unread_count: 未读消息数量
            - is_active: 对话是否活跃
            - created_at: 创建时间
            - updated_at: 更新时间
            """
            __tablename__ = 'chat_conversation'
            __table_args__ = {'extend_existing': True}  # 允许表重新定义
            
            id = db.Column(db.Integer, primary_key=True)
            conversation_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
            user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
            caregiver_id = db.Column(db.Integer, db.ForeignKey('caregiver.id'), nullable=False, index=True)
            last_message_id = db.Column(db.Integer, db.ForeignKey('chat_message.id'))
            last_message_content = db.Column(db.Text)
            last_message_time = db.Column(db.DateTime, index=True)
            unread_count = db.Column(db.Integer, default=0)
            is_active = db.Column(db.Boolean, default=True, index=True)
            created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
            updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

            def to_dict(self) -> Dict[str, Any]:
                """转换为字典格式"""
                return {
                    "id": self.id,
                    "conversation_id": self.conversation_id,
                    "user_id": self.user_id,
                    "caregiver_id": self.caregiver_id,
                    "last_message_id": self.last_message_id,
                    "last_message_content": self.last_message_content,
                    "last_message_time": self.last_message_time.isoformat() if self.last_message_time else None,
                    "unread_count": self.unread_count,
                    "is_active": self.is_active,
                    "created_at": self.created_at.isoformat() if self.created_at else None,
                    "updated_at": self.updated_at.isoformat() if self.updated_at else None
                }

            def __repr__(self):
                return f"<ChatConversation(id={self.id}, conversation_id='{self.conversation_id}', unread={self.unread_count})>"
        
        cls._model_class = ChatConversationModel
        return ChatConversationModel
