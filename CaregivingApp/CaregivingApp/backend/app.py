from flask import Flask, render_template, redirect, url_for, g, request, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from collections import Counter
import uuid  
import bcrypt  

# 配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "../web/uploads")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
APP_SECRET = "caregiving-system-secret-key-2024"  # 生产环境请更换
DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, "caregiving.db"))

# 初始化Flask应用
app = Flask(
    __name__,
    static_folder='../web',        
    static_url_path='/',          
    template_folder='../web'     
)
app.config['SECRET_KEY'] = 'your_unique_secret_key'  # 随机复杂字符串
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB文件限制
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 初始化数据库
db = SQLAlchemy(app)

# --------------------------
# 数据模型
# --------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M")
        }

class Caregiver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)  # 新增：手机号唯一
    id_file = db.Column(db.String(200), nullable=False)  
    cert_file = db.Column(db.String(200), nullable=False)  
    password_hash = db.Column(db.String(256), nullable=False)  # 新增：护工密码
    is_approved = db.Column(db.Boolean, default=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "id_file": self.id_file,
            "cert_file": self.cert_file,
            "id_file_url": f"/uploads/{self.id_file}",  
            "cert_file_url": f"/uploads/{self.cert_file}",  
            "is_approved": self.is_approved,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M")
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
    """验证文件类型是否允许上传"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hash_password(password: str) -> str:
    """使用bcrypt加密密码"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(hashed_password: str, input_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(input_password.encode(), hashed_password.encode())

def generate_token(user_id: int, user_type: str = 'user') -> str:
    """生成JWT令牌，区分用户类型"""
    payload = {
        "user_id": user_id,
        "user_type": user_type,  # 'user' 或 'caregiver' 或 'admin'
        "exp": datetime.utcnow() + timedelta(hours=2)  
    }
    return jwt.encode(payload, APP_SECRET, algorithm="HS256")

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """验证JWT令牌"""
    try:
        return jwt.decode(token, APP_SECRET, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

# 请求钩子：验证登录状态
@app.before_request
def check_login_status():
    g.user = None
    # 不需要登录的页面
    public_routes = [
        'index', 'admin_login_page', 'static', 
        'user_register_page', 'caregiver_register_page',
        'user_login_page', 'caregiver_login_page'
    ]
    if request.endpoint in public_routes:
        return
    
    # 验证token
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
    def add_user(email: str, password: str) -> User:
        user = User(email=email, password_hash=hash_password(password))
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        return User.query.filter_by(email=email).first()

    @staticmethod
    def verify_user(email: str, password: str) -> Optional[User]:
        user = User.query.filter_by(email=email).first()
        if user and verify_password(user.password_hash, password):
            return user
        return None

    @staticmethod
    def get_all_users() -> List[User]:
        return User.query.all()

    @staticmethod
    def delete_user(user_id: int) -> bool:
        user = User.query.get(user_id)
        if not user:
            return False
        db.session.delete(user)
        db.session.commit()
        return True

    # 护工相关操作
    @staticmethod
    def add_caregiver(data: Dict[str, Any]) -> Caregiver:
        """添加护工信息（包含密码）"""
        caregiver = Caregiver(
            name=data['name'],
            phone=data['phone'],
            id_file=data['id_file'],
            cert_file=data['cert_file'],
            password_hash=hash_password(data['password'])  # 存储加密后的密码
        )
        db.session.add(caregiver)
        db.session.commit()
        return caregiver

    @staticmethod
    def get_caregiver_by_phone(phone: str) -> Optional[Caregiver]:
        """通过手机号查询护工"""
        return Caregiver.query.filter_by(phone=phone).first()

    @staticmethod
    def verify_caregiver(phone: str, password: str) -> Optional[Caregiver]:
        """验证护工登录信息"""
        caregiver = Caregiver.query.filter_by(phone=phone).first()
        if caregiver and caregiver.is_approved and verify_password(caregiver.password_hash, password):
            return caregiver
        return None

    @staticmethod
    def get_unapproved_caregivers() -> List[Caregiver]:
        return Caregiver.query.filter_by(is_approved=False).all()

    @staticmethod
    def get_approved_caregivers() -> List[Caregiver]:
        return Caregiver.query.filter_by(is_approved=True).all()

    @staticmethod
    def approve_caregiver(caregiver_id: int) -> bool:
        caregiver = Caregiver.query.get(caregiver_id)
        if not caregiver or caregiver.is_approved:
            return False
        caregiver.is_approved = True
        db.session.commit()
        return True

    @staticmethod
    def reject_caregiver(caregiver_id: int) -> bool:
        caregiver = Caregiver.query.get(caregiver_id)
        if not caregiver or caregiver.is_approved:
            return False
        db.session.delete(caregiver)
        db.session.commit()
        return True

# --------------------------
# 爬虫逻辑
# --------------------------
def parse_salary(salary_str: str) -> (int, int):
    """解析薪资字符串为整数范围（元/月）"""
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
    """爬取单页职位数据（适配前程无忧）"""
    with app.app_context():
        try:
            url = f"https://search.51job.com/list/{city_code},000000,0000,00,9,99,护工,2,{page}.html"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                "Referer": "https://www.51job.com/"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'gbk'  # 适配网站编码
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取职位列表
            job_list = soup.find("div", class_="j_joblist")
            if not job_list:
                return

            job_items = job_list.find_all("div", class_="el")
            for item in job_items:
                # 职位名称
                job_name_tag = item.find("span", class_="jname at")
                job_name = job_name_tag.get_text(strip=True) if job_name_tag else "未知职位"

                # 公司名称
                company_tag = item.find("a", class_="cname at")
                company = company_tag.get_text(strip=True) if company_tag else "未知公司"

                # 工作城市
                city_tag = item.find("span", class_="d at")
                city_text = city_tag.get_text(strip=True).split('|')[0] if city_tag else "未知城市"

                # 薪资
                salary_tag = item.find("span", class_="sal")
                salary_str = salary_tag.get_text(strip=True) if salary_tag else "0"
                salary_low, salary_high = parse_salary(salary_str)

                # 经验和学历
                exp_edu_tag = item.find("p", class_="order")
                if exp_edu_tag:
                    exp_edu = exp_edu_tag.get_text(strip=True).split('|')
                    experience = exp_edu[1].strip() if len(exp_edu) > 1 else "不限"
                    education = exp_edu[2].strip() if len(exp_edu) > 2 else "不限"
                else:
                    experience = "不限"
                    education = "不限"

                # 技能要求
                desc_tag = item.find("p", class_="text")
                skills = desc_tag.get_text(strip=True) if desc_tag else ""
                skill_keywords = ["护理", "养老", "健康", "医疗", "持证", "经验", "耐心"]
                extracted_skills = [kw for kw in skill_keywords if kw in skills]
                skills_str = ",".join(extracted_skills) if extracted_skills else "无明确要求"

                # 保存到数据库
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
    """系统首页"""
    return render_template('index.html')

@app.route('/admin-login.html')
def admin_login_page():
    """管理员登录页"""
    return render_template('admin-login.html')

@app.route('/user-register.html')
def user_register_page():
    """用户注册页面"""
    return render_template('user-register.html')

@app.route('/user-login.html')
def user_login_page():
    """用户登录页面"""
    return render_template('user-login.html')

@app.route('/caregiver-register.html')
def caregiver_register_page():
    """护工入驻页面"""
    return render_template('caregiver-register.html')

@app.route('/caregiver-login.html')
def caregiver_login_page():
    """护工登录页面"""
    return render_template('caregiver-login.html')

@app.route('/admin-dashboard.html')
def admin_dashboard():
    """管理员仪表盘"""
    if not (g.user and g.user.get('user_type') == 'admin'):
        return redirect(url_for('admin_login_page'))
    
    # 统计数据
    user_count = User.query.count()
    approved_count = Caregiver.query.filter_by(is_approved=True).count()
    unapproved_count = Caregiver.query.filter_by(is_approved=False).count()
    job_count = JobData.query.count()
    
    return render_template(
        'admin-dashboard.html',
        user_count=user_count,
        approved_count=approved_count,
        unapproved_count=unapproved_count,
        job_count=job_count
    )

@app.route('/admin-caregivers.html')
def admin_caregivers():
    """护工管理页"""
    if not (g.user and g.user.get('user_type') == 'admin'):
        return redirect(url_for('admin_login_page'))
    
    unapproved = DataStore.get_unapproved_caregivers()
    approved = DataStore.get_approved_caregivers()
    return render_template(
        'admin-caregivers.html',
        unapproved=unapproved,
        approved=approved
    )

@app.route('/admin-users.html')
def admin_users():
    """用户管理页"""
    if not (g.user and g.user.get('user_type') == 'admin'):
        return redirect(url_for('admin_login_page'))
    
    users = DataStore.get_all_users()
    return render_template('admin-users.html', users=users)

@app.route('/admin-job-analysis.html')
def admin_job_analysis():
    """就业数据分析页"""
    if not (g.user and g.user.get('user_type') == 'admin'):
        return redirect(url_for('admin_login_page'))
    
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
    """前端访问上传的证件文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --------------------------
# API接口
# --------------------------
@app.route('/api/login/admin', methods=['POST'])
def admin_login():
    """管理员登录接口"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # 管理员验证（实际项目应从数据库查询）
    if username == 'admin' and password == 'admin123':
        token = generate_token(0, 'admin')
        session['token'] = f'Bearer {token}'  # 保存到session
        return jsonify({
            'success': True,
            'data': {'token': token},
            'message': '登录成功'
        })
    return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

# 用户注册接口
@app.route('/api/user/register', methods=['POST'])
def user_register():
    """用户注册接口"""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    # 校验邮箱格式
    if not email or '@' not in email:
        return jsonify({'success': False, 'message': '请输入有效的邮箱地址'}), 400
    
    # 校验密码长度
    if not password or len(password) < 6:
        return jsonify({'success': False, 'message': '密码长度不能少于6位'}), 400
    
    # 校验邮箱是否已存在
    if DataStore.get_user_by_email(email):
        return jsonify({'success': False, 'message': '邮箱已被注册'}), 400
    
    # 存储用户信息
    try:
        user = DataStore.add_user(email, password)
        return jsonify({
            'success': True,
            'data': user.to_dict(),
            'message': '注册成功'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'注册失败：{str(e)}'}), 500

# 用户登录接口
@app.route('/api/user/login', methods=['POST'])
def user_login():
    """用户登录接口"""
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
    return jsonify({'success': False, 'message': '邮箱或密码错误'}), 401

# 护工证件文件上传接口
@app.route('/api/caregiver/upload', methods=['POST'])
def upload_files():
    """护工证件文件上传接口"""
    # 检查文件是否存在
    if 'id-info' not in request.files or 'cert-info' not in request.files:
        return jsonify({'success': False, 'message': '请上传身份证和资格证文件'}), 400
    
    id_file = request.files['id-info']
    cert_file = request.files['cert-info']
    
    # 检查文件是否为空
    if id_file.filename == '' or cert_file.filename == '':
        return jsonify({'success': False, 'message': '文件不能为空'}), 400
    
    # 验证文件类型
    if not (allowed_file(id_file.filename) and allowed_file(cert_file.filename)):
        return jsonify({'success': False, 'message': '仅支持png、jpg、jpeg、gif、pdf格式'}), 400
    
    try:
        # 生成唯一文件名（避免重复）
        id_ext = id_file.filename.rsplit('.', 1)[1].lower()
        cert_ext = cert_file.filename.rsplit('.', 1)[1].lower()
        id_filename = f"id_{uuid.uuid4()}.{id_ext}"
        cert_filename = f"cert_{uuid.uuid4()}.{cert_ext}"
        
        # 保存文件
        id_file.save(os.path.join(app.config['UPLOAD_FOLDER'], id_filename))
        cert_file.save(os.path.join(app.config['UPLOAD_FOLDER'], cert_filename))
        
        return jsonify({
            'success': True,
            'data': {
                'id_file': id_filename,
                'cert_file': cert_filename
            },
            'message': '文件上传成功'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'文件上传失败：{str(e)}'}), 500

# 护工入驻信息提交接口
@app.route('/api/caregiver/register', methods=['POST'])
def caregiver_register():
    """护工入驻信息提交接口"""
    data = request.json
    # 接收前端提交的信息
    name = data.get('name')
    phone = data.get('phone')
    password = data.get('password')
    id_file = data.get('id_file')
    cert_file = data.get('cert_file')
    
    # 校验必填字段
    if not all([name, phone, password, id_file, cert_file]):
        return jsonify({'success': False, 'message': '请完善所有信息'}), 400
    
    # 校验手机号格式
    if not phone or not phone.startswith('1') or len(phone) != 11:
        return jsonify({'success': False, 'message': '请输入有效的手机号'}), 400
    
    # 校验密码长度
    if len(password) < 6:
        return jsonify({'success': False, 'message': '密码长度不能少于6位'}), 400
    
    # 校验手机号是否已注册
    if DataStore.get_caregiver_by_phone(phone):
        return jsonify({'success': False, 'message': '该手机号已注册'}), 400
    
    # 存储护工信息（待审核状态）
    try:
        caregiver = DataStore.add_caregiver({
            'name': name,
            'phone': phone,
            'password': password,
            'id_file': id_file,
            'cert_file': cert_file
        })
        return jsonify({
            'success': True,
            'data': caregiver.to_dict(),
            'message': '提交成功，等待管理员审核'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'提交失败：{str(e)}'}), 500

# 护工登录接口
@app.route('/api/caregiver/login', methods=['POST'])
def caregiver_login():
    """护工登录接口"""
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
    """退出登录"""
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

# 管理员接口：删除用户
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
    pages = int(data.get('pages', 5))  # 爬取页数
    city_code = data.get('city', '020000')  # 城市代码（020000=广州）
    
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
    
    # 按城市统计平均薪资
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
        
        # 保存分析结果
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
    
    # 统计技能出现次数
    skill_counts = Counter()
    for job in job_datas:
        if job.skills and job.skills != "无明确要求":
            skills = job.skills.split(',')
            skill_counts.update(skills)
    
    try:
        result = {'skill_counts': dict(skill_counts.most_common(10))}  # 前10技能
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
    db.create_all()  # 首次运行创建表

# --------------------------
# 启动服务
# --------------------------
if __name__ == '__main__':
    try:
        from waitress import serve
        print("使用waitress启动服务...")
        serve(app, host='0.0.0.0', port=8000)
    except ImportError:
        print("使用开发服务器启动...")
        app.run(debug=True, host='0.0.0.0', port=8000)
