# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
配置测试脚本
====================================

用于测试数据库配置是否正确加载
"""

import os
import sys

# 添加back目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'back'))

def test_config():
    """测试配置加载"""
    print("Testing configuration loading...")
    print("=" * 50)
    
    try:
        # 导入配置
        from config.settings import (
            MYSQL_HOST, MYSQL_PORT, MYSQL_USERNAME, 
            MYSQL_PASSWORD, MYSQL_DATABASE, DATABASE_URI
        )
        
        print("Configuration imported successfully")
        print(f"MySQL Host: {MYSQL_HOST}")
        print(f"MySQL Port: {MYSQL_PORT}")
        print(f"MySQL Username: {MYSQL_USERNAME}")
        print(f"MySQL Database: {MYSQL_DATABASE}")
        print(f"Database URI: {DATABASE_URI}")
        
        # 测试数据库连接
        print("\nTesting database connection...")
        import pymysql
        
        try:
            connection = pymysql.connect(
                host=MYSQL_HOST,
                port=int(MYSQL_PORT),
                user=MYSQL_USERNAME,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
                charset='utf8mb4'
            )
            
            print("Database connection successful!")
            
            # 测试查询
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                print(f"MySQL Version: {version[0]}")
            
            connection.close()
            
        except Exception as e:
            print(f"Database connection failed: {str(e)}")
            print("\nTroubleshooting suggestions:")
            print("1. Check if MySQL service is running")
            print("2. Check if port number is correct")
            print("3. Check if username and password are correct")
            print("4. Check if database exists")
            
    except ImportError as e:
        print(f"Configuration import failed: {str(e)}")
    except Exception as e:
        print(f"Test failed: {str(e)}")

def test_local_config():
    """测试本地配置文件"""
    print("\nChecking local configuration file...")
    
    local_config_path = "back/config/config_local.py"
    if os.path.exists(local_config_path):
        print(f"Local config file exists: {local_config_path}")
        
        # 读取配置文件内容
        with open(local_config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "MYSQL_PORT = \"3308\"" in content:
            print("Port configuration is correct (3308)")
        else:
            print("Port configuration is incorrect")
            
    else:
        print(f"Local config file does not exist: {local_config_path}")

if __name__ == "__main__":
    test_local_config()
    test_config() 