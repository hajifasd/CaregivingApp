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
            
            # 统一字段映射 - 支持多种前端字段格式
            sender_id = (message_data.get('senderId') or 
                        message_data.get('sender_id') or 
                        message_data.get('senderId'))
            receiver_id = (message_data.get('receiverId') or 
                          message_data.get('recipient_id') or 
                          message_data.get('receiverId'))
            sender_type = (message_data.get('senderType') or 
                          message_data.get('sender_type') or 
                          'user')
            receiver_type = (message_data.get('receiverType') or 
                            message_data.get('recipient_type') or 
                            'caregiver')
            sender_name = (message_data.get('senderName') or 
                          message_data.get('sender_name') or 
                          '用户')
            content = message_data.get('content', '')
            message_type = message_data.get('type') or message_data.get('message_type', 'text')
            
            # 处理ID类型转换 - 支持字符串和整数ID
            try:
                # 如果是字符串ID，尝试提取数字部分
                if isinstance(sender_id, str):
                    if sender_id.startswith('caregiver_'):
                        sender_id_int = int(sender_id.replace('caregiver_', ''))
                    elif sender_id.startswith('user_'):
                        sender_id_int = int(sender_id.replace('user_', ''))
                    else:
                        sender_id_int = int(sender_id) if sender_id.isdigit() else sender_id
                else:
                    sender_id_int = int(sender_id) if str(sender_id).isdigit() else sender_id
                
                if isinstance(receiver_id, str):
                    if receiver_id.startswith('caregiver_'):
                        receiver_id_int = int(receiver_id.replace('caregiver_', ''))
                    elif receiver_id.startswith('user_'):
                        receiver_id_int = int(receiver_id.replace('user_', ''))
                    else:
                        receiver_id_int = int(receiver_id) if receiver_id.isdigit() else receiver_id
                else:
                    receiver_id_int = int(receiver_id) if str(receiver_id).isdigit() else receiver_id
                    
            except (ValueError, AttributeError):
                # 如果无法转换为整数，使用原始值
                sender_id_int = sender_id
                receiver_id_int = receiver_id
            
            # 创建对话ID - 确保一致性
            conversation_id = f"{min(sender_id_int, receiver_id_int)}_{max(sender_id_int, receiver_id_int)}"
            
            logger.info(f"保存消息到对话: {conversation_id}, 发送者: {sender_id_int}({sender_type}), 接收者: {receiver_id_int}({receiver_type})")
            
            # 保存聊天消息
            chat_message = ChatMessageModel(
                conversation_id=conversation_id,
                sender_id=sender_id_int,
                sender_type=sender_type,
                sender_name=sender_name,
                recipient_id=receiver_id_int,
                recipient_type=receiver_type,
                content=content,
                message_type=message_type,
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
            
            # 转换为字典格式返回 - 使用前端期望的字段名
            saved_message = chat_message.to_dict()
            saved_message.update({
                'senderId': chat_message.sender_id,
                'senderName': chat_message.sender_name,
                'senderType': chat_message.sender_type,
                'receiverId': chat_message.recipient_id,
                'receiverType': chat_message.recipient_type,
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
            # 统一字段映射 - 与数据库存储保持一致
            sender_id = (message_data.get('senderId') or 
                        message_data.get('sender_id') or 
                        message_data.get('senderId'))
            receiver_id = (message_data.get('receiverId') or 
                          message_data.get('recipient_id') or 
                          message_data.get('receiverId'))
            sender_name = (message_data.get('senderName') or 
                          message_data.get('sender_name') or 
                          '用户')
            content = message_data.get('content', '')
            message_type = message_data.get('type') or message_data.get('message_type', 'text')
            
            message = {
                'id': self.message_id_counter,
                'senderId': sender_id,
                'senderName': sender_name,
                'receiverId': receiver_id,
                'content': content,
                'timestamp': message_data.get('timestamp') or datetime.now().isoformat(),
                'type': message_type,
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
                # 处理字符串ID格式
                if isinstance(user_id, str):
                    if user_id.startswith('user_'):
                        user_id_int = int(user_id.replace('user_', ''))
                    elif user_id.startswith('caregiver_'):
                        user_id_int = int(user_id.replace('caregiver_', ''))
                    else:
                        user_id_int = int(user_id) if user_id.isdigit() else user_id
                else:
                    user_id_int = int(user_id) if str(user_id).isdigit() else user_id
                
                if isinstance(contact_id, str):
                    if contact_id.startswith('user_'):
                        contact_id_int = int(contact_id.replace('user_', ''))
                    elif contact_id.startswith('caregiver_'):
                        contact_id_int = int(contact_id.replace('caregiver_', ''))
                    else:
                        contact_id_int = int(contact_id) if contact_id.isdigit() else contact_id
                else:
                    contact_id_int = int(contact_id) if str(contact_id).isdigit() else contact_id
                
                # 创建对话ID
                conversation_id = f"{min(user_id_int, contact_id_int)}_{max(user_id_int, contact_id_int)}"
            except (ValueError, AttributeError):
                # 如果无法转换为整数，使用原始字符串
                conversation_id = f"{min(user_id, contact_id)}_{max(user_id, contact_id)}"
            
            logger.info(f"查询对话ID: {conversation_id}, 用户ID: {user_id_int}, 联系人ID: {contact_id_int}")
            
            # 查询聊天记录
            chat_messages = ChatMessageModel.query.filter_by(
                conversation_id=conversation_id
            ).order_by(ChatMessageModel.created_at.asc()).limit(limit).all()
            
            # 转换为字典格式，使用前端期望的字段名
            result = []
            for msg in chat_messages:
                msg_dict = msg.to_dict()
                # 添加前端期望的字段
                msg_dict.update({
                    'senderId': msg.sender_id,
                    'senderName': msg.sender_name,
                    'senderType': msg.sender_type,
                    'receiverId': msg.recipient_id,
                    'receiverType': msg.recipient_type,
                    'timestamp': msg.created_at.isoformat() if msg.created_at else None,
                    'type': msg.message_type
                })
                result.append(msg_dict)
            
            logger.info(f"查询到 {len(result)} 条聊天记录")
            return result
            
        except Exception as e:
            logger.error(f"获取聊天历史失败: {str(e)}")
            return []
    
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

    def get_user_conversations(self, user_id: str, user_type: str = 'user') -> List[Dict[str, Any]]:
        """
        获取用户的所有对话列表
        
        Args:
            user_id: 用户ID
            user_type: 用户类型（user或caregiver）
            
        Returns:
            对话列表
        """
        try:
            if not self.db:
                logger.warning("数据库未设置，使用内存存储查询")
                return []
            
            # 从数据库查询
            from models.chat import ChatConversation
            ChatConversationModel = ChatConversation.get_model(self.db)
            
            # 根据用户类型查询对话
            if user_type == 'user':
                conversations = ChatConversationModel.query.filter_by(user_id=user_id, is_active=True).all()
            else:
                conversations = ChatConversationModel.query.filter_by(caregiver_id=user_id, is_active=True).all()
            
            # 转换为字典格式
            result = []
            for conv in conversations:
                result.append(conv.to_dict())
            
            logger.info(f"查询到 {len(result)} 个对话")
            return result
            
        except Exception as e:
            logger.error(f"获取对话列表失败: {str(e)}")
            return []

    def mark_messages_as_read(self, user_id: str, contact_id: str) -> bool:
        """
        标记消息为已读
        
        Args:
            user_id: 当前用户ID
            contact_id: 联系人ID
            
        Returns:
            是否成功
        """
        try:
            if not self.db:
                logger.warning("数据库未设置，无法标记已读")
                return False
            
            # 从数据库更新
            from models.chat import ChatMessage
            ChatMessageModel = ChatMessage.get_model(self.db)
            
            # 处理ID类型转换
            try:
                user_id_int = int(user_id) if str(user_id).isdigit() else user_id
                contact_id_int = int(contact_id) if str(contact_id).isdigit() else contact_id
                conversation_id = f"{min(user_id_int, contact_id_int)}_{max(user_id_int, contact_id_int)}"
            except (ValueError, AttributeError):
                conversation_id = f"{min(user_id, contact_id)}_{max(user_id, contact_id)}"
            
            # 更新未读消息为已读
            updated = ChatMessageModel.query.filter_by(
                conversation_id=conversation_id,
                recipient_id=user_id_int,
                is_read=False
            ).update({'is_read': True})
            
            self.db.session.commit()
            logger.info(f"标记了 {updated} 条消息为已读")
            return True
            
        except Exception as e:
            logger.error(f"标记消息已读失败: {str(e)}")
            if self.db:
                self.db.session.rollback()
            return False

    def get_unread_count(self, user_id: str, user_type: str = 'user') -> int:
        """
        获取用户未读消息数量
        
        Args:
            user_id: 用户ID
            user_type: 用户类型
            
        Returns:
            未读消息数量
        """
        try:
            if not self.db:
                logger.warning("数据库未设置，无法获取未读数量")
                return 0
            
            # 从数据库查询
            from models.chat import ChatMessage
            ChatMessageModel = ChatMessage.get_model(self.db)
            
            # 查询未读消息数量
            unread_count = ChatMessageModel.query.filter_by(
                recipient_id=user_id,
                is_read=False
            ).count()
            
            logger.info(f"用户 {user_id} 有 {unread_count} 条未读消息")
            return unread_count
            
        except Exception as e:
            logger.error(f"获取未读消息数量失败: {str(e)}")
            return 0

    def search_messages(self, user_id: str, user_type: str, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        搜索消息内容
        
        Args:
            user_id: 用户ID
            user_type: 用户类型
            keyword: 搜索关键词
            limit: 限制返回数量
            
        Returns:
            搜索结果列表
        """
        try:
            if not self.db:
                logger.warning("数据库未设置，无法搜索消息")
                return []
            
            # 从数据库搜索
            from models.chat import ChatMessage
            ChatMessageModel = ChatMessage.get_model(self.db)
            
            # 搜索用户发送或接收的消息中包含关键词的内容
            messages = ChatMessageModel.query.filter(
                ChatMessageModel.content.like(f'%{keyword}%'),
                (ChatMessageModel.sender_id == user_id) | (ChatMessageModel.recipient_id == user_id)
            ).order_by(ChatMessageModel.created_at.desc()).limit(limit).all()
            
            # 转换为字典格式
            result = []
            for msg in messages:
                result.append(msg.to_dict())
            
            logger.info(f"搜索关键词 '{keyword}' 找到 {len(result)} 条消息")
            return result
            
        except Exception as e:
            logger.error(f"搜索消息失败: {str(e)}")
            return []

# 创建全局消息服务实例
message_service = MessageService()
