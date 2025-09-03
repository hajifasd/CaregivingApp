"""
护工资源管理系统 - 消息服务
====================================

处理消息的保存、检索、标记已读等业务逻辑，支持数据库存储
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
import json

logger = logging.getLogger(__name__)

class MessageService:
    """消息服务类"""
    
    def __init__(self, db=None):
        self.db = db
        self.messages = []  # 内存存储，作为备用
        self.message_id_counter = 1
    
    def set_db(self, db):
        """设置数据库连接"""
        self.db = db
    
    def save_message(self, message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        保存消息到数据库
        
        Args:
            message_data: 消息数据
            
        Returns:
            保存后的消息对象，包含ID和时间戳
        """
        try:
            if not self.db:
                logger.warning("数据库未设置，使用内存存储")
                return self._save_to_memory(message_data)
            
            # 导入聊天记录模型
            from models.chat import ChatMessage, ChatConversation
            ChatMessageModel = ChatMessage.get_model(self.db)
            ChatConversationModel = ChatConversation.get_model(self.db)
            
            # 处理ID类型转换
            sender_id = message_data.get('senderId')
            receiver_id = message_data.get('receiverId')
            
            # 尝试转换为整数，如果失败则使用原始值
            try:
                sender_id_int = int(sender_id) if str(sender_id).isdigit() else sender_id
                receiver_id_int = int(receiver_id) if str(receiver_id).isdigit() else receiver_id
            except (ValueError, AttributeError):
                sender_id_int = sender_id
                receiver_id_int = receiver_id
            
            # 创建对话ID
            conversation_id = f"{min(sender_id_int, receiver_id_int)}_{max(sender_id_int, receiver_id_int)}"
            
            logger.info(f"保存消息到对话: {conversation_id}")
            
            # 保存聊天消息
            chat_message = ChatMessageModel(
                conversation_id=conversation_id,
                sender_id=sender_id_int,
                sender_type=message_data.get('senderType', 'user'),
                sender_name=message_data.get('senderName', '用户'),
                recipient_id=receiver_id_int,
                recipient_type=message_data.get('receiverType', 'caregiver'),
                content=message_data.get('content'),
                message_type=message_data.get('type', 'text'),
                is_read=False,
                created_at=datetime.now(timezone.utc)
            )
            
            self.db.session.add(chat_message)
            self.db.session.flush()  # 获取消息ID
            
            # 更新或创建对话记录
            conversation = ChatConversationModel.query.filter_by(
                conversation_id=conversation_id
            ).first()
            
            if conversation:
                # 更新现有对话
                conversation.last_message_id = chat_message.id
                conversation.last_message_content = chat_message.content
                conversation.last_message_time = chat_message.created_at
                conversation.unread_count += 1
                conversation.updated_at = datetime.now(timezone.utc)
            else:
                # 创建新对话
                conversation = ChatConversationModel(
                    conversation_id=conversation_id,
                    user_id=min(sender_id_int, receiver_id_int),
                    caregiver_id=max(sender_id_int, receiver_id_int),
                    last_message_id=chat_message.id,
                    last_message_content=chat_message.content,
                    last_message_time=chat_message.created_at,
                    unread_count=1,
                    is_active=True,
                    created_at=datetime.now(timezone.utc)
                )
                self.db.session.add(conversation)
            
            self.db.session.commit()
            
            logger.info(f"消息保存成功: ID={chat_message.id}, 对话={conversation_id}")
            
            # 转换为字典格式返回
            saved_message = chat_message.to_dict()
            saved_message.update({
                'senderId': chat_message.sender_id,
                'senderName': chat_message.sender_name,
                'receiverId': chat_message.recipient_id,
                'timestamp': chat_message.created_at.isoformat(),
                'type': chat_message.message_type
            })
            
            return saved_message
            
        except Exception as e:
            logger.error(f"保存消息失败: {str(e)}")
            if self.db and self.db.session.is_active:
                self.db.session.rollback()
            # 回退到内存存储
            return self._save_to_memory(message_data)
    
    def _save_to_memory(self, message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """保存消息到内存存储（备用方案）"""
        try:
            message = {
                'id': self.message_id_counter,
                'senderId': message_data.get('senderId'),
                'senderName': message_data.get('senderName'),
                'receiverId': message_data.get('receiverId'),
                'content': message_data.get('content'),
                'timestamp': message_data.get('timestamp') or datetime.now().isoformat(),
                'type': message_data.get('type', 'text'),
                'isRead': False,
                'created_at': datetime.now().isoformat()
            }
            
            self.messages.append(message)
            self.message_id_counter += 1
            
            logger.info(f"消息保存到内存成功: ID={message['id']}, 发送者={message['senderId']}")
            return message
            
        except Exception as e:
            logger.error(f"保存消息到内存失败: {str(e)}")
            return None
    
    def get_chat_history(self, user_id: str, contact_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取两个用户之间的聊天历史
        
        Args:
            user_id: 当前用户ID
            contact_id: 联系人ID
            limit: 限制返回的消息数量
            
        Returns:
            聊天历史消息列表
        """
        try:
            if not self.db:
                logger.warning("数据库未设置，使用内存存储查询")
                return self._get_from_memory(user_id, contact_id, limit)
            
            # 从数据库查询
            from models.chat import ChatMessage
            ChatMessageModel = ChatMessage.get_model(self.db)
            
            # 处理ID类型转换，支持字符串和整数ID
            try:
                # 尝试转换为整数
                user_id_int = int(user_id) if str(user_id).isdigit() else user_id
                contact_id_int = int(contact_id) if str(contact_id).isdigit() else contact_id
                
                # 创建对话ID
                conversation_id = f"{min(user_id_int, contact_id_int)}_{max(user_id_int, contact_id_int)}"
            except (ValueError, AttributeError):
                # 如果无法转换为整数，使用原始字符串
                conversation_id = f"{min(user_id, contact_id)}_{max(user_id, contact_id)}"
            
            logger.info(f"查询对话ID: {conversation_id}")
            
            # 查询聊天记录
            chat_messages = ChatMessageModel.query.filter_by(
                conversation_id=conversation_id
            ).order_by(ChatMessageModel.created_at.desc()).limit(limit).all()
            
            # 转换为字典格式
            result = []
            for msg in reversed(chat_messages):  # 重新排序，最新的在后
                try:
                    message_dict = msg.to_dict()
                    message_dict.update({
                        'senderId': msg.sender_id,
                        'senderName': msg.sender_name,
                        'receiverId': msg.recipient_id,
                        'timestamp': msg.created_at.isoformat(),
                        'type': msg.message_type
                    })
                    result.append(message_dict)
                except Exception as e:
                    logger.warning(f"转换消息格式失败: {e}, 消息ID: {msg.id}")
                    continue
            
            logger.info(f"从数据库获取聊天历史成功: 用户={user_id}, 联系人={contact_id}, 消息数={len(result)}")
            return result
            
        except Exception as e:
            logger.error(f"获取聊天历史失败: {str(e)}")
            # 回退到内存查询
            return self._get_from_memory(user_id, contact_id, limit)
    
    def _get_from_memory(self, user_id: str, contact_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """从内存存储获取聊天历史（备用方案）"""
        try:
            # 筛选相关的消息
            chat_messages = []
            for message in self.messages:
                if ((message['senderId'] == user_id and message['receiverId'] == contact_id) or
                    (message['senderId'] == contact_id and message['receiverId'] == user_id)):
                    chat_messages.append(message)
            
            # 按时间排序（最新的在前）
            chat_messages.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # 限制数量
            if limit:
                chat_messages = chat_messages[:limit]
            
            # 重新排序（最新的在后，符合聊天界面的显示习惯）
            chat_messages.sort(key=lambda x: x['timestamp'])
            
            logger.info(f"从内存获取聊天历史成功: 用户={user_id}, 联系人={contact_id}, 消息数={len(chat_messages)}")
            return chat_messages
            
        except Exception as e:
            logger.error(f"从内存获取聊天历史失败: {str(e)}")
            return []
    
    def get_user_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        获取用户的所有对话列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            对话列表
        """
        try:
            if not self.db:
                logger.warning("数据库未设置，无法获取对话列表")
                return []
            
            # 从数据库查询
            from models.chat import ChatConversation
            ChatConversationModel = ChatConversation.get_model(self.db)
            
            # 查询用户的对话
            conversations = ChatConversationModel.query.filter_by(
                user_id=int(user_id)
            ).order_by(ChatConversationModel.updated_at.desc()).all()
            
            # 转换为字典格式
            result = []
            for conv in conversations:
                result.append(conv.to_dict())
            
            logger.info(f"获取用户对话列表成功: 用户={user_id}, 对话数={len(result)}")
            return result
            
        except Exception as e:
            logger.error(f"获取用户对话列表失败: {str(e)}")
            return []
    
    def mark_messages_as_read(self, user_id: str, contact_id: str) -> bool:
        """
        标记消息为已读
        
        Args:
            user_id: 用户ID
            contact_id: 联系人ID
            
        Returns:
            是否成功
        """
        try:
            if not self.db:
                logger.warning("数据库未设置，无法标记消息已读")
                return False
            
            # 从数据库更新
            from models.chat import ChatMessage, ChatConversation
            ChatMessageModel = ChatMessage.get_model(self.db)
            ChatConversationModel = ChatConversation.get_model(self.db)
            
            # 创建对话ID
            conversation_id = f"{min(int(user_id), int(contact_id))}_{max(int(user_id), int(contact_id))}"
            
            # 标记消息为已读
            ChatMessageModel.query.filter_by(
                conversation_id=conversation_id,
                recipient_id=int(user_id),
                is_read=False
            ).update({'is_read': True})
            
            # 重置未读计数
            ChatConversationModel.query.filter_by(
                conversation_id=conversation_id
            ).update({'unread_count': 0})
            
            self.db.session.commit()
            
            logger.info(f"标记消息已读成功: 用户={user_id}, 联系人={contact_id}")
            return True
            
        except Exception as e:
            logger.error(f"标记消息已读失败: {str(e)}")
            if self.db:
                self.db.session.rollback()
            return False
    
    def get_unread_count(self, user_id: str) -> int:
        """
        获取用户未读消息数量
        
        Args:
            user_id: 用户ID
            
        Returns:
            未读消息数量
        """
        try:
            if not self.db:
                logger.warning("数据库未设置，无法获取未读消息数量")
                return 0
            
            # 从数据库查询
            from models.chat import ChatConversation
            ChatConversationModel = ChatConversation.get_model(self.db)
            
            # 查询用户的未读消息总数
            total_unread = self.db.session.query(
                self.db.func.sum(ChatConversationModel.unread_count)
            ).filter_by(user_id=int(user_id)).scalar()
            
            return total_unread or 0
            
        except Exception as e:
            logger.error(f"获取未读消息数量失败: {str(e)}")
            return 0

# 创建全局消息服务实例
message_service = MessageService()
