# -*- coding: utf-8 -*-
"""
数据库初始化脚本
====================================

用于检查和初始化数据库表结构
"""

import os
import sys

# 添加back目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'back'))

def init_database():
    """初始化数据库"""
    print("Database initialization script")
    print("=" * 50)
    
    try:
        # 导入配置
        from config.settings import DATABASE_URI
        print(f"Database URI: {DATABASE_URI}")
        
        # 导入Flask应用和数据库
        from app import app, db
        
        with app.app_context():
            # 检查现有表
            print("\nChecking existing tables...")
            try:
                result = db.session.execute("SHOW TABLES")
                tables = [row[0] for row in result]
                print(f"Existing tables: {tables}")
            except Exception as e:
                print(f"Error checking tables: {e}")
                tables = []
            
            # 创建所有表
            print("\nCreating database tables...")
            db.create_all()
            print("Database tables created successfully!")
            
            # 再次检查表
            print("\nVerifying tables...")
            result = db.session.execute("SHOW TABLES")
            tables = [row[0] for row in result]
            print(f"Tables after creation: {tables}")
            
            # 检查user表结构
            if 'user' in tables:
                print("\nChecking user table structure...")
                result = db.session.execute("DESCRIBE user")
                columns = [row[0] for row in result]
                print(f"User table columns: {columns}")
            
            print("\nDatabase initialization completed!")
            
    except Exception as e:
        print(f"Database initialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_database() 