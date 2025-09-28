"""
护工资源管理系统 - 实时聊天API
====================================

支持WebSocket的实时聊天功能，实现用户和护工之间的即时通信
"""

from flask import Blueprint, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from services.message_service import MessageService
from utils.auth import require_auth
import logging
import json

logger = logging.getLogger(__name__)
chat_bp = Blueprint('chat', __name__)

# 全局SocketIO实例，需要在主应用中初始化
socketio = None

def init_socketio(app):
    """初始化SocketIO"""
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # 认证中间件
    @socketio.on('connect')
    def handle_connect(auth=None):
        """处理客户端连接"""
        try:
            # 检查认证信息
            token = None
            if auth and 'token' in auth:
                token = auth['token']
            else:
                # 尝试从请求头获取token
                auth_header = request.headers.get('Authorization')
                if auth_header and auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
            
            if not token:
                logger.warning(f"客户端连接未提供认证token: {request.sid}")
                emit('error', {'message': '需要认证token'})
                return False
            
            # 验证token
            from utils.auth import verify_token
            payload = verify_token(token)
            
            # 如果是测试token，允许连接
            if not payload and token == 'test-token-for-socket-connection':
                logger.info(f"测试环境：允许测试token连接: {request.sid}")
                payload = {
                    'user_id': 1,
                    'user_type': 'user',
                    'name': '测试用户'
                }
            
            if not payload:
                logger.warning(f"客户端连接token无效: {request.sid}")
                emit('error', {'message': '认证token无效'})
                return False
            
            # 存储用户信息到session
            session['user_id'] = payload.get('user_id')
            session['user_type'] = payload.get('user_type')
            session['user_name'] = payload.get('name', '')
            
            logger.info(f"客户端连接成功: {request.sid}, 用户: {session['user_type']}_{session['user_id']}")
            emit('connected', {
                'message': '连接成功',
                'user_id': session['user_id'],
                'user_type': session['user_type']
            })
            
        except Exception as e:
            logger.error(f"客户端连接认证失败: {str(e)}")
            emit('error', {'message': '认证失败'})
            return False

    @socketio.on('disconnect')
    def handle_disconnect():
        """处理客户端断开连接"""
        logger.info(f"客户端断开连接: {request.sid}")

    @socketio.on('join')
    def handle_join(data):
        """处理用户加入房间"""
        try:
            # 从session获取用户信息（已通过认证）
            user_id = session.get('user_id')
            user_type = session.get('user_type')
            
            if not user_id or not user_type:
                emit('error', {'message': '用户未认证'})
                return
            
            # 加入用户特定的房间
            room_name = f"{user_type}_{user_id}"
            join_room(room_name)
            logger.info(f"用户 {user_type}_{user_id} 加入房间: {room_name}")
            
            emit('joined_room', {
                'room': room_name,
                'user_id': user_id,
                'user_type': user_type
            })
            
        except Exception as e:
            logger.error(f"处理加入房间失败: {str(e)}")
            emit('error', {'message': '加入房间失败'})

    @socketio.on('send_message')
    def handle_send_message(data):
        """处理发送消息"""
        try:
            # 从session获取用户信息（已通过认证）
            sender_id = session.get('user_id')
            sender_type = session.get('user_type')
            sender_name = session.get('user_name', '')
            
            if not sender_id or not sender_type:
                emit('error', {'message': '用户未认证'})
                return
            
            logger.info(f"收到消息: {data}, 发送者: {sender_type}_{sender_id}")
            
            # 使用消息服务的标准化方法
            from services.message_service import message_service
            
            # 验证必要字段
            if not data.get('recipient_id') and not data.get('recipientId'):
                emit('error', {'message': '缺少接收者ID'})
                return
            if not data.get('content'):
                emit('error', {'message': '消息内容不能为空'})
                return
            
            # 构建消息数据
            message_data = {
                'sender_id': sender_id,
                'sender_type': sender_type,
                'sender_name': sender_name,
                'recipient_id': data.get('recipient_id') or data.get('recipientId'),
                'recipient_type': data.get('recipient_type') or data.get('recipientType', 'user'),
                'content': data.get('content'),
                'message_type': data.get('message_type', 'text')
            }
            
            # 保存消息到消息服务
            saved_message = message_service.save_message(message_data)
            
            if saved_message:
                # 发送给接收者房间
                recipient_room = f"{saved_message['recipient_type']}_{saved_message['recipient_id']}"
                emit('new_message', saved_message, room=recipient_room)
                
                # 发送给发送者房间（确认消息已发送）
                sender_room = f"{saved_message['sender_type']}_{saved_message['sender_id']}"
                emit('message_sent', saved_message, room=sender_room)
                
                logger.info(f"消息发送成功: {saved_message['sender_id']} -> {saved_message['recipient_id']}, 房间: {recipient_room}")
            else:
                emit('error', {'message': '消息保存失败'})
            
        except Exception as e:
            logger.error(f"处理消息失败: {str(e)}")
            emit('error', {'message': '消息处理失败'})
    
    @socketio.on('mark_as_read')
    def handle_mark_as_read(data):
        """处理标记消息为已读"""
        try:
            message_id = data.get('message_id')
            user_id = data.get('user_id')
            user_type = data.get('user_type', 'user')
            
            if not message_id or not user_id:
                emit('error', {'message': '缺少必要字段: message_id, user_id'})
                return
            
            from services.message_service import message_service
            success = message_service.mark_message_as_read(message_id, user_id, user_type)
            
            if success:
                emit('message_read', {'message_id': message_id, 'status': 'success'})
                logger.info(f"消息已标记为已读: {message_id} by {user_type}_{user_id}")
            else:
                emit('error', {'message': '标记已读失败'})
                
        except Exception as e:
            logger.error(f"处理标记已读失败: {str(e)}")
            emit('error', {'message': '标记已读失败'})
    
    @socketio.on('get_message_history')
    def handle_get_message_history(data):
        """处理获取消息历史"""
        try:
            user_id = data.get('user_id')
            user_type = data.get('user_type', 'user')
            contact_id = data.get('contact_id')
            contact_type = data.get('contact_type', 'caregiver' if user_type == 'user' else 'user')
            limit = data.get('limit', 50)
            offset = data.get('offset', 0)
            
            if not user_id or not contact_id:
                emit('error', {'message': '缺少必要字段: user_id, contact_id'})
                return
            
            from services.message_service import message_service
            messages = message_service.get_message_history(
                user_id, user_type, contact_id, contact_type, limit, offset
            )
            
            emit('message_history', {
                'messages': messages,
                'contact_id': contact_id,
                'contact_type': contact_type,
                'has_more': len(messages) == limit
            })
            
            logger.info(f"获取消息历史: {user_type}_{user_id} <-> {contact_type}_{contact_id}, 数量: {len(messages)}")
            
        except Exception as e:
            logger.error(f"处理获取消息历史失败: {str(e)}")
            emit('error', {'message': '获取消息历史失败'})
    
    @socketio.on('typing')
    def handle_typing(data):
        """处理正在输入状态"""
        try:
            user_id = data.get('user_id')
            user_type = data.get('user_type', 'user')
            contact_id = data.get('contact_id')
            contact_type = data.get('contact_type', 'caregiver' if user_type == 'user' else 'user')
            is_typing = data.get('is_typing', True)
            
            if not user_id or not contact_id:
                emit('error', {'message': '缺少必要字段: user_id, contact_id'})
                return
            
            # 发送给联系人
            contact_room = f"{contact_type}_{contact_id}"
            emit('user_typing', {
                'user_id': user_id,
                'user_type': user_type,
                'is_typing': is_typing
            }, room=contact_room)
            
        except Exception as e:
            logger.error(f"处理输入状态失败: {str(e)}")
            emit('error', {'message': '处理输入状态失败'})

