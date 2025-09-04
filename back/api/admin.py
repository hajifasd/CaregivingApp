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
                "id": caregiver.id if caregiver.id is not None else 0,
                "phone": caregiver.phone if caregiver.phone is not None else "未设置",
                "name": caregiver.name if caregiver.name is not None else "未设置",
                "created_at": caregiver.created_at.strftime("%Y-%m-%d") if caregiver.created_at is not None else "未知",
                "approved_at": caregiver.approved_at.strftime("%Y-%m-%d") if caregiver.approved_at is not None else "N/A",
                "status": "正常" if caregiver.is_approved is not None and caregiver.is_approved else "待审核",
                "is_approved": bool(caregiver.is_approved) if caregiver.is_approved is not None else False,
                "gender": caregiver.gender if caregiver.gender is not None else "未设置",
                "age": caregiver.age if caregiver.age is not None else "未设置",
                "experience_years": caregiver.experience_years if caregiver.experience_years is not None else 0,
                "hourly_rate": caregiver.hourly_rate if caregiver.hourly_rate is not None else "未设置",
                "qualification": caregiver.qualification if caregiver.qualification is not None else "未设置",
                "rating": caregiver.rating if caregiver.rating is not None else 0,
                "review_count": caregiver.review_count if caregiver.review_count is not None else 0
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
        force_delete = data.get('force_delete', False)  # 是否强制删除
        
        if not caregiver_id:
            return jsonify({'success': False, 'message': '缺少护工ID'}), 400
        
        # 获取模型
        from models.caregiver import Caregiver
        CaregiverModel = Caregiver.get_model(db)
        
        caregiver = CaregiverModel.query.get(caregiver_id)
        if not caregiver:
            return jsonify({'success': False, 'message': '护工不存在'}), 404
        
        # 检查护工状态
        if caregiver.is_approved and not force_delete:
            return jsonify({
                'success': False, 
                'message': '该护工已通过审核，建议先暂停账号。如需强制删除，请设置force_delete=true'
            }), 400
        
        # 导入所需的模型（在函数开始就导入，避免作用域问题）
        from models.employment_contract import EmploymentContract, ContractApplication
        from models.business import Appointment
        from models.caregiver_hire_info import CaregiverHireInfo
        from models.chat import ChatConversation
        
        # 如果强制删除，跳过关联数据检查
        if not force_delete:
            # 检查是否有进行中的服务或合同
            try:
                # 检查就业合同
                EmploymentContractModel = EmploymentContract.get_model(db)
                active_contracts = EmploymentContractModel.query.filter_by(
                    caregiver_id=caregiver_id,
                    status='active'
                ).count()
                
                if active_contracts > 0:
                    return jsonify({
                        'success': False,
                        'message': f'该护工有{active_contracts}个进行中的服务合同，无法删除。请先完成或终止相关合同。'
                    }), 400
                
                # 检查预约
                AppointmentModel = Appointment.get_model(db)
                active_appointments = AppointmentModel.query.filter_by(
                    caregiver_id=caregiver_id,
                    status='confirmed'
                ).count()
                
                if active_appointments > 0:
                    return jsonify({
                        'success': False,
                        'message': f'该护工有{active_appointments}个已确认的预约，无法删除。请先取消相关预约。'
                    }), 400
                    
                # 检查护工雇佣信息
                CaregiverHireInfoModel = CaregiverHireInfo.get_model(db)
                hire_info_count = CaregiverHireInfoModel.query.filter_by(
                    caregiver_id=caregiver_id
                ).count()
                
                if hire_info_count > 0:
                    return jsonify({
                        'success': False,
                        'message': f'该护工有{hire_info_count}条雇佣信息记录，无法删除。请先清理相关数据。'
                    }), 400
                
                # 检查合同申请
                ContractApplicationModel = ContractApplication.get_model(db)
                contract_app_count = ContractApplicationModel.query.filter_by(
                    caregiver_id=caregiver_id
                ).count()
                
                if contract_app_count > 0:
                    return jsonify({
                        'success': False,
                        'message': f'该护工有{contract_app_count}条合同申请记录，无法删除。请先清理相关数据。'
                    }), 400
                
                # 检查聊天对话
                ChatConversationModel = ChatConversation.get_model(db)
                chat_count = ChatConversationModel.query.filter_by(
                    caregiver_id=caregiver_id
                ).count()
                
                if chat_count > 0:
                    return jsonify({
                        'success': False,
                        'message': f'该护工有{chat_count}条聊天对话记录，无法删除。请先清理相关数据。'
                    }), 400
                    
            except Exception as e:
                logger.warning(f"检查护工关联数据失败: {e}")
                # 如果检查失败，继续执行删除操作
        
        # 删除护工相关文件
        from flask import current_app
        upload_folder = current_app.config['UPLOAD_FOLDER']
        
        file_attributes = ['id_file', 'cert_file', 'avatar_url']
        deleted_files = []
        
        for file_attr in file_attributes:
            filename = getattr(caregiver, file_attr, None)
            if filename and filename.strip():
                file_path = os.path.join(upload_folder, filename)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        deleted_files.append(filename)
                        logger.info(f"成功删除护工文件: {filename}")
                    except Exception as e:
                        logger.warning(f"删除护工文件 {filename} 失败: {e}")
        
        # 如果是强制删除，先删除关联数据
        if force_delete:
            try:
                # 删除护工雇佣信息
                CaregiverHireInfoModel = CaregiverHireInfo.get_model(db)
                hire_info_records = CaregiverHireInfoModel.query.filter_by(
                    caregiver_id=caregiver_id
                ).all()
                
                for record in hire_info_records:
                    db.session.delete(record)
                
                logger.info(f"强制删除护工时，已删除{len(hire_info_records)}条雇佣信息记录")
                
                # 删除就业合同
                EmploymentContractModel = EmploymentContract.get_model(db)
                contract_records = EmploymentContractModel.query.filter_by(
                    caregiver_id=caregiver_id
                ).all()
                
                for record in contract_records:
                    db.session.delete(record)
                
                logger.info(f"强制删除护工时，已删除{len(contract_records)}条就业合同记录")
                
                # 删除预约记录
                AppointmentModel = Appointment.get_model(db)
                appointment_records = AppointmentModel.query.filter_by(
                    caregiver_id=caregiver_id
                ).all()
                
                for record in appointment_records:
                    db.session.delete(record)
                
                logger.info(f"强制删除护工时，已删除{len(appointment_records)}条预约记录")
                
                # 删除合同申请记录
                ContractApplicationModel = ContractApplication.get_model(db)
                contract_app_records = ContractApplicationModel.query.filter_by(
                    caregiver_id=caregiver_id
                ).all()
                
                for record in contract_app_records:
                    db.session.delete(record)
                
                logger.info(f"强制删除护工时，已删除{len(contract_app_records)}条合同申请记录")
                
                # 删除聊天对话记录
                ChatConversationModel = ChatConversation.get_model(db)
                chat_records = ChatConversationModel.query.filter_by(
                    caregiver_id=caregiver_id
                ).all()
                
                for record in chat_records:
                    db.session.delete(record)
                
                logger.info(f"强制删除护工时，已删除{len(chat_records)}条聊天对话记录")
                
            except Exception as e:
                logger.warning(f"强制删除护工时清理关联数据失败: {e}")
                # 继续执行删除操作
        
        # 记录删除操作
        logger.info(f"管理员删除护工账号: ID={caregiver_id}, 姓名={caregiver.name}, 手机={caregiver.phone}")
        
        # 删除护工记录
        db.session.delete(caregiver)
        db.session.commit()
        
        # 构建响应消息
        message = '护工账号删除成功'
        if deleted_files:
            message += f'，已删除{len(deleted_files)}个相关文件'
        
        return jsonify({
            'success': True,
            'message': message,
            'deleted_files': deleted_files,
            'caregiver_info': {
                'id': caregiver_id,
                'name': caregiver.name,
                'phone': caregiver.phone
            }
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

@admin_bp.route('/api/admin/suspend-caregiver-account', methods=['POST'])
def suspend_caregiver_account():
    """暂停护工账号接口"""
    try:
        data = request.json
        caregiver_id = data.get('id')
        reason = data.get('reason', '管理员暂停')
        
        if not caregiver_id:
            return jsonify({'success': False, 'message': '缺少护工ID'}), 400
        
        # 获取模型
        from models.caregiver import Caregiver
        CaregiverModel = Caregiver.get_model(db)
        
        caregiver = CaregiverModel.query.get(caregiver_id)
        if not caregiver:
            return jsonify({'success': False, 'message': '护工不存在'}), 404
        
        if not caregiver.is_approved:
            return jsonify({'success': False, 'message': '该护工尚未通过审核，无法暂停'}), 400
        
        # 暂停账号
        caregiver.available = False
        caregiver.status = 'suspended'
        
        # 记录暂停原因和时间
        from datetime import datetime, timezone
        caregiver.suspended_at = datetime.now(timezone.utc)
        caregiver.suspension_reason = reason
        
        db.session.commit()
        
        logger.info(f"管理员暂停护工账号: ID={caregiver_id}, 姓名={caregiver.name}, 原因={reason}")
        
        return jsonify({
            'success': True,
            'message': '护工账号暂停成功',
            'caregiver_info': {
                'id': caregiver_id,
                'name': caregiver.name,
                'phone': caregiver.phone,
                'status': 'suspended',
                'suspended_at': caregiver.suspended_at.strftime("%Y-%m-%d %H:%M"),
                'reason': reason
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"暂停护工账号失败: {e}")
        return jsonify({'success': False, 'message': f'暂停护工账号失败：{str(e)}'}), 500

@admin_bp.route('/api/admin/restore-caregiver-account', methods=['POST'])
def restore_caregiver_account():
    """恢复护工账号接口"""
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
        
        if caregiver.status != 'suspended':
            return jsonify({'success': False, 'message': '该护工账号未被暂停'}), 400
        
        # 恢复账号
        caregiver.available = True
        caregiver.status = 'active'
        caregiver.suspended_at = None
        caregiver.suspension_reason = None
        
        db.session.commit()
        
        logger.info(f"管理员恢复护工账号: ID={caregiver_id}, 姓名={caregiver.name}")
        
        return jsonify({
            'success': True,
            'message': '护工账号恢复成功',
            'caregiver_info': {
                'id': caregiver_id,
                'name': caregiver.name,
                'phone': caregiver.phone,
                'status': 'active'
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"恢复护工账号失败: {e}")
        return jsonify({'success': False, 'message': f'恢复护工账号失败：{str(e)}'}), 500

@admin_bp.route('/api/admin/batch-caregiver-operation', methods=['POST'])
def batch_caregiver_operation():
    """批量护工操作接口"""
    try:
        data = request.json
        caregiver_ids = data.get('caregiver_ids', [])
        operation = data.get('operation')  # 'suspend', 'restore', 'delete'
        reason = data.get('reason', '批量操作')
        
        if not caregiver_ids:
            return jsonify({'success': False, 'message': '缺少护工ID列表'}), 400
        
        if not operation:
            return jsonify({'success': False, 'message': '缺少操作类型'}), 400
        
        if operation not in ['suspend', 'restore', 'delete']:
            return jsonify({'success': False, 'message': '不支持的操作类型'}), 400
        
        # 获取模型
        from models.caregiver import Caregiver
        CaregiverModel = Caregiver.get_model(db)
        
        # 查询护工
        caregivers = CaregiverModel.query.filter(CaregiverModel.id.in_(caregiver_ids)).all()
        
        if not caregivers:
            return jsonify({'success': False, 'message': '未找到指定的护工'}), 404
        
        success_count = 0
        failed_count = 0
        failed_reasons = []
        
        for caregiver in caregivers:
            try:
                if operation == 'suspend':
                    if caregiver.is_approved:
                        caregiver.available = False
                        caregiver.status = 'suspended'
                        from datetime import datetime, timezone
                        caregiver.suspended_at = datetime.now(timezone.utc)
                        caregiver.suspension_reason = reason
                        success_count += 1
                    else:
                        failed_count += 1
                        failed_reasons.append(f"护工{caregiver.name}(ID:{caregiver.id})未通过审核，无法暂停")
                        
                elif operation == 'restore':
                    if caregiver.status == 'suspended':
                        caregiver.available = True
                        caregiver.status = 'active'
                        caregiver.suspended_at = None
                        caregiver.suspension_reason = None
                        success_count += 1
                    else:
                        failed_count += 1
                        failed_reasons.append(f"护工{caregiver.name}(ID:{caregiver.id})未被暂停，无法恢复")
                        
                elif operation == 'delete':
                    # 检查是否可以删除
                    if caregiver.is_approved:
                        failed_count += 1
                        failed_reasons.append(f"护工{caregiver.name}(ID:{caregiver.id})已通过审核，建议先暂停")
                        continue
                    
                    # 删除相关文件
                    from flask import current_app
                    upload_folder = current_app.config['UPLOAD_FOLDER']
                    
                    for file_attr in ['id_file', 'cert_file', 'avatar_url']:
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
                    success_count += 1
                    
            except Exception as e:
                failed_count += 1
                failed_reasons.append(f"护工{caregiver.name}(ID:{caregiver.id})操作失败: {str(e)}")
                logger.error(f"批量操作护工失败: ID={caregiver.id}, 操作={operation}, 错误={e}")
        
        # 提交事务
        db.session.commit()
        
        # 记录操作日志
        logger.info(f"批量护工操作: 操作={operation}, 成功={success_count}, 失败={failed_count}, 护工IDs={caregiver_ids}")
        
        # 构建响应
        response_data = {
            'success': True,
            'message': f'批量操作完成，成功{success_count}个，失败{failed_count}个',
            'operation': operation,
            'total_count': len(caregiver_ids),
            'success_count': success_count,
            'failed_count': failed_count
        }
        
        if failed_reasons:
            response_data['failed_reasons'] = failed_reasons
        
        return jsonify(response_data)
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"批量护工操作失败: {e}")
        return jsonify({'success': False, 'message': f'批量操作失败：{str(e)}'}), 500
