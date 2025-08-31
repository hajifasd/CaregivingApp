import sqlite3
import hashlib
import os
from datetime import datetime

# 数据库路径
db_path = '../caregiving.db'

def create_test_user():
    """Create a test user"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查用户是否已存在
    cursor.execute("SELECT id FROM user WHERE phone = ?", ("13800138000",))
    if cursor.fetchone():
        print("Test user already exists")
        return True
    
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
    print("✓ Test user created successfully!")
    return True

def create_test_caregiver():
    """Create a test caregiver"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查护工是否已存在
    cursor.execute("SELECT id FROM caregiver WHERE phone = ?", ("13800138001",))
    if cursor.fetchone():
        print("Test caregiver already exists")
        return True
    
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
    print("✓ Test caregiver created successfully!")
    return True

def create_service_types():
    """Create service types if they don't exist"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    service_types = [
        ("老年护理", "为老年人提供日常生活照料和护理服务"),
        ("母婴护理", "为产妇和新生儿提供专业护理服务"),
        ("医疗护理", "为患者提供医疗辅助和护理服务"),
        ("康复护理", "为康复期患者提供专业康复护理"),
        ("育儿嫂", "为婴幼儿提供专业照料服务")
    ]
    
    for name, description in service_types:
        cursor.execute("SELECT id FROM service_type WHERE name = ?", (name,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO service_type (name, description)
                VALUES (?, ?)
            """, (name, description))
            print(f"✓ Service type '{name}' created")
    
    conn.commit()
    conn.close()

def main():
    """Create all test accounts"""
    print("Creating test accounts...")
    print("=" * 50)
    
    try:
        # 创建测试用户
        create_test_user()
        
        # 创建测试护工
        create_test_caregiver()
        
        # 创建服务类型
        create_service_types()
        
        print("=" * 50)
        print("All test accounts created successfully!")
        print("\nTest Account Information:")
        print("-" * 30)
        print("User Account:")
        print("  Phone: 13800138000")
        print("  Password: 123456")
        print("  Status: Approved")
        print()
        print("Caregiver Account:")
        print("  Phone: 13800138001")
        print("  Password: 123456")
        print("  Status: Approved")
        print()
        print("Admin Account:")
        print("  Username: admin")
        print("  Password: admin123")
        print()
        print("You can now test the login functionality!")
        
    except Exception as e:
        print(f"Error creating test accounts: {e}")

if __name__ == "__main__":
    main() 