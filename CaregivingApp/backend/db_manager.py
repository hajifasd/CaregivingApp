#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理工具
用于查看、添加、修改和删除数据库中的信息
"""

import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="caregiving.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"✅ 成功连接到数据库: {self.db_path}")
            return True
        except Exception as e:
            print(f"❌ 连接数据库失败: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.conn:
            self.conn.close()
            print("✅ 数据库连接已关闭")
    
    def show_tables(self):
        """显示所有表"""
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()
            print("\n📋 数据库中的表:")
            for i, table in enumerate(tables, 1):
                print(f"  {i}. {table[0]}")
            return tables
        except Exception as e:
            print(f"❌ 获取表列表失败: {e}")
            return []
    
    def show_table_structure(self, table_name):
        """显示表结构"""
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = self.cursor.fetchall()
            print(f"\n🏗️ 表 '{table_name}' 的结构:")
            print(f"{'序号':<4} {'字段名':<20} {'类型':<15} {'非空':<6} {'默认值':<10} {'主键':<6}")
            print("-" * 70)
            for col in columns:
                print(f"{col[0]:<4} {col[1]:<20} {col[2]:<15} {col[3]:<6} {col[4]:<10} {col[5]:<6}")
            return columns
        except Exception as e:
            print(f"❌ 获取表结构失败: {e}")
            return []
    
    def show_table_data(self, table_name, limit=10):
        """显示表数据"""
        try:
            # 先获取列名
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in self.cursor.fetchall()]
            
            # 查询数据
            self.cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
            rows = self.cursor.fetchall()
            
            print(f"\n📊 表 '{table_name}' 的数据 (显示前{limit}条):")
            if columns:
                print("列名:", " | ".join(columns))
                print("-" * (len(" | ".join(columns)) + 10))
            
            for i, row in enumerate(rows, 1):
                print(f"{i}. {row}")
            
            return rows
        except Exception as e:
            print(f"❌ 获取表数据失败: {e}")
            return []
    
    def add_user(self, name, phone, password, email=None):
        """添加用户"""
        try:
            if not email:
                email = f"user_{phone}_{int(datetime.now().timestamp())}@temp.com"
            
            # 检查手机号是否已存在
            self.cursor.execute("SELECT id FROM user WHERE phone = ?", (phone,))
            if self.cursor.fetchone():
                print(f"❌ 手机号 {phone} 已存在")
                return False
            
            # 插入新用户
            self.cursor.execute("""
                INSERT INTO user (name, phone, email, password_hash, is_approved, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, phone, email, f"hashed_{password}", False, datetime.now()))
            
            self.conn.commit()
            print(f"✅ 成功添加用户: {name} ({phone})")
            return True
        except Exception as e:
            print(f"❌ 添加用户失败: {e}")
            self.conn.rollback()
            return False
    
    def add_caregiver(self, name, phone, password, id_file="temp_id.jpg", cert_file="temp_cert.jpg"):
        """添加护工"""
        try:
            # 检查手机号是否已存在
            self.cursor.execute("SELECT id FROM caregiver WHERE phone = ?", (phone,))
            if self.cursor.fetchone():
                print(f"❌ 手机号 {phone} 已存在")
                return False
            
            # 插入新护工
            self.cursor.execute("""
                INSERT INTO caregiver (name, phone, password_hash, id_file, cert_file, is_approved, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, phone, f"hashed_{password}", id_file, cert_file, False, datetime.now()))
            
            self.conn.commit()
            print(f"✅ 成功添加护工: {name} ({phone})")
            return True
        except Exception as e:
            print(f"❌ 添加护工失败: {e}")
            self.conn.rollback()
            return False
    
    def search_user(self, keyword):
        """搜索用户"""
        try:
            self.cursor.execute("""
                SELECT id, name, phone, email, is_approved, created_at 
                FROM user 
                WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
            
            users = self.cursor.fetchall()
            if users:
                print(f"\n🔍 搜索关键词 '{keyword}' 的结果:")
                print("ID | 姓名 | 手机号 | 邮箱 | 审核状态 | 创建时间")
                print("-" * 80)
                for user in users:
                    status = "✅ 已审核" if user[4] else "⏳ 待审核"
                    print(f"{user[0]} | {user[1] or 'N/A'} | {user[2] or 'N/A'} | {user[3]} | {status} | {user[5]}")
            else:
                print(f"🔍 未找到包含 '{keyword}' 的用户")
            
            return users
        except Exception as e:
            print(f"❌ 搜索用户失败: {e}")
            return []
    
    def update_user_approval(self, user_id, approved=True):
        """更新用户审核状态"""
        try:
            self.cursor.execute("""
                UPDATE user 
                SET is_approved = ?, approved_at = ? 
                WHERE id = ?
            """, (approved, datetime.now() if approved else None, user_id))
            
            if self.cursor.rowcount > 0:
                self.conn.commit()
                status = "审核通过" if approved else "取消审核"
                print(f"✅ 用户 {user_id} {status}")
                return True
            else:
                print(f"❌ 用户 {user_id} 不存在")
                return False
        except Exception as e:
            print(f"❌ 更新用户状态失败: {e}")
            self.conn.rollback()
            return False

def main():
    """主函数 - 交互式数据库管理"""
    print("🏥 护理助手数据库管理工具")
    print("=" * 50)
    
    # 检查数据库文件是否存在
    if not os.path.exists("caregiving.db"):
        print("❌ 数据库文件 'caregiving.db' 不存在")
        print("请先启动Flask应用创建数据库")
        return
    
    db = DatabaseManager()
    if not db.connect():
        return
    
    try:
        while True:
            print("\n" + "=" * 50)
            print("请选择操作:")
            print("1. 查看所有表")
            print("2. 查看表结构")
            print("3. 查看表数据")
            print("4. 添加用户")
            print("5. 添加护工")
            print("6. 搜索用户")
            print("7. 审核用户")
            print("0. 退出")
            
            choice = input("\n请输入选项 (0-7): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                db.show_tables()
            elif choice == "2":
                table_name = input("请输入表名: ").strip()
                if table_name:
                    db.show_table_structure(table_name)
            elif choice == "3":
                table_name = input("请输入表名: ").strip()
                limit = input("请输入显示条数 (默认10): ").strip()
                limit = int(limit) if limit.isdigit() else 10
                if table_name:
                    db.show_table_data(table_name, limit)
            elif choice == "4":
                name = input("请输入姓名: ").strip()
                phone = input("请输入手机号: ").strip()
                password = input("请输入密码: ").strip()
                email = input("请输入邮箱 (可选): ").strip()
                if name and phone and password:
                    db.add_user(name, phone, password, email if email else None)
                else:
                    print("❌ 姓名、手机号和密码不能为空")
            elif choice == "5":
                name = input("请输入姓名: ").strip()
                phone = input("请输入手机号: ").strip()
                password = input("请输入密码: ").strip()
                if name and phone and password:
                    db.add_caregiver(name, phone, password)
                else:
                    print("❌ 姓名、手机号和密码不能为空")
            elif choice == "6":
                keyword = input("请输入搜索关键词: ").strip()
                if keyword:
                    db.search_user(keyword)
                else:
                    print("❌ 搜索关键词不能为空")
            elif choice == "7":
                user_id = input("请输入用户ID: ").strip()
                if user_id.isdigit():
                    action = input("审核通过? (y/n): ").strip().lower()
                    approved = action in ['y', 'yes', '是']
                    db.update_user_approval(int(user_id), approved)
                else:
                    print("❌ 请输入有效的用户ID")
            else:
                print("❌ 无效选项，请重新选择")
    
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
    finally:
        db.disconnect()
        print("\n👋 感谢使用数据库管理工具！")

if __name__ == "__main__":
    main() 