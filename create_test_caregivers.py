#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试护工数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from back.app import app, db
from back.models.caregiver import Caregiver

def create_test_caregivers():
    """创建测试护工数据"""
    with app.app_context():
        try:
            CaregiverModel = Caregiver.get_model(db)
            
            # 检查是否已有护工数据
            existing_count = CaregiverModel.query.count()
            print(f"当前护工数量: {existing_count}")
            
            if existing_count > 0:
                print("数据库中已有护工数据，跳过创建")
                return
            
            # 创建测试护工数据
            test_caregivers = [
                {
                    'name': '张护士',
                    'phone': '13800138001',
                    'email': 'zhang@example.com',
                    'age': 28,
                    'gender': '女',
                    'experience_years': 5,
                    'specialties': '老年护理,康复护理',
                    'hourly_rate': 50.0,
                    'is_available': True,
                    'avatar_url': '/uploads/avatars/default-caregiver.png'
                },
                {
                    'name': '李护工',
                    'phone': '13800138002',
                    'email': 'li@example.com',
                    'age': 35,
                    'gender': '男',
                    'experience_years': 8,
                    'specialties': '重症护理,术后护理',
                    'hourly_rate': 60.0,
                    'is_available': True,
                    'avatar_url': '/uploads/avatars/default-caregiver.png'
                },
                {
                    'name': '王护理',
                    'phone': '13800138003',
                    'email': 'wang@example.com',
                    'age': 30,
                    'gender': '女',
                    'experience_years': 6,
                    'specialties': '儿科护理,母婴护理',
                    'hourly_rate': 55.0,
                    'is_available': True,
                    'avatar_url': '/uploads/avatars/default-caregiver.png'
                },
                {
                    'name': '陈师傅',
                    'phone': '13800138004',
                    'email': 'chen@example.com',
                    'age': 42,
                    'gender': '男',
                    'experience_years': 10,
                    'specialties': '长期护理,失能护理',
                    'hourly_rate': 45.0,
                    'is_available': True,
                    'avatar_url': '/uploads/avatars/default-caregiver.png'
                },
                {
                    'name': '刘护士长',
                    'phone': '13800138005',
                    'email': 'liu@example.com',
                    'age': 38,
                    'gender': '女',
                    'experience_years': 12,
                    'specialties': '护理管理,专业培训',
                    'hourly_rate': 80.0,
                    'is_available': True,
                    'avatar_url': '/uploads/avatars/default-caregiver.png'
                }
            ]
            
            # 插入测试数据
            for caregiver_data in test_caregivers:
                caregiver = CaregiverModel(**caregiver_data)
                db.session.add(caregiver)
            
            db.session.commit()
            print(f"✅ 成功创建 {len(test_caregivers)} 个测试护工")
            
            # 验证创建结果
            final_count = CaregiverModel.query.count()
            print(f"当前护工总数: {final_count}")
            
        except Exception as e:
            print(f"❌ 创建测试护工失败: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    create_test_caregivers()
