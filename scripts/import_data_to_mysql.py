#!/usr/bin/env python3
"""
护工资源管理系统 - MySQL 数据导入脚本
====================================

功能说明：
- 将备份的 JSON 数据导入到 MySQL 数据库
- 支持所有数据表的批量导入
- 自动处理数据类型转换
- 验证导入结果

使用步骤：
1. 确保 MySQL 数据库已创建表结构
2. 确保有有效的 JSON 备份文件
3. 运行此脚本：python import_data_to_mysql.py

依赖要求：
- MySQL 数据库已连接
- 表结构已创建
- JSON 备份文件存在
- Flask-SQLAlchemy 已安装

注意事项：
- 导入前会清空目标表数据
- 建议在导入前备份 MySQL 数据
- 确保 JSON 文件格式正确

作者：护工资源管理系统开发团队
创建时间：2024年
版本：1.0
"""

import os
import sys
import json
import glob
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def find_backup_file():
    """查找最新的备份文件"""
    print("=== 查找备份文件 ===")
    
    # 查找所有备份文件
    backup_files = glob.glob("sqlite_backup_*.json")
    if not backup_files:
        print("❌ 未找到备份文件")
        return None
    
    # 按修改时间排序，获取最新的
    latest_file = max(backup_files, key=os.path.getmtime)
    print(f"📁 使用备份文件: {latest_file}")
    return latest_file

def load_backup_data(backup_file):
    """加载备份数据"""
    print(f"=== 加载备份数据: {backup_file} ===")
    
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("✅ 成功加载备份数据")
        for table_name, records in data.items():
            print(f"   - {table_name}: {len(records)} 条记录")
        
        return data
        
    except Exception as e:
        print(f"❌ 加载备份数据失败: {e}")
        return None

def import_data_to_mysql(backup_data):
    """将数据导入到 MySQL"""
    print("\n=== 导入数据到 MySQL ===")
    
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
            
            # 定义导入映射
            import_mapping = {
                'user': UserModel,
                'caregiver': CaregiverModel,
                'service_type': ServiceTypeModel,
                'job_data': JobDataModel,
                'analysis_result': AnalysisResultModel,
                'appointment': AppointmentModel,
                'employment': EmploymentModel,
                'message': MessageModel
            }
            
            total_imported = 0
            
            for table_name, model in import_mapping.items():
                print(f"📥 导入表 {table_name}...")
                
                if table_name not in backup_data:
                    print(f"⚠️  跳过表 {table_name}（无备份数据）")
                    continue
                
                try:
                    # 清空现有数据
                    model.query.delete()
                    
                    # 导入新数据
                    records = backup_data[table_name]
                    imported_count = 0
                    
                    for record_data in records:
                        try:
                            # 处理日期时间字段
                            for key, value in record_data.items():
                                if isinstance(value, str) and 'T' in value:
                                    try:
                                        record_data[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                                    except:
                                        pass
                            
                            # 创建记录
                            record = model(**record_data)
                            db.session.add(record)
                            imported_count += 1
                            
                        except Exception as e:
                            print(f"⚠️  跳过记录: {e}")
                            continue
                    
                    # 提交事务
                    db.session.commit()
                    print(f"✅ {table_name}: 成功导入 {imported_count} 条记录")
                    total_imported += imported_count
                    
                except Exception as e:
                    print(f"❌ {table_name}: 导入失败 - {e}")
                    db.session.rollback()
                    continue
            
            # 处理特殊表
            if 'caregiver_service' in backup_data:
                print("⚠️  跳过表 caregiver_service（无对应模型）")
            
            print(f"\n🎉 数据导入完成！总共导入 {total_imported} 条记录")
            return True
            
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def verify_import():
    """验证导入结果"""
    print("\n=== 验证导入数据 ===")
    
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
            
            # 验证各个表
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
            
            print("📊 数据统计:")
            for table_name, model in tables:
                try:
                    count = model.query.count()
                    print(f"   - {table_name}: {count} 条记录")
                except Exception as e:
                    print(f"   - {table_name}: 查询失败 - {e}")
            
            return True
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def main():
    """主函数 - 执行完整的数据导入流程"""
    print("🚀 开始数据导入到 MySQL")
    print("=" * 40)
    
    # 1. 查找备份文件
    backup_file = find_backup_file()
    if not backup_file:
        return
    
    # 2. 加载备份数据
    backup_data = load_backup_data(backup_file)
    if not backup_data:
        return
    
    # 3. 导入数据到 MySQL
    if not import_data_to_mysql(backup_data):
        return
    
    # 4. 验证导入结果
    verify_import()
    
    print("\n" + "=" * 40)
    print("✅ 数据导入完成！")
    print("📋 下一步:")
    print("1. 启动应用测试功能")
    print("2. 验证数据完整性")
    print("3. 进行功能测试")

if __name__ == "__main__":
    main()
