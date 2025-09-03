"""
护工资源管理系统 - 聘用合同数据模型
====================================

专门用于管理用户和护工之间的正式聘用关系，包括合同签订、服务记录、费用结算等
"""

from datetime import datetime, timezone
from typing import Dict, Any

class EmploymentContract:
    """聘用合同模型包装器"""
    
    _model_class = None
    
    def __init__(self):
        pass
    
    @classmethod
    def get_model(cls, db):
        """获取实际的SQLAlchemy模型"""
        if cls._model_class is not None:
            return cls._model_class
        
        class EmploymentContractModel(db.Model):
            """聘用合同模型 - 存储用户与护工之间的正式聘用合同
            
            字段说明：
            - id: 合同唯一标识
            - contract_number: 合同编号
            - user_id: 用户ID（外键关联）
            - caregiver_id: 护工ID（外键关联）
            - service_type: 服务类型（老年护理、母婴护理、康复护理等）
            - contract_type: 合同类型（临时、长期、全职）
            - start_date: 合同开始日期
            - end_date: 合同结束日期
            - work_schedule: 工作时间安排（JSON格式）
            - hourly_rate: 时薪
            - total_hours: 总服务时长
            - total_amount: 合同总金额
            - payment_terms: 付款条件
            - status: 合同状态（draft草稿, active生效, completed完成, terminated终止）
            - terms_conditions: 合同条款
            - created_at: 创建时间
            - updated_at: 更新时间
            """
            __tablename__ = 'employment_contract'
            __table_args__ = {'extend_existing': True}
            
            id = db.Column(db.Integer, primary_key=True)
            contract_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
            user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
            caregiver_id = db.Column(db.Integer, db.ForeignKey('caregiver.id'), nullable=False)
            service_type = db.Column(db.String(50), nullable=False)
            contract_type = db.Column(db.String(20), nullable=False)  # temporary, long_term, full_time
            start_date = db.Column(db.Date, nullable=False)
            end_date = db.Column(db.Date)
            work_schedule = db.Column(db.JSON)  # 工作时间安排
            hourly_rate = db.Column(db.Numeric(10, 2), nullable=False)
            total_hours = db.Column(db.Integer, default=0)
            total_amount = db.Column(db.Numeric(10, 2), default=0)
            payment_terms = db.Column(db.String(200))
            status = db.Column(db.String(20), default='draft')
            terms_conditions = db.Column(db.Text)
            created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
            updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
            
            def to_dict(self) -> Dict[str, Any]:
                """转换为字典格式"""
                return {
                    "id": self.id,
                    "contract_number": self.contract_number,
                    "user_id": self.user_id,
                    "caregiver_id": self.caregiver_id,
                    "service_type": self.service_type,
                    "contract_type": self.contract_type,
                    "start_date": self.start_date.isoformat() if self.start_date else None,
                    "end_date": self.end_date.isoformat() if self.end_date else None,
                    "work_schedule": self.work_schedule,
                    "hourly_rate": float(self.hourly_rate) if self.hourly_rate else 0,
                    "total_hours": self.total_hours,
                    "total_amount": float(self.total_amount) if self.total_amount else 0,
                    "payment_terms": self.payment_terms,
                    "status": self.status,
                    "terms_conditions": self.terms_conditions,
                    "created_at": self.created_at.isoformat() if self.created_at else None,
                    "updated_at": self.updated_at.isoformat() if self.updated_at else None
                }
            
            def __repr__(self):
                return f"<EmploymentContract(id={self.id}, contract_number='{self.contract_number}', status='{self.status}')>"
        
        cls._model_class = EmploymentContractModel
        return EmploymentContractModel

