#!/usr/bin/env python3
"""
配置管理脚本
====================================

用于快速设置和管理数据库配置
"""

import os
import sys
import json
from pathlib import Path

def create_env_file():
    """创建 .env 文件"""
    env_content = """# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USERNAME=root
MYSQL_PASSWORD=your_password_here
MYSQL_DATABASE=caregiving_db

# 应用配置
APP_SECRET=your_app_secret_key_here
FLASK_SECRET_KEY=your_flask_secret_key_here

# 管理员配置
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
"""
    
    env_file = Path('.env')
    if env_file.exists():
        print("⚠️  .env 文件已存在，跳过创建")
        return
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    print("✅ 已创建 .env 文件")

def create_local_config():
    """创建本地配置文件"""
    config_content = '''"""
本地配置文件 - 个人数据库配置
====================================

此文件包含个人开发环境的数据库配置
请根据您的本地环境修改这些配置
注意：此文件不应该提交到版本控制系统
"""

# ==================== 数据库配置 ====================
# 请根据您的本地MySQL配置修改以下参数

# MySQL 主机地址
MYSQL_HOST = "localhost"

# MySQL 端口号
MYSQL_PORT = "3306"

# MySQL 用户名
MYSQL_USERNAME = "root"

# MySQL 密码
MYSQL_PASSWORD = "your_password_here"

# MySQL 数据库名
MYSQL_DATABASE = "caregiving_db"

# ==================== 应用配置 ====================
# 应用密钥（建议使用随机生成的密钥）
APP_SECRET = "your_app_secret_key_here"

# Flask 密钥
FLASK_SECRET_KEY = "your_flask_secret_key_here"

# ==================== 管理员配置 ====================
# 管理员用户名
ADMIN_USERNAME = "admin"

# 管理员密码
ADMIN_PASSWORD = "admin123"
'''
    
    config_file = Path('back/config/config_local.py')
    if config_file.exists():
        print("⚠️  本地配置文件已存在，跳过创建")
        return
    
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    print("✅ 已创建本地配置文件 back/config/config_local.py")

def interactive_config():
    """交互式配置"""
    print("\n🔧 交互式配置数据库参数")
    print("=" * 50)
    
    config = {}
    
    # 数据库配置
    config['MYSQL_HOST'] = input("MySQL 主机地址 (默认: localhost): ").strip() or "localhost"
    config['MYSQL_PORT'] = input("MySQL 端口号 (默认: 3306): ").strip() or "3306"
    config['MYSQL_USERNAME'] = input("MySQL 用户名 (默认: root): ").strip() or "root"
    config['MYSQL_PASSWORD'] = input("MySQL 密码: ").strip()
    config['MYSQL_DATABASE'] = input("MySQL 数据库名 (默认: caregiving_db): ").strip() or "caregiving_db"
    
    # 应用配置
    config['APP_SECRET'] = input("应用密钥 (默认: 随机生成): ").strip() or "caregiving-system-secret-key-2024"
    config['FLASK_SECRET_KEY'] = input("Flask 密钥 (默认: 随机生成): ").strip() or "your_unique_secret_key"
    
    # 管理员配置
    config['ADMIN_USERNAME'] = input("管理员用户名 (默认: admin): ").strip() or "admin"
    config['ADMIN_PASSWORD'] = input("管理员密码 (默认: admin123): ").strip() or "admin123"
    
    return config

def update_local_config(config):
    """更新本地配置文件"""
    config_content = f'''"""
本地配置文件 - 个人数据库配置
====================================

此文件包含个人开发环境的数据库配置
请根据您的本地环境修改这些配置
注意：此文件不应该提交到版本控制系统
"""

# ==================== 数据库配置 ====================
# 请根据您的本地MySQL配置修改以下参数

# MySQL 主机地址
MYSQL_HOST = "{config['MYSQL_HOST']}"

# MySQL 端口号
MYSQL_PORT = "{config['MYSQL_PORT']}"

# MySQL 用户名
MYSQL_USERNAME = "{config['MYSQL_USERNAME']}"

# MySQL 密码
MYSQL_PASSWORD = "{config['MYSQL_PASSWORD']}"

# MySQL 数据库名
MYSQL_DATABASE = "{config['MYSQL_DATABASE']}"

# ==================== 应用配置 ====================
# 应用密钥（建议使用随机生成的密钥）
APP_SECRET = "{config['APP_SECRET']}"

# Flask 密钥
FLASK_SECRET_KEY = "{config['FLASK_SECRET_KEY']}"

# ==================== 管理员配置 ====================
# 管理员用户名
ADMIN_USERNAME = "{config['ADMIN_USERNAME']}"

# 管理员密码
ADMIN_PASSWORD = "{config['ADMIN_PASSWORD']}"
'''
    
    config_file = Path('back/config/config_local.py')
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    print("✅ 已更新本地配置文件")

def create_gitignore_entries():
    """创建 .gitignore 条目"""
    gitignore_content = """
# 本地配置文件
back/config/config_local.py
.env
*.env

# 数据库文件
*.db
*.sqlite
*.sqlite3

# 日志文件
*.log

# 临时文件
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
"""
    
    gitignore_file = Path('.gitignore')
    if gitignore_file.exists():
        with open(gitignore_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'config_local.py' not in content:
            with open(gitignore_file, 'a', encoding='utf-8') as f:
                f.write(gitignore_content)
            print("✅ 已更新 .gitignore 文件")
        else:
            print("⚠️  .gitignore 文件已包含相关条目")
    else:
        with open(gitignore_file, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        print("✅ 已创建 .gitignore 文件")

def main():
    """主函数"""
    print("🚀 护工资源管理系统 - 配置管理工具")
    print("=" * 50)
    
    while True:
        print("\n请选择操作：")
        print("1. 创建环境变量文件 (.env)")
        print("2. 创建本地配置文件 (config_local.py)")
        print("3. 交互式配置数据库参数")
        print("4. 更新 .gitignore 文件")
        print("5. 执行所有操作")
        print("0. 退出")
        
        choice = input("\n请输入选项 (0-5): ").strip()
        
        if choice == '1':
            create_env_file()
        elif choice == '2':
            create_local_config()
        elif choice == '3':
            config = interactive_config()
            update_local_config(config)
        elif choice == '4':
            create_gitignore_entries()
        elif choice == '5':
            create_env_file()
            create_local_config()
            create_gitignore_entries()
            print("\n🎉 所有配置已完成！")
            print("\n📝 使用说明：")
            print("1. 编辑 back/config/config_local.py 文件，修改您的数据库配置")
            print("2. 或者设置环境变量（推荐用于生产环境）")
            print("3. 本地配置文件不会被提交到版本控制系统")
        elif choice == '0':
            print("👋 再见！")
            break
        else:
            print("❌ 无效选项，请重新选择")

if __name__ == "__main__":
    main() 