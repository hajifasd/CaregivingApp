# -*- coding: utf-8 -*-
"""
护工资源管理系统 - 重构后的主应用
====================================

重构后的精简版主应用，使用模块化结构
"""

from flask import Flask, render_template, redirect, url_for, g, request, jsonify, session, send_from_directory
import os
import logging
import sys
import jwt
from functools import wraps
from sqlalchemy import inspect

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 添加父目录到Python路径，用于导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入配置
from config.settings import (
    WEB_FOLDER, UPLOAD_FOLDER, FLASK_SECRET_KEY, 
    MAX_CONTENT_LENGTH, SQLALCHEMY_TRACK_MODIFICATIONS, DATABASE_URI
)

# 导入配置验证器
from config.config_validator import validate_config

# 导入扩展
from extensions import db

# 数据库初始化（使用 MySQL）
# from database.database import init_database

# 导入API蓝图
from api.auth import auth_bp
from api.admin import admin_bp
from api.caregiver import caregiver_bp
from api.user import user_bp
from api.caregiver_business import caregiver_business_bp
from api.chat import chat_bp, init_socketio
from api.employment_contract import employment_contract_bp
from api.caregiver_hire_info import caregiver_hire_info_bp
from api.notification import notification_bp
from api.file_upload import file_upload_bp
from api.bigdata import bigdata_bp
from api.job import job_bp
from api.emergency import emergency_bp

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