class ServiceRecord:
    """服务记录模型包装器"""
    
    _model_class = None
    
    def __init__(self):
        pass
    
    @classmethod
    def get_model(cls, db):
        """获取实际的SQLAlchemy模型"""
        if cls._model_class is not None:
            return cls._model_class
        
        class ServiceRecordModel(db.Model):
            """服务记录模型 - 记录护工每次服务的详细信息
            
            字段说明：
            - id: 记录唯一标识
            - contract_id: 合同ID（外键关联）
            - service_date: 服务日期
            - start_time: 开始时间
            - end_time: 结束时间
            - actual_hours: 实际服务时长
            - service_content: 服务内容描述
            - quality_rating: 服务质量评分（1-5）
            - user_feedback: 用户反馈
            - status: 记录状态（scheduled已安排, in_progress进行中, completed已完成, cancelled已取消）
            - created_at: 创建时间
            """
            __tablename__ = 'service_record'
            __table_args__ = {'extend_existing': True}
            
            id = db.Column(db.Integer, primary_key=True)
            contract_id = db.Column(db.Integer, db.ForeignKey('employment_contract.id'), nullable=False)
            service_date = db.Column(db.Date, nullable=False)
            start_time = db.Column(db.Time, nullable=False)
            end_time = db.Column(db.Time, nullable=False)
            actual_hours = db.Column(db.Numeric(4, 2), nullable=False)  # 实际服务时长
            service_content = db.Column(db.Text)
            quality_rating = db.Column(db.Integer)  # 1-5分
            user_feedback = db.Column(db.Text)
            status = db.Column(db.String(20), default='scheduled')
            created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
            
            def to_dict(self) -> Dict[str, Any]:
                """转换为字典格式"""
                return {
                    "id": self.id,
                    "contract_id": self.contract_id,
                    "service_date": self.service_date.isoformat() if self.service_date else None,
                    "start_time": self.start_time.isoformat() if self.start_time else None,
                    "end_time": self.end_time.isoformat() if self.end_time else None,
                    "actual_hours": float(self.actual_hours) if self.actual_hours else 0,
                    "service_content": self.service_content,
                    "quality_rating": self.quality_rating,
                    "user_feedback": self.user_feedback,
                    "status": self.status,
                    "created_at": self.created_at.isoformat() if self.created_at else None
                }
            
            def __repr__(self):
                return f"<ServiceRecord(id={self.id}, contract_id={self.contract_id}, date='{self.service_date}')>"
        
        cls._model_class = ServiceRecordModel
        return ServiceRecordModel

class ContractApplication:
    """合同申请模型包装器"""
    
    _model_class = None
    
    def __init__(self):
        pass
    
    @classmethod
    def get_model(cls, db):
        """获取实际的SQLAlchemy模型"""
        if cls._model_class is not None:
            return cls._model_class
        
        class ContractApplicationModel(db.Model):
            """合同申请模型 - 存储用户向护工发出的聘用申请
            
            字段说明：
            - id: 申请唯一标识
            - user_id: 用户ID（外键关联）
            - caregiver_id: 护工ID（外键关联）
            - service_type: 服务类型
            - proposed_start_date: 建议开始日期
            - proposed_end_date: 建议结束日期
            - proposed_hours: 建议服务时长
            - proposed_rate: 建议时薪
            - application_message: 申请说明
            - status: 申请状态（pending待回复, accepted已接受, rejected已拒绝, withdrawn已撤回）
            - caregiver_response: 护工回复
            - response_time: 回复时间
            - created_at: 创建时间
            """
            __tablename__ = 'contract_application'
            __table_args__ = {'extend_existing': True}
            
            id = db.Column(db.Integer, primary_key=True)
            user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
            caregiver_id = db.Column(db.Integer, db.ForeignKey('caregiver.id'), nullable=False)
            service_type = db.Column(db.String(50), nullable=False)
            proposed_start_date = db.Column(db.Date, nullable=False)
            proposed_end_date = db.Column(db.Date)
            proposed_hours = db.Column(db.Integer)
            proposed_rate = db.Column(db.Numeric(10, 2))
            application_message = db.Column(db.Text)
            status = db.Column(db.String(20), default='pending')
            caregiver_response = db.Column(db.Text)
            response_time = db.Column(db.DateTime)
            created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
            
            def to_dict(self) -> Dict[str, Any]:
                """转换为字典格式"""
                return {
                    "id": self.id,
                    "user_id": self.user_id,
                    "caregiver_id": self.caregiver_id,
                    "service_type": self.service_type,
                    "proposed_start_date": self.proposed_start_date.isoformat() if self.proposed_start_date else None,
                    "proposed_end_date": self.proposed_end_date.isoformat() if self.proposed_end_date else None,
                    "proposed_hours": self.proposed_hours,
                    "proposed_rate": float(self.proposed_rate) if self.proposed_rate else None,
                    "application_message": self.application_message,
                    "status": self.status,
                    "caregiver_response": self.caregiver_response,
                    "response_time": self.response_time.isoformat() if self.response_time else None,
                    "created_at": self.created_at.isoformat() if self.created_at else None
                }
            
            def __repr__(self):
                return f"<ContractApplication(id={self.id}, user_id={self.user_id}, caregiver_id={self.caregiver_id}, status='{self.status}')>"
        
        cls._model_class = ContractApplicationModel
        return ContractApplicationModel
