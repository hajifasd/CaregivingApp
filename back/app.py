"""
护工资源管理系统 - 重构后的主应用
====================================

重构后的精简版主应用，使用模块化结构
"""

from flask import Flask, render_template, redirect, url_for, g, request, jsonify, session, send_from_directory
import os
import logging
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 添加父目录到Python路径，用于导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入配置
from config.settings import (
    WEB_FOLDER, UPLOAD_FOLDER, FLASK_SECRET_KEY, 
    MAX_CONTENT_LENGTH, SQLALCHEMY_TRACK_MODIFICATIONS, DATABASE_URI
)

# 导入扩展
from extensions import db

# 导入数据库初始化
from database.database import init_database

# 导入API蓝图
from api.auth import auth_bp

# ==================== 日志配置 ====================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== 目录验证和创建 ====================
if not os.path.exists(WEB_FOLDER):
    logger.error(f"web文件夹不存在: {WEB_FOLDER}")
    try:
        os.makedirs(WEB_FOLDER)
        logger.info(f"已自动创建web文件夹: {WEB_FOLDER}")
    except Exception as e:
        logger.error(f"创建web文件夹失败: {str(e)}")

# ==================== Flask应用初始化 ====================
app = Flask(
    __name__,
    static_folder=WEB_FOLDER,
    static_url_path='/',
    template_folder=WEB_FOLDER
)

# ==================== 应用配置 ====================
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

# ==================== 扩展初始化 ====================
db.init_app(app)

# ==================== 注册蓝图 ====================
app.register_blueprint(auth_bp)

# ==================== 上传目录权限检查 ====================
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    test_file = os.path.join(UPLOAD_FOLDER, "test_write_permission.tmp")
    with open(test_file, "w") as f:
        f.write("test")
    os.remove(test_file)
    logger.info(f"上传文件夹准备就绪: {UPLOAD_FOLDER}")
except Exception as e:
    logger.error(f"上传文件夹创建或权限检查失败: {str(e)}")

# ==================== 请求钩子 ====================
@app.before_request
def check_login_status():
    """请求前钩子：验证用户登录状态"""
    g.user = None
    
    # 定义公开路由（无需登录验证）
    public_routes = [
        'index', 'static',
        'admin_login_page', 
        'user_register_page', 'caregiver_register_page'
    ]
    
    if request.endpoint in public_routes:
        return

# ==================== 页面路由 ====================
@app.route('/')
def index():
    """网站首页"""
    template_path = os.path.join(WEB_FOLDER, 'index.html')
    if not os.path.exists(template_path):
        logger.error(f"index.html模板文件不存在: {template_path}")
        return "网站首页模板不存在", 500
    return render_template('index.html')

@app.route('/admin-login.html')
def admin_login_page():
    """管理员登录页面"""
    template_path = os.path.join(WEB_FOLDER, 'admin-login.html')
    if not os.path.exists(template_path):
        logger.error(f"admin-login.html模板文件不存在: {template_path}")
        return "管理员登录模板不存在", 500
    return render_template('admin-login.html')

@app.route('/user-register.html')
def user_register_page():
    """用户注册页面"""
    template_path = os.path.join(WEB_FOLDER, 'user-register.html')
    if not os.path.exists(template_path):
        logger.error(f"user-register.html模板文件不存在: {template_path}")
        return "用户注册模板不存在", 500
    return render_template('user-register.html')

@app.route('/caregiver-register.html')
def caregiver_register_page():
    """护工注册页面"""
    template_path = os.path.join(WEB_FOLDER, 'caregiver-register.html')
    if not os.path.exists(template_path):
        logger.error(f"caregiver-register.html模板文件不存在: {template_path}")
        return "护工注册模板不存在", 500
    return render_template('caregiver-register.html')

# ==================== 文件访问 ====================
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """访问上传的文件"""
    if '..' in filename or '/' in filename or '\\' in filename:
        logger.warning(f"尝试访问非法文件路径: {filename}")
        return "非法访问", 403
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ==================== 启动服务 ====================
if __name__ == '__main__':
    # 启动前验证web文件夹
    if not os.path.exists(WEB_FOLDER):
        print(f"错误：web文件夹不存在于路径 {WEB_FOLDER}")
        print("请检查文件夹路径是否正确")
    else:
        print(f"成功找到web文件夹: {WEB_FOLDER}")
        print("模板文件列表:")
        for file in os.listdir(WEB_FOLDER):
            if file.endswith('.html'):
                print(f"- {file}")
    
    # 初始化数据库
    try:
        init_database(app)
        print("数据库初始化完成")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        print("继续启动应用...")
    
    try:
        from waitress import serve
        print("使用waitress启动服务...")
        serve(app, host='0.0.0.0', port=8000)
    except ImportError:
        print("使用开发服务器启动...")
        app.run(debug=True, host='0.0.0.0', port=8000) 