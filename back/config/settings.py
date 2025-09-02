# -*- coding: utf-8 -*-
"""
护工资源管理系统 - 配置文件
====================================

包含所有应用配置参数，集中管理便于维护
"""

import os

# ==================== 环境变量加载 ====================
# 尝试加载 .env 文件（如果存在）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not available, skipping .env file loading")

# ==================== 环境检测 ====================
ENV = os.getenv("FLASK_ENV", "development")  # development, production, testing
DEBUG = ENV == "development"

# ==================== 基础目录配置 ====================
# 修复路径计算，确保从backend目录正确计算
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # config目录
BACKEND_DIR = os.path.dirname(BASE_DIR)                # backend目录
ROOT_DIR = os.path.dirname(BACKEND_DIR)                # 根目录 (D:\CaregivingApp)
WEB_FOLDER = os.path.join(ROOT_DIR, 'web')            # web文件夹路径 (D:\CaregivingApp\web)
UPLOAD_FOLDER = os.path.join(WEB_FOLDER, "uploads")    # 文件上传目录

# ==================== 文件上传配置 ====================
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# ==================== 安全配置 ====================
APP_SECRET = os.getenv("APP_SECRET", "caregiving-system-secret-key-2024")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", 'your_unique_secret_key')

# ==================== 数据库配置 ====================
# MySQL 数据库配置
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USERNAME = os.getenv("MYSQL_USERNAME", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "20040924")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "caregiving_db")

# ==================== 本地配置覆盖 ====================
# 尝试导入本地配置文件（如果存在且不是生产环境）
if ENV != "production":
    try:
        from .config_local import *
        print("已加载本地配置文件 config_local.py")
    except ImportError:
        print("未找到本地配置文件，使用默认配置")
        pass

# 构建 MySQL 连接字符串（在本地配置加载之后）
DATABASE_URI = 'mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4'.format(
    username=MYSQL_USERNAME,
    password=MYSQL_PASSWORD,
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    database=MYSQL_DATABASE
)

# 备用 SQLite 配置（已迁移到 MySQL）
# DATABASE_URI = 'sqlite:///{}'.format(os.path.join(ROOT_DIR, "database", "caregiving.db"))

SQLALCHEMY_TRACK_MODIFICATIONS = False

# ==================== 管理员配置 ====================
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# ==================== JWT配置 ====================
JWT_EXPIRATION_HOURS = 2

# ==================== 生产环境配置 ====================
if ENV == "production":
    # 生产环境安全配置
    DEBUG = False
    # 强制使用HTTPS
    PREFERRED_URL_SCHEME = 'https'
    # 更长的JWT过期时间
    JWT_EXPIRATION_HOURS = 24
    # 生产环境日志级别
    LOG_LEVEL = "WARNING"
else:
    # 开发环境配置
    DEBUG = True
    LOG_LEVEL = "DEBUG" 