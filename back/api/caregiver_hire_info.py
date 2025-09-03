"""
护工资源管理系统 - 护工聘用信息API
====================================

护工聘用信息的增删改查API接口
"""

from flask import Blueprint, request, jsonify
from flask_socketio import emit
import logging
from datetime import datetime, timezone

# 导入数据库和模型
from extensions import db
from models.caregiver_hire_info import CaregiverHireInfo
from models.caregiver import Caregiver
from utils.auth import verify_token

# 创建蓝图
caregiver_hire_info_bp = Blueprint('caregiver_hire_info', __name__)

# 日志记录
logger = logging.getLogger(__name__)

@caregiver_hire_info_bp.route('/api/caregiver/hire-info', methods=['GET'])
def get_caregiver_hire_info():
    """获取护工的聘用信息"""
    try:
        # 验证护工token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        payload = verify_token(token)
        if not payload or payload.get('user_type') != 'caregiver':
            return jsonify({
                'success': False,
                'message': '未授权访问'
            }), 401
        
        caregiver_id = payload.get('user_id')
        
        # 获取护工聘用信息
        CaregiverHireInfoModel = CaregiverHireInfo.get_model(db)
        hire_info = CaregiverHireInfoModel.query.filter_by(caregiver_id=caregiver_id).first()
        
        if hire_info:
            return jsonify({
                'success': True,
                'data': hire_info.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': '未找到聘用信息'
            })
            
    except Exception as e:
        logger.error(f"获取护工聘用信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500

@caregiver_hire_info_bp.route('/api/caregiver/hire-info', methods=['POST'])
def create_or_update_caregiver_hire_info():
    """创建或更新护工聘用信息"""
    try:
        # 验证护工token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        payload = verify_token(token)
        if not payload or payload.get('user_type') != 'caregiver':
            return jsonify({
                'success': False,
                'message': '未授权访问'
            }), 401
        
        caregiver_id = payload.get('user_id')
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['service_type', 'status', 'hourly_rate', 'work_time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'缺少必填字段: {field}'
                }), 400
        
        # 获取或创建聘用信息
        CaregiverHireInfoModel = CaregiverHireInfo.get_model(db)
        hire_info = CaregiverHireInfoModel.query.filter_by(caregiver_id=caregiver_id).first()
        
        if hire_info:
            # 更新现有信息
            hire_info.service_type = data['service_type']
            hire_info.status = data['status']
            hire_info.hourly_rate = data['hourly_rate']
            hire_info.work_time = data['work_time']
            hire_info.service_area = data.get('service_area')
            hire_info.available_time = data.get('available_time')
            hire_info.skills = data.get('skills')
            hire_info.commitment = data.get('commitment')
            hire_info.updated_at = datetime.now(timezone.utc)
        else:
            # 创建新信息
            hire_info = CaregiverHireInfoModel(
                caregiver_id=caregiver_id,
                service_type=data['service_type'],
                status=data['status'],
                hourly_rate=data['hourly_rate'],
                work_time=data['work_time'],
                service_area=data.get('service_area'),
                available_time=data.get('available_time'),
                skills=data.get('skills'),
                commitment=data.get('commitment')
            )
            db.session.add(hire_info)
        
        db.session.commit()
        
        logger.info(f"护工聘用信息保存成功: caregiver_id={caregiver_id}")
        
        return jsonify({
            'success': True,
            'message': '聘用信息保存成功',
            'data': hire_info.to_dict()
        })
        
    except Exception as e:
        logger.error(f"保存护工聘用信息失败: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500

@caregiver_hire_info_bp.route('/api/caregiver/hire-info', methods=['DELETE'])
def delete_caregiver_hire_info():
    """删除护工聘用信息"""
    try:
        # 验证护工token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        payload = verify_token(token)
        if not payload or payload.get('user_type') != 'caregiver':
            return jsonify({
                'success': False,
                'message': '未授权访问'
            }), 401
        
        caregiver_id = payload.get('user_id')
        
        # 删除聘用信息
        CaregiverHireInfoModel = CaregiverHireInfo.get_model(db)
        hire_info = CaregiverHireInfoModel.query.filter_by(caregiver_id=caregiver_id).first()
        
        if hire_info:
            db.session.delete(hire_info)
            db.session.commit()
            
            logger.info(f"护工聘用信息删除成功: caregiver_id={caregiver_id}")
            
            return jsonify({
                'success': True,
                'message': '聘用信息删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '未找到聘用信息'
            }), 404
            
    except Exception as e:
        logger.error(f"删除护工聘用信息失败: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500

@caregiver_hire_info_bp.route('/api/caregivers/hire-info', methods=['GET'])
def get_all_caregivers_hire_info():
    """获取所有护工的聘用信息（用于用户端显示）"""
    try:
        # 获取查询参数
        service_type = request.args.get('service_type')
        status = request.args.get('status')
        min_rate = request.args.get('min_rate')
        max_rate = request.args.get('max_rate')
        
        # 获取护工聘用信息
        CaregiverHireInfoModel = CaregiverHireInfo.get_model(db)
        CaregiverModel = Caregiver.get_model(db)
        
        # 构建查询
        query = db.session.query(CaregiverHireInfoModel, CaregiverModel).join(
            CaregiverModel, CaregiverHireInfoModel.caregiver_id == CaregiverModel.id
        ).filter(CaregiverModel.is_approved == True)  # 只显示已审核的护工
        
        # 应用筛选条件
        if service_type:
            query = query.filter(CaregiverHireInfoModel.service_type == service_type)
        
        if status:
            query = query.filter(CaregiverHireInfoModel.status == status)
        
        if min_rate:
            query = query.filter(CaregiverHireInfoModel.hourly_rate >= float(min_rate))
        
        if max_rate:
            query = query.filter(CaregiverHireInfoModel.hourly_rate <= float(max_rate))
        
        # 执行查询
        results = query.all()
        
        # 格式化结果 - 合并护工信息和聘用信息为扁平结构
        caregivers_data = []
        for hire_info, caregiver in results:
            caregiver_data = {
                'caregiver_id': caregiver.id,
                'name': caregiver.name,
                'phone': caregiver.phone,
                'gender': caregiver.gender,
                'age': caregiver.age,
                'avatar': caregiver.avatar_url or 'https://picsum.photos/id/64/400/300',
                'qualification': caregiver.qualification,
                'introduction': caregiver.introduction,
                'experience_years': caregiver.experience_years,
                'rating': caregiver.rating or '5.0',
                'review_count': caregiver.review_count or 0,
                # 聘用信息
                'service_type': hire_info.service_type,
                'status': hire_info.status,
                'hourly_rate': float(hire_info.hourly_rate) if hire_info.hourly_rate else 50.0,
                'work_time': hire_info.work_time,
                'service_area': hire_info.service_area,
                'available_time': hire_info.available_time,
                'skills': hire_info.skills,
                'commitment': hire_info.commitment
            }
            caregivers_data.append(caregiver_data)
        
        logger.info(f"获取护工聘用信息成功: 共{len(caregivers_data)}条记录")
        
        return jsonify({
            'success': True,
            'data': caregivers_data
        })
        
    except Exception as e:
        logger.error(f"获取护工聘用信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500
