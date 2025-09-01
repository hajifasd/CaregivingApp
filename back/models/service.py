"""
护工资源管理系统 - 服务类型数据模型
====================================

服务类型数据模型定义，包含服务类型和关联表
"""

class ServiceType:
    """服务类型数据模型包装器"""
    
    _model_class = None
    
    def __init__(self):
        pass
    
    @classmethod
    def get_model(cls, db):
        """获取实际的SQLAlchemy模型"""
        if cls._model_class is not None:
            return cls._model_class
        
        class ServiceTypeModel(db.Model):
            """服务类型数据模型
            
            字段说明：
            - id: 服务类型唯一标识
            - name: 服务类型名称（唯一，必填）
            - description: 服务类型描述
            """
            __tablename__ = 'service_type'
            
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(50), unique=True, nullable=False)
            description = db.Column(db.String(200))
        
        cls._model_class = ServiceTypeModel
        return ServiceTypeModel
    
    @classmethod
    def get_association_table(cls, db):
        """获取关联表"""
        return db.Table('caregiver_service',
            db.Column('caregiver_id', db.Integer, db.ForeignKey('caregiver.id'), primary_key=True),
            db.Column('service_type_id', db.Integer, db.ForeignKey('service_type.id'), primary_key=True)
        ) 