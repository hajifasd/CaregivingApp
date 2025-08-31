from flask import Flask, render_template, redirect, url_for, g, request, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
import jwt
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import uuid
import bcrypt
import logging

# 配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 明确指定web文件夹路径（假设与backend文件夹同级）
WEB_FOLDER = os.path.join(os.path.dirname(BASE_DIR), 'web')
UPLOAD_FOLDER = os.path.join(WEB_FOLDER, "uploads")  # 上传文件保存到web/uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
APP_SECRET = os.getenv("APP_SECRET", "caregiving-system-secret-key-2024")
DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, "caregiving.db"))

# 初始化日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 验证web文件夹是否存在
if not os.path.exists(WEB_FOLDER):
    logger.error(f"web文件夹不存在: {WEB_FOLDER}")
    logger.error(f"请确保web文件夹与backend文件夹同级，或修改WEB_FOLDER路径配置")
    # 尝试创建web文件夹作为备选方案
    try:
        os.makedirs(WEB_FOLDER)
        logger.info(f"已自动创建web文件夹: {WEB_FOLDER}")
    except Exception as e:
        logger.error(f"创建web文件夹失败: {str(e)}")

# 初始化Flask应用
app = Flask(
    __name__,
    static_folder=WEB_FOLDER,  # 静态文件目录（CSS、JS等）
    static_url_path='/',       # 静态文件访问路径
    template_folder=WEB_FOLDER # 模板文件目录（HTML文件）
)

# 应用配置
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY", 'your_unique_secret_key')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB文件限制

# 确保上传文件夹存在并具有正确权限
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    # 检查文件夹是否可写
    test_file = os.path.join(UPLOAD_FOLDER, "test_write_permission.tmp")
    with open(test_file, "w") as f:
        f.write("test")
    os.remove(test_file)
    logger.info(f"上传文件夹准备就绪: {UPLOAD_FOLDER}")
except Exception as e:
    logger.error(f"上传文件夹创建或权限检查失败: {str(e)}")

# 初始化数据库
db = SQLAlchemy(app)

# --------------------------
# 数据模型
# --------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    id_file = db.Column(db.String(200))  # 用户身份证文件
    is_approved = db.Column(db.Boolean, default=False)  # 是否审核通过
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    approved_at = db.Column(db.DateTime, index=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "id_file": self.id_file,
            "id_file_url": f"/uploads/{self.id_file}" if (self.id_file and self.id_file.strip()) else None,
            "is_approved": self.is_approved,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M"),
            "approved_at": self.approved_at.strftime("%Y-%m-%d %H:%M") if self.approved_at else None
        }

class Caregiver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    id_file = db.Column(db.String(200), nullable=False)  # 不允许为空
    cert_file = db.Column(db.String(200), nullable=False)  # 不允许为空
    password_hash = db.Column(db.String(256), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    approved_at = db.Column(db.DateTime, index=True)

    def to_dict(self) -> Dict[str, Any]:
        valid_id_file = self.id_file and self.id_file.strip()
        valid_cert_file = self.cert_file and self.cert_file.strip()
        
        if not valid_id_file or not valid_cert_file:
            logger.warning(f"护工ID: {self.id} 存在不完整的材料文件")
            
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "id_file": self.id_file,
            "cert_file": self.cert_file,
            "id_file_url": f"/uploads/{self.id_file}" if valid_id_file else None,
            "cert_file_url": f"/uploads/{self.cert_file}" if valid_cert_file else None,
            "is_approved": self.is_approved,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M"),
            "approved_at": self.approved_at.strftime("%Y-%m-%d %H:%M") if self.approved_at else None
        }

class JobData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_name = db.Column(db.String(100))
    company = db.Column(db.String(100))
    city = db.Column(db.String(20))
    salary_low = db.Column(db.Integer)
    salary_high = db.Column(db.Integer)
    experience = db.Column(db.String(50))
    education = db.Column(db.String(20))
    skills = db.Column(db.String(200))
    crawl_time = db.Column(db.DateTime, default=datetime.utcnow)

class AnalysisResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    result = db.Column(db.JSON)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

