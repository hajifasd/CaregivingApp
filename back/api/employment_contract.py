"""
护工资源管理系统 - 聘用合同管理API
====================================

提供用户和护工之间聘用关系的API接口，包括申请、合同、服务记录等
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date, time
from decimal import Decimal
import json

# 创建蓝图
employment_contract_bp = Blueprint('employment_contract', __name__)

@employment_contract_bp.route('/api/employment/apply', methods=['POST'])
def create_application():
    """创建聘用申请"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['user_id', 'caregiver_id', 'service_type', 'proposed_start_date']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'缺少必需字段: {field}'
                }), 400
        
        # 解析日期
        try:
            proposed_start_date = datetime.strptime(data['proposed_start_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'message': '开始日期格式错误，应为YYYY-MM-DD'
            }), 400
        
        proposed_end_date = None
        if data.get('proposed_end_date'):
            try:
                proposed_end_date = datetime.strptime(data['proposed_end_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': '结束日期格式错误，应为YYYY-MM-DD'
                }), 400
        
        # 解析数值字段
        proposed_hours = data.get('proposed_hours')
        proposed_rate = None
        if data.get('proposed_rate'):
            try:
                proposed_rate = Decimal(str(data['proposed_rate']))
            except:
                return jsonify({
                    'success': False,
                    'message': '时薪格式错误'
                }), 400
        
        # 调用服务创建申请
        from services.employment_contract_service import employment_contract_service
        result = employment_contract_service.create_contract_application(
            user_id=data['user_id'],
            caregiver_id=data['caregiver_id'],
            service_type=data['service_type'],
            proposed_start_date=proposed_start_date,
            proposed_end_date=proposed_end_date,
            proposed_hours=proposed_hours,
            proposed_rate=proposed_rate,
            application_message=data.get('application_message', '')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建申请失败: {str(e)}'
        }), 500

@employment_contract_bp.route('/api/employment/respond', methods=['POST'])
def respond_to_application():
    """护工回复聘用申请"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['application_id', 'caregiver_id', 'response', 'status']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'缺少必需字段: {field}'
                }), 400
        
        # 验证状态值
        valid_statuses = ['accepted', 'rejected']
        if data['status'] not in valid_statuses:
            return jsonify({
                'success': False,
                'message': f'无效的状态值，应为: {", ".join(valid_statuses)}'
            }), 400
        
        # 调用服务回复申请
        from services.employment_contract_service import employment_contract_service
        result = employment_contract_service.respond_to_application(
            application_id=data['application_id'],
            caregiver_id=data['caregiver_id'],
            response=data['response'],
            status=data['status']
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'回复申请失败: {str(e)}'
        }), 500

@employment_contract_bp.route('/api/employment/cancel', methods=['POST'])
def cancel_application():
    """用户取消聘用申请"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        if 'application_id' not in data:
            return jsonify({
                'success': False,
                'message': '缺少申请ID'
            }), 400
        
        application_id = data['application_id']
        
        # 调用服务取消申请
        from services.employment_contract_service import employment_contract_service
        result = employment_contract_service.cancel_application(application_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': '申请已取消'
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message'] or '取消失败'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'取消申请失败: {str(e)}'
        }), 500

