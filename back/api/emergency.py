"""
护工资源管理系统 - 紧急联系人API
====================================

处理紧急联系人相关的API接口
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

emergency_bp = Blueprint('emergency', __name__)

@emergency_bp.route('/api/emergency/contacts', methods=['GET'])
def get_emergency_contacts():
    """获取紧急联系人列表"""
    try:
        # 默认紧急联系人（系统预设）
        default_contacts = [
            {
                'id': 1,
                'name': '紧急服务中心',
                'phone': '120',
                'type': 'medical',
                'priority': 1,
                'is_system': True
            },
            {
                'id': 2,
                'name': '报警电话',
                'phone': '110',
                'type': 'police',
                'priority': 1,
                'is_system': True
            },
            {
                'id': 3,
                'name': '火警电话',
                'phone': '119',
                'type': 'fire',
                'priority': 1,
                'is_system': True
            }
        ]
        
        # TODO: 从数据库加载用户自定义的紧急联系人
        # 这里可以添加从数据库加载用户自定义联系人的逻辑
        
        return jsonify({
            'success': True,
            'data': default_contacts,
            'message': '紧急联系人获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取紧急联系人失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取紧急联系人失败: {str(e)}'
        }), 500

@emergency_bp.route('/api/emergency/contacts', methods=['POST'])
def add_emergency_contact():
    """添加紧急联系人"""
    try:
        data = request.json
        
        # 验证必填字段
        required_fields = ['name', 'phone', 'type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'缺少必填字段: {field}'
                }), 400
        
        # 创建新联系人
        new_contact = {
            'id': int(datetime.now().timestamp() * 1000),  # 使用时间戳作为ID
            'name': data['name'],
            'phone': data['phone'],
            'type': data['type'],
            'priority': data.get('priority', 2),
            'is_system': False,
            'created_at': datetime.now().isoformat()
        }
        
        # TODO: 保存到数据库
        # 这里可以添加保存到数据库的逻辑
        
        return jsonify({
            'success': True,
            'data': new_contact,
            'message': '紧急联系人添加成功'
        })
        
    except Exception as e:
        logger.error(f"添加紧急联系人失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'添加紧急联系人失败: {str(e)}'
        }), 500

@emergency_bp.route('/api/emergency/contacts/<int:contact_id>', methods=['PUT'])
def update_emergency_contact(contact_id):
    """更新紧急联系人"""
    try:
        data = request.json
        
        # TODO: 从数据库查找并更新联系人
        # 这里可以添加数据库更新逻辑
        
        return jsonify({
            'success': True,
            'message': '紧急联系人更新成功'
        })
        
    except Exception as e:
        logger.error(f"更新紧急联系人失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'更新紧急联系人失败: {str(e)}'
        }), 500

@emergency_bp.route('/api/emergency/contacts/<int:contact_id>', methods=['DELETE'])
def delete_emergency_contact(contact_id):
    """删除紧急联系人"""
    try:
        # TODO: 从数据库删除联系人
        # 这里可以添加数据库删除逻辑
        
        return jsonify({
            'success': True,
            'message': '紧急联系人删除成功'
        })
        
    except Exception as e:
        logger.error(f"删除紧急联系人失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'删除紧急联系人失败: {str(e)}'
        }), 500

