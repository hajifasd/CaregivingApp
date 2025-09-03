"""
护工资源管理系统 - 通知管理API
====================================

提供通知的查询、标记已读等API接口
"""

from flask import Blueprint, request, jsonify
from services.notification_service import notification_service

# 创建蓝图
notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/api/notifications', methods=['GET'])
def get_notifications():
    """获取用户通知列表"""
    try:
        # 获取查询参数
        user_id = request.args.get('user_id', type=int)
        user_type = request.args.get('user_type')
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        if not user_id or not user_type:
            return jsonify({
                'success': False,
                'message': '缺少必需参数: user_id, user_type'
            }), 400
        
        # 获取通知列表
        result = notification_service.get_user_notifications(user_id, user_type, limit, offset)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取通知失败: {str(e)}'
        }), 500

@notification_bp.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
def mark_notification_read():
    """标记通知为已读"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        user_type = data.get('user_type')
        
        if not user_id or not user_type:
            return jsonify({
                'success': False,
                'message': '缺少必需参数: user_id, user_type'
            }), 400
        
        notification_id = request.view_args.get('notification_id')
        
        # 标记通知为已读
        result = notification_service.mark_as_read(notification_id, user_id, user_type)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'操作失败: {str(e)}'
        }), 500

@notification_bp.route('/api/notifications/read-all', methods=['POST'])
def mark_all_notifications_read():
    """标记所有通知为已读"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        user_type = data.get('user_type')
        
        if not user_id or not user_type:
            return jsonify({
                'success': False,
                'message': '缺少必需参数: user_id, user_type'
            }), 400
        
        # 标记所有通知为已读
        result = notification_service.mark_all_as_read(user_id, user_type)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'操作失败: {str(e)}'
        }), 500

@notification_bp.route('/api/notifications/unread-count', methods=['GET'])
def get_unread_count():
    """获取未读通知数量"""
    try:
        user_id = request.args.get('user_id', type=int)
        user_type = request.args.get('user_type')
        
        if not user_id or not user_type:
            return jsonify({
                'success': False,
                'message': '缺少必需参数: user_id, user_type'
            }), 400
        
        unread_count = notification_service.get_unread_count(user_id, user_type)
        
        return jsonify({
            'success': True,
            'data': {
                'unread_count': unread_count
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取未读数量失败: {str(e)}'
        }), 500
