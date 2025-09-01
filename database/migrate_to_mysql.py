#!/usr/bin/env python3
"""
护工资源管理系统 - SQLite 到 MySQL 数据库迁移脚本
================================================

功能说明：
- 将现有的 SQLite 数据库迁移到 MySQL 数据库
- 备份 SQLite 数据到 JSON 文件
- 创建 MySQL 数据库和表结构
- 导入数据到 MySQL
- 验证迁移结果

使用步骤：
1. 确保 MySQL 服务正在运行
2. 配置 .env 文件中的 MySQL 连接信息
3. 运行此脚本：python migrate_to_mysql.py

依赖要求：
- MySQL 服务运行中
- PyMySQL 包已安装
- Flask-SQLAlchemy 已安装
- 有效的 MySQL root 密码

作者：护工资源管理系统开发团队
创建时间：2024年
版本：1.0
"""

import os
import sys
import json
import datetime
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def backup_sqlite_data():
    """备份 SQLite 数据库数据到 JSON 文件"""
    print("=== 备份 SQLite 数据 ===")
    
    try:
        from back.config.settings import ROOT_DIR
        from back.extensions import db
        from flask import Flask
        
        # 临时使用 SQLite 配置
        sqlite_db_path = os.path.join(ROOT_DIR, "database", "caregiving.db")
        sqlite_uri = f'sqlite:///{sqlite_db_path}'
        
        # 创建临时应用
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            # 导入所有模型
            from back.models.user import User
            from back.models.caregiver import Caregiver
            from back.models.service import ServiceType
            from back.models.business import JobData, AnalysisResult, Appointment, Employment, Message
            
            # 获取模型类
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
            backup_filename = f"sqlite_backup_{timestamp}.json"
            backup_path = os.path.join(ROOT_DIR, backup_filename)
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 备份完成: {backup_filename}")
            return backup_path
            
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return None

def test_mysql_connection():
    """测试 MySQL 数据库连接"""
    print("\n=== 测试 MySQL 连接 ===")
    
    try:
        from back.config.settings import DATABASE_URI
        from back.extensions import db
        from flask import Flask
        
        # 创建应用
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            # 测试连接
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
            print("✅ MySQL 连接成功！")
            return True
            
    except Exception as e:
        print(f"❌ MySQL 连接失败: {e}")
        return False

def create_mysql_tables():
    """创建 MySQL 表结构"""
    print("\n=== 创建 MySQL 表结构 ===")
    
    try:
        from back.config.settings import DATABASE_URI
        from back.extensions import db
        from flask import Flask
        
        # 导入所有模型
        from back.models.user import User
        from back.models.caregiver import Caregiver
        from back.models.service import ServiceType
        from back.models.business import JobData, AnalysisResult, Appointment, Employment, Message
        
        # 创建应用
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
            print("✅ MySQL 表创建成功！")
            
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

def main():
    """主函数 - 执行完整的迁移流程"""
    print("🚀 SQLite 到 MySQL 数据库迁移")
    print("=" * 50)
    
    # 1. 备份 SQLite 数据
    backup_path = backup_sqlite_data()
    if not backup_path:
        print("❌ 备份失败，终止迁移")
        return
    
    # 2. 测试 MySQL 连接
    if not test_mysql_connection():
        print("❌ MySQL 连接失败，请检查配置")
        return
    
    # 3. 创建 MySQL 表结构
    if not create_mysql_tables():
        print("❌ 创建表失败，终止迁移")
        return
    
    print("\n🎉 迁移准备完成！")
    print("📋 下一步:")
    print("1. 运行: python import_data_to_mysql.py")
    print("2. 验证数据迁移")
    print("3. 启动应用测试")

if __name__ == "__main__":
    main()
