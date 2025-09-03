#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建护工聘用信息表
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from models.caregiver_hire_info import CaregiverHireInfo

def create_caregiver_hire_info_tables():
    """创建护工聘用信息表"""
    try:
        with app.app_context():
            # 先初始化护工模型，确保外键表存在
            from models.caregiver import Caregiver
            CaregiverModel = Caregiver.get_model(db)
            
            # 获取护工聘用信息模型类
            CaregiverHireInfoModel = CaregiverHireInfo.get_model(db)
            
            # 创建表
            db.create_all()
            print("✅ 护工聘用信息表创建成功")
            
            # 可选：插入示例数据
            should_insert = input("是否插入示例数据？(y/n): ").lower().strip()
            if should_insert == 'y':
                insert_sample_data_func()
                
    except Exception as e:
        print(f"❌ 创建护工聘用信息表失败: {e}")
        import traceback
        traceback.print_exc()

def insert_sample_data_func():
    """插入示例数据"""
    try:
        with app.app_context():
            # 获取模型类
            CaregiverHireInfoModel = CaregiverHireInfo.get_model(db)
            from models.caregiver import Caregiver
            CaregiverModel = Caregiver.get_model(db)
            
            # 获取现有的护工
            caregivers = CaregiverModel.query.limit(3).all()
            
            if not caregivers:
                print("⚠️  没有找到护工数据，无法插入示例聘用信息")
                return
            
            # 示例聘用信息数据
            sample_data = [
                {
                    'service_type': '居家护理',
                    'status': 'available',
                    'hourly_rate': 50.0,
                    'work_time': '全职',
                    'service_area': '北京市朝阳区',
                    'available_time': '周一至周日 8:00-20:00',
                    'skills': '老年护理,康复护理,生活照料',
                    'commitment': '专业护理服务，经验丰富，服务周到，有爱心和耐心'
                },
                {
                    'service_type': '医院陪护',
                    'status': 'available',
                    'hourly_rate': 60.0,
                    'work_time': '兼职',
                    'service_area': '北京市海淀区',
                    'available_time': '周一至周五 18:00-次日8:00',
                    'skills': '医院陪护,术后护理,输液观察',
                    'commitment': '专业医院陪护，熟悉医院流程，细心负责'
                },
                {
                    'service_type': '母婴护理',
                    'status': 'available',
                    'hourly_rate': 80.0,
                    'work_time': '全职',
                    'service_area': '北京市西城区',
                    'available_time': '周一至周日 24小时',
                    'skills': '新生儿护理,产妇护理,母乳喂养指导',
                    'commitment': '专业母婴护理师，有丰富的新生儿和产妇护理经验'
                }
            ]
            
            # 插入数据
            for i, caregiver in enumerate(caregivers):
                if i < len(sample_data):
                    hire_info = CaregiverHireInfoModel(
                        caregiver_id=caregiver.id,
                        **sample_data[i]
                    )
                    db.session.add(hire_info)
            
            db.session.commit()
            print(f"✅ 成功插入 {len(caregivers)} 条示例聘用信息")
            
    except Exception as e:
        print(f"❌ 插入示例数据失败: {e}")
        db.session.rollback()
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("🚀 开始创建护工聘用信息表...")
    create_caregiver_hire_info_tables()
    print("✨ 完成！")
