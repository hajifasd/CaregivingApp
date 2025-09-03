#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建聘用关系数据库表脚本
用于在现有数据库中创建聘用合同、服务记录、合同申请等表结构
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_employment_tables():
    """创建聘用关系相关的数据库表"""
    try:
        print("🚀 开始创建聘用关系数据库表...")
        
        # 导入必要的模块
        from extensions import db
        from models.user import User
        from models.caregiver import Caregiver
        from models.employment_contract import EmploymentContract, ServiceRecord, ContractApplication
        
        # 创建应用上下文
        from app import app
        
        with app.app_context():
            print("📋 正在创建基础表...")
            # 先创建基础表
            UserModel = User.get_model(db)
            CaregiverModel = Caregiver.get_model(db)
            
            print("📋 正在创建聘用合同表...")
            EmploymentContractModel = EmploymentContract.get_model(db)
            
            print("📋 正在创建服务记录表...")
            ServiceRecordModel = ServiceRecord.get_model(db)
            
            print("📋 正在创建合同申请表...")
            ContractApplicationModel = ContractApplication.get_model(db)
            
            # 创建表
            db.create_all()
            
            print("✅ 聘用关系表创建完成！")
            
            # 显示表结构信息
            print("\n📊 表结构信息:")
            print(f"- user: 用户表")
            print(f"- caregiver: 护工表")
            print(f"- employment_contract: 聘用合同表")
            print(f"- service_record: 服务记录表")
            print(f"- contract_application: 合同申请表")
            
            # 检查表是否创建成功
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['user', 'caregiver', 'employment_contract', 'service_record', 'contract_application']
            for table in required_tables:
                if table in tables:
                    print(f"✅ {table} 表创建成功")
                else:
                    print(f"❌ {table} 表创建失败")
            
            return True
            
    except Exception as e:
        print(f"❌ 创建聘用关系表失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def insert_sample_data():
    """插入示例聘用数据"""
    try:
        print("\n📝 正在插入示例聘用数据...")
        
        from extensions import db
        from models.employment_contract import EmploymentContract, ServiceRecord, ContractApplication
        from datetime import datetime, timezone, date, time
        from decimal import Decimal
        from app import app
        
        with app.app_context():
            # 获取模型
            EmploymentContractModel = EmploymentContract.get_model(db)
            ServiceRecordModel = ServiceRecord.get_model(db)
            ContractApplicationModel = ContractApplication.get_model(db)
            
            # 创建示例合同申请
            application = ContractApplicationModel(
                user_id=1,  # 用户17661895382
                caregiver_id=2,  # 护工17661895381
                service_type="老年护理",
                proposed_start_date=date(2024, 12, 1),
                proposed_end_date=date(2024, 12, 31),
                proposed_hours=40,
                proposed_rate=Decimal('50.00'),
                application_message="您好，我母亲需要专业的老年护理服务，包括日常照料和康复训练。希望能与您合作，提供优质的服务。",
                status='pending',
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(application)
            
            # 创建示例聘用合同
            contract = EmploymentContractModel(
                contract_number="CONTRACT_20241201_ABC12345",
                user_id=1,
                caregiver_id=2,
                service_type="老年护理",
                contract_type="temporary",
                start_date=date(2024, 12, 1),
                end_date=date(2024, 12, 31),
                work_schedule={
                    "monday": {"start": "08:00", "end": "12:00"},
                    "wednesday": {"start": "08:00", "end": "12:00"},
                    "friday": {"start": "08:00", "end": "12:00"}
                },
                hourly_rate=Decimal('50.00'),
                total_hours=40,
                total_amount=Decimal('2000.00'),
                payment_terms="月结",
                status='active',
                terms_conditions="1. 护工需按时到岗，提供专业护理服务\n2. 用户按时支付服务费用\n3. 双方遵守合同约定",
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(contract)
            
            db.session.commit()
            
            # 创建示例服务记录
            service_record = ServiceRecordModel(
                contract_id=contract.id,
                service_date=date(2024, 12, 2),
                start_time=time(8, 0),
                end_time=time(12, 0),
                actual_hours=Decimal('4.0'),
                service_content="提供日常护理服务，包括协助洗漱、穿衣、进食，进行简单的康复训练，监测身体状况。",
                quality_rating=5,
                user_feedback="服务很专业，态度很好，母亲很满意。",
                status='completed',
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(service_record)
            
            db.session.commit()
            
            print("✅ 示例聘用数据插入成功！")
            print(f"   - 创建了1个合同申请")
            print(f"   - 创建了1个聘用合同")
            print(f"   - 创建了1条服务记录")
            
            return True
            
    except Exception as e:
        print(f"❌ 插入示例数据失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 护工资源管理系统 - 聘用关系表创建脚本")
    print("=" * 60)
    
    # 创建表
    if create_employment_tables():
        print("\n🎯 表创建完成！")
        
        # 询问是否插入示例数据
        try:
            choice = input("\n是否插入示例聘用数据？(y/n): ").strip().lower()
            if choice in ['y', 'yes', '是']:
                insert_sample_data()
        except KeyboardInterrupt:
            print("\n\n👋 用户取消操作")
        except Exception as e:
            print(f"\n❌ 插入示例数据时出错: {e}")
    else:
        print("\n💥 表创建失败！")
        sys.exit(1)
    
    print("\n🎉 脚本执行完成！")
