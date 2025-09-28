"""
护工资源管理系统 - 聘用合同管理服务
====================================

处理用户和护工之间的聘用关系，包括申请、合同签订、服务记录等
"""

from datetime import datetime, timezone, date, time
from typing import Dict, Any, List, Optional
from decimal import Decimal
import uuid

class EmploymentContractService:
    """聘用合同管理服务"""
    
    def __init__(self, db=None):
        self.db = db
        self.contract_model = None
        self.service_record_model = None
        self.application_model = None
    
    def set_db(self, db):
        """设置数据库连接"""
        self.db = db
        from models.employment_contract import EmploymentContract, ServiceRecord, ContractApplication
        self.contract_model = EmploymentContract.get_model(db)
        self.service_record_model = ServiceRecord.get_model(db)
        self.application_model = ContractApplication.get_model(db)
    
    def create_contract_application(self, user_id: int, caregiver_id: int, 
                                  service_type: str, proposed_start_date: date,
                                  proposed_end_date: Optional[date] = None,
                                  proposed_hours: Optional[int] = None,
                                  proposed_rate: Optional[Decimal] = None,
                                  application_message: str = "") -> Dict[str, Any]:
        """创建聘用申请"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            # 检查是否已有待处理的申请
            existing_application = self.application_model.query.filter_by(
                user_id=user_id,
                caregiver_id=caregiver_id,
                status='pending'
            ).first()
            
            if existing_application:
                return {"success": False, "message": "您已向该护工发出申请，请等待回复"}
            
            # 创建新申请
            application = self.application_model(
                user_id=user_id,
                caregiver_id=caregiver_id,
                service_type=service_type,
                proposed_start_date=proposed_start_date,
                proposed_end_date=proposed_end_date,
                proposed_hours=proposed_hours,
                proposed_rate=proposed_rate,
                application_message=application_message,
                status='pending'
            )
            
            self.db.session.add(application)
            self.db.session.commit()
            
            # 为护工创建工作机会通知
            try:
                from services.notification_service import notification_service
                notification_service.set_db(self.db)
                notification_service.create_job_opportunity_notification(
                    caregiver_id=caregiver_id,
                    user_id=user_id,
                    application_id=application.id,
                    service_type=service_type
                )
            except Exception as e:
                # 通知创建失败不影响主流程
                print(f"创建通知失败: {e}")
            
            return {
                "success": True,
                "message": "申请提交成功，护工将收到工作机会通知",
                "data": application.to_dict()
            }
            
        except Exception as e:
            self.db.session.rollback()
            return {"success": False, "message": f"创建申请失败: {str(e)}"}
    
    def respond_to_application(self, application_id: int, caregiver_id: int,
                             response: str, status: str) -> Dict[str, Any]:
        """护工回复聘用申请"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            application = self.application_model.query.get(application_id)
            if not application:
                return {"success": False, "message": "申请不存在"}
            
            if application.caregiver_id != caregiver_id:
                return {"success": False, "message": "无权操作此申请"}
            
            if application.status != 'pending':
                return {"success": False, "message": "申请已被处理"}
            
            # 更新申请状态
            application.caregiver_response = response
            application.status = status
            application.response_time = datetime.now(timezone.utc)
            
            self.db.session.commit()
            
            return {
                "success": True,
                "message": "回复成功",
                "data": application.to_dict()
            }
            
        except Exception as e:
            self.db.session.rollback()
            return {"success": False, "message": f"回复失败: {str(e)}"}
    
    def cancel_application(self, application_id: int) -> Dict[str, Any]:
        """取消聘用申请（从数据库中删除）"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            # 获取申请信息
            application = self.application_model.query.get(application_id)
            if not application:
                return {"success": False, "message": "申请不存在"}
            
            # 检查申请状态，只有pending状态的申请才能取消
            if application.status != 'pending':
                return {"success": False, "message": "只有待回复的申请才能取消"}
            
            # 从数据库中删除申请记录
            self.db.session.delete(application)
            self.db.session.commit()
            
            return {
                "success": True,
                "message": "申请已取消"
            }
            
        except Exception as e:
            self.db.session.rollback()
            return {"success": False, "message": f"取消申请失败: {str(e)}"}
    
    def create_employment_contract(self, application_id: int, 
                                 contract_type: str = 'temporary',
                                 work_schedule: Dict = None,
                                 terms_conditions: str = "") -> Dict[str, Any]:
        """基于申请创建聘用合同"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            # 获取申请信息
            application = self.application_model.query.get(application_id)
            if not application:
                return {"success": False, "message": "申请不存在"}
            
            if application.status != 'accepted':
                return {"success": False, "message": "申请尚未被接受"}
            
            # 生成合同编号
            contract_number = f"CONTRACT_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
            
            # 计算合同金额
            total_amount = 0
            if application.proposed_rate and application.proposed_hours:
                total_amount = application.proposed_rate * application.proposed_hours
            
            # 创建合同
            contract = self.contract_model(
                contract_number=contract_number,
                user_id=application.user_id,
                caregiver_id=application.caregiver_id,
                service_type=application.service_type,
                contract_type=contract_type,
                start_date=application.proposed_start_date,
                end_date=application.proposed_end_date,
                work_schedule=work_schedule or {},
                hourly_rate=application.proposed_rate or Decimal('0'),
                total_hours=application.proposed_hours or 0,
                total_amount=total_amount,
                payment_terms="月结",
                status='active',
                terms_conditions=terms_conditions
            )
            
            self.db.session.add(contract)
            self.db.session.commit()
            
            return {
                "success": True,
                "message": "合同创建成功",
                "data": contract.to_dict()
            }
            
        except Exception as e:
            self.db.session.rollback()
            return {"success": False, "message": f"创建合同失败: {str(e)}"}
    
    def get_user_contracts(self, user_id: int, status: Optional[str] = None) -> Dict[str, Any]:
        """获取用户的聘用合同"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            query = self.contract_model.query.filter_by(user_id=user_id)
            if status:
                query = query.filter_by(status=status)
            
            contracts = query.order_by(self.contract_model.created_at.desc()).all()
            
            return {
                "success": True,
                "data": [contract.to_dict() for contract in contracts]
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取合同失败: {str(e)}"}
    
    def get_caregiver_contracts(self, caregiver_id: int, status: Optional[str] = None) -> Dict[str, Any]:
        """获取护工的聘用合同"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            query = self.contract_model.query.filter_by(caregiver_id=caregiver_id)
            if status:
                query = query.filter_by(status=status)
            
            contracts = query.order_by(self.contract_model.created_at.desc()).all()
            
            return {
                "success": True,
                "data": [contract.to_dict() for contract in contracts]
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取合同失败: {str(e)}"}
    
    def get_contract_details(self, contract_id: int) -> Dict[str, Any]:
        """获取合同详细信息"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            contract = self.contract_model.query.get(contract_id)
            if not contract:
                return {"success": False, "message": "合同不存在"}
            
            return {
                "success": True,
                "data": contract.to_dict()
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取合同详情失败: {str(e)}"}
    
    def create_service_record(self, contract_id: int, service_date: date,
                            start_time: time, end_time: time,
                            service_content: str = "") -> Dict[str, Any]:
        """创建服务记录"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            # 计算实际服务时长
            start_datetime = datetime.combine(service_date, start_time)
            end_datetime = datetime.combine(service_date, end_time)
            actual_hours = (end_datetime - start_datetime).total_seconds() / 3600
            
            # 创建服务记录
            service_record = self.service_record_model(
                contract_id=contract_id,
                service_date=service_date,
                start_time=start_time,
                end_time=end_time,
                actual_hours=Decimal(str(round(actual_hours, 2))),
                service_content=service_content,
                status='completed'
            )
            
            self.db.session.add(service_record)
            self.db.session.commit()
            
            return {
                "success": True,
                "message": "服务记录创建成功",
                "data": service_record.to_dict()
            }
            
        except Exception as e:
            self.db.session.rollback()
            return {"success": False, "message": f"创建服务记录失败: {str(e)}"}
    
    def get_contract_service_records(self, contract_id: int) -> Dict[str, Any]:
        """获取合同的服务记录"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            records = self.service_record_model.query.filter_by(
                contract_id=contract_id
            ).order_by(self.service_record_model.service_date.desc()).all()
            
            return {
                "success": True,
                "data": [record.to_dict() for record in records]
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取服务记录失败: {str(e)}"}
    
    def update_contract_status(self, contract_id: int, new_status: str) -> Dict[str, Any]:
        """更新合同状态"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            contract = self.contract_model.query.get(contract_id)
            if not contract:
                return {"success": False, "message": "合同不存在"}
            
            contract.status = new_status
            contract.updated_at = datetime.now(timezone.utc)
            
            self.db.session.commit()
            
            return {
                "success": True,
                "message": "合同状态更新成功",
                "data": contract.to_dict()
            }
            
        except Exception as e:
            self.db.session.rollback()
            return {"success": False, "message": f"更新合同状态失败: {str(e)}"}
    
    def get_user_applications(self, user_id: int) -> Dict[str, Any]:
        """获取用户的申请列表"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            # 获取申请列表，同时关联护工信息
            applications = self.application_model.query.filter_by(
                user_id=user_id
            ).order_by(self.application_model.created_at.desc()).all()
            
            # 获取护工模型
            try:
                from models.caregiver import CaregiverModel
                caregiver_model = CaregiverModel.get_model(self.db)
            except Exception as e:
                print(f"导入护工模型失败: {e}")
                # 如果导入失败，返回基本数据
                return {
                    "success": True,
                    "data": [app.to_dict() for app in applications]
                }
            
            # 为每个申请添加护工详细信息
            enriched_applications = []
            for app in applications:
                app_dict = app.to_dict()
                
                # 获取护工信息
                caregiver = caregiver_model.query.get(app.caregiver_id)
                if caregiver:
                    app_dict.update({
                        'caregiver_name': caregiver.name,
                        'caregiver_avatar': caregiver.avatar_url,
                        'caregiver_rating': caregiver.rating,
                        'caregiver_phone': caregiver.phone,
                        'caregiver_location': getattr(caregiver, 'location', ''),
                        'caregiver_experience': getattr(caregiver, 'experience_years', 0)
                    })
                else:
                    # 如果护工不存在，提供默认值
                    app_dict.update({
                        'caregiver_name': '未知护工',
                        'caregiver_avatar': None,
                        'caregiver_rating': 0,
                        'caregiver_phone': '',
                        'caregiver_location': '',
                        'caregiver_experience': 0
                    })
                
                enriched_applications.append(app_dict)
            
            return {
                "success": True,
                "data": enriched_applications
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取申请列表失败: {str(e)}"}
    
    def get_caregiver_applications(self, caregiver_id: int) -> Dict[str, Any]:
        """获取护工收到的申请列表"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            # 获取申请列表，同时关联用户信息
            applications = self.application_model.query.filter_by(
                caregiver_id=caregiver_id
            ).order_by(self.application_model.created_at.desc()).all()
            
            # 获取用户模型
            try:
                from models.user import UserModel
                user_model = UserModel.get_model(self.db)
            except Exception as e:
                print(f"导入用户模型失败: {e}")
                # 如果导入失败，返回基本数据
                return {
                    "success": True,
                    "data": [app.to_dict() for app in applications]
                }
            
            # 为每个申请添加用户详细信息
            enriched_applications = []
            for app in applications:
                app_dict = app.to_dict()
                
                # 获取用户信息
                user = user_model.query.get(app.user_id)
                if user:
                    app_dict.update({
                        'user_name': user.name,
                        'user_avatar': getattr(user, 'avatar_url', None),
                        'user_phone': user.phone,
                        'user_address': getattr(user, 'address', '')
                    })
                else:
                    # 如果用户不存在，提供默认值
                    app_dict.update({
                        'user_name': '未知用户',
                        'user_avatar': None,
                        'user_phone': '',
                        'user_address': ''
                    })
                
                enriched_applications.append(app_dict)
            
            return {
                "success": True,
                "data": enriched_applications
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取申请列表失败: {str(e)}"}

    def get_application_detail(self, application_id: int) -> Dict[str, Any]:
        """获取申请详情"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            # 获取申请详情
            application = self.application_model.query.get(application_id)
            if not application:
                return {"success": False, "message": "申请不存在"}
            
            # 获取用户信息
            try:
                from models.user import UserModel
                user_model = UserModel.get_model(self.db)
                user = user_model.query.get(application.user_id)
                
                app_dict = application.to_dict()
                if user:
                    app_dict.update({
                        'user_name': user.name,
                        'user_avatar': getattr(user, 'avatar_url', None),
                        'user_phone': user.phone,
                        'user_address': getattr(user, 'address', '')
                    })
                else:
                    app_dict.update({
                        'user_name': '未知用户',
                        'user_avatar': None,
                        'user_phone': '',
                        'user_address': ''
                    })
                
                return {
                    "success": True,
                    "data": app_dict
                }
                
            except Exception as e:
                # 如果获取用户信息失败，返回基本申请信息
                return {
                    "success": True,
                    "data": application.to_dict()
                }
            
        except Exception as e:
            return {"success": False, "message": f"获取申请详情失败: {str(e)}"}

    def get_user_hired_caregivers(self, user_id: int) -> Dict[str, Any]:
        """获取用户已经聘用的护工列表（用于消息页面的新建对话）"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            # 获取状态为'accepted'的申请，表示护工已同意聘用
            accepted_applications = self.application_model.query.filter_by(
                user_id=user_id,
                status='accepted'
            ).order_by(self.application_model.created_at.desc()).all()
            
            # 获取护工模型
            try:
                from models.caregiver import Caregiver
                caregiver_model = Caregiver.get_model(self.db)
            except Exception as e:
                print(f"导入护工模型失败: {e}")
                # 如果导入失败，返回基本数据
                return {
                    "success": True,
                    "data": [app.to_dict() for app in accepted_applications]
                }
            
            # 为每个已接受的申请添加护工详细信息
            hired_caregivers = []
            for app in accepted_applications:
                app_dict = app.to_dict()
                
                # 获取护工信息
                caregiver = caregiver_model.query.get(app.caregiver_id)
                if caregiver:
                    app_dict.update({
                        'caregiver_name': caregiver.name,
                        'caregiver_avatar': caregiver.avatar_url or 'https://picsum.photos/id/64/400/300',
                        'caregiver_rating': caregiver.rating or '5.0',
                        'caregiver_phone': caregiver.phone,
                        'caregiver_location': getattr(caregiver, 'location', ''),
                        'caregiver_experience': getattr(caregiver, 'experience_years', 0),
                        'caregiver_qualification': getattr(caregiver, 'qualification', ''),
                        'caregiver_introduction': getattr(caregiver, 'introduction', '')
                    })
                else:
                    # 如果护工不存在，提供默认值
                    app_dict.update({
                        'caregiver_name': '未知护工',
                        'caregiver_avatar': 'https://picsum.photos/id/64/400/300',
                        'caregiver_rating': '5.0',
                        'caregiver_phone': '',
                        'caregiver_location': '',
                        'caregiver_experience': 0,
                        'caregiver_qualification': '',
                        'caregiver_introduction': ''
                    })
                
                hired_caregivers.append(app_dict)
            
            return {
                "success": True,
                "data": hired_caregivers
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取已聘用护工列表失败: {str(e)}"}

# 创建全局服务实例
employment_contract_service = EmploymentContractService()
