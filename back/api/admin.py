"""
护工资源管理系统 - 管理员API
====================================

管理员相关接口，包括护工审核、用户管理等
"""

from flask import Blueprint, request, jsonify
from extensions import db
import os
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/admin/approve', methods=['POST'])
def approve_caregiver():
    """批准护工接口"""
    # 获取模型
    from models.caregiver import Caregiver
    CaregiverModel = Caregiver.get_model(db)
    
    data = request.json
    caregiver_id = data.get('id')
    
    if not caregiver_id:
        return jsonify({'success': False, 'message': '缺少护工ID'}), 400
    
    try:
        caregiver = CaregiverModel.query.get(caregiver_id)
        if not caregiver:
            return jsonify({'success': False, 'message': '护工不存在'}), 404
        
        if caregiver.is_approved:
            return jsonify({'success': False, 'message': '护工已被批准'}), 400
        
        # 批准护工
        from datetime import datetime, timezone
        caregiver.is_approved = True
        caregiver.approved_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '护工批准成功'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"批准护工失败: {e}")
        return jsonify({'success': False, 'message': f'操作失败：{str(e)}'}), 500

@admin_bp.route('/api/admin/reject', methods=['POST'])
def reject_caregiver():
    """拒绝护工接口"""
    # 获取模型
    from models.caregiver import Caregiver
    CaregiverModel = Caregiver.get_model(db)
    
    data = request.json
    caregiver_id = data.get('id')
    
    if not caregiver_id:
        return jsonify({'success': False, 'message': '缺少护工ID'}), 400
    
    try:
        caregiver = CaregiverModel.query.get(caregiver_id)
        if not caregiver:
            return jsonify({'success': False, 'message': '护工不存在'}), 404
        
        if caregiver.is_approved:
            return jsonify({'success': False, 'message': '护工已被批准，无法拒绝'}), 400
        
        # 删除护工文件
        from flask import current_app
        upload_folder = current_app.config['UPLOAD_FOLDER']
        
        for file_attr in ['id_file', 'cert_file']:
            filename = getattr(caregiver, file_attr, None)
            if filename and filename.strip():
                file_path = os.path.join(upload_folder, filename)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        logger.warning(f"删除护工文件 {filename} 失败: {e}")
        
        # 删除护工记录
        db.session.delete(caregiver)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '护工拒绝成功'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"拒绝护工失败: {e}")
        return jsonify({'success': False, 'message': f'操作失败：{str(e)}'}), 500

@admin_bp.route('/api/admin/approve-user', methods=['POST'])
def approve_user():
    """批准用户接口"""
    # 获取模型
    from models.user import User
    UserModel = User.get_model(db)
    
    data = request.json
    user_id = data.get('id')
    
    if not user_id:
        return jsonify({'success': False, 'message': '缺少用户ID'}), 400
    
    try:
        user = UserModel.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        if user.is_approved:
            return jsonify({'success': False, 'message': '用户已被批准'}), 400
        
        # 批准用户
        from datetime import datetime, timezone
        user.is_approved = True
        user.approved_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '用户批准成功'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"批准用户失败: {e}")
        return jsonify({'success': False, 'message': f'操作失败：{str(e)}'}), 500

@admin_bp.route('/api/admin/delete-user', methods=['POST'])
def delete_user():
    """删除用户接口"""
    # 获取模型
    from models.user import User
    UserModel = User.get_model(db)
    
    data = request.json
    user_id = data.get('id')
    
    if not user_id:
        return jsonify({'success': False, 'message': '缺少用户ID'}), 400
    
    try:
        user = UserModel.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 删除用户文件
        from flask import current_app
        upload_folder = current_app.config['UPLOAD_FOLDER']
        
        if user.id_file and user.id_file.strip():
            file_path = os.path.join(upload_folder, user.id_file)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.warning(f"删除用户文件 {user.id_file} 失败: {e}")
        
        # 删除用户记录
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '用户删除成功'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除用户失败: {e}")
        return jsonify({'success': False, 'message': f'操作失败：{str(e)}'}), 500