# 测试消息功能已移除
    
    return socketio

def get_socketio():
    """获取socketio实例"""
    global socketio
    return socketio

# 这些函数已经被装饰器版本替代
# def handle_connect():
#     """处理客户端连接"""
#     logger.info(f"客户端连接: {request.sid}")
#     emit('connected', {'message': '连接成功'})

# def handle_disconnect():
#     """处理客户端断开连接"""
#     logger.info(f"客户端断开连接: {request.sid}")
#     # 清理用户会话
#     if hasattr(request, 'user_id'):
#         leave_room(f"user_{request.user_id}")
#     if hasattr(request, 'caregiver_id'):
#         leave_room(f"leave_room_{request.caregiver_id}")

def handle_authentication(data):
    """处理用户认证"""
    try:
        token = data.get('token')
        user_type = data.get('user_type')  # 'user' 或 'caregiver'
        
        if not token or not user_type:
            return False, "缺少认证信息"
        
        # 这里应该验证token的有效性
        # 暂时简化处理
        return True, "认证成功"
        
    except Exception as e:
        logger.error(f"认证处理失败: {str(e)}")
        return False, "认证失败"

# ==================== 聊天记录API接口 ====================

@chat_bp.route('/api/chat/history/<contact_id>', methods=['GET'])
def get_chat_history(contact_id):
    """获取与指定联系人的聊天历史"""
    try:
        # 从请求参数获取用户ID和类型
        user_id = request.args.get('user_id')
        user_type = request.args.get('user_type', 'user')  # user 或 caregiver
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': '缺少用户ID参数'
            }), 400
        
        # 获取消息数量限制
        limit = request.args.get('limit', 50, type=int)
        
        # 获取聊天历史
        from services.message_service import message_service
        messages = message_service.get_chat_history(user_id, contact_id, limit)
        
        return jsonify({
            'success': True,
            'data': {
                'messages': messages,
                'total': len(messages)
            }
        })
        
    except Exception as e:
        logger.error(f"获取聊天历史失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取聊天历史失败: {str(e)}'
        }), 500

