"""
护工资源管理系统 - 服务类型数据模型
====================================

服务类型数据模型定义，包含服务类型和关联表
"""

import sys
import os

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extensions import db

class ServiceType(db.Model):
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

# 护工与服务类型的多对多关联表
caregiver_service = db.Table('caregiver_service',
    db.Column('caregiver_id', db.Integer, db.ForeignKey('caregiver.id'), primary_key=True),
    db.Column('service_type_id', db.Integer, db.ForeignKey('service_type.id'), primary_key=True)
) 