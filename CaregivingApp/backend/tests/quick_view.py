#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速查看数据库内容的简单脚本
"""

import sqlite3
import sys

def quick_view_db(db_path="caregiving.db"):
    """快速查看数据库内容"""
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"🏥 数据库: {db_path}")
        print("=" * 60)
        
        # 1. 查看所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📋 数据库中的表 ({len(tables)}个):")
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table[0]}")
        
        print("\n" + "=" * 60)
        
        # 2. 查看每个表的基本信息
        for table_name in [t[0] for t in tables]:
            print(f"\n📊 表: {table_name}")
            print("-" * 40)
            
            # 查看表结构
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"字段数: {len(columns)}")
            
            # 查看数据条数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"数据条数: {count}")
            
            # 显示前3条数据
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                print("前3条数据:")
                for i, row in enumerate(rows, 1):
                    print(f"  {i}. {row}")
            else:
                print("暂无数据")
        
        conn.close()
        print(f"\n✅ 数据库查看完成")
        
    except FileNotFoundError:
        print(f"❌ 数据库文件 '{db_path}' 不存在")
        print("请先启动Flask应用创建数据库")
    except Exception as e:
        print(f"❌ 查看数据库失败: {e}")

def add_sample_user(db_path="caregiving.db"):
    """添加示例用户"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查user表是否有name和phone字段
        cursor.execute("PRAGMA table_info(user)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'name' not in columns or 'phone' not in columns:
            print("❌ user表缺少name或phone字段")
            print("请先重启Flask应用创建正确的表结构")
            return
        
        # 添加示例用户
        cursor.execute("""
            INSERT INTO user (name, phone, email, password_hash, is_approved, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, ('测试用户', '13800138000', 'test@example.com', 'hashed_password', 0))
        
        conn.commit()
        print("✅ 成功添加示例用户: 测试用户 (13800138000)")
        conn.close()
        
    except Exception as e:
        print(f"❌ 添加示例用户失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "add_user":
        add_sample_user()
    else:
        quick_view_db() 