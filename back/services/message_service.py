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
        self._model_class = None  # 缓存模型类
    
    def set_db(self, db):
        """设置数据库连接"""
        self.db = db
        logger.info("消息服务数据库连接已设置")
    
    def get_model(self):
        """获取消息模型类"""
        if not self.db:
            logger.error("数据库连接未设置，无法获取模型")
            return None
            
        if self._model_class is None:
            try:
                from models.chat import ChatMessage
                self._model_class = ChatMessage.get_model(self.db)
                logger.info("消息模型类已加载")
            except Exception as e:
                logger.error(f"加载消息模型失败: {str(e)}")
                return None
        
        return self._model_class
    
    def _normalize_message_data(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化消息数据格式
        
        Args:
            message_data: 原始消息数据
            
        Returns:
            标准化后的消息数据
        """
        # 统一字段映射 - 支持多种前端字段格式
        normalized = {
            'sender_id': (message_data.get('senderId') or 
                         message_data.get('sender_id') or 
                         message_data.get('senderId')),
            'recipient_id': (message_data.get('receiverId') or 
                           message_data.get('recipient_id') or 
                           message_data.get('receiverId')),
            'sender_type': (message_data.get('senderType') or 
                           message_data.get('sender_type') or 
                           'user'),
            'recipient_type': (message_data.get('receiverType') or 
                             message_data.get('recipient_type') or 
                             'caregiver'),
            'sender_name': (message_data.get('senderName') or 
                           message_data.get('sender_name') or 
                           '用户'),
            'content': message_data.get('content', ''),
            'message_type': message_data.get('type') or message_data.get('message_type', 'text'),
            'timestamp': message_data.get('timestamp') or message_data.get('created_at')
        }
        
        # 验证必要字段
        if not normalized['sender_id'] or not normalized['recipient_id'] or not normalized['content']:
            raise ValueError("缺少必要字段: sender_id, recipient_id, content")
        
        return normalized
    
    def get_message_history(self, user_id: int, user_type: str, contact_id: int, 
                          contact_type: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取消息历史
        
        Args:
            user_id: 用户ID
            user_type: 用户类型
            contact_id: 联系人ID
            contact_type: 联系人类型
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            消息历史列表
        """
        try:
            if not self.db:
                logger.warning("数据库未设置，返回空列表")
                return []
            
            from models.chat import ChatMessage
            ChatMessageModel = ChatMessage.get_model(self.db)
            
            # 创建对话ID
            conversation_id = f"{min(user_id, contact_id)}_{max(user_id, contact_id)}"
            
            # 查询消息历史
            messages = ChatMessageModel.query.filter(
                ChatMessageModel.conversation_id == conversation_id
            ).order_by(ChatMessageModel.created_at.desc()).offset(offset).limit(limit).all()
            
            # 转换为字典格式
            result = []
            for message in messages:
                result.append(message.to_dict())
            
            logger.info(f"获取消息历史: {user_type}_{user_id} <-> {contact_type}_{contact_id}, 数量: {len(result)}")
            return result
            
        except Exception as e:
            logger.error(f"获取消息历史失败: {str(e)}")
            return []
    
    def mark_message_as_read(self, message_id: int, user_id: int, user_type: str) -> bool:
        """
        标记消息为已读
        
        Args:
            message_id: 消息ID
            user_id: 用户ID
            user_type: 用户类型
            
        Returns:
            是否成功
        """
        try:
            if not self.db:
                logger.warning("数据库未设置，无法标记已读")
                return False
            
            from models.chat import ChatMessage
            ChatMessageModel = ChatMessage.get_model(self.db)
            
            # 查找消息
            message = ChatMessageModel.query.get(message_id)
            if not message:
                logger.warning(f"消息不存在: {message_id}")
                return False
            
            # 检查用户是否有权限标记此消息为已读
            if (message.recipient_id == user_id and message.recipient_type == user_type):
                message.is_read = True
                self.db.session.commit()
                logger.info(f"消息已标记为已读: {message_id} by {user_type}_{user_id}")
                return True
            else:
                logger.warning(f"用户无权限标记消息为已读: {user_type}_{user_id} -> {message_id}")
                return False
                
        except Exception as e:
            logger.error(f"标记消息已读失败: {str(e)}")
            return False
    
    def _normalize_id(self, user_id) -> int:
        """
        标准化用户ID格式
        
        Args:
            user_id: 用户ID（可能是字符串或整数）
            
        Returns:
            标准化的整数ID
        """
        try:
            if isinstance(user_id, str):
                if user_id.startswith('caregiver_'):
                    return int(user_id.replace('caregiver_', ''))
                elif user_id.startswith('user_'):
                    return int(user_id.replace('user_', ''))
                else:
                    return int(user_id) if user_id.isdigit() else user_id
            else:
                return int(user_id) if str(user_id).isdigit() else user_id
        except (ValueError, AttributeError):
            # 如果无法转换为整数，使用原始值
            return user_id
    
    def save_message(self, message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        保存消息到数据库
        
        Args:
            message_data: 消息数据，支持多种字段格式
            
        Returns:
            保存后的消息对象，包含ID和时间戳
        """
        try:
            if not self.db:
                logger.warning("数据库未设置，使用内存存储")
                return self._save_to_memory(message_data)
            
            # 获取消息模型类
            ChatMessageModel = self.get_model()
            if not ChatMessageModel:
                logger.error("无法获取消息模型，使用内存存储")
                return self._save_to_memory(message_data)
            
            # 导入对话模型
            try:
                from models.chat import ChatConversation
                ChatConversationModel = ChatConversation.get_model(self.db)
            except Exception as e:
                logger.warning(f"无法加载对话模型: {str(e)}")
                ChatConversationModel = None
            
            # 统一字段映射 - 支持多种前端字段格式
            normalized_data = self._normalize_message_data(message_data)
            
            sender_id = normalized_data['sender_id']
            receiver_id = normalized_data['recipient_id']
            sender_type = normalized_data['sender_type']
            receiver_type = normalized_data['recipient_type']
            sender_name = normalized_data['sender_name']
            content = normalized_data['content']
            message_type = normalized_data['message_type']
            
            # 处理ID类型转换 - 支持字符串和整数ID
            sender_id_int = self._normalize_id(sender_id)
            receiver_id_int = self._normalize_id(receiver_id)
            
            # 创建对话ID - 确保一致性
            conversation_id = f"{min(sender_id_int, receiver_id_int)}_{max(sender_id_int, receiver_id_int)}"
            
            logger.info(f"保存消息到对话: {conversation_id}, 发送者: {sender_id_int}({sender_type}), 接收者: {receiver_id_int}({receiver_type})")
            
            # 开始数据库事务
            try:
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
                
                # 更新或创建对话记录（如果对话模型可用）
                if ChatConversationModel:
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
                
                # 提交事务
                self.db.session.commit()
                logger.info(f"消息保存成功: ID={chat_message.id}, 对话={conversation_id}")
                
            except Exception as db_error:
                # 回滚事务
                self.db.session.rollback()
                logger.error(f"数据库操作失败: {str(db_error)}")
                # 尝试使用内存存储作为备用
                logger.info("尝试使用内存存储作为备用")
                return self._save_to_memory(message_data)
            
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
    
    def get_caregiver_messages(self, caregiver_id: int, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        获取护工的消息列表
        
        Args:
            caregiver_id: 护工ID
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            消息列表和统计信息
        """
        try:
            if not self.db:
                logger.warning("数据库未设置，使用内存存储")
                return {
                    "success": True,
                    "data": [],
                    "total": 0,
                    "message": "数据库未设置"
                }
            
            # 导入聊天记录模型
            from models.chat import ChatMessage, ChatConversation
            ChatMessageModel = ChatMessage.get_model(self.db)
            ChatConversationModel = ChatConversation.get_model(self.db)
            
            # 获取护工的消息
            messages = ChatMessageModel.query.filter(
                ChatMessageModel.recipient_id == caregiver_id
            ).order_by(ChatMessageModel.timestamp.desc()).offset(offset).limit(limit).all()
            
            # 获取总数
            total = ChatMessageModel.query.filter(
                ChatMessageModel.recipient_id == caregiver_id
            ).count()
            
            # 转换为前端需要的格式
            result = []
            for msg in messages:
                result.append({
                    'id': msg.id,
                    'contactId': f'user_{msg.sender_id}',
                    'type': 'user',
                    'sender': f'用户{msg.sender_id}',
                    'avatar': f'/uploads/avatars/default-user.png',
                    'content': msg.content,
                    'time': msg.timestamp.strftime('%H:%M') if msg.timestamp else '00:00',
                    'unread': not msg.is_read
                })
            
            return {
                "success": True,
                "data": result,
                "total": total,
                "message": "获取成功"
            }
            
        except Exception as e:
            logger.error(f"获取护工消息失败: {str(e)}")
            return {
                "success": False,
                "data": [],
                "total": 0,
                "message": f"获取失败: {str(e)}"
            }
    
    def get_conversations(self, user_id: int, user_type: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取对话列表
        
        Args:
            user_id: 用户ID
            user_type: 用户类型
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            对话列表
        """
        try:
            if not self.db:
                logger.warning("数据库未设置，返回空列表")
                return []
            
            ChatMessageModel = self.get_model()
            if not ChatMessageModel:
                logger.error("无法获取消息模型")
                return []
            
            # 查询用户相关的对话
            if user_type == 'user':
                # 用户查询与护工的对话
                conversations = ChatMessageModel.query.filter(
                    ChatMessageModel.sender_id == user_id,
                    ChatMessageModel.sender_type == 'user'
                ).union(
                    ChatMessageModel.query.filter(
                        ChatMessageModel.recipient_id == user_id,
                        ChatMessageModel.recipient_type == 'user'
                    )
                ).order_by(ChatMessageModel.timestamp.desc()).all()
            else:
                # 护工查询与用户的对话
                conversations = ChatMessageModel.query.filter(
                    ChatMessageModel.sender_id == user_id,
                    ChatMessageModel.sender_type == 'caregiver'
                ).union(
                    ChatMessageModel.query.filter(
                        ChatMessageModel.recipient_id == user_id,
                        ChatMessageModel.recipient_type == 'caregiver'
                    )
                ).order_by(ChatMessageModel.timestamp.desc()).all()
            
            # 按对话分组
            conversation_map = {}
            for msg in conversations:
                # 确定对话的另一方
                if user_type == 'user':
                    if msg.sender_id == user_id:
                        # 用户发送的消息，对方是护工
                        other_id = msg.recipient_id
                        other_type = msg.recipient_type
                        other_name = msg.recipient_name
                    else:
                        # 护工发送的消息，对方是护工
                        other_id = msg.sender_id
                        other_type = msg.sender_type
                        other_name = msg.sender_name
                else:
                    if msg.sender_id == user_id:
                        # 护工发送的消息，对方是用户
                        other_id = msg.recipient_id
                        other_type = msg.recipient_type
                        other_name = msg.recipient_name
                    else:
                        # 用户发送的消息，对方是用户
                        other_id = msg.sender_id
                        other_type = msg.sender_type
                        other_name = msg.sender_name
                
                conversation_key = f"{other_type}_{other_id}"
                
                if conversation_key not in conversation_map:
                    conversation_map[conversation_key] = {
                        'contactId': conversation_key,
                        'type': other_type,
                        'name': other_name or f'{other_type.title()}{other_id}',
                        'avatar': f'/uploads/avatars/default-{other_type}.png',
                        'content': msg.content,
                        'time': msg.timestamp.strftime('%H:%M') if msg.timestamp else '00:00',
                        'unread': not msg.is_read if msg.recipient_id == user_id else False,
                        'lastMessage': msg
                    }
                else:
                    # 更新最新消息
                    if msg.timestamp > conversation_map[conversation_key]['lastMessage'].timestamp:
                        conversation_map[conversation_key].update({
                            'content': msg.content,
                            'time': msg.timestamp.strftime('%H:%M') if msg.timestamp else '00:00',
                            'unread': not msg.is_read if msg.recipient_id == user_id else conversation_map[conversation_key]['unread'],
                            'lastMessage': msg
                        })
            
            # 转换为列表并排序
            result = list(conversation_map.values())
            result.sort(key=lambda x: x['lastMessage'].timestamp, reverse=True)
            
            # 应用分页
            result = result[offset:offset + limit]
            
            logger.info(f"获取对话列表: {user_type}_{user_id}, 数量: {len(result)}")
            return result
            
        except Exception as e:
            logger.error(f"获取对话列表失败: {str(e)}")
            return []

# 创建全局消息服务实例
message_service = MessageService()
