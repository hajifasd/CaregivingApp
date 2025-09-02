# -*- coding: utf-8 -*-
"""
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

# MySQL 端口号 - 修改为您的实际端口
MYSQL_PORT = "3308"

# MySQL 用户名
MYSQL_USERNAME = "root"

# MySQL 密码
MYSQL_PASSWORD = "781299"

# MySQL 数据库名
MYSQL_DATABASE = "caregiving_db"

# ==================== 应用配置 ====================
# 应用密钥（建议使用随机生成的密钥）
APP_SECRET = "caregiving-system-secret-key-2024"

# Flask 密钥
FLASK_SECRET_KEY = "your_unique_secret_key"

# ==================== 管理员配置 ====================
# 管理员用户名
ADMIN_USERNAME = "admin"

# 管理员密码
ADMIN_PASSWORD = "admin123" 