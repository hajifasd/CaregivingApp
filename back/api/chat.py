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

    @socketio.on('send_message')
    def handle_send_message(data):
        """处理发送消息"""
        try:
            logger.info(f"收到消息: {data}")
            
            # 保存消息到消息服务
            from services.message_service import message_service
            saved_message = message_service.save_message(data)
            
            if saved_message:
                # 广播消息给所有连接的客户端
                emit('message_received', saved_message, broadcast=True)
                logger.info(f"消息保存并广播成功: ID={saved_message['id']}")
            else:
                emit('error', {'message': '消息保存失败'})
            
        except Exception as e:
            logger.error(f"处理消息失败: {str(e)}")
            emit('error', {'message': '消息处理失败'})

    @socketio.on('test_message')
    def handle_test_message(data):
        """处理测试消息"""
        try:
            logger.info(f"收到测试消息: {data}")
            from datetime import datetime
            emit('message_received', {
                'content': f'测试回复: {data.get("message", "测试消息")}',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"处理测试消息失败: {str(e)}")
            emit('error', {'message': '测试消息处理失败'})
    
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
        # 从请求参数获取用户ID
        user_id = request.args.get('user_id')
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

@chat_bp.route('/api/chat/conversations', methods=['GET'])
def get_user_conversations():
    """获取用户的所有对话列表"""
    try:
        # 从请求参数获取用户ID
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': '缺少用户ID参数'
            }), 400
        
        # 获取对话列表
        from services.message_service import message_service
        conversations = message_service.get_user_conversations(user_id)
        
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
        # 从请求参数获取用户ID
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': '缺少用户ID参数'
            }), 400
        
        # 获取未读消息数量
        from services.message_service import message_service
        unread_count = message_service.get_unread_count(user_id)
        
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
        keyword = request.args.get('keyword')
        limit = request.args.get('limit', 20, type=int)
        
        if not user_id or not keyword:
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        # 搜索消息（暂时返回空结果，后续可以扩展）
        # 这里可以实现基于数据库的全文搜索
        return jsonify({
            'success': True,
            'data': {
                'messages': [],
                'total': 0,
                'keyword': keyword
            }
        })
        
    except Exception as e:
        logger.error(f"搜索消息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'搜索消息失败: {str(e)}'
        }), 500
