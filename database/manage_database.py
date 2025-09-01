#!/usr/bin/env python3
"""
护工资源管理系统 - 数据库管理脚本
================================

功能说明：
- 数据库连接测试
- 表结构创建
- 数据备份和恢复
- 数据库状态检查

使用步骤：
1. 确保 MySQL 服务正在运行
2. 配置 .env 文件中的 MySQL 连接信息
3. 运行相应功能：python manage_database.py [功能]

支持功能：
- test: 测试数据库连接
- create: 创建表结构
- backup: 备份数据
- status: 检查数据库状态
- reset: 重置数据库（清空所有数据）

作者：护工资源管理系统开发团队
创建时间：2024年
版本：1.0
"""

import os
import sys
import json
import datetime
import argparse

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_connection():
    """测试数据库连接"""
    print("=== 测试数据库连接 ===")
    
    try:
        from back.config.settings import DATABASE_URI
        from back.extensions import db
        from flask import Flask
        
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
            print("✅ 数据库连接成功！")
            return True
            
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def create_tables():
    """创建数据库表结构"""
    print("=== 创建数据库表结构 ===")
    
    try:
        from back.config.settings import DATABASE_URI
        from back.extensions import db
        from flask import Flask
        
        # 导入所有模型
        from back.models.user import User
        from back.models.caregiver import Caregiver
        from back.models.service import ServiceType
        from back.models.business import JobData, AnalysisResult, Appointment, Employment, Message
        
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            # 获取所有模型
            UserModel = User.get_model(db)
            CaregiverModel = Caregiver.get_model(db)
            ServiceTypeModel = ServiceType.get_model(db)
            JobDataModel = JobData.get_model(db)
            AnalysisResultModel = AnalysisResult.get_model(db)
            AppointmentModel = Appointment.get_model(db)
            EmploymentModel = Employment.get_model(db)
            MessageModel = Message.get_model(db)
            
            # 创建所有表
            db.create_all()
            print("✅ 数据库表创建成功！")
            
            # 显示创建的表
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✅ 已创建 {len(tables)} 个表:")
            for table in tables:
                print(f"   - {table}")
            
            return True
            
    except Exception as e:
        print(f"❌ 创建表失败: {e}")
        return False

def backup_data():
    """备份数据库数据"""
    print("=== 备份数据库数据 ===")
    
    try:
        from back.config.settings import DATABASE_URI
        from back.extensions import db
        from flask import Flask
        
        # 导入所有模型
        from back.models.user import User
        from back.models.caregiver import Caregiver
        from back.models.service import ServiceType
        from back.models.business import JobData, AnalysisResult, Appointment, Employment, Message
        
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            # 获取所有模型
            UserModel = User.get_model(db)
            CaregiverModel = Caregiver.get_model(db)
            ServiceTypeModel = ServiceType.get_model(db)
            JobDataModel = JobData.get_model(db)
            AnalysisResultModel = AnalysisResult.get_model(db)
            AppointmentModel = Appointment.get_model(db)
            EmploymentModel = Employment.get_model(db)
            MessageModel = Message.get_model(db)
            
            # 备份数据
            backup_data = {}
            
            # 备份各个表的数据
            tables = [
                ('user', UserModel),
                ('caregiver', CaregiverModel),
                ('service_type', ServiceTypeModel),
                ('job_data', JobDataModel),
                ('analysis_result', AnalysisResultModel),
                ('appointment', AppointmentModel),
                ('employment', EmploymentModel),
                ('message', MessageModel)
            ]
            
            for table_name, model in tables:
                try:
                    records = model.query.all()
                    backup_data[table_name] = []
                    for record in records:
                        # 转换为字典，处理日期时间
                        record_dict = {}
                        for column in model.__table__.columns:
                            value = getattr(record, column.name)
                            if hasattr(value, 'isoformat'):  # 处理日期时间
                                value = value.isoformat()
                            record_dict[column.name] = value
                        backup_data[table_name].append(record_dict)
                    print(f"✅ {table_name}: {len(backup_data[table_name])} 条记录")
                except Exception as e:
                    print(f"⚠️  {table_name}: 备份失败 - {e}")
                    backup_data[table_name] = []
            
            # 保存备份文件
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"mysql_backup_{timestamp}.json"
            backup_path = os.path.join(os.path.dirname(__file__), backup_filename)
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 备份完成: {backup_filename}")
            return backup_path
            
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return None

