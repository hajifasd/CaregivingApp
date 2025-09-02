# -*- coding: utf-8 -*-
"""
简单的数据库表创建脚本
"""

import os
import sys

# 添加back目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'back'))

def create_tables():
    """创建数据库表"""
    print("Creating database tables...")
    
    try:
        # 导入Flask应用和数据库
        from app import app, db
        
        with app.app_context():
            # 创建所有表
            print("Creating tables...")
            db.create_all()
            print("Tables created successfully!")
            
            # 检查表
            print("Checking tables...")
            result = db.session.execute("SHOW TABLES")
            tables = [row[0] for row in result]
            print("Tables: " + str(tables))
            
    except Exception as e:
        print("Error: " + str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_tables() 