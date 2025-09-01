"""
护工资源管理系统 - 业务数据模型
====================================

包含预约、聘用、消息、职位数据等业务相关模型
"""

from datetime import datetime, timezone

class JobData:
    """职位数据模型包装器"""
    
    _model_class = None
    
    def __init__(self):
        pass
    
    @classmethod
    def get_model(cls, db):
        """获取实际的SQLAlchemy模型"""
        if cls._model_class is not None:
            return cls._model_class
        
        class JobDataModel(db.Model):
            """职位数据模型 - 存储从招聘网站爬取的职位信息
            
            字段说明：
            - id: 职位唯一标识
            - job_name: 职位名称
            - company: 公司名称
            - city: 城市
            - salary_low: 最低薪资
            - salary_high: 最高薪资
            - experience: 经验要求
            - education: 学历要求
            - skills: 技能要求
            - crawl_time: 爬取时间
            """
            __tablename__ = 'job_data'
            
            id = db.Column(db.Integer, primary_key=True)
            job_name = db.Column(db.String(100))
            company = db.Column(db.String(100))
            city = db.Column(db.String(20))
            salary_low = db.Column(db.Integer)
            salary_high = db.Column(db.Integer)
            experience = db.Column(db.String(50))
            education = db.Column(db.String(20))
            skills = db.Column(db.String(200))
            crawl_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
        
        cls._model_class = JobDataModel
        return JobDataModel

class AnalysisResult:
    """数据分析结果模型包装器"""
    
    _model_class = None
    
    def __init__(self):
        pass
    
    @classmethod
    def get_model(cls, db):
        """获取实际的SQLAlchemy模型"""
        if cls._model_class is not None:
            return cls._model_class
        
        class AnalysisResultModel(db.Model):
            """数据分析结果模型 - 存储职位数据分析的结果
            
            字段说明：
            - id: 结果唯一标识
            - type: 分析类型（如：salary_by_city, skill_counts等）
            - result: 分析结果（JSON格式）
            - create_time: 创建时间
            """
            __tablename__ = 'analysis_result'
            
            id = db.Column(db.Integer, primary_key=True)
            type = db.Column(db.String(50))
            result = db.Column(db.JSON)
            create_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
        
        cls._model_class = AnalysisResultModel
        return AnalysisResultModel

class Appointment:
    """预约模型包装器"""
    
    _model_class = None
    
    def __init__(self):
        pass
    
    @classmethod
    def get_model(cls, db):
        """获取实际的SQLAlchemy模型"""
        if cls._model_class is not None:
            return cls._model_class
        
        class AppointmentModel(db.Model):
            """预约模型 - 存储用户与护工的预约信息
            
            字段说明：
            - id: 预约唯一标识
            - user_id: 用户ID（外键关联）
            - caregiver_id: 护工ID（外键关联）
            - service_type: 服务类型
            - date: 预约日期
            - start_time: 开始时间
            - end_time: 结束时间
            - notes: 备注信息
            - status: 预约状态（pending待确认, confirmed已确认, completed已完成, cancelled已取消）
            - created_at: 创建时间
            """
            __tablename__ = 'appointment'
            
            id = db.Column(db.Integer, primary_key=True)
            user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
            caregiver_id = db.Column(db.Integer, db.ForeignKey('caregiver.id'), nullable=False)
            service_type = db.Column(db.String(50), nullable=False)
            date = db.Column(db.Date, nullable=False)
            start_time = db.Column(db.Time, nullable=False)
            end_time = db.Column(db.Time, nullable=False)
            notes = db.Column(db.Text)
            status = db.Column(db.String(20), default="pending")
            created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
        
        cls._model_class = AppointmentModel
        return AppointmentModel

class Employment:
    """长期聘用模型包装器"""
    
    _model_class = None
    
    def __init__(self):
        pass
    
    @classmethod
    def get_model(cls, db):
        """获取实际的SQLAlchemy模型"""
        if cls._model_class is not None:
            return cls._model_class
        
        class EmploymentModel(db.Model):
            """长期聘用模型 - 存储用户与护工的长期聘用关系
            
            字段说明：
            - id: 聘用唯一标识
            - user_id: 用户ID（外键关联）
            - caregiver_id: 护工ID（外键关联）
            - service_type: 服务类型
            - start_date: 开始日期
            - end_date: 结束日期（可为空，表示长期有效）
            - frequency: 服务频率（每周几次）
            - duration_per_session: 每次服务时长
            - status: 聘用状态（active活跃, terminated终止, completed完成）
            - notes: 备注信息
            - created_at: 创建时间
            """
            __tablename__ = 'employment'
            
            id = db.Column(db.Integer, primary_key=True)
            user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
            caregiver_id = db.Column(db.Integer, db.ForeignKey('caregiver.id'), nullable=False)
            service_type = db.Column(db.String(50), nullable=False)
            start_date = db.Column(db.Date, nullable=False)
            end_date = db.Column(db.Date)
            frequency = db.Column(db.String(50))
            duration_per_session = db.Column(db.String(20))
            status = db.Column(db.String(20), default="active")
            notes = db.Column(db.Text)
            created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
        
        cls._model_class = EmploymentModel
        return EmploymentModel

class Message:
    """消息模型包装器"""
    
    _model_class = None
    
    def __init__(self):
        pass
    
    @classmethod
    def get_model(cls, db):
        """获取实际的SQLAlchemy模型"""
        if cls._model_class is not None:
            return cls._model_class
        
        class MessageModel(db.Model):
            """消息模型 - 存储用户、护工、管理员之间的消息
            
            字段说明：
            - id: 消息唯一标识
            - sender_id: 发送者ID
            - sender_type: 发送者类型（user用户, caregiver护工, admin管理员）
            - recipient_id: 接收者ID
            - recipient_type: 接收者类型（user用户, caregiver护工, admin管理员）
            - content: 消息内容
            - is_read: 是否已读
            - created_at: 创建时间
            """
            __tablename__ = 'message'
            
            id = db.Column(db.Integer, primary_key=True)
            sender_id = db.Column(db.Integer, nullable=False)
            sender_type = db.Column(db.String(20), nullable=False)
            recipient_id = db.Column(db.Integer, nullable=False)
            recipient_type = db.Column(db.String(20), nullable=False)
            content = db.Column(db.Text, nullable=False)
            is_read = db.Column(db.Boolean, default=False)
            created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
        
        cls._model_class = MessageModel
        return MessageModel 