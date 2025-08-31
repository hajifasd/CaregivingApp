import sqlite3
import hashlib
import os
from datetime import datetime

# 数据库路径
db_path = '../caregiving.db'

def create_test_caregiver():
    """Create a test caregiver directly in the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查护工是否已存在
    cursor.execute("SELECT id FROM caregiver WHERE phone = ?", ("13800138001",))
    if cursor.fetchone():
        print("Test caregiver already exists")
        conn.close()
        return
    
    # 创建密码哈希
    password = "123456"
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # 插入测试护工
    cursor.execute("""
        INSERT INTO caregiver (name, phone, id_file, cert_file, password_hash, is_approved, created_at, approved_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "Test Caregiver",
        "13800138001",
        "test_id_file.jpg",
        "test_cert_file.jpg",
        password_hash,
        True,  # 设置为已审核
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()
    print("Test caregiver created successfully!")
    print("Account: 13800138001")
    print("Password: 123456")

if __name__ == "__main__":
    create_test_caregiver() 