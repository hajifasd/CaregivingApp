#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建通知系统表
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from models.notification import Notification

def create_notification_tables():
    """创建通知系统表"""
    try:
        with app.app_context():
            # 获取通知模型类
            NotificationModel = Notification.get_model(db)
            
            # 创建表
            db.create_all()
            print("✅ 通知系统表创建成功")
            
            # 可选：插入示例数据
            should_insert = input("是否插入示例数据？(y/n): ").lower().strip()
            if should_insert == 'y':
                insert_sample_data()
                
    except Exception as e:
        print(f"❌ 创建通知系统表失败: {e}")
        import traceback
        traceback.print_exc()

def insert_sample_data():
    """插入示例数据"""
    try:
        with app.app_context():
            # 获取模型类
            NotificationModel = Notification.get_model(db)
            
            # 示例通知数据
            sample_data = [
                {
                    'recipient_id': 1,
                    'recipient_type': 'caregiver',
                    'sender_id': 1,
                    'sender_type': 'user',
                    'notification_type': 'job_opportunity',
                    'title': '新的工作机会',
                    'content': '您收到了一个居家护理服务的工作机会，请及时查看并回复。',
                    'related_id': 1,
                    'related_type': 'contract_application',
                    'priority': 'high'
                },
                {
                    'recipient_id': 1,
                    'recipient_type': 'user',
                    'sender_id': 1,
                    'sender_type': 'caregiver',
                    'notification_type': 'application_response',
                    'title': '护工接受了您的工作申请',
                    'content': '护工已接受您的居家护理服务申请，请查看详情。',
                    'related_id': 1,
                    'related_type': 'contract_application',
                    'priority': 'high'
                }
            ]
            
            # 插入数据
            for data in sample_data:
                notification = NotificationModel(**data)
                db.session.add(notification)
            
            db.session.commit()
            print(f"✅ 成功插入 {len(sample_data)} 条示例通知")
            
    except Exception as e:
        print(f"❌ 插入示例数据失败: {e}")
        db.session.rollback()
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("🚀 开始创建通知系统表...")
    create_notification_tables()
    print("✨ 完成！")
