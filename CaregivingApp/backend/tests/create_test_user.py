import sqlite3
import hashlib
import os
from datetime import datetime

# 数据库路径
db_path = 'caregiving.db'

def create_test_user():
    """Create a test user directly in the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查用户是否已存在
    cursor.execute("SELECT id FROM user WHERE phone = ?", ("13800138000",))
    if cursor.fetchone():
        print("Test user already exists")
        conn.close()
        return
    
    # 创建密码哈希
    password = "123456"
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # 插入测试用户
    cursor.execute("""
        INSERT INTO user (email, password_hash, name, phone, is_approved, created_at, approved_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "test_user_13800138000@temp.com",
        password_hash,
        "Test User",
        "13800138000",
        True,  # 设置为已审核
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()
    print("Test user created successfully!")
    print("Account: 13800138000")
    print("Password: 123456")

if __name__ == "__main__":
    create_test_user() 