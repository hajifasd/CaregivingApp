#!/usr/bin/env python3
"""
数据库状态检查脚本
快速检查数据库连接和表状态
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'back'))

try:
    from back.config.settings import DATABASE_URI, MYSQL_HOST, MYSQL_PORT, MYSQL_USERNAME, MYSQL_DATABASE
    from back.extensions import db
    from flask import Flask
    from sqlalchemy import text
    
    print("🔍 检查数据库连接状态...")
    
    # 创建Flask应用实例
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化数据库
    db.init_app(app)
    
    with app.app_context():
        try:
            with db.engine.connect() as connection:
                # 测试连接
                result = connection.execute(text("SELECT 1"))
                
                # 获取表数量
                result = connection.execute(text("SHOW TABLES"))
                tables = result.fetchall()
                
                # 获取总记录数
                total_records = 0
                for table in tables:
                    table_name = table[0]
                    result = connection.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.fetchone()[0]
                    total_records += count
                
                print("✅ 数据库连接正常")
                print(f"📍 主机: {MYSQL_HOST}:{MYSQL_PORT}")
                print(f"🗄️ 数据库: {MYSQL_DATABASE}")
                print(f"📊 表数量: {len(tables)}")
                print(f"📈 总记录数: {total_records}")
                print("🎉 数据库已成功连接!")
                
        except Exception as e:
            print(f"❌ 数据库连接失败: {str(e)}")
            
except Exception as e:
    print(f"❌ 检查失败: {str(e)}")
