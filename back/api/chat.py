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
    
    # 注册事件处理器
    @socketio.on('connect')
    def handle_connect():
        """处理客户端连接"""
        logger.info(f"客户端连接: {request.sid}")
        emit('connected', {'message': '连接成功'})

    @socketio.on('disconnect')
    def handle_disconnect():
        """处理客户端断开连接"""
        logger.info(f"客户端断开连接: {request.sid}")

    @socketio.on('join')
    def handle_join(data):
        """处理用户加入房间"""
        try:
            user_id = data.get('user_id')
            user_type = data.get('user_type')  # 'user' 或 'caregiver'
            
            if not user_id or not user_type:
                emit('error', {'message': '缺少用户ID或类型'})
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
            logger.info(f"收到消息: {data}")
            
            # 支持两种字段格式（前端可能使用不同的命名）
            sender_id = data.get('sender_id') or data.get('senderId')
            recipient_id = data.get('recipient_id') or data.get('receiverId')
            content = data.get('content')
            sender_type = data.get('sender_type') or data.get('senderType', 'user')
            recipient_type = data.get('recipient_type') or data.get('receiverType', 'caregiver')
            sender_name = data.get('sender_name') or data.get('senderName', '用户')
            
            # 验证必要字段
            if not sender_id or not recipient_id or not content:
                emit('error', {'message': '缺少必要字段: sender_id, recipient_id, content'})
                return
            
            # 标准化消息数据
            normalized_data = {
                'sender_id': sender_id,
                'sender_name': sender_name,
                'sender_type': sender_type,
                'recipient_id': recipient_id,
                'recipient_type': recipient_type,
                'content': content,
                'type': data.get('type', 'text'),
                'timestamp': data.get('timestamp')
            }
            
            # 保存消息到消息服务
            from services.message_service import message_service
            saved_message = message_service.save_message(normalized_data)
            
            if saved_message:
                # 发送给接收者房间
                recipient_room = f"{recipient_type}_{recipient_id}"
                emit('message_received', saved_message, room=recipient_room)
                
                # 发送给发送者房间（确认消息已发送）
                sender_room = f"{sender_type}_{sender_id}"
                emit('message_sent', saved_message, room=sender_room)
                
                logger.info(f"消息发送成功: {sender_id} -> {recipient_id}, 房间: {recipient_room}")
            else:
                emit('error', {'message': '消息保存失败'})
            
        except Exception as e:
            logger.error(f"处理消息失败: {str(e)}")
            emit('error', {'message': '消息处理失败'})

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
