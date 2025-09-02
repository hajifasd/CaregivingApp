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

@admin_bp.route('/api/admin/get-all-users', methods=['GET'])
def get_all_users():
    """获取所有用户账号信息接口"""
    try:
        # 获取模型
        from models.user import User
        UserModel = User.get_model(db)
        
        # 查询所有用户
        users = UserModel.query.all()
        
        # 转换为字典格式
        user_list = []
        for user in users:
            user_info = {
                "id": user.id,
                "email": user.email,
                "phone": user.phone,
                "name": user.name or "未设置",
                "created_at": user.created_at.strftime("%Y-%m-%d") if user.created_at else "N/A",
                "last_login": "N/A",  # 暂时设为N/A，后续可以添加last_login字段
                "status": "正常" if user.is_approved else "待审核",
                "is_approved": user.is_approved,
                "is_verified": user.is_verified
            }
            user_list.append(user_info)
        
        return jsonify({
            'success': True,
            'data': user_list
        })
    except Exception as e:
        logger.error(f"获取用户列表失败: {e}")
        return jsonify({'success': False, 'message': f'获取用户列表失败：{str(e)}'}), 500

@admin_bp.route('/api/admin/reset-password', methods=['POST'])
def reset_user_password():
    """重置用户密码接口"""
    try:
        data = request.json
        user_id = data.get('id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '缺少用户ID'}), 400
        
        # 获取模型
        from models.user import User
        UserModel = User.get_model(db)
        
        user = UserModel.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 生成新密码（8位随机密码）
        import random
        import string
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        # 设置新密码
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'密码重置成功，新密码：{new_password}',
            'new_password': new_password
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"重置密码失败: {e}")
        return jsonify({'success': False, 'message': f'重置密码失败：{str(e)}'}), 500

@admin_bp.route('/api/admin/delete-account', methods=['POST'])
def delete_user_account():
    """删除用户账号接口"""
    try:
        data = request.json
        user_id = data.get('id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '缺少用户ID'}), 400
        
        # 获取模型
        from models.user import User
        UserModel = User.get_model(db)
        
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
            'message': '账号删除成功'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除账号失败: {e}")
        return jsonify({'success': False, 'message': f'删除账号失败：{str(e)}'}), 500

@admin_bp.route('/api/admin/activate-account', methods=['POST'])
def activate_user_account():
    """激活用户账号接口"""
    try:
        data = request.json
        user_id = data.get('id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '缺少用户ID'}), 400
        
        # 获取模型
        from models.user import User
        UserModel = User.get_model(db)
        
        user = UserModel.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 激活账号
        user.is_approved = True
        if not user.approved_at:
            from datetime import datetime, timezone
            user.approved_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '账号激活成功'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"激活账号失败: {e}")
        return jsonify({'success': False, 'message': f'激活账号失败：{str(e)}'}), 500

@admin_bp.route('/api/admin/get-all-caregivers', methods=['GET'])
def get_all_caregivers():
    """获取所有护工账号信息接口"""
    try:
        # 获取模型
        from models.caregiver import Caregiver
        CaregiverModel = Caregiver.get_model(db)
        
        # 查询所有护工
        caregivers = CaregiverModel.query.all()
        
        # 转换为字典格式
        caregiver_list = []
        for caregiver in caregivers:
            caregiver_info = {
                "id": caregiver.id,
                "email": caregiver.email,
                "phone": caregiver.phone,
                "name": caregiver.name or "未设置",
                "created_at": caregiver.created_at.strftime("%Y-%m-%d") if caregiver.created_at else "N/A",
                "last_login": "N/A",  # 暂时设为N/A，后续可以添加last_login字段
                "status": "正常" if caregiver.is_approved else "待审核",
                "is_approved": caregiver.is_approved,
                "gender": caregiver.gender,
                "age": caregiver.age,
                "experience_years": caregiver.experience_years,
                "hourly_rate": caregiver.hourly_rate
            }
            caregiver_list.append(caregiver_info)
        
        return jsonify({
            'success': True,
            'data': caregiver_list
        })
    except Exception as e:
        logger.error(f"获取护工列表失败: {e}")
        return jsonify({'success': False, 'message': f'获取护工列表失败：{str(e)}'}), 500

@admin_bp.route('/api/admin/reset-caregiver-password', methods=['POST'])
def reset_caregiver_password():
    """重置护工密码接口"""
    try:
        data = request.json
        caregiver_id = data.get('id')
        
        if not caregiver_id:
            return jsonify({'success': False, 'message': '缺少护工ID'}), 400
        
        # 获取模型
        from models.caregiver import Caregiver
        CaregiverModel = Caregiver.get_model(db)
        
        caregiver = CaregiverModel.query.get(caregiver_id)
        if not caregiver:
            return jsonify({'success': False, 'message': '护工不存在'}), 404
        
        # 生成新密码（8位随机密码）
        import random
        import string
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        # 设置新密码
        caregiver.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'密码重置成功，新密码：{new_password}',
            'new_password': new_password
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"重置护工密码失败: {e}")
        return jsonify({'success': False, 'message': f'重置护工密码失败：{str(e)}'}), 500

@admin_bp.route('/api/admin/delete-caregiver-account', methods=['POST'])
def delete_caregiver_account():
    """删除护工账号接口"""
    try:
        data = request.json
        caregiver_id = data.get('id')
        
        if not caregiver_id:
            return jsonify({'success': False, 'message': '缺少护工ID'}), 400
        
        # 获取模型
        from models.caregiver import Caregiver
        CaregiverModel = Caregiver.get_model(db)
        
        caregiver = CaregiverModel.query.get(caregiver_id)
        if not caregiver:
            return jsonify({'success': False, 'message': '护工不存在'}), 404
        
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
            'message': '护工账号删除成功'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除护工账号失败: {e}")
        return jsonify({'success': False, 'message': f'删除护工账号失败：{str(e)}'}), 500

@admin_bp.route('/api/admin/activate-caregiver-account', methods=['POST'])
def activate_caregiver_account():
    """激活护工账号接口"""
    try:
        data = request.json
        caregiver_id = data.get('id')
        
        if not caregiver_id:
            return jsonify({'success': False, 'message': '缺少护工ID'}), 400
        
        # 获取模型
        from models.caregiver import Caregiver
        CaregiverModel = Caregiver.get_model(db)
        
        caregiver = CaregiverModel.query.get(caregiver_id)
        if not caregiver:
            return jsonify({'success': False, 'message': '护工不存在'}), 404
        
        # 激活账号
        caregiver.is_approved = True
        if not caregiver.approved_at:
            from datetime import datetime, timezone
            caregiver.approved_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '护工账号激活成功'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"激活护工账号失败: {e}")
        return jsonify({'success': False, 'message': f'激活护工账号失败：{str(e)}'}), 500