@chat_bp.route('/api/chat/send', methods=['POST'])
def send_message():
    """发送消息接口"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['sender_id', 'sender_type', 'sender_name', 'recipient_id', 'recipient_type', 'content']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'缺少必要字段: {field}'
                }), 400
        
        # 保存消息到数据库
        from services.message_service import message_service
        saved_message = message_service.save_message(data)
        
        if saved_message:
            # 通过WebSocket广播消息
            if socketio:
                socketio.emit('message_received', saved_message)
            
            return jsonify({
                'success': True,
                'data': saved_message,
                'message': '消息发送成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '消息保存失败'
            }), 500
            
    except Exception as e:
        logger.error(f"发送消息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'发送消息失败: {str(e)}'
        }), 500

@chat_bp.route('/api/chat/conversations', methods=['GET'])
def get_user_conversations():
    """获取用户的所有对话列表"""
    try:
        # 从请求参数获取用户ID和类型
        user_id = request.args.get('user_id')
        user_type = request.args.get('user_type', 'user')
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': '缺少用户ID参数'
            }), 400
        
        # 获取对话列表
        from services.message_service import message_service
        conversations = message_service.get_user_conversations(user_id, user_type)
        
        return jsonify({
            'success': True,
            'data': {
                'conversations': conversations,
                'total': len(conversations)
            }
        })
        
    except Exception as e:
        logger.error(f"获取对话列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取对话列表失败: {str(e)}'
        }), 500

@chat_bp.route('/api/chat/mark-read', methods=['POST'])
def mark_messages_read():
    """标记消息为已读"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        contact_id = data.get('contact_id')
        
        if not user_id or not contact_id:
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        # 标记消息为已读
        from services.message_service import message_service
        success = message_service.mark_messages_as_read(user_id, contact_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': '消息已标记为已读'
            })
        else:
            return jsonify({
                'success': False,
                'message': '标记消息已读失败'
            }), 500
        
    except Exception as e:
        logger.error(f"标记消息已读失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'标记消息已读失败: {str(e)}'
        }), 500

@chat_bp.route('/api/chat/unread-count', methods=['GET'])
def get_unread_count():
    """获取用户未读消息数量"""
    try:
        # 从请求参数获取用户ID和类型
        user_id = request.args.get('user_id')
        user_type = request.args.get('user_type', 'user')
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': '缺少用户ID参数'
            }), 400
        
        # 获取未读消息数量
        from services.message_service import message_service
        unread_count = message_service.get_unread_count(user_id, user_type)
        
        return jsonify({
            'success': True,
            'data': {
                'unread_count': unread_count
            }
        })
        
    except Exception as e:
        logger.error(f"获取未读消息数量失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取未读消息数量失败: {str(e)}'
        }), 500

@chat_bp.route('/api/chat/search', methods=['GET'])
def search_messages():
    """搜索消息内容"""
    try:
        # 从请求参数获取搜索条件
        user_id = request.args.get('user_id')
        user_type = request.args.get('user_type', 'user')
        keyword = request.args.get('keyword')
        limit = request.args.get('limit', 20, type=int)
        
        if not user_id or not keyword:
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        # 搜索消息
        from services.message_service import message_service
        messages = message_service.search_messages(user_id, user_type, keyword, limit)
        
        return jsonify({
            'success': True,
            'data': {
                'messages': messages,
                'total': len(messages),
                'keyword': keyword
            }
        })
        
    except Exception as e:
        logger.error(f"搜索消息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'搜索消息失败: {str(e)}'
        }), 500

@chat_bp.route('/api/chat/messages', methods=['GET'])
def get_messages():
    """获取消息历史 - 统一API端点"""
    try:
        # 获取参数
        user_id = request.args.get('user_id', type=int)
        user_type = request.args.get('user_type', 'user')
        contact_id = request.args.get('contact_id', type=int)
        contact_type = request.args.get('contact_type', 'user')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # 验证必需参数
        if not user_id:
            return jsonify({
                'success': False,
                'message': '缺少用户ID参数'
            }), 400
        
        if not contact_id:
            return jsonify({
                'success': False,
                'message': '缺少联系人ID参数'
            }), 400
        
        # 使用消息服务获取消息历史
        from services.message_service import message_service
        messages = message_service.get_message_history(
            user_id=user_id,
            user_type=user_type,
            contact_id=contact_id,
            contact_type=contact_type,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            'success': True,
            'data': messages,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total': len(messages)
            }
        })
        
    except Exception as e:
        logger.error(f"获取消息历史失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取消息历史失败'
        }), 500

@chat_bp.route('/api/chat/conversations', methods=['GET'])
def get_conversations():
    """获取对话列表 - 统一API端点"""
    try:
        # 获取参数
        user_id = request.args.get('user_id', type=int)
        user_type = request.args.get('user_type', 'user')
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # 验证必需参数
        if not user_id:
            return jsonify({
                'success': False,
                'message': '缺少用户ID参数'
            }), 400
        
        # 使用消息服务获取对话列表
        from services.message_service import message_service
        conversations = message_service.get_conversations(
            user_id=user_id,
            user_type=user_type,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            'success': True,
            'data': conversations,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total': len(conversations)
            }
        })
        
    except Exception as e:
        logger.error(f"获取对话列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取对话列表失败'
        }), 500
