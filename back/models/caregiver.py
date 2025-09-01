"""
护工资源管理系统 - 护工数据模型
====================================

护工数据模型定义，包含所有护工相关字段和方法
"""

from datetime import datetime, timezone
from typing import Dict, Any
import sys
import os

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extensions import db
from utils.auth import hash_password

class Caregiver(db.Model):
    """护工数据模型
    
    字段说明：
    - id: 护工唯一标识
    - name: 护工姓名（必填）
    - phone: 手机号（唯一，必填）
    - id_file: 身份证文件路径（必填）
    - cert_file: 证书文件路径（必填）
    - password_hash: 加密后的密码（必填）
    - is_approved: 是否通过审核
    - created_at: 创建时间
    - approved_at: 审核通过时间
    - gender: 性别
    - age: 年龄
    - avatar_url: 头像URL
    - id_card: 身份证号
    - qualification: 资格证书
    - introduction: 个人介绍
    - experience_years: 工作年限
    - hourly_rate: 时薪
    - rating: 评分
    - review_count: 评价数量
    - status: 状态
    - available: 是否可用
    """
    __tablename__ = 'caregiver'
    
    # 基础字段
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    id_file = db.Column(db.String(200), nullable=False)
    cert_file = db.Column(db.String(200), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # 审核状态字段
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    approved_at = db.Column(db.DateTime, index=True)
    
    # 护工信息字段
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    avatar_url = db.Column(db.String(200))
    id_card = db.Column(db.String(18))
    qualification = db.Column(db.String(100))
    introduction = db.Column(db.Text)
    experience_years = db.Column(db.Integer)
    hourly_rate = db.Column(db.Float)
    rating = db.Column(db.Float, default=0)
    review_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default="pending")
    available = db.Column(db.Boolean, default=True)
    
    # 服务类型多对多关系
    service_types = db.relationship('ServiceType', secondary='caregiver_service', backref='caregivers')

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        valid_id_file = self.id_file and self.id_file.strip()
        valid_cert_file = self.cert_file and self.cert_file.strip()
        
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "id_file": self.id_file,
            "cert_file": self.cert_file,
            "id_file_url": f"/uploads/{self.id_file}" if valid_id_file else None,
            "cert_file_url": f"/uploads/{self.cert_file}" if valid_cert_file else None,
            "is_approved": self.is_approved,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M"),
            "approved_at": self.approved_at.strftime("%Y-%m-%d %H:%M") if self.approved_at else None,
            # 扩展字段
            "gender": self.gender,
            "age": self.age,
            "avatar_url": self.avatar_url,
            "id_card": self.id_card,
            "qualification": self.qualification,
            "introduction": self.introduction,
            "experience_years": self.experience_years,
            "hourly_rate": self.hourly_rate,
            "rating": self.rating,
            "review_count": self.review_count,
            "status": self.status,
            "available": self.available,
            "service_types": [st.name for st in self.service_types]
        }

    def set_password(self, password: str):
        """设置密码"""
        self.password_hash = hash_password(password) 