# ==================== 认证检查装饰器 ====================
def require_auth_page(user_type=None):
    """页面认证检查装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 获取token
            token = None
            auth_header = request.headers.get('Authorization')
            
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                # 尝试从cookie获取token
                token = request.cookies.get(f'{user_type}_token') if user_type else None
                
                # 如果cookie中没有token，尝试从请求参数获取（用于页面访问）
                if not token and user_type:
                    token = request.args.get(f'{user_type}_token')
            
            if not token:
                # 调试信息
                logger.warning(f"页面认证失败: user_type={user_type}, auth_header={auth_header}, cookies={request.cookies}, args={request.args}")
                # 返回登录页面而不是JSON错误
                if user_type == 'admin':
                    return redirect('/admin/admin-login.html')
                elif user_type == 'caregiver':
                    return redirect('/')
                else:
                    return redirect('/')
            
            try:
                # 验证token - 使用与generate_token相同的密钥
                from config.settings import FLASK_SECRET_KEY
                data = jwt.decode(token, FLASK_SECRET_KEY, algorithms=['HS256'])
                
                # 检查用户类型
                if user_type and data.get('user_type') != user_type:
                    if user_type == 'admin':
                        return redirect('/admin/admin-login.html')
                    elif user_type == 'caregiver':
                        return redirect('/caregiver/')
                    else:
                        return redirect('/')
                
                # 将用户信息存储到g对象中
                g.current_user = {
                    'user_id': data['user_id'],
                    'user_type': data['user_type'],
                    'name': data.get('name', '')
                }
                
            except jwt.ExpiredSignatureError:
                if user_type == 'admin':
                    return redirect('/admin/admin-login.html')
                elif user_type == 'caregiver':
                    return redirect('/')
                else:
                    return redirect('/')
            except jwt.InvalidTokenError:
                if user_type == 'admin':
                    return redirect('/admin/admin-login.html')
                elif user_type == 'caregiver':
                    return redirect('/')
                else:
                    return redirect('/')
            except Exception as e:
                logger.error(f"认证检查失败: {str(e)}")
                if user_type == 'admin':
                    return redirect('/admin/admin-login.html')
                elif user_type == 'caregiver':
                    return redirect('/')
                else:
                    return redirect('/')
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==================== 应用配置 ====================
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}

# ==================== 扩展初始化 ====================
db.init_app(app)

# ==================== 模型初始化 ====================
def init_models():
    """初始化数据模型"""
    from models.user import User
    from models.caregiver import Caregiver
    from models.service import ServiceType
    from models.business import JobData, AnalysisResult, Appointment, Employment, Message
    from models.chat import ChatMessage, ChatConversation
    from models.employment_contract import EmploymentContract, ServiceRecord, ContractApplication
    from models.caregiver_hire_info import CaregiverHireInfo
    
    # 创建实际的模型类
    UserModel = User.get_model(db)
    CaregiverModel = Caregiver.get_model(db)
    ServiceTypeModel = ServiceType.get_model(db)
    JobDataModel = JobData.get_model(db)
    AnalysisResultModel = AnalysisResult.get_model(db)
    AppointmentModel = Appointment.get_model(db)
    EmploymentModel = Employment.get_model(db)
    MessageModel = Message.get_model(db)
    ChatMessageModel = ChatMessage.get_model(db)
    ChatConversationModel = ChatConversation.get_model(db)
    EmploymentContractModel = EmploymentContract.get_model(db)
    ServiceRecordModel = ServiceRecord.get_model(db)
    ContractApplicationModel = ContractApplication.get_model(db)
    CaregiverHireInfoModel = CaregiverHireInfo.get_model(db)
    
    # 初始化消息服务，设置数据库连接
    from services.message_service import message_service
    message_service.set_db(db)
    
    # 初始化聘用合同服务，设置数据库连接
    from services.employment_contract_service import employment_contract_service
    employment_contract_service.set_db(db)
    
    return (UserModel, CaregiverModel, ServiceTypeModel, 
            JobDataModel, AnalysisResultModel, AppointmentModel, 
            EmploymentModel, MessageModel, ChatMessageModel, ChatConversationModel,
            EmploymentContractModel, ServiceRecordModel, ContractApplicationModel,
            CaregiverHireInfoModel)

# 全局模型变量
UserModel = None
CaregiverModel = None
ServiceTypeModel = None
JobDataModel = None
AnalysisResultModel = None
AppointmentModel = None
EmploymentModel = None
MessageModel = None
ChatMessageModel = None
ChatConversationModel = None
EmploymentContractModel = None
ServiceRecordModel = None
ContractApplicationModel = None

# ==================== 注册蓝图 ====================
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(caregiver_bp)
app.register_blueprint(user_bp)
app.register_blueprint(caregiver_business_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(employment_contract_bp)
app.register_blueprint(caregiver_hire_info_bp)
app.register_blueprint(notification_bp)
app.register_blueprint(file_upload_bp)
app.register_blueprint(bigdata_bp)
app.register_blueprint(job_bp)
app.register_blueprint(emergency_bp)

# ==================== 初始化SocketIO ====================
socketio = init_socketio(app)

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
        'admin_login_page', 'admin_caregivers_page', 'admin_dashboard_page',
        'admin_users_page', 'admin_job_analysis_page',
        'user_register_page', 'user_dashboard_page', 'user_home_page',
        'user_caregivers_page', 'user_appointments_page', 'user_employments_page',
        'user_messages_page', 'user_profile_page',
        'caregiver_register_page', 'caregiver_dashboard_page'
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

@app.route('/admin/login')
@app.route('/admin/admin-login.html')
def admin_login_page():
    """管理员登录页面"""
    template_path = os.path.join(WEB_FOLDER, 'admin', 'admin-login.html')
    if not os.path.exists(template_path):
        logger.error(f"admin-login.html模板文件不存在: {template_path}")
        return "管理员登录模板不存在", 500
    return render_template('admin/admin-login.html')

@app.route('/user/register')
@app.route('/user/user-register.html')
def user_register_page():
    """用户注册页面"""
    template_path = os.path.join(WEB_FOLDER, 'user', 'user-register.html')
    if not os.path.exists(template_path):
        logger.error(f"user-register.html模板文件不存在: {template_path}")
        return "用户注册模板不存在", 500
    return render_template('user/user-register.html')

@app.route('/caregiver/register')
@app.route('/caregiver/caregiver-register.html')
def caregiver_register_page():
    """护工注册页面"""
    template_path = os.path.join(WEB_FOLDER, 'caregiver', 'caregiver-register.html')
    if not os.path.exists(template_path):
        logger.error(f"caregiver-register.html模板文件不存在: {template_path}")
        return "护工注册模板不存在", 500
    return render_template('caregiver/caregiver-register.html')

@app.route('/admin/caregivers')
@app.route('/admin/admin-caregivers.html')
def admin_caregivers_page():
    """管理员护工管理页面"""
    template_path = os.path.join(WEB_FOLDER, 'admin', 'admin-caregivers.html')
    if not os.path.exists(template_path):
        logger.error(f"admin-caregivers.html模板文件不存在: {template_path}")
        return "管理员护工管理模板不存在", 500
    
    # 在应用上下文中获取模型
    from models.caregiver import Caregiver
    CaregiverModel = Caregiver.get_model(db)
    
    # 获取待审核护工
    unapproved = CaregiverModel.query.filter(
        CaregiverModel.is_approved == False
    ).order_by(CaregiverModel.created_at.desc()).all()
    
    # 获取已批准护工
    approved = CaregiverModel.query.filter(
        CaregiverModel.is_approved == True
    ).order_by(CaregiverModel.approved_at.desc()).all()
    
    return render_template('admin/admin-caregivers.html', unapproved=unapproved, approved=approved)

@app.route('/admin/dashboard')
@app.route('/admin/admin-dashboard.html')
@require_auth_page('admin')
def admin_dashboard_page():
    """管理员仪表盘页面"""
    template_path = os.path.join(WEB_FOLDER, 'admin', 'admin-dashboard.html')
    if not os.path.exists(template_path):
        logger.error(f"admin-dashboard.html模板文件不存在: {template_path}")
        return "管理员仪表盘模板不存在", 500
    
    # 在应用上下文中获取模型
    from models.user import User
    from models.caregiver import Caregiver
    from models.business import JobData
    
    UserModel = User.get_model(db)
    CaregiverModel = Caregiver.get_model(db)
    JobDataModel = JobData.get_model(db)
    
    # 获取统计数据
    user_count = UserModel.query.count()
    approved_user_count = UserModel.query.filter_by(is_approved=True).count()
    pending_user_count = UserModel.query.filter_by(is_approved=False).count()
    
    approved_caregiver_count = CaregiverModel.query.filter_by(is_approved=True).count()
    unapproved_caregiver_count = CaregiverModel.query.filter_by(is_approved=False).count()
    
    # 获取职位数据数量
    job_count = JobDataModel.query.count()
    
    return render_template('admin/admin-dashboard.html', 
                         user_count=user_count,
                         approved_user_count=approved_user_count,
                         pending_user_count=pending_user_count,
                         approved_caregiver_count=approved_caregiver_count,
                         unapproved_caregiver_count=unapproved_caregiver_count,
                         job_count=job_count)

@app.route('/admin/bigdata-dashboard')
@app.route('/admin/admin-bigdata-dashboard.html')
def admin_bigdata_dashboard_page():
    """管理员大数据仪表盘页面"""
    try:
        template_path = os.path.join(WEB_FOLDER, 'admin', 'admin-bigdata-dashboard.html')
        if not os.path.exists(template_path):
            logger.error(f"admin-bigdata-dashboard.html模板文件不存在: {template_path}")
            return "大数据仪表盘模板不存在", 500
        
        return send_from_directory(WEB_FOLDER, 'admin/admin-bigdata-dashboard.html')
    except Exception as e:
        logger.error(f"大数据仪表盘页面错误: {e}")
        return redirect(url_for('admin_login_page'))

@app.route('/admin/users')
@app.route('/admin/admin-users.html')
def admin_users_page():
    """管理员用户管理页面"""
    template_path = os.path.join(WEB_FOLDER, 'admin', 'admin-users.html')
    if not os.path.exists(template_path):
        logger.error(f"admin-users.html模板文件不存在: {template_path}")
        return "管理员用户管理模板不存在", 500
    
    # 在应用上下文中获取模型
    from models.user import User
    UserModel = User.get_model(db)
    
    # 获取待审核用户
    pending_users = UserModel.query.filter_by(is_approved=False).order_by(UserModel.created_at.desc()).all()
    
    # 获取已审核用户
    approved_users = UserModel.query.filter_by(is_approved=True).order_by(UserModel.approved_at.desc()).all()
    
    return render_template('admin/admin-users.html', pending=pending_users, approved=approved_users)

@app.route('/admin/job-analysis')
@app.route('/admin/admin-job-analysis.html')
def admin_job_analysis_page():
    """管理员职位分析页面"""
    template_path = os.path.join(WEB_FOLDER, 'admin', 'admin-job-analysis.html')
    if not os.path.exists(template_path):
        logger.error(f"admin-job-analysis.html模板文件不存在: {template_path}")
        return "管理员职位分析模板不存在", 500
    
    # 这里可以添加职位分析的数据
    # 暂时返回空数据
    return render_template('admin/admin-job-analysis.html')

@app.route('/user/dashboard')
@app.route('/user/user-dashboard.html')
def user_dashboard_page():
    """用户仪表盘页面"""
    template_path = os.path.join(WEB_FOLDER, 'user', 'user-dashboard.html')
    if not os.path.exists(template_path):
        logger.error(f"user-dashboard.html模板文件不存在: {template_path}")
        return "用户仪表盘模板不存在", 500
    
    return render_template('user/user-dashboard.html')

# 添加更多用户端路由
@app.route('/user/home')
@app.route('/user/user-home.html')
def user_home_page():
    """用户主页"""
    template_path = os.path.join(WEB_FOLDER, 'user', 'user-home.html')
    if not os.path.exists(template_path):
        logger.error(f"user-home.html模板文件不存在: {template_path}")
        return "用户主页模板不存在", 500
    return render_template('user/user-home.html')

@app.route('/user/caregivers')
@app.route('/user/user-caregivers.html')
def user_caregivers_page():
    """用户护工列表页面"""
    template_path = os.path.join(WEB_FOLDER, 'user', 'user-caregivers.html')
    if not os.path.exists(template_path):
        logger.error(f"user-caregivers.html模板文件不存在: {template_path}")
        return "用户护工列表模板不存在", 500
    return render_template('user/user-caregivers.html')

@app.route('/user/appointments')
@app.route('/user/user-appointments.html')
def user_appointments_page():
    """用户预约管理页面"""
    template_path = os.path.join(WEB_FOLDER, 'user', 'user-appointments.html')
    if not os.path.exists(template_path):
        logger.error(f"user-appointments.html模板文件不存在: {template_path}")
        return "用户预约管理模板不存在", 500
    return render_template('user/user-appointments.html')

@app.route('/user/employments')
@app.route('/user/user-employments.html')
def user_employments_page():
    """用户雇佣管理页面"""
    template_path = os.path.join(WEB_FOLDER, 'user', 'user-employments.html')
    if not os.path.exists(template_path):
        logger.error(f"user-employments.html模板文件不存在: {template_path}")
        return "用户雇佣管理模板不存在", 500
    return render_template('user/user-employments.html')

@app.route('/user/messages')
@app.route('/user/user-messages.html')
def user_messages_page():
    """用户消息管理页面"""
    template_path = os.path.join(WEB_FOLDER, 'user', 'user-messages.html')
    if not os.path.exists(template_path):
        logger.error(f"user-messages.html模板文件不存在: {template_path}")
        return "用户消息管理模板不存在", 500
    return render_template('user/user-messages.html')

@app.route('/user/profile')
@app.route('/user/user-profile.html')
def user_profile_page():
    """用户资料页面"""
    template_path = os.path.join(WEB_FOLDER, 'user', 'user-profile.html')
    if not os.path.exists(template_path):
        logger.error(f"user-profile.html模板文件不存在: {template_path}")
        return "用户资料模板不存在", 500
    return render_template('user/user-profile.html')

# 护工端路由已删除，护工登录后直接跳转到仪表盘


@app.route('/caregiver/dashboard')
@app.route('/caregiver/caregiver-dashboard.html')
def caregiver_dashboard_page():
    """护工仪表盘页面"""
    template_path = os.path.join(WEB_FOLDER, 'caregiver', 'caregiver-dashboard.html')
    if not os.path.exists(template_path):
        logger.error(f"caregiver-dashboard.html模板文件不存在: {template_path}")
        return "护工仪表盘模板不存在", 500
    return render_template('caregiver/caregiver-dashboard.html')

@app.route('/caregiver/messages')
@app.route('/caregiver/caregiver-messages.html')
def caregiver_messages_page():
    """护工消息页面"""
    template_path = os.path.join(WEB_FOLDER, 'caregiver', 'caregiver-messages.html')
    if not os.path.exists(template_path):
        logger.error(f"caregiver-messages.html模板文件不存在: {template_path}")
        return "护工消息模板不存在", 500
    return render_template('caregiver/caregiver-messages.html')

# 护工端多页面路由
@app.route('/caregiver/profile')
def caregiver_profile_page():
    """护工个人信息页面"""
    template_path = os.path.join(WEB_FOLDER, 'caregiver', 'caregiver-profile.html')
    if not os.path.exists(template_path):
        logger.error(f"caregiver-profile.html模板文件不存在: {template_path}")
        return "护工个人信息模板不存在", 500
    return render_template('caregiver/caregiver-profile.html')

@app.route('/caregiver/hire-info')
def caregiver_hire_info_page():
    """护工聘用信息页面"""
    template_path = os.path.join(WEB_FOLDER, 'caregiver', 'caregiver-hire-info.html')
    if not os.path.exists(template_path):
        logger.error(f"caregiver-hire-info.html模板文件不存在: {template_path}")
        return "护工聘用信息模板不存在", 500
    return render_template('caregiver/caregiver-hire-info.html')

@app.route('/caregiver/job-opportunities')
def caregiver_job_opportunities_page():
    """护工工作申请页面"""
    template_path = os.path.join(WEB_FOLDER, 'caregiver', 'caregiver-job-opportunities.html')
    if not os.path.exists(template_path):
        logger.error(f"caregiver-job-opportunities.html模板文件不存在: {template_path}")
        return "护工工作申请模板不存在", 500
    return render_template('caregiver/caregiver-job-opportunities.html')

@app.route('/caregiver/jobs')
def caregiver_jobs_page():
    """护工工作机会页面"""
    template_path = os.path.join(WEB_FOLDER, 'caregiver', 'caregiver-jobs.html')
    if not os.path.exists(template_path):
        logger.error(f"caregiver-jobs.html模板文件不存在: {template_path}")
        return "护工工作机会模板不存在", 500
    return render_template('caregiver/caregiver-jobs.html')

@app.route('/caregiver/appointments')
def caregiver_appointments_page():
    """护工预约页面"""
    template_path = os.path.join(WEB_FOLDER, 'caregiver', 'caregiver-appointments.html')
    if not os.path.exists(template_path):
        logger.error(f"caregiver-appointments.html模板文件不存在: {template_path}")
        return "护工预约模板不存在", 500
    return render_template('caregiver/caregiver-appointments.html')

@app.route('/caregiver/schedule')
def caregiver_schedule_page():
    """护工工作安排页面"""
    template_path = os.path.join(WEB_FOLDER, 'caregiver', 'caregiver-schedule.html')
    if not os.path.exists(template_path):
        logger.error(f"caregiver-schedule.html模板文件不存在: {template_path}")
        return "护工工作安排模板不存在", 500
    return render_template('caregiver/caregiver-schedule.html')

@app.route('/caregiver/earnings')
def caregiver_earnings_page():
    """护工收入统计页面"""
    template_path = os.path.join(WEB_FOLDER, 'caregiver', 'caregiver-earnings.html')
    if not os.path.exists(template_path):
        logger.error(f"caregiver-earnings.html模板文件不存在: {template_path}")
        return "护工收入统计模板不存在", 500
    return render_template('caregiver/caregiver-earnings.html')

@app.route('/caregiver/location')
def caregiver_location_page():
    """护工位置服务页面"""
    template_path = os.path.join(WEB_FOLDER, 'caregiver', 'caregiver-location.html')
    if not os.path.exists(template_path):
        logger.error(f"caregiver-location.html模板文件不存在: {template_path}")
        return "护工位置服务模板不存在", 500
    return render_template('caregiver/caregiver-location.html')

@app.route('/caregiver/reviews')
def caregiver_reviews_page():
    """护工评价管理页面"""
    template_path = os.path.join(WEB_FOLDER, 'caregiver', 'caregiver-reviews.html')
    if not os.path.exists(template_path):
        logger.error(f"caregiver-reviews.html模板文件不存在: {template_path}")
        return "护工评价管理模板不存在", 500
    return render_template('caregiver/caregiver-reviews.html')

@app.route('/caregiver/settings')
def caregiver_settings_page():
    """护工设置页面"""
    template_path = os.path.join(WEB_FOLDER, 'caregiver', 'caregiver-settings.html')
    if not os.path.exists(template_path):
        logger.error(f"caregiver-settings.html模板文件不存在: {template_path}")
        return "护工设置模板不存在", 500
    return render_template('caregiver/caregiver-settings.html')

# ==================== 旧URL重定向 ====================
@app.route('/admin-login.html')
def redirect_admin_login():
    """重定向旧的管理员登录URL"""
    return redirect(url_for('admin_login_page'))

@app.route('/user-register.html')
def redirect_user_register():
    """重定向旧的用户注册URL"""
    return redirect(url_for('user_register_page'))

@app.route('/caregiver-register.html')
def redirect_caregiver_register():
    """重定向旧的护工注册URL"""
    return redirect(url_for('caregiver_register_page'))

@app.route('/admin-caregivers.html')
def redirect_admin_caregivers():
    """重定向旧的管理员护工管理URL"""
    return redirect(url_for('admin_caregivers_page'))

@app.route('/admin-dashboard.html')
def redirect_admin_dashboard():
    """重定向旧的管理员仪表盘URL"""
    return redirect(url_for('admin_dashboard_page'))

@app.route('/admin-users.html')
def redirect_admin_users():
    """重定向旧的管理员用户管理URL"""
    return redirect(url_for('admin_users_page'))

@app.route('/admin-job-analysis.html')
def redirect_admin_job_analysis():
    """重定向旧的管理员职位分析URL"""
    return redirect(url_for('admin_job_analysis_page'))

@app.route('/user-dashboard.html')
def redirect_user_dashboard():
    """重定向旧的用户仪表盘URL"""
    return redirect(url_for('user_dashboard_page'))

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
        
        # 检查根目录HTML文件
        for file in os.listdir(WEB_FOLDER):
            if file.endswith('.html'):
                print(f"- {file}")
        
        # 检查各端目录
        for subdir in ['admin', 'user', 'caregiver']:
            subdir_path = os.path.join(WEB_FOLDER, subdir)
            if os.path.exists(subdir_path):
                print(f"\n{subdir.upper()}端文件:")
                for file in os.listdir(subdir_path):
                    if file.endswith('.html'):
                        print(f"  - {subdir}/{file}")
    
    # 初始化数据库（MySQL 已迁移完成）
    try:
        with app.app_context():
            from extensions import init_database
            init_database(app)
            
            # 初始化所有数据模型和服务
            init_models()
            print("数据模型初始化完成")
            
        print("数据库初始化完成")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        print("请检查数据库配置和连接")
        print("继续启动应用...")
    
    # 添加数据库测试API端点
    @app.route('/api/test/database', methods=['GET'])
    def test_database_connection():
        """测试数据库连接"""
        try:
            with db.engine.connect() as connection:
                result = connection.execute(db.text('SELECT 1 as test'))
                test_value = result.fetchone()[0]
            
            # 获取表信息 - 使用新版本SQLAlchemy的方法
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            return jsonify({
                'success': True,
                'data': {
                    'connection': 'OK',
                    'test_query': test_value,
                    'tables': tables,
                    'table_count': len(tables)
                }
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'数据库连接失败: {str(e)}'
            }), 500
    
    @app.route('/api/test/message-service', methods=['GET'])
    def test_message_service():
        """测试消息服务"""
        try:
            from services.message_service import message_service
            
            # 检查消息服务状态
            service_status = {
                'db_connected': message_service.db is not None,
                'model_loaded': message_service.get_model() is not None,
                'memory_messages': len(message_service.messages)
            }
            
            return jsonify({
                'success': True,
                'data': service_status
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'消息服务测试失败: {str(e)}'
            }), 500
    
    @app.route('/api/test/caregivers', methods=['GET'])
    def test_caregivers():
        """测试护工数据"""
        try:
            from models.caregiver import Caregiver
            CaregiverModel = Caregiver.get_model(db)
            
            # 获取护工总数
            total_caregivers = CaregiverModel.query.count()
            
            # 获取前5个护工
            caregivers = CaregiverModel.query.limit(5).all()
            
            result = []
            for caregiver in caregivers:
                result.append({
                    'id': caregiver.id,
                    'name': caregiver.name,
                    'phone': caregiver.phone,
                    'avatar': caregiver.avatar_url or '/uploads/avatars/default-caregiver.png'
                })
            
            return jsonify({
                'success': True,
                'data': {
                    'total_caregivers': total_caregivers,
                    'sample_caregivers': result
                }
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'护工数据测试失败: {str(e)}'
            }), 500
    
    @app.route('/api/test/save-message', methods=['POST'])
    def test_save_message():
        """测试保存消息"""
        try:
            from services.message_service import message_service
            
            message_data = request.json
            saved_message = message_service.save_message(message_data)
            
            if saved_message:
                return jsonify({
                    'success': True,
                    'data': saved_message
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '消息保存失败'
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'保存消息测试失败: {str(e)}'
            }), 500
    
    @app.route('/api/test/get-messages', methods=['GET'])
    def test_get_messages():
        """测试获取消息"""
        try:
            from services.message_service import message_service
            
            user_id = request.args.get('user_id', type=int)
            user_type = request.args.get('user_type', 'user')
            contact_id = request.args.get('contact_id', type=int)
            contact_type = request.args.get('contact_type', 'caregiver')
            
            messages = message_service.get_message_history(
                user_id, user_type, contact_id, contact_type, limit=10
            )
            
            return jsonify({
                'success': True,
                'data': messages
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取消息测试失败: {str(e)}'
            }), 500
    
    # 验证配置
    print("🔍 验证应用配置...")
    config_result = validate_config()
    
    if not config_result['is_valid']:
        print("❌ 配置验证失败，请修复错误后重新启动")
        sys.exit(1)
    
    if config_result['has_warnings']:
        print("⚠️  配置验证通过，但存在警告项，建议修复")
    
    try:
        print("🚀 启动支持WebSocket的服务器...")
        socketio.run(app, host='127.0.0.1', port=8000, debug=True, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"启动失败: {e}")
        print("尝试使用开发服务器启动...")
        app.run(debug=True, host='127.0.0.1', port=8000) 