"""
护工资源管理系统 - 配置文件
====================================

包含所有应用配置参数，集中管理便于维护
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

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
APP_SECRET = os.getenv("APP_SECRET", "dev-secret-key-change-in-production")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-flask-secret-key-change-in-production")

# 开发环境警告
if APP_SECRET == "dev-secret-key-change-in-production" or FLASK_SECRET_KEY == "dev-flask-secret-key-change-in-production":
    print("⚠️  警告：正在使用开发环境默认密钥，生产环境请设置APP_SECRET和FLASK_SECRET_KEY环境变量")

# ==================== 数据库配置 ====================
# MySQL 数据库配置 - 开发环境提供默认值
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USERNAME = os.getenv("MYSQL_USERNAME", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "20040924")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "caregiving_db")

# 开发环境警告
if MYSQL_PASSWORD == "20040924":
    print("⚠️  警告：正在使用开发环境默认数据库密码，生产环境请设置MYSQL_PASSWORD环境变量")

# 构建 MySQL 连接字符串，简化连接池配置
DATABASE_URI = f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4'

# 备用 SQLite 配置（已迁移到 MySQL）
# DATABASE_URI = 'sqlite:///{}'.format(os.path.join(ROOT_DIR, "database", "caregiving.db"))

SQLALCHEMY_TRACK_MODIFICATIONS = False

# ==================== 管理员配置 ====================
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# 开发环境警告
if ADMIN_PASSWORD == "admin123":
    print("⚠️  警告：正在使用开发环境默认管理员密码，生产环境请设置ADMIN_PASSWORD环境变量")

# ==================== JWT配置 ====================
JWT_EXPIRATION_HOURS = 2 