@employment_contract_bp.route('/api/employment/contract', methods=['POST'])
def create_contract():
    """创建聘用合同"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        if 'application_id' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必需字段: application_id'
            }), 400
        
        # 调用服务创建合同
        from services.employment_contract_service import employment_contract_service
        result = employment_contract_service.create_employment_contract(
            application_id=data['application_id'],
            contract_type=data.get('contract_type', 'temporary'),
            work_schedule=data.get('work_schedule', {}),
            terms_conditions=data.get('terms_conditions', '')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建合同失败: {str(e)}'
        }), 500

@employment_contract_bp.route('/api/employment/contracts/user/<int:user_id>', methods=['GET'])
def get_user_contracts(user_id):
    """获取用户的聘用合同"""
    try:
        status = request.args.get('status')
        
        from services.employment_contract_service import employment_contract_service
        result = employment_contract_service.get_user_contracts(user_id, status)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取合同失败: {str(e)}'
        }), 500

@employment_contract_bp.route('/api/employment/contracts/caregiver/<int:caregiver_id>', methods=['GET'])
def get_caregiver_contracts(caregiver_id):
    """获取护工的聘用合同"""
    try:
        status = request.args.get('status')
        
        from services.employment_contract_service import employment_contract_service
        result = employment_contract_service.get_caregiver_contracts(caregiver_id, status)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取合同失败: {str(e)}'
        }), 500

@employment_contract_bp.route('/api/employment/contract/<int:contract_id>', methods=['GET'])
def get_contract_details(contract_id):
    """获取合同详细信息"""
    try:
        from services.employment_contract_service import employment_contract_service
        result = employment_contract_service.get_contract_details(contract_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取合同详情失败: {str(e)}'
        }), 500

@employment_contract_bp.route('/api/employment/service-record', methods=['POST'])
def create_service_record():
    """创建服务记录"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['contract_id', 'service_date', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'缺少必需字段: {field}'
                }), 400
        
        # 解析日期和时间
        try:
            service_date = datetime.strptime(data['service_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'message': '服务日期格式错误，应为YYYY-MM-DD'
            }), 400
        
        try:
            start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        except ValueError:
            return jsonify({
                'success': False,
                'message': '开始时间格式错误，应为HH:MM'
            }), 400
        
        try:
            end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        except ValueError:
            return jsonify({
                'success': False,
                'message': '结束时间格式错误，应为HH:MM'
            }), 400
        
        # 调用服务创建服务记录
        from services.employment_contract_service import employment_contract_service
        result = employment_contract_service.create_service_record(
            contract_id=data['contract_id'],
            service_date=service_date,
            start_time=start_time,
            end_time=end_time,
            service_content=data.get('service_content', '')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建服务记录失败: {str(e)}'
        }), 500

@employment_contract_bp.route('/api/employment/service-records/<int:contract_id>', methods=['GET'])
def get_service_records(contract_id):
    """获取合同的服务记录"""
    try:
        from services.employment_contract_service import employment_contract_service
        result = employment_contract_service.get_contract_service_records(contract_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取服务记录失败: {str(e)}'
        }), 500

@employment_contract_bp.route('/api/employment/contract/<int:contract_id>/status', methods=['PUT'])
def update_contract_status(contract_id):
    """更新合同状态"""
    try:
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必需字段: status'
            }), 400
        
        # 验证状态值
        valid_statuses = ['draft', 'active', 'completed', 'terminated']
        if data['status'] not in valid_statuses:
            return jsonify({
                'success': False,
                'message': f'无效的状态值，应为: {", ".join(valid_statuses)}'
            }), 400
        
        # 调用服务更新状态
        from services.employment_contract_service import employment_contract_service
        result = employment_contract_service.update_contract_status(
            contract_id, data['status']
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新合同状态失败: {str(e)}'
        }), 500

@employment_contract_bp.route('/api/employment/applications/user/<int:user_id>', methods=['GET'])
def get_user_applications(user_id):
    """获取用户的申请列表"""
    try:
        from services.employment_contract_service import employment_contract_service
        result = employment_contract_service.get_user_applications(user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取申请列表失败: {str(e)}'
        }), 500

@employment_contract_bp.route('/api/employment/applications/caregiver/<int:caregiver_id>', methods=['GET'])
def get_caregiver_applications(caregiver_id):
    """获取护工收到的申请列表"""
    try:
        from services.employment_contract_service import employment_contract_service
        result = employment_contract_service.get_caregiver_applications(caregiver_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取申请列表失败: {str(e)}'
        }), 500

@employment_contract_bp.route('/api/employment/hired-caregivers/user/<int:user_id>', methods=['GET'])
def get_user_hired_caregivers(user_id):
    """获取用户已经聘用的护工列表（用于消息页面的新建对话）"""
    try:
        from services.employment_contract_service import employment_contract_service
        result = employment_contract_service.get_user_hired_caregivers(user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取已聘用护工列表失败: {str(e)}'
        }), 500