# --------------------------
# 辅助函数
# --------------------------
def allowed_file(filename: str) -> bool:
    """检查文件是否为允许的格式"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(hashed_password: str, input_password: str) -> bool:
    return bcrypt.checkpw(input_password.encode(), hashed_password.encode())

def generate_token(user_id: int, user_type: str = 'user') -> str:
    payload = {
        "user_id": user_id,
        "user_type": user_type,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    return jwt.encode(payload, APP_SECRET, algorithm="HS256")

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, APP_SECRET, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

# 请求钩子：验证登录状态
@app.before_request
def check_login_status():
    g.user = None
    public_routes = [
        'index', 'admin_login_page', 'static',
        'user_register_page', 'caregiver_register_page',
        'user_login_page', 'caregiver_login_page'
    ]
    if request.endpoint in public_routes:
        return

    token = request.headers.get('Authorization') or session.get('token')
    if token and token.startswith('Bearer '):
        payload = verify_token(token[7:])
        if payload:
            g.user = payload

# --------------------------
# 数据操作工具类
# --------------------------
class DataStore:
    # 用户相关操作
    @staticmethod
    def add_user(email: str, password: str, id_file: str = None) -> User:
        user = User(
            email=email,
            password_hash=hash_password(password),
            id_file=id_file,
            is_approved=False
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        return User.query.filter_by(email=email).first()

    @staticmethod
    def verify_user(email: str, password: str) -> Optional[User]:
        user = User.query.filter_by(email=email).first()
        if user and user.is_approved and verify_password(user.password_hash, password):
            return user
        return None

    @staticmethod
    def get_all_users() -> List[User]:
        return User.query.all()

    @staticmethod
    def get_pending_users() -> List[User]:
        return User.query.filter(
            User.is_approved == False,
            User.id_file != None,
            User.id_file != ''
        ).order_by(User.created_at.desc()).all()

    @staticmethod
    def get_approved_users() -> List[User]:
        return User.query.filter(
            User.is_approved == True,
            User.id_file != None,
            User.id_file != ''
        ).order_by(
            User.approved_at.desc() if User.approved_at else User.created_at.desc()
        ).all()

    @staticmethod
    def delete_user(user_id: int) -> bool:
        try:
            with db.session.begin_nested():
                user = User.query.get(user_id)
                if not user:
                    return False
                
                if user.id_file and user.id_file.strip() and os.path.exists(os.path.join(UPLOAD_FOLDER, user.id_file)):
                    try:
                        os.remove(os.path.join(UPLOAD_FOLDER, user.id_file))
                    except Exception as e:
                        logger.error(f"删除用户文件失败: {e}")
                        
                db.session.delete(user)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除用户失败: {e}")
            return False

    @staticmethod
    def approve_user(user_id: int) -> bool:
        user = User.query.get(user_id)
        if not user or user.is_approved:
            return False
        user.is_approved = True
        user.approved_at = datetime.utcnow()
        db.session.commit()
        return True

    # 护工相关操作
    @staticmethod
    def add_caregiver(data: Dict[str, Any]) -> Caregiver:
        caregiver = Caregiver(
            name=data['name'],
            phone=data['phone'],
            id_file=data['id_file'],
            cert_file=data['cert_file'],
            password_hash=hash_password(data['password'])
        )
        db.session.add(caregiver)
        db.session.commit()
        return caregiver

    @staticmethod
    def get_caregiver_by_phone(phone: str) -> Optional[Caregiver]:
        return Caregiver.query.filter_by(phone=phone).first()

    @staticmethod
    def verify_caregiver(phone: str, password: str) -> Optional[Caregiver]:
        caregiver = Caregiver.query.filter_by(phone=phone).first()
        if caregiver and caregiver.is_approved and verify_password(caregiver.password_hash, password):
            return caregiver
        return None

    @staticmethod
    def get_unapproved_caregivers() -> List[Caregiver]:
        return Caregiver.query.filter(
            Caregiver.is_approved == False,
            Caregiver.id_file != '',
            Caregiver.cert_file != ''
        ).order_by(Caregiver.created_at.desc()).all()

    @staticmethod
    def get_approved_caregivers() -> List[Caregiver]:
        return Caregiver.query.filter(
            Caregiver.is_approved == True,
            Caregiver.id_file != '',
            Caregiver.cert_file != ''
        ).order_by(Caregiver.approved_at.desc() if Caregiver.approved_at else Caregiver.created_at.desc()).all()

    @staticmethod
    def approve_caregiver(caregiver_id: int) -> bool:
        caregiver = Caregiver.query.get(caregiver_id)
        if not caregiver or caregiver.is_approved:
            return False
        caregiver.is_approved = True
        caregiver.approved_at = datetime.utcnow()
        db.session.commit()
        return True

    @staticmethod
    def reject_caregiver(caregiver_id: int) -> bool:
        try:
            with db.session.begin_nested():
                caregiver = Caregiver.query.get(caregiver_id)
                if not caregiver or caregiver.is_approved:
                    return False
                
                for file_attr in ['id_file', 'cert_file']:
                    filename = getattr(caregiver, file_attr, None)
                    if filename and filename.strip() and os.path.exists(os.path.join(UPLOAD_FOLDER, filename)):
                        try:
                            os.remove(os.path.join(UPLOAD_FOLDER, filename))
                        except Exception as e:
                            logger.error(f"删除护工文件 {filename} 失败: {e}")
                
                db.session.delete(caregiver)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"拒绝护工失败: {e}")
            return False

# --------------------------
# 爬虫逻辑
# --------------------------
def parse_salary(salary_str: str) -> tuple[int, int]:
    try:
        salary_str = salary_str.replace(' ', '').replace('元/月', '')
        if '-' in salary_str:
            low, high = salary_str.split('-')
            return int(float(low)*1000), int(float(high)*1000)
        elif '以上' in salary_str:
            low = salary_str.replace('以上', '')
            return int(float(low)*1000), int(float(low)*1000)
        else:
            return int(float(salary_str)*1000), int(float(salary_str)*1000)
    except:
        return 0, 0

def crawl_page(page: int, city_code: str) -> None:
    with app.app_context():
        try:
            url = f"https://search.51job.com/list/{city_code},000000,0000,00,9,99,护工,2,{page}.html"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                "Referer": "https://www.51job.com/"
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'gbk'
            soup = BeautifulSoup(response.text, 'html.parser')

            job_list = soup.find("div", class_="j_joblist")
            if not job_list:
                return

            job_items = job_list.find_all("div", class_="el")
            for item in job_items:
                job_name_tag = item.find("span", class_="jname at")
                job_name = job_name_tag.get_text(strip=True) if job_name_tag else "未知职位"

                company_tag = item.find("a", class_="cname at")
                company = company_tag.get_text(strip=True) if company_tag else "未知公司"

                city_tag = item.find("span", class_="d at")
                city_text = city_tag.get_text(strip=True).split('|')[0] if city_tag else "未知城市"

                salary_tag = item.find("span", class_="sal")
                salary_str = salary_tag.get_text(strip=True) if salary_tag else "0"
                salary_low, salary_high = parse_salary(salary_str)

                exp_edu_tag = item.find("p", class_="order")
                if exp_edu_tag:
                    exp_edu = exp_edu_tag.get_text(strip=True).split('|')
                    experience = exp_edu[1].strip() if len(exp_edu) > 1 else "不限"
                    education = exp_edu[2].strip() if len(exp_edu) > 2 else "不限"
                else:
                    experience = "不限"
                    education = "不限"

                desc_tag = item.find("p", class_="text")
                skills = desc_tag.get_text(strip=True) if desc_tag else ""
                skill_keywords = ["护理", "养老", "健康", "医疗", "持证", "经验", "耐心"]
                extracted_skills = [kw for kw in skill_keywords if kw in skills]
                skills_str = ",".join(extracted_skills) if extracted_skills else "无明确要求"

                job_data = JobData(
                    job_name=job_name,
                    company=company,
                    city=city_text,
                    salary_low=salary_low,
                    salary_high=salary_high,
                    experience=experience,
                    education=education,
                    skills=skills_str
                )
                db.session.add(job_data)
            
            db.session.commit()
            print(f"已爬取第{page}页，获取{len(job_items)}条数据")
        except Exception as e:
            print(f"爬取第{page}页失败：{str(e)}")
            db.session.rollback()

# --------------------------
# 页面路由
# --------------------------
@app.route('/')
def index():
    # 检查模板文件是否存在
    template_path = os.path.join(WEB_FOLDER, 'index.html')
    if not os.path.exists(template_path):
        logger.error(f"index.html模板文件不存在: {template_path}")
        return "网站首页模板不存在", 500
    return render_template('index.html')

@app.route('/admin-login.html')
def admin_login_page():
    template_path = os.path.join(WEB_FOLDER, 'admin-login.html')
    if not os.path.exists(template_path):
        logger.error(f"admin-login.html模板文件不存在: {template_path}")
        return "管理员登录模板不存在", 500
    return render_template('admin-login.html')

@app.route('/user-register.html')
def user_register_page():
    template_path = os.path.join(WEB_FOLDER, 'user-register.html')
    if not os.path.exists(template_path):
        logger.error(f"user-register.html模板文件不存在: {template_path}")
        return "用户注册模板不存在", 500
    return render_template('user-register.html')

@app.route('/user-login.html')
def user_login_page():
    template_path = os.path.join(WEB_FOLDER, 'user-login.html')
    if not os.path.exists(template_path):
        logger.error(f"user-login.html模板文件不存在: {template_path}")
        return "用户登录模板不存在", 500
    return render_template('user-login.html')

@app.route('/caregiver-register.html')
def caregiver_register_page():
    # 检查模板文件是否存在
    template_path = os.path.join(WEB_FOLDER, 'caregiver-register.html')
    if not os.path.exists(template_path):
        logger.error(f"caregiver-register.html模板文件不存在: {template_path}")
        return "护工注册模板不存在", 500
    return render_template('caregiver-register.html')

@app.route('/caregiver-login.html')
def caregiver_login_page():
    template_path = os.path.join(WEB_FOLDER, 'caregiver-login.html')
    if not os.path.exists(template_path):
        logger.error(f"caregiver-login.html模板文件不存在: {template_path}")
        return "护工登录模板不存在", 500
    return render_template('caregiver-login.html')

@app.route('/admin-dashboard.html')
def admin_dashboard():
    if not (g.user and g.user.get('user_type') == 'admin'):
        return redirect(url_for('admin_login_page'))

    template_path = os.path.join(WEB_FOLDER, 'admin-dashboard.html')
    if not os.path.exists(template_path):
        logger.error(f"admin-dashboard.html模板文件不存在: {template_path}")
        return "管理员面板模板不存在", 500

    user_count = User.query.count()
    approved_user_count = User.query.filter_by(is_approved=True).count()
    pending_user_count = User.query.filter_by(is_approved=False).count()

    approved_caregiver_count = Caregiver.query.filter_by(is_approved=True).count()
    unapproved_caregiver_count = Caregiver.query.filter_by(is_approved=False).count()
    job_count = JobData.query.count()

    return render_template(
        'admin-dashboard.html',
        user_count=user_count,
        approved_user_count=approved_user_count,
        pending_user_count=pending_user_count,
        approved_caregiver_count=approved_caregiver_count,
        unapproved_caregiver_count=unapproved_caregiver_count,
        job_count=job_count
    )

@app.route('/admin-caregivers.html')
def admin_caregivers():
    if not (g.user and g.user.get('user_type') == 'admin'):
        return redirect(url_for('admin_login_page'))

    template_path = os.path.join(WEB_FOLDER, 'admin-caregivers.html')
    if not os.path.exists(template_path):
        logger.error(f"admin-caregivers.html模板文件不存在: {template_path}")
        return "管理员护工管理模板不存在", 500

    unapproved = DataStore.get_unapproved_caregivers()
    approved = DataStore.get_approved_caregivers()
    return render_template(
        'admin-caregivers.html',
        unapproved=unapproved,
        approved=approved
    )

@app.route('/admin-users.html')
def admin_users():
    if not (g.user and g.user.get('user_type') == 'admin'):
        return redirect(url_for('admin_login_page'))

    template_path = os.path.join(WEB_FOLDER, 'admin-users.html')
    if not os.path.exists(template_path):
        logger.error(f"admin-users.html模板文件不存在: {template_path}")
        return "管理员用户管理模板不存在", 500

    pending_users = DataStore.get_pending_users()
    approved_users = DataStore.get_approved_users()
    return render_template(
        'admin-users.html',
        pending=pending_users,
        approved=approved_users
    )

@app.route('/admin-job-analysis.html')
def admin_job_analysis():
    if not (g.user and g.user.get('user_type') == 'admin'):
        return redirect(url_for('admin_login_page'))

    template_path = os.path.join(WEB_FOLDER, 'admin-job-analysis.html')
    if not os.path.exists(template_path):
        logger.error(f"admin-job-analysis.html模板文件不存在: {template_path}")
        return "管理员职位分析模板不存在", 500

    salary_result = AnalysisResult.query.filter_by(type='salary_by_city').first()
    skill_result = AnalysisResult.query.filter_by(type='skill_counts').first()
    return render_template(
        'admin-job-analysis.html',
        salary=salary_result.result if salary_result else None,
        skills=skill_result.result if skill_result else None
    )

# 访问上传的文件
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # 安全检查，防止路径遍历攻击
    if '..' in filename or '/' in filename or '\\' in filename:
        logger.warning(f"尝试访问非法文件路径: {filename}")
        return "非法访问", 403
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --------------------------
# API接口
# --------------------------
@app.route('/api/login/admin', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

    if username == admin_username and password == admin_password:
        token = generate_token(0, 'admin')
        session['token'] = f'Bearer {token}'
        return jsonify({
            'success': True,
            'data': {'token': token},
            'message': '登录成功'
        })
    return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

# 用户身份证上传接口
@app.route('/api/user/upload-id', methods=['POST'])
def upload_user_id():
    if 'id-file' not in request.files:
        return jsonify({'success': False, 'message': '请上传身份证文件'}), 400

    id_file = request.files['id-file']

    if id_file.filename == '':
        return jsonify({'success': False, 'message': '文件不能为空'}), 400

    if not allowed_file(id_file.filename):
        return jsonify({'success': False, 'message': '仅支持png、jpg、jpeg、gif、pdf格式'}), 400

    if id_file.content_length == 0:
        return jsonify({'success': False, 'message': '文件内容不能为空'}), 400

    try:
        file_ext = id_file.filename.rsplit('.', 1)[1].lower()
        filename = f"user_id_{uuid.uuid4().hex}.{file_ext}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        id_file.save(file_path)
        
        # 验证文件是否保存成功
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            raise Exception("文件保存失败")
        
        return jsonify({
            'success': True,
            'data': {'id_file': filename},
            'message': '身份证上传成功'
        })
    except Exception as e:
        logger.error(f"用户身份证上传失败: {e}")
        return jsonify({'success': False, 'message': f'文件上传失败：{str(e)}'}), 500

# 用户注册接口
@app.route('/api/user/register', methods=['POST'])
def user_register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    id_file = data.get('id_file')

    if not email or '@' not in email:
        return jsonify({'success': False, 'message': '请输入有效的邮箱地址'}), 400

    if not password or len(password) < 6:
        return jsonify({'success': False, 'message': '密码长度不能少于6位'}), 400

    if not id_file or not id_file.strip():
        return jsonify({'success': False, 'message': '请上传身份证'}), 400

    if DataStore.get_user_by_email(email):
        return jsonify({'success': False, 'message': '邮箱已被注册'}), 400

    try:
        user = DataStore.add_user(email, password, id_file)
        return jsonify({
            'success': True,
            'data': user.to_dict(),
            'message': '注册成功，等待管理员审核'
        })
    except Exception as e:
        logger.error(f"用户注册失败: {e}")
        return jsonify({'success': False, 'message': f'注册失败：{str(e)}'}), 500

# 用户登录接口
@app.route('/api/user/login', methods=['POST'])
def user_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'success': False, 'message': '请输入邮箱和密码'}), 400

    user = DataStore.verify_user(email, password)
    if user:
        token = generate_token(user.id, 'user')
        return jsonify({
            'success': True,
            'data': {'token': token, 'user': user.to_dict()},
            'message': '登录成功'
        })
    elif DataStore.get_user_by_email(email) and not user:
        return jsonify({'success': False, 'message': '您的申请尚未通过审核'}), 403
    else:
        return jsonify({'success': False, 'message': '邮箱或密码错误'}), 401

# 护工证件文件上传接口（优化版）
@app.route('/api/caregiver/upload', methods=['POST'])
def upload_files():
    try:
        # 记录请求信息用于调试
        logger.info(f"收到文件上传请求，文件字段: {list(request.files.keys())}")

        # 检查是否有必要的文件字段
        if 'id_file' not in request.files:
            logger.warning("文件上传缺少 'id_file' 字段")
            return jsonify({'success': False, 'message': '请上传身份证照片文件'}), 400
        
        if 'cert_file' not in request.files:
            logger.warning("文件上传缺少 'cert_file' 字段")
            return jsonify({'success': False, 'message': '请上传护工等级证书文件'}), 400
        
        id_file = request.files['id_file']
        cert_file = request.files['cert_file']
        
        # 记录文件基本信息
        logger.info(f"身份证文件: {id_file.filename}, 大小: {id_file.content_length}")
        logger.info(f"证书文件: {cert_file.filename}, 大小: {cert_file.content_length}")
        
        # 添加调试信息
        logger.info(f"请求头: {request.headers}")
        logger.info(f"表单数据: {request.form}")
        logger.info(f"文件存储路径: {app.config['UPLOAD_FOLDER']}")
        logger.info(f"当前工作目录: {os.getcwd()}")
        logger.info(f"上传文件夹权限: {os.access(app.config['UPLOAD_FOLDER'], os.W_OK)}")
        
        # 检查文件名是否为空
        if id_file.filename == '':
            logger.warning("身份证文件名为空")
            return jsonify({'success': False, 'message': '身份证照片文件名为空，请选择有效的文件'}), 400
        
        if cert_file.filename == '':
            logger.warning("证书文件名为空")
            return jsonify({'success': False, 'message': '护工等级证书文件名为空，请选择有效的文件'}), 400
        
        # 检查文件格式
        if not allowed_file(id_file.filename):
            logger.warning(f"身份证文件格式不允许: {id_file.filename}")
            return jsonify({'success': False, 'message': '身份证照片仅支持png、jpg、jpeg、gif格式'}), 400
        
        if not allowed_file(cert_file.filename):
            logger.warning(f"证书文件格式不允许: {cert_file.filename}")
            return jsonify({'success': False, 'message': '护工等级证书仅支持png、jpg、jpeg、gif、pdf格式'}), 400
        
        # 文件内容检查将在保存后执行
        
        # 检查文件大小是否超过限制
        max_size = 16 * 1024 * 1024  # 16MB
        if id_file.content_length > max_size:
            logger.warning(f"身份证文件过大: {id_file.content_length} bytes")
            return jsonify({'success': False, 'message': '身份证照片文件过大，最大支持16MB'}), 400
        
        if cert_file.content_length > max_size:
            logger.warning(f"证书文件过大: {cert_file.content_length} bytes")
            return jsonify({'success': False, 'message': '护工等级证书文件过大，最大支持16MB'}), 400
        
        # 处理文件保存
        try:
            # 生成唯一文件名
            id_ext = id_file.filename.rsplit('.', 1)[1].lower()
            cert_ext = cert_file.filename.rsplit('.', 1)[1].lower()
            id_filename = f"id_{uuid.uuid4().hex}.{id_ext}"
            cert_filename = f"cert_{uuid.uuid4().hex}.{cert_ext}"
            
            id_path = os.path.join(app.config['UPLOAD_FOLDER'], id_filename)
            cert_path = os.path.join(app.config['UPLOAD_FOLDER'], cert_filename)
            
            # 保存文件 - 使用chunk方式保存大文件并记录实际写入大小
            id_size = 0
            with open(id_path, 'wb') as f:
                while chunk := id_file.read(4096):
                    actual_size = len(chunk)
                    id_size += actual_size
                    f.write(chunk)
            logger.info(f"身份证文件实际写入大小: {id_size}字节")
            
            cert_size = 0
            with open(cert_path, 'wb') as f:
                while chunk := cert_file.read(4096):
                    actual_size = len(chunk)
                    cert_size += actual_size
                    f.write(chunk)
            logger.info(f"证书文件实际写入大小: {cert_size}字节")
            
            # 验证文件是否保存成功（增强版检查）
            if not os.path.exists(id_path) or os.path.getsize(id_path) == 0:
                raise Exception("身份证文件保存失败或内容为空")
            
            if not os.path.exists(cert_path) or os.path.getsize(cert_path) == 0:
                # 清理已保存的身份证文件
                if os.path.exists(id_path):
                    os.remove(id_path)
                raise Exception("护工等级证书文件保存失败或内容为空")
                
            logger.info(f"文件上传成功: {id_filename}, {cert_filename}")
            return jsonify({
                'success': True,
                'data': {
                    'id_file': id_filename,
                    'cert_file': cert_filename
                },
                'message': '文件上传成功'
            })
            
        except Exception as e:
            logger.error(f"文件保存失败: {str(e)}")
            return jsonify({'success': False, 'message': f'文件保存失败：{str(e)}'}), 500
        
    except Exception as e:
        logger.error(f"文件上传处理异常: {str(e)}")
        return jsonify({'success': False, 'message': '服务器处理文件时发生错误'}), 500

# 护工入驻信息提交接口
@app.route('/api/caregiver/register', methods=['POST'])
def caregiver_register():
    try:
        data = request.json
        logger.info(f"收到护工注册信息: {data.get('phone')}")

        # 验证必要字段
        required_fields = ['name', 'phone', 'password', 'id_file', 'cert_file']
        for field in required_fields:
            if field not in data or not data[field] or not str(data[field]).strip():
                logger.warning(f"护工注册缺少必要字段: {field}")
                return jsonify({'success': False, 'message': f'请完善{field}信息'}), 400
        
        # 验证手机号格式
        if not data['phone'].startswith('1') or len(data['phone']) != 11:
            logger.warning(f"手机号格式错误: {data['phone']}")
            return jsonify({'success': False, 'message': '请输入有效的手机号'}), 400
        
        # 验证密码长度
        if len(data['password']) < 6:
            logger.warning(f"密码长度不足: {len(data['password'])}")
            return jsonify({'success': False, 'message': '密码长度不能少于6位'}), 400
        
        # 检查手机号是否已注册
        if DataStore.get_caregiver_by_phone(data['phone']):
            logger.warning(f"手机号已注册: {data['phone']}")
            return jsonify({'success': False, 'message': '该手机号已注册'}), 400
        
        # 创建护工记录
        caregiver = DataStore.add_caregiver({
            'name': data['name'],
            'phone': data['phone'],
            'password': data['password'],
            'id_file': data['id_file'],
            'cert_file': data['cert_file']
        })
        
        logger.info(f"护工注册成功: {caregiver.id}")
        return jsonify({
            'success': True,
            'data': caregiver.to_dict(),
            'message': '提交成功，等待管理员审核'
        })
        
    except Exception as e:
        logger.error(f"护工注册失败: {str(e)}")
        return jsonify({'success': False, 'message': f'提交失败：{str(e)}'}), 500


# 护工登录接口
@app.route('/api/caregiver/login', methods=['POST'])
def caregiver_login():
    data = request.json
    phone = data.get('phone')
    password = data.get('password')
    
    if not phone or not password:
        return jsonify({'success': False, 'message': '请输入手机号和密码'}), 400
    
    caregiver = DataStore.verify_caregiver(phone, password)
    if caregiver:
        token = generate_token(caregiver.id, 'caregiver')
        return jsonify({
            'success': True,
            'data': {'token': token, 'caregiver': caregiver.to_dict()},
            'message': '登录成功'
        })
    elif DataStore.get_caregiver_by_phone(phone) and not caregiver:
        return jsonify({'success': False, 'message': '您的申请尚未通过审核'}), 403
    else:
        return jsonify({'success': False, 'message': '手机号或密码错误'}), 401

# 退出登录
@app.route('/api/logout')
def logout():
    session.pop('token', None)
    return jsonify({'success': True, 'message': '已成功退出'})

# 管理员接口：获取待审核护工
@app.route('/api/admin/unapproved-caregivers')
def api_unapproved_caregivers():
    if not (g.user and g.user.get('user_type') == 'admin'):
        return jsonify({'success': False, 'message': '无权限'}), 403
    caregivers = DataStore.get_unapproved_caregivers()
    return jsonify({
        'success': True, 
        'data': [c.to_dict() for c in caregivers]
    })

# 管理员接口：批准护工
@app.route('/api/admin/approve', methods=['POST'])
def api_approve_caregiver():
    if not (g.user and g.user.get('user_type') == 'admin'):
        return jsonify({'success': False, 'message': '无权限'}), 403
    data = request.json
    caregiver_id = data.get('id')
    if not caregiver_id:
        return jsonify({'success': False, 'message': '请提供护工ID'}), 400
    
    success = DataStore.approve_caregiver(caregiver_id)
    if success:
        return jsonify({'success': True, 'message': '批准成功'})
    return jsonify({'success': False, 'message': '批准失败，护工不存在或已审核'}), 400

# 管理员接口：拒绝护工
@app.route('/api/admin/reject', methods=['POST'])
def api_reject_caregiver():
    if not (g.user and g.user.get('user_type') == 'admin'):
        return jsonify({'success': False, 'message': '无权限'}), 403
    data = request.json
    caregiver_id = data.get('id')
    if not caregiver_id:
        return jsonify({'success': False, 'message': '请提供护工ID'}), 400
    
    success = DataStore.reject_caregiver(caregiver_id)
    if success:
        return jsonify({'success': True, 'message': '拒绝成功'})
    return jsonify({'success': False, 'message': '拒绝失败，护工不存在或已审核'}), 400

# 管理员接口：用户管理相关
@app.route('/api/admin/pending-users')
def api_pending_users():
    if not (g.user and g.user.get('user_type') == 'admin'):
        return jsonify({'success': False, 'message': '无权限'}), 403
    users = DataStore.get_pending_users()
    return jsonify({
        'success': True, 
        'data': [u.to_dict() for u in users]
    })

@app.route('/api/admin/approved-users')
def api_approved_users():
    if not (g.user and g.user.get('user_type') == 'admin'):
        return jsonify({'success': False, 'message': '无权限'}), 403
    users = DataStore.get_approved_users()
    return jsonify({
        'success': True, 
        'data': [u.to_dict() for u in users]
    })

@app.route('/api/admin/approve-user', methods=['POST'])
def api_approve_user():
    if not (g.user and g.user.get('user_type') == 'admin'):
        return jsonify({'success': False, 'message': '无权限'}), 403
    data = request.json
    user_id = data.get('id')
    if not user_id:
        return jsonify({'success': False, 'message': '请提供用户ID'}), 400
    
    success = DataStore.approve_user(user_id)
    if success:
        return jsonify({'success': True, 'message': '用户批准成功'})
    return jsonify({'success': False, 'message': '批准失败，用户不存在或已审核'}), 400

@app.route('/api/admin/reject-user', methods=['POST'])
def api_reject_user():
    if not (g.user and g.user.get('user_type') == 'admin'):
        return jsonify({'success': False, 'message': '无权限'}), 403
    data = request.json
    user_id = data.get('id')
    if not user_id:
        return jsonify({'success': False, 'message': '请提供用户ID'}), 400
    
    success = DataStore.delete_user(user_id)
    if success:
        return jsonify({'success': True, 'message': '用户已拒绝并删除'})
    return jsonify({'success': False, 'message': '拒绝失败，用户不存在'}), 400

# 管理员接口：删除用户（已审核用户）
@app.route('/api/admin/delete-user', methods=['POST'])
def api_delete_user():
    if not (g.user and g.user.get('user_type') == 'admin'):
        return jsonify({'success': False, 'message': '无权限'}), 403
    data = request.json
    user_id = data.get('id')
    if not user_id:
        return jsonify({'success': False, 'message': '请提供用户ID'}), 400
    
    success = DataStore.delete_user(user_id)
    if success:
        return jsonify({'success': True, 'message': '删除成功'})
    return jsonify({'success': False, 'message': '删除失败，用户不存在'}), 400

# 职位数据爬取接口
@app.route('/api/job/crawl/start', methods=['POST'])
def start_crawl():
    if not (g.user and g.user.get('user_type') == 'admin'):
        return jsonify({'success': False, 'message': '无权限'}), 403
    data = request.json
    pages = int(data.get('pages', 5))
    city_code = data.get('city', '020000')
    
    if pages < 1 or pages > 20:
        return jsonify({'success': False, 'message': '爬取页数应在1-20之间'}), 400
    
    try:
        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.map(lambda p: crawl_page(p, city_code), range(1, pages+1))
        return jsonify({'success': True, 'message': f'已启动爬取{pages}页数据'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'爬取失败：{str(e)}'}), 500

# 薪资数据分析接口
@app.route('/api/job/analysis/salary')
def analyze_salary():
    if not (g.user and g.user.get('user_type') == 'admin'):
        return jsonify({'success': False, 'message': '无权限'}), 403
    job_datas = JobData.query.all()
    if not job_datas:
        return jsonify({'success': False, 'message': '无数据可分析，请先爬取职位数据'}), 400
    
    city_salary = {}
    for job in job_datas:
        if job.city not in city_salary:
            city_salary[job.city] = []
        avg_salary = (job.salary_low + job.salary_high) // 2
        city_salary[job.city].append(avg_salary)
    
    try:
        result = {
            'city_avg': {city: sum(sals)//len(sals) for city, sals in city_salary.items()},
            'total_avg': sum((sum(sals) for sals in city_salary.values())) // sum((len(sals) for sals in city_salary.values()))
        }
        
        analysis = AnalysisResult(type='salary_by_city', result=result)
        db.session.add(analysis)
        db.session.commit()
        return jsonify({'success': True, 'data': result, 'message': '薪资分析完成'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'分析失败：{str(e)}'}), 500

# 技能需求分析接口
@app.route('/api/job/analysis/skills')
def analyze_skills():
    if not (g.user and g.user.get('user_type') == 'admin'):
        return jsonify({'success': False, 'message': '无权限'}), 403
    job_datas = JobData.query.all()
    if not job_datas:
        return jsonify({'success': False, 'message': '无数据可分析，请先爬取职位数据'}), 400
    
    skill_counts = Counter()
    for job in job_datas:
        if job.skills and job.skills != "无明确要求":
            skills = job.skills.split(',')
            skill_counts.update(skills)
    
    try:
        result = {'skill_counts': dict(skill_counts.most_common(10))}
        analysis = AnalysisResult(type='skill_counts', result=result)
        db.session.add(analysis)
        db.session.commit()
        return jsonify({'success': True, 'data': result, 'message': '技能分析完成'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'分析失败：{str(e)}'}), 500

# --------------------------
# 初始化数据库
# --------------------------
with app.app_context():
    db.create_all()

# --------------------------
# 启动服务
# --------------------------
if __name__ == '__main__':
    # 启动前再次验证web文件夹
    if not os.path.exists(WEB_FOLDER):
        print(f"错误：web文件夹不存在于路径 {WEB_FOLDER}")
        print("请检查文件夹路径是否正确")
    else:
        print(f"成功找到web文件夹: {WEB_FOLDER}")
        print("模板文件列表:")
        for file in os.listdir(WEB_FOLDER):
            if file.endswith('.html'):
                print(f"- {file}")
    
    try:
        from waitress import serve
        print("使用waitress启动服务...")
        serve(app, host='0.0.0.0', port=8000)
    except ImportError:
        print("使用开发服务器启动...")
        app.run(debug=True, host='0.0.0.0', port=8000)
