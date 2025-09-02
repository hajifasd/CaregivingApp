# -*- coding: utf-8 -*-
import os
import sys

# 添加back目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'back'))

try:
    from config.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE, DATABASE_URI
    
    print("Configuration loaded successfully")
    print("MySQL Host:", MYSQL_HOST)
    print("MySQL Port:", MYSQL_PORT)
    print("MySQL Username:", MYSQL_USERNAME)
    print("MySQL Database:", MYSQL_DATABASE)
    print("Database URI:", DATABASE_URI)
    
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
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print("MySQL Version:", version[0])
        
        connection.close()
        
    except Exception as e:
        print("Database connection failed:", str(e))
        
except Exception as e:
    print("Test failed:", str(e)) 