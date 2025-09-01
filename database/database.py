"""
护工资源管理系统 - 数据库初始化
====================================

数据库表创建和示例数据初始化
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 添加父目录到Python路径，用于导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from back.extensions import db
from back.models import User, Caregiver, ServiceType, JobData, AnalysisResult, Appointment, Employment, Message
from datetime import datetime, date, timezone
from back.utils.auth import hash_password

def init_database(app):
    """初始化数据库"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("数据库表创建完成")
        
        # 初始化示例数据
        initialize_sample_data()

def initialize_sample_data():
    """初始化示例数据"""
    # 检查是否已有数据
    if ServiceType.query.count() > 0:
        print("示例数据已存在，跳过初始化")
        return
    
    print("开始初始化示例数据...")
    
    # 添加服务类型
    service_types = [
        ServiceType(name="老年护理", description="为老年人提供日常照料和护理服务"),
        ServiceType(name="母婴护理", description="为产妇和新生儿提供专业护理服务"),
        ServiceType(name="医疗护理", description="提供专业医疗护理服务，包括术后护理等"),
        ServiceType(name="康复护理", description="为需要康复的人士提供专业康复训练和护理")
    ]
    db.session.add_all(service_types)
    db.session.commit()
    print(f"已添加 {len(service_types)} 种服务类型")
    
    # 添加示例用户
    user = User(
        email="user@example.com",
        name="张阿姨",
        gender="女",
        birth_date=date(1965, 8, 12),
        address="北京市朝阳区建国路88号",
        emergency_contact="李小明（儿子）",
        phone="13800138000",
        emergency_contact_phone="13900139000",
        special_needs="本人需要定期进行康复护理，希望护工有相关经验，每周一、三、五上午需要服务。",
        avatar_url="https://picsum.photos/id/64/120/120",
        is_verified=True,
        is_approved=True,
        approved_at=datetime.now(timezone.utc)
    )
    user.set_password("123456")
    db.session.add(user)
    db.session.commit()
    print(f"已添加示例用户: {user.name}")
    
    # 添加示例护工
    caregiver1 = Caregiver(
        name="李敏",
        phone="13700137001",
        id_file="sample_id_001.jpg",
        cert_file="sample_cert_001.jpg",
        gender="女",
        age=45,
        avatar_url="https://picsum.photos/id/26/120/120",
        id_card="1101011978XXXX1234",
        qualification="高级护理证书",
        introduction="擅长老年日常护理、康复辅助，有耐心，责任心强，持有专业护理证书。",
        experience_years=5,
        hourly_rate=180.0,
        rating=4.8,
        review_count=126,
        status="approved",
        available=True,
        is_approved=True,
        approved_at=datetime.now(timezone.utc)
    )
    caregiver1.set_password("123456")
    caregiver1.service_types = [service_types[0], service_types[3]]  # 老年护理、康复护理
    
    caregiver2 = Caregiver(
        name="王芳",
        phone="13700137002",
        id_file="sample_id_002.jpg",
        cert_file="sample_cert_002.jpg",
        gender="女",
        age=38,
        avatar_url="https://picsum.photos/id/91/120/120",
        id_card="1101021985XXXX5678",
        qualification="高级母婴护理师证书",
        introduction="专业母婴护理师，擅长新生儿照料、产后恢复指导，服务细致周到。",
        experience_years=8,
        hourly_rate=220.0,
        rating=4.9,
        review_count=98,
        status="approved",
        available=True,
        is_approved=True,
        approved_at=datetime.now(timezone.utc)
    )
    caregiver2.set_password("123456")
    caregiver2.service_types = [service_types[1]]  # 母婴护理
    
    caregiver3 = Caregiver(
        name="张伟",
        phone="13700137003",
        id_file="sample_id_003.jpg",
        cert_file="sample_cert_003.jpg",
        gender="男",
        age=50,
        avatar_url="https://picsum.photos/id/177/120/120",
        id_card="1101031973XXXX9012",
        qualification="护师资格证",
        introduction="原医院护士，擅长术后护理、医疗辅助，熟悉各种医疗设备使用。",
        experience_years=10,
        hourly_rate=260.0,
        rating=4.7,
        review_count=76,
        status="approved",
        available=True,
        is_approved=True,
        approved_at=datetime.now(timezone.utc)
    )
    caregiver3.set_password("123456")
    caregiver3.service_types = [service_types[2], service_types[3]]  # 医疗护理、康复护理
    
    db.session.add_all([caregiver1, caregiver2, caregiver3])
    db.session.commit()
    print(f"已添加 {3} 名护工")
    
    print("示例数据初始化完成") 