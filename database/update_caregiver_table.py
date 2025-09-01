"""
护工资源管理系统 - 护工表结构更新脚本
====================================

更新护工表结构，移除身份证文件相关字段，添加新的字段
"""

import pymysql
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def update_caregiver_table():
    """更新护工表结构"""
    try:
        # 数据库连接配置
        host = os.getenv('MYSQL_HOST', 'localhost')
        port = int(os.getenv('MYSQL_PORT', 3306))
        user = os.getenv('MYSQL_USERNAME', 'root')
        password = os.getenv('MYSQL_PASSWORD', '20040924')
        database = os.getenv('MYSQL_DATABASE', 'caregiving_db')
        
        # 连接数据库
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        print("开始更新护工表结构...")
        
        # 检查表是否存在
        cursor.execute("SHOW TABLES LIKE 'caregiver'")
        if not cursor.fetchone():
            print("护工表不存在，创建新表...")
            create_caregiver_table(cursor)
        else:
            print("护工表已存在，更新表结构...")
            update_existing_table(cursor)
        
        # 提交更改
        connection.commit()
        print("护工表结构更新完成！")
        
        # 显示更新后的表结构
        cursor.execute("DESCRIBE caregiver")
        columns = cursor.fetchall()
        print("\n更新后的护工表结构:")
        for column in columns:
            print(f"  {column[0]} - {column[1]} - {column[2]} - {column[3]} - {column[4]} - {column[5]}")
        
    except Exception as e:
        print(f"更新护工表结构失败: {e}")
        if 'connection' in locals():
            connection.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def create_caregiver_table(cursor):
    """创建新的护工表"""
    create_table_sql = """
    CREATE TABLE caregiver (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        phone VARCHAR(20) UNIQUE NOT NULL,
        password_hash VARCHAR(256) NOT NULL,
        is_approved BOOLEAN DEFAULT FALSE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        approved_at DATETIME NULL,
        gender VARCHAR(10) NULL,
        age INT NULL,
        avatar_url VARCHAR(200) NULL,
        qualification VARCHAR(100) NULL,
        introduction TEXT NULL,
        experience_years INT NULL,
        hourly_rate FLOAT NULL,
        rating FLOAT DEFAULT 0,
        review_count INT DEFAULT 0,
        status VARCHAR(20) DEFAULT 'pending',
        available BOOLEAN DEFAULT TRUE,
        INDEX idx_phone (phone),
        INDEX idx_created_at (created_at),
        INDEX idx_approved_at (approved_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    cursor.execute(create_table_sql)
    print("新护工表创建成功")

def update_existing_table(cursor):
    """更新现有护工表结构"""
    try:
        # 检查并添加新字段
        new_columns = [
            ('gender', 'VARCHAR(10) NULL'),
            ('age', 'INT NULL'),
            ('avatar_url', 'VARCHAR(200) NULL'),
            ('qualification', 'VARCHAR(100) NULL'),
            ('introduction', 'TEXT NULL'),
            ('experience_years', 'INT NULL'),
            ('hourly_rate', 'FLOAT NULL'),
            ('rating', 'FLOAT DEFAULT 0'),
            ('review_count', 'INT DEFAULT 0'),
            ('status', 'VARCHAR(20) DEFAULT "pending"'),
            ('available', 'BOOLEAN DEFAULT TRUE')
        ]
        
        # 获取现有字段列表
        cursor.execute("SHOW COLUMNS FROM caregiver")
        existing_columns = [column[0] for column in cursor.fetchall()]
        
        # 添加缺失的字段
        for column_name, column_def in new_columns:
            if column_name not in existing_columns:
                print(f"添加字段: {column_name}")
                cursor.execute(f"ALTER TABLE caregiver ADD COLUMN {column_name} {column_def}")
        
        # 检查并移除旧字段
        old_columns = ['id_file', 'cert_file', 'id_card']
        for column_name in old_columns:
            if column_name in existing_columns:
                print(f"移除字段: {column_name}")
                cursor.execute(f"ALTER TABLE caregiver DROP COLUMN {column_name}")
        
        # 确保必要的索引存在
        indexes_to_add = [
            ('idx_phone', 'phone'),
            ('idx_created_at', 'created_at'),
            ('idx_approved_at', 'approved_at')
        ]
        
        cursor.execute("SHOW INDEX FROM caregiver")
        existing_indexes = [index[2] for index in cursor.fetchall()]
        
        for index_name, column_name in indexes_to_add:
            if index_name not in existing_indexes:
                print(f"添加索引: {index_name} on {column_name}")
                cursor.execute(f"CREATE INDEX {index_name} ON caregiver ({column_name})")
        
        print("表结构更新完成")
        
    except Exception as e:
        print(f"更新表结构时出错: {e}")
        raise

if __name__ == "__main__":
    print("护工资源管理系统 - 护工表结构更新")
    print("=" * 50)
    
    # 确认操作
    confirm = input("此操作将更新护工表结构，是否继续？(y/N): ")
    if confirm.lower() == 'y':
        update_caregiver_table()
    else:
        print("操作已取消")