def check_status():
    """检查数据库状态"""
    print("=== 检查数据库状态 ===")
    
    try:
        from back.config.settings import DATABASE_URI
        from back.extensions import db
        from flask import Flask
        
        # 导入所有模型
        from back.models.user import User
        from back.models.caregiver import Caregiver
        from back.models.service import ServiceType
        from back.models.business import JobData, AnalysisResult, Appointment, Employment, Message
        
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            # 获取所有模型
            UserModel = User.get_model(db)
            CaregiverModel = Caregiver.get_model(db)
            ServiceTypeModel = ServiceType.get_model(db)
            JobDataModel = JobData.get_model(db)
            AnalysisResultModel = AnalysisResult.get_model(db)
            AppointmentModel = Appointment.get_model(db)
            EmploymentModel = Employment.get_model(db)
            MessageModel = Message.get_model(db)
            
            # 检查各个表的状态
            tables = [
                ('user', UserModel),
                ('caregiver', CaregiverModel),
                ('service_type', ServiceTypeModel),
                ('job_data', JobDataModel),
                ('analysis_result', AnalysisResultModel),
                ('appointment', AppointmentModel),
                ('employment', EmploymentModel),
                ('message', MessageModel)
            ]
            
            print("📊 数据库状态:")
            total_records = 0
            for table_name, model in tables:
                try:
                    count = model.query.count()
                    print(f"   - {table_name}: {count} 条记录")
                    total_records += count
                except Exception as e:
                    print(f"   - {table_name}: 查询失败 - {e}")
            
            print(f"\n📈 总计: {total_records} 条记录")
            return True
            
    except Exception as e:
        print(f"❌ 状态检查失败: {e}")
        return False

def reset_database():
    """重置数据库（清空所有数据）"""
    print("=== 重置数据库 ===")
    print("⚠️  警告：此操作将清空所有数据！")
    
    confirm = input("确认要清空所有数据吗？(输入 'yes' 确认): ")
    if confirm.lower() != 'yes':
        print("❌ 操作已取消")
        return False
    
    try:
        from back.config.settings import DATABASE_URI
        from back.extensions import db
        from flask import Flask
        
        # 导入所有模型
        from back.models.user import User
        from back.models.caregiver import Caregiver
        from back.models.service import ServiceType
        from back.models.business import JobData, AnalysisResult, Appointment, Employment, Message
        
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            # 获取所有模型
            UserModel = User.get_model(db)
            CaregiverModel = Caregiver.get_model(db)
            ServiceTypeModel = ServiceType.get_model(db)
            JobDataModel = JobData.get_model(db)
            AnalysisResultModel = AnalysisResult.get_model(db)
            AppointmentModel = Appointment.get_model(db)
            EmploymentModel = Employment.get_model(db)
            MessageModel = Message.get_model(db)
            
            # 清空所有表
            tables = [
                ('user', UserModel),
                ('caregiver', CaregiverModel),
                ('service_type', ServiceTypeModel),
                ('job_data', JobDataModel),
                ('analysis_result', AnalysisResultModel),
                ('appointment', AppointmentModel),
                ('employment', EmploymentModel),
                ('message', MessageModel)
            ]
            
            for table_name, model in tables:
                try:
                    count = model.query.count()
                    model.query.delete()
                    print(f"✅ {table_name}: 清空了 {count} 条记录")
                except Exception as e:
                    print(f"❌ {table_name}: 清空失败 - {e}")
            
            db.session.commit()
            print("✅ 数据库重置完成！")
            return True
            
    except Exception as e:
        print(f"❌ 重置失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='护工资源管理系统数据库管理工具')
    parser.add_argument('action', choices=['test', 'create', 'backup', 'status', 'reset'], 
                       help='要执行的操作')
    
    args = parser.parse_args()
    
    print("🚀 护工资源管理系统 - 数据库管理工具")
    print("=" * 50)
    
    if args.action == 'test':
        test_connection()
    elif args.action == 'create':
        create_tables()
    elif args.action == 'backup':
        backup_data()
    elif args.action == 'status':
        check_status()
    elif args.action == 'reset':
        reset_database()
    else:
        print("❌ 未知操作")
        parser.print_help()

if __name__ == "__main__":
    main()
