from flask import Flask, render_template, redirect, url_for, g, request, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
import jwt
from datetime import datetime, timedelta, date, timezone
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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    approved_at = db.Column(db.DateTime, index=True)
    
    # 扩展用户信息字段
    name = db.Column(db.String(100))
    gender = db.Column(db.String(10))
    birth_date = db.Column(db.Date)
    address = db.Column(db.String(200))
    emergency_contact = db.Column(db.String(100))  # 紧急联系人姓名
    phone = db.Column(db.String(20))  # 用户本人电话（原emergency_phone修改为phone）
    emergency_contact_phone = db.Column(db.String(20))  # 新增：紧急联系人电话
    special_needs = db.Column(db.Text)
    avatar_url = db.Column(db.String(200))
    is_verified = db.Column(db.Boolean, default=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "id_file": self.id_file,
            "id_file_url": f"/uploads/{self.id_file}" if (self.id_file and self.id_file.strip()) else None,
            "is_approved": self.is_approved,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M"),
            "approved_at": self.approved_at.strftime("%Y-%m-%d %H:%M") if self.approved_at else None,
            # 扩展字段
            "name": self.name,
            "gender": self.gender,
            "birth_date": self.birth_date.strftime("%Y-%m-%d") if self.birth_date else None,
            "address": self.address,
            "emergency_contact": self.emergency_contact,
            "phone": self.phone,  # 用户本人电话
            "emergency_contact_phone": self.emergency_contact_phone,  # 紧急联系人电话
            "special_needs": self.special_needs,
            "avatar_url": self.avatar_url,
            "is_verified": self.is_verified
        }

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

class Caregiver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    id_file = db.Column(db.String(200), nullable=False)  # 不允许为空
    cert_file = db.Column(db.String(200), nullable=False)  # 不允许为空
    password_hash = db.Column(db.String(256), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    approved_at = db.Column(db.DateTime, index=True)
    
    # 扩展护工信息字段
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    avatar_url = db.Column(db.String(200))
    id_card = db.Column(db.String(18))  # 身份证号
    qualification = db.Column(db.String(100))  # 资格证书
    introduction = db.Column(db.Text)  # 个人介绍
    experience_years = db.Column(db.Integer)  # 工作年限
    hourly_rate = db.Column(db.Float)  # 时薪
    rating = db.Column(db.Float, default=0)  # 评分
    review_count = db.Column(db.Integer, default=0)  # 评价数量
    status = db.Column(db.String(20), default="pending")  # 状态
    available = db.Column(db.Boolean, default=True)  # 是否可用
    
    # 服务类型多对多关系
    service_types = db.relationship('ServiceType', secondary='caregiver_service', backref='caregivers')

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
            "approved_at": self.approved_at.strftime("%Y-%m-%d %H:%M") if self.approved_at else None,
            # 扩展字段
            "gender": self.gender,
            "age": self.age,
            "avatar_url": self.avatar_url,
            "id_card": self.id_card,
            "qualification": self.qualification,
            "introduction": self.introduction,
            "experience_years": self.experience_years,
            "hourly_rate": self.hourly_rate,
            "rating": self.rating,
            "review_count": self.review_count,
            "status": self.status,
            "available": self.available,
            "service_types": [st.name for st in self.service_types]
        }

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

class ServiceType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))

# 护工与服务类型的多对多关联表
caregiver_service = db.Table('caregiver_service',
    db.Column('caregiver_id', db.Integer, db.ForeignKey('caregiver.id'), primary_key=True),
    db.Column('service_type_id', db.Integer, db.ForeignKey('service_type.id'), primary_key=True)
)

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
    crawl_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class AnalysisResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    result = db.Column(db.JSON)
    create_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# 预约模型
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    caregiver_id = db.Column(db.Integer, db.ForeignKey('caregiver.id'), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default="pending")  # pending, confirmed, completed, cancelled
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 关联
    user = db.relationship('User', backref=db.backref('appointments', lazy=True))
    caregiver = db.relationship('Caregiver', backref=db.backref('appointments', lazy=True))

# 长期聘用模型
class Employment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    caregiver_id = db.Column(db.Integer, db.ForeignKey('caregiver.id'), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)  # 可以为空，表示长期有效
    frequency = db.Column(db.String(50))  # 每周几次
    duration_per_session = db.Column(db.String(20))  # 每次时长
    status = db.Column(db.String(20), default="active")  # active, terminated, completed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 关联
    user = db.relationship('User', backref=db.backref('employments', lazy=True))
    caregiver = db.relationship('Caregiver', backref=db.backref('employments', lazy=True))

# 消息模型
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, nullable=False)
    sender_type = db.Column(db.String(20), nullable=False)  # user, caregiver, admin
    recipient_id = db.Column(db.Integer, nullable=False)
    recipient_type = db.Column(db.String(20), nullable=False)  # user, caregiver, admin
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

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
        "exp": datetime.now(timezone.utc) + timedelta(hours=2)
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
    def get_user_by_id(user_id: int) -> Optional[User]:
        return User.query.get(user_id)

    @staticmethod
    def update_user_profile(user_id: int, data: dict) -> bool:
        user = User.query.get(user_id)
        if not user:
            return False
            
        # 更新可修改的字段，包含修改后的phone和新增的emergency_contact_phone
        updatable_fields = [
            'name', 'gender', 'birth_date', 'address',
            'emergency_contact', 'phone', 'emergency_contact_phone',
            'special_needs', 'avatar_url'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])
                
        db.session.commit()
        return True

    @staticmethod
    def update_user_password(user_id: int, old_password: str, new_password: str) -> bool:
        user = User.query.get(user_id)
        if not user or not verify_password(user.password_hash, old_password):
            return False
            
        user.password_hash = hash_password(new_password)
        db.session.commit()
        return True

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
        user.approved_at = datetime.now(timezone.utc)
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
    def get_caregiver_by_id(caregiver_id: int) -> Optional[Caregiver]:
        return Caregiver.query.get(caregiver_id)

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
    def get_approved_caregivers(filters: dict = None) -> List[Caregiver]:
        query = Caregiver.query.filter(
            Caregiver.is_approved == True,
            Caregiver.id_file != '',
            Caregiver.cert_file != ''
        )
        
        # 应用筛选条件
        if filters:
            if 'service_type' in filters and filters['service_type']:
                query = query.join(caregiver_service).join(ServiceType).filter(
                    ServiceType.name == filters['service_type']
                )
            if 'experience' in filters and filters['experience']:
                query = query.filter(Caregiver.experience_years >= int(filters['experience']))
            if 'min_rating' in filters and filters['min_rating']:
                query = query.filter(Caregiver.rating >= float(filters['min_rating']))
            if 'price_range' in filters and filters['price_range']:
                min_price, max_price = filters['price_range'].split('-')
                query = query.filter(
                    Caregiver.hourly_rate >= float(min_price),
                    Caregiver.hourly_rate <= float(max_price)
                )
        
        return query.order_by(
            Caregiver.approved_at.desc() if Caregiver.approved_at else Caregiver.created_at.desc()
        ).all()

    @staticmethod
    def approve_caregiver(caregiver_id: int) -> bool:
        caregiver = Caregiver.query.get(caregiver_id)
        if not caregiver or caregiver.is_approved:
            return False
        caregiver.is_approved = True
        caregiver.approved_at = datetime.now(timezone.utc)
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

    # 服务类型相关操作
    @staticmethod
    def get_all_service_types() -> List[ServiceType]:
        return ServiceType.query.all()

    # 预约相关操作
    @staticmethod
    def create_appointment(data: dict) -> Appointment:
        appointment = Appointment(
            user_id=data['user_id'],
            caregiver_id=data['caregiver_id'],
            service_type=data['service_type'],
            date=data['date'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            notes=data.get('notes', '')
        )
        db.session.add(appointment)
        db.session.commit()
        return appointment

    @staticmethod
    def get_user_appointments(user_id: int, status: str = None) -> List[Appointment]:
        query = Appointment.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Appointment.date.desc(), Appointment.start_time.desc()).all()

    @staticmethod
    def get_appointment_by_id(appointment_id: int) -> Optional[Appointment]:
        return Appointment.query.get(appointment_id)

    @staticmethod
    def cancel_appointment(appointment_id: int) -> bool:
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return False
            
        # 检查是否可以取消（例如：未过期）
        appointment_date = datetime.combine(appointment.date, appointment.start_time)
        if appointment_date < datetime.now():
            return False
            
        appointment.status = "cancelled"
        db.session.commit()
        return True

    @staticmethod
    def update_appointment_status(appointment_id: int, status: str) -> bool:
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return False
            
        valid_statuses = ["pending", "confirmed", "completed", "cancelled"]
        if status not in valid_statuses:
            return False
            
        appointment.status = status
        db.session.commit()
        return True

    # 聘用相关操作
    @staticmethod
    def create_employment(data: dict) -> Employment:
        employment = Employment(
            user_id=data['user_id'],
            caregiver_id=data['caregiver_id'],
            service_type=data['service_type'],
            start_date=data['start_date'],
            end_date=data.get('end_date'),
            frequency=data['frequency'],
            duration_per_session=data['duration_per_session'],
            notes=data.get('notes', '')
        )
        db.session.add(employment)
        db.session.commit()
        return employment

    @staticmethod
    def get_user_employments(user_id: int, status: str = None) -> List[Employment]:
        query = Employment.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Employment.start_date.desc()).all()

    @staticmethod
    def get_employment_by_id(employment_id: int) -> Optional[Employment]:
        return Employment.query.get(employment_id)

    @staticmethod
    def terminate_employment(employment_id: int) -> bool:
        employment = Employment.query.get(employment_id)
        if not employment:
            return False
            
        employment.status = "terminated"
        employment.end_date = date.today()
        db.session.commit()
        return True

    @staticmethod
    def update_employment_schedule(employment_id: int, data: dict) -> bool:
        employment = Employment.query.get(employment_id)
        if not employment:
            return False
            
        updatable_fields = ['frequency', 'duration_per_session', 'notes']
        for field in updatable_fields:
            if field in data:
                setattr(employment, field, data[field])
                
        db.session.commit()
        return True

    # 消息相关操作
    @staticmethod
    def send_message(data: dict) -> Message:
        message = Message(
            sender_id=data['sender_id'],
            sender_type=data['sender_type'],
            recipient_id=data['recipient_id'],
            recipient_type=data['recipient_type'],
            content=data['content']
        )
        db.session.add(message)
        db.session.commit()
        return message

    @staticmethod
    def get_user_messages(user_id: int) -> List[Message]:
        return Message.query.filter_by(
            recipient_id=user_id,
            recipient_type='user'
        ).order_by(Message.created_at.desc()).all()

    @staticmethod
    def get_message_by_id(message_id: int) -> Optional[Message]:
        return Message.query.get(message_id)

    @staticmethod
    def mark_message_as_read(message_id: int) -> bool:
        message = Message.query.get(message_id)
        if not message:
            return False
            
        message.is_read = True
        db.session.commit()
        return True

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

# 用户头像上传接口
@app.route('/api/user/upload-avatar', methods=['POST'])
def upload_user_avatar():
    if not g.user or g.user.get('user_type') != 'user':
        return jsonify({'success': False, 'message': '请先登录'}), 401
        
    if 'avatar' not in request.files:
        return jsonify({'success': False, 'message': '请上传头像文件'}), 400

    avatar = request.files['avatar']

    if avatar.filename == '':
        return jsonify({'success': False, 'message': '文件不能为空'}), 400

    if not allowed_file(avatar.filename):
        return jsonify({'success': False, 'message': '仅支持png、jpg、jpeg、gif格式'}), 400

    try:
        file_ext = avatar.filename.rsplit('.', 1)[1].lower()
        filename = f"avatar_{uuid.uuid4().hex}.{file_ext}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        avatar.save(file_path)
        
        # 更新用户头像URL
        user = DataStore.get_user_by_id(g.user.get('user_id'))
        if user:
            # 删除旧头像
            if user.avatar_url and user.avatar_url.startswith('/uploads/'):
                old_filename = user.avatar_url.split('/')[-1]
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], old_filename)
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except Exception as e:
                        logger.warning(f"删除旧头像失败: {e}")
            
            user.avatar_url = f"/uploads/{filename}"
            db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {'avatar_url': f"/uploads/{filename}"},
            'message': '头像上传成功'
        })
    except Exception as e:
        logger.error(f"用户头像上传失败: {e}")
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

# 获取用户个人信息
@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    if not g.user or g.user.get('user_type') != 'user':
        return jsonify({'success': False, 'message': '请先登录'}), 401
        
    user = DataStore.get_user_by_id(g.user.get('user_id'))
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
        
    return jsonify({
        'success': True,
        'data': user.to_dict()
    })

# 更新用户个人信息
@app.route('/api/user/profile', methods=['PUT'])
def update_user_profile():
    if not g.user or g.user.get('user_type') != 'user':
        return jsonify({'success': False, 'message': '请先登录'}), 401
        
    data = request.json
    success = DataStore.update_user_profile(g.user.get('user_id'), data)
    
    if success:
        updated_user = DataStore.get_user_by_id(g.user.get('user_id'))
        return jsonify({
            'success': True,
            'data': updated_user.to_dict(),
            'message': '个人信息更新成功'
        })
    return jsonify({'success': False, 'message': '更新失败'}), 500

# 修改密码接口
@app.route('/api/user/password', methods=['PUT'])
def update_user_password():
    if not g.user or g.user.get('user_type') != 'user':
        return jsonify({'success': False, 'message': '请先登录'}), 401
        
    data = request.json
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password or len(new_password) < 6:
        return jsonify({'success': False, 'message': '请输入有效的密码信息'}), 400
        
    success = DataStore.update_user_password(
        g.user.get('user_id'), 
        old_password, 
        new_password
    )
    
    if success:
        return jsonify({
            'success': True,
            'message': '密码修改成功'
        })
    return jsonify({'success': False, 'message': '原密码错误或修改失败'}), 400

# 护工证件文件上传接口
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
            
            # 保存文件
            id_file.save(id_path)
            cert_file.save(cert_path)
            
            # 验证文件是否保存成功
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

# 护工查询与筛选接口
@app.route('/api/caregivers', methods=['GET'])
def get_caregivers():
    # 获取筛选参数
    filters = {
        'service_type': request.args.get('service_type'),
        'experience': request.args.get('experience'),
        'min_rating': request.args.get('min_rating'),
        'price_range': request.args.get('price_range')
    }
    
    # 过滤空值
    filters = {k: v for k, v in filters.items() if v is not None and v.strip() != ''}
    
    caregivers = DataStore.get_approved_caregivers(filters)
    return jsonify({
        'success': True,
        'data': [c.to_dict() for c in caregivers],
        'count': len(caregivers)
    })

# 获取护工详情接口
@app.route('/api/caregivers/<int:caregiver_id>', methods=['GET'])
def get_caregiver_detail(caregiver_id):
    caregiver = DataStore.get_caregiver_by_id(caregiver_id)
    if not caregiver or not caregiver.is_approved:
        return jsonify({'success': False, 'message': '护工不存在或未通过审核'}), 404
        
    return jsonify({
        'success': True,
        'data': caregiver.to_dict()
    })

# 获取服务类型列表
@app.route('/api/service-types', methods=['GET'])
def get_service_types():
    service_types = DataStore.get_all_service_types()
    return jsonify({
        'success': True,
        'data': [{'id': st.id, 'name': st.name, 'description': st.description} for st in service_types]
    })

# 创建预约接口
@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    if not g.user or g.user.get('user_type') != 'user':
        return jsonify({'success': False, 'message': '请先登录'}), 401
        
    data = request.json
    required_fields = ['caregiver_id', 'service_type', 'date', 'start_time', 'end_time']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'success': False, 'message': f'请提供{field}信息'}), 400
    
    try:
        # 转换日期时间格式
        appointment_data = {
            'user_id': g.user.get('user_id'),
            'caregiver_id': int(data['caregiver_id']),
            'service_type': data['service_type'],
            'date': datetime.strptime(data['date'], '%Y-%m-%d').date(),
            'start_time': datetime.strptime(data['start_time'], '%H:%M').time(),
            'end_time': datetime.strptime(data['end_time'], '%H:%M').time(),
            'notes': data.get('notes', '')
        }
        
        # 检查时间是否合理（结束时间晚于开始时间）
        if appointment_data['start_time'] >= appointment_data['end_time']:
            return jsonify({'success': False, 'message': '结束时间必须晚于开始时间'}), 400
            
        # 检查护工是否存在且已批准
        caregiver = DataStore.get_caregiver_by_id(appointment_data['caregiver_id'])
        if not caregiver or not caregiver.is_approved:
            return jsonify({'success': False, 'message': '护工不存在或未通过审核'}), 400
        
        appointment = DataStore.create_appointment(appointment_data)
        return jsonify({
            'success': True,
            'data': {
                'id': appointment.id,
                'status': appointment.status,
                'created_at': appointment.created_at.strftime('%Y-%m-%d %H:%M')
            },
            'message': '预约创建成功，等待护工确认'
        })
    except Exception as e:
        logger.error(f"创建预约失败: {e}")
        return jsonify({'success': False, 'message': f'创建预约失败：{str(e)}'}), 500

# 获取用户预约列表
@app.route('/api/user/appointments', methods=['GET'])
def get_user_appointments():
    if not g.user or g.user.get('user_type') != 'user':
        return jsonify({'success': False, 'message': '请先登录'}), 401
        
    status = request.args.get('status')
    appointments = DataStore.get_user_appointments(g.user.get('user_id'), status)
    
    # 格式化返回数据
    result = []
    for appt in appointments:
        caregiver = DataStore.get_caregiver_by_id(appt.caregiver_id)
        result.append({
            'id': appt.id,
            'caregiver': {
                'id': caregiver.id,
                'name': caregiver.name,
                'avatar_url': caregiver.avatar_url
            } if caregiver else None,
            'service_type': appt.service_type,
            'date': appt.date.strftime('%Y-%m-%d'),
            'start_time': appt.start_time.strftime('%H:%M'),
            'end_time': appt.end_time.strftime('%H:%M'),
            'status': appt.status,
            'notes': appt.notes,
            'created_at': appt.created_at.strftime('%Y-%m-%d %H:%M')
        })
        
    return jsonify({
        'success': True,
        'data': result,
        'count': len(result)
    })

# 取消预约接口
@app.route('/api/appointments/<int:appointment_id>/cancel', methods=['PUT'])
def cancel_appointment(appointment_id):
    if not g.user or g.user.get('user_type') != 'user':
        return jsonify({'success': False, 'message': '请先登录'}), 401
        
    appointment = DataStore.get_appointment_by_id(appointment_id)
    if not appointment:
        return jsonify({'success': False, 'message': '预约不存在'}), 404
        
    # 验证预约属于当前用户
    if appointment.user_id != g.user.get('user_id'):
        return jsonify({'success': False, 'message': '无权操作此预约'}), 403
        
    success = DataStore.cancel_appointment(appointment_id)
    if success:
        return jsonify({
            'success': True,
            'message': '预约已取消'
        })
    return jsonify({'success': False, 'message': '取消失败，可能已过期或状态不允许取消'}), 400

# 更新预约状态（护工确认）
@app.route('/api/appointments/<int:appointment_id>/status', methods=['PUT'])
def update_appointment_status(appointment_id):
    if not g.user or g.user.get('user_type') != 'caregiver':
        return jsonify({'success': False, 'message': '请先登录护工账号'}), 401
        
    data = request.json
    status = data.get('status')
    if not status:
        return jsonify({'success': False, 'message': '请提供状态信息'}), 400
        
    appointment = DataStore.get_appointment_by_id(appointment_id)
    if not appointment:
        return jsonify({'success': False, 'message': '预约不存在'}), 404
        
    # 验证预约属于当前护工
    if appointment.caregiver_id != g.user.get('user_id'):
        return jsonify({'success': False, 'message': '无权操作此预约'}), 403
        
    success = DataStore.update_appointment_status(appointment_id, status)
    if success:
        return jsonify({
            'success': True,
            'message': f'预约状态已更新为{status}'
        })
    return jsonify({'success': False, 'message': '更新状态失败'}), 400

# 创建长期聘用接口
@app.route('/api/employments', methods=['POST'])
def create_employment():
    if not g.user or g.user.get('user_type') != 'user':
        return jsonify({'success': False, 'message': '请先登录'}), 401
        
    data = request.json
    required_fields = ['caregiver_id', 'service_type', 'start_date', 'frequency', 'duration_per_session']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'success': False, 'message': f'请提供{field}信息'}), 400
    
    try:
        # 转换日期格式
        employment_data = {
            'user_id': g.user.get('user_id'),
            'caregiver_id': int(data['caregiver_id']),
            'service_type': data['service_type'],
            'start_date': datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            'end_date': datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
            'frequency': data['frequency'],
            'duration_per_session': data['duration_per_session'],
            'notes': data.get('notes', '')
        }
        
        # 检查护工是否存在且已批准
        caregiver = DataStore.get_caregiver_by_id(employment_data['caregiver_id'])
        if not caregiver or not caregiver.is_approved:
            return jsonify({'success': False, 'message': '护工不存在或未通过审核'}), 400
        
        employment = DataStore.create_employment(employment_data)
        return jsonify({
            'success': True,
            'data': {
                'id': employment.id,
                'status': employment.status,
                'created_at': employment.created_at.strftime('%Y-%m-%d %H:%M')
            },
            'message': '长期聘用关系创建成功'
        })
    except Exception as e:
        logger.error(f"创建长期聘用失败: {e}")
        return jsonify({'success': False, 'message': f'创建失败：{str(e)}'}), 500

# 获取用户聘用列表
@app.route('/api/user/employments', methods=['GET'])
def get_user_employments():
    if not g.user or g.user.get('user_type') != 'user':
        return jsonify({'success': False, 'message': '请先登录'}), 401
        
    status = request.args.get('status')
    employments = DataStore.get_user_employments(g.user.get('user_id'), status)
    
    # 格式化返回数据
    result = []
    for emp in employments:
        caregiver = DataStore.get_caregiver_by_id(emp.caregiver_id)
        result.append({
            'id': emp.id,
            'caregiver': {
                'id': caregiver.id,
                'name': caregiver.name,
                'avatar_url': caregiver.avatar_url
            } if caregiver else None,
            'service_type': emp.service_type,
            'start_date': emp.start_date.strftime('%Y-%m-%d'),
            'end_date': emp.end_date.strftime('%Y-%m-%d') if emp.end_date else None,
            'frequency': emp.frequency,
            'duration_per_session': emp.duration_per_session,
            'status': emp.status,
            'notes': emp.notes,
            'created_at': emp.created_at.strftime('%Y-%m-%d %H:%M')
        })
        
    return jsonify({
        'success': True,
        'data': result,
        'count': len(result)
    })

# 获取聘用详情
@app.route('/api/employments/<int:employment_id>', methods=['GET'])
def get_employment_detail(employment_id):
    if not g.user:
        return jsonify({'success': False, 'message': '请先登录'}), 401
        
    employment = DataStore.get_employment_by_id(employment_id)
    if not employment:
        return jsonify({'success': False, 'message': '聘用记录不存在'}), 404
        
    # 验证权限（用户或护工）
    if (g.user.get('user_type') == 'user' and employment.user_id != g.user.get('user_id')) or \
       (g.user.get('user_type') == 'caregiver' and employment.caregiver_id != g.user.get('user_id')):
        return jsonify({'success': False, 'message': '无权查看此聘用记录'}), 403
        
    caregiver = DataStore.get_caregiver_by_id(employment.caregiver_id)
    user = DataStore.get_user_by_id(employment.user_id)
    
    return jsonify({
        'success': True,
        'data': {
            'id': employment.id,
            'caregiver': {
                'id': caregiver.id,
                'name': caregiver.name,
                'avatar_url': caregiver.avatar_url,
                'phone': caregiver.phone
            } if caregiver else None,
            'user': {
                'id': user.id,
                'name': user.name,
                'phone': user.phone  # 这里使用用户本人电话
            } if user else None,
            'service_type': employment.service_type,
            'start_date': employment.start_date.strftime('%Y-%m-%d'),
            'end_date': employment.end_date.strftime('%Y-%m-%d') if employment.end_date else None,
            'frequency': employment.frequency,
            'duration_per_session': employment.duration_per_session,
            'status': employment.status,
            'notes': employment.notes,
            'created_at': employment.created_at.strftime('%Y-%m-%d %H:%M')
        }
    })

# 终止聘用接口
@app.route('/api/employments/<int:employment_id>/terminate', methods=['PUT'])
def terminate_employment(employment_id):
    if not g.user or g.user.get('user_type') != 'user':
        return jsonify({'success': False, 'message': '请先登录'}), 401
        
    employment = DataStore.get_employment_by_id(employment_id)
    if not employment:
        return jsonify({'success': False, 'message': '聘用记录不存在'}), 404
        
    # 验证属于当前用户
    if employment.user_id != g.user.get('user_id'):
        return jsonify({'success': False, 'message': '无权操作此聘用记录'}), 403
        
    # 检查是否已终止
    if employment.status == 'terminated':
        return jsonify({'success': False, 'message': '此聘用记录已终止'}), 400
        
    success = DataStore.terminate_employment(employment_id)
    if success:
        return jsonify({
            'success': True,
            'message': '长期聘用已终止'
        })
    return jsonify({'success': False, 'message': '操作失败'}), 500

# 调整服务安排
@app.route('/api/employments/<int:employment_id>/schedule', methods=['PUT'])
def update_employment_schedule(employment_id):
    if not g.user or g.user.get('user_type') != 'user':
        return jsonify({'success': False, 'message': '请先登录'}), 401
        
    employment = DataStore.get_employment_by_id(employment_id)
    if not employment:
        return jsonify({'success': False, 'message': '聘用记录不存在'}), 404
        
    # 验证属于当前用户
    if employment.user_id != g.user.get('user_id'):
        return jsonify({'success': False, 'message': '无权操作此聘用记录'}), 403
        
    # 检查是否已终止
    if employment.status == 'terminated':
        return jsonify({'success': False, 'message': '此聘用记录已终止，无法调整'}), 400
        
    data = request.json
    update_data = {
        'frequency': data.get('frequency'),
        'duration_per_session': data.get('duration_per_session'),
        'notes': data.get('notes')
    }
    
    # 过滤空值
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    if not update_data:
        return jsonify({'success': False, 'message': '请提供需要更新的信息'}), 400
        
    success = DataStore.update_employment_schedule(employment_id, update_data)
    if success:
        return jsonify({
            'success': True,
            'message': '服务安排已更新'
        })
    return jsonify({'success': False, 'message': '操作失败'}), 500

# 获取消息列表
@app.route('/api/user/messages', methods=['GET'])
def get_user_messages():
    if not g.user or g.user.get('user_type') != 'user':
        return jsonify({'success': False, 'message': '请先登录'}), 401
        
    messages = DataStore.get_user_messages(g.user.get('user_id'))
    
    # 格式化返回数据
    result = []
    for msg in messages:
        # 获取发送方信息
        sender = None
        if msg.sender_type == 'caregiver':
            caregiver = DataStore.get_caregiver_by_id(msg.sender_id)
            if caregiver:
                sender = {
                    'id': caregiver.id,
                    'name': caregiver.name,
                    'avatar_url': caregiver.avatar_url,
                    'type': 'caregiver'
                }
        
        result.append({
            'id': msg.id,
            'sender': sender,
            'content': msg.content,
            'is_read': msg.is_read,
            'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M')
        })
        
    return jsonify({
        'success': True,
        'data': result,
        'unread_count': sum(1 for msg in messages if not msg.is_read),
        'total_count': len(result)
    })

# 获取消息详情
@app.route('/api/user/messages/<int:message_id>', methods=['GET'])
def get_message_detail(message_id):
    if not g.user or g.user.get('user_type') != 'user':
        return jsonify({'success': False, 'message': '请先登录'}), 401
        
    message = DataStore.get_message_by_id(message_id)
    if not message or message.recipient_id != g.user.get('user_id') or message.recipient_type != 'user':
        return jsonify({'success': False, 'message': '消息不存在或无权查看'}), 404
        
    # 标记为已读
    if not message.is_read:
        DataStore.mark_message_as_read(message_id)
        
    # 获取发送方信息
    sender = None
    if message.sender_type == 'caregiver':
        caregiver = DataStore.get_caregiver_by_id(message.sender_id)
        if caregiver:
            sender = {
                'id': caregiver.id,
                'name': caregiver.name,
                'avatar_url': caregiver.avatar_url,
                'type': 'caregiver'
            }
    
    return jsonify({
        'success': True,
        'data': {
            'id': message.id,
            'sender': sender,
            'content': message.content,
            'is_read': message.is_read,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M')
        }
    })

# 发送消息接口
@app.route('/api/user/messages', methods=['POST'])
def send_message():
    if not g.user or g.user.get('user_type') != 'user':
        return jsonify({'success': False, 'message': '请先登录'}), 401
        
    data = request.json
    recipient_id = data.get('recipient_id')
    content = data.get('content')
    
    if not recipient_id or not content:
        return jsonify({'success': False, 'message': '请提供接收方ID和消息内容'}), 400
        
    # 检查接收方是否存在
    caregiver = DataStore.get_caregiver_by_id(recipient_id)
    if not caregiver or not caregiver.is_approved:
        return jsonify({'success': False, 'message': '接收方不存在或未通过审核'}), 400
        
    try:
        message = DataStore.send_message({
            'sender_id': g.user.get('user_id'),
            'sender_type': 'user',
            'recipient_id': recipient_id,
            'recipient_type': 'caregiver',
            'content': content
        })
        
        return jsonify({
            'success': True,
            'data': {
                'id': message.id,
                'created_at': message.created_at.strftime('%Y-%m-%d %H:%M')
            },
            'message': '消息发送成功'
        })
    except Exception as e:
        logger.error(f"发送消息失败: {e}")
        return jsonify({'success': False, 'message': f'发送失败：{str(e)}'}), 500

# --------------------------
# 初始化数据库和示例数据
# --------------------------
def initialize_sample_data():
    with app.app_context():
        # 检查是否已有数据
        if ServiceType.query.count() > 0:
            print("示例数据已存在，跳过初始化")
            return
        
        print("开始初始化示例数据...")
        
        # 添加服务类型
        service_types = [
            ServiceType(name="老年护理", description="为老年人提供日常照料和护理服务"),
            ServiceType(name="母婴护理", description="为产妇和新生儿提供专业护理服务"),
            ServiceType(name="医疗护理", description="提供专业医疗护理服务，包括术后护理等"),
            ServiceType(name="康复护理", description="为需要康复的人士提供专业康复训练和护理")
        ]
        db.session.add_all(service_types)
        db.session.commit()
        print(f"已添加 {len(service_types)} 种服务类型")
        
        # 添加示例用户（修改phone字段）
        user = User(
            email="user@example.com",
            name="张阿姨",
            gender="女",
            birth_date=date(1965, 8, 12),
            address="北京市朝阳区建国路88号",
            emergency_contact="李小明（儿子）",
            phone="13800138000",  # 用户本人电话
            emergency_contact_phone="13900139000",  # 紧急联系人电话
            special_needs="本人需要定期进行康复护理，希望护工有相关经验，每周一、三、五上午需要服务。",
            avatar_url="https://picsum.photos/id/64/120/120",
            is_verified=True,
            is_approved=True,
            approved_at=datetime.now(timezone.utc)
        )
        user.set_password("123456")
        db.session.add(user)
        db.session.commit()
        print(f"已添加示例用户: {user.name}")
        
        # 添加示例护工
        caregiver1 = Caregiver(
            name="李敏",
            phone="13700137001",
            gender="女",
            age=45,
            avatar_url="https://picsum.photos/id/26/120/120",
            id_card="1101011978XXXX1234",
            qualification="高级护理证书",
            introduction="擅长老年日常护理、康复辅助，有耐心，责任心强，持有专业护理证书。",
            experience_years=5,
            hourly_rate=180.0,
            rating=4.8,
            review_count=126,
            status="approved",
            available=True,
            is_approved=True,
            approved_at=datetime.now(timezone.utc)
        )
        caregiver1.set_password("123456")
        caregiver1.service_types = [service_types[0], service_types[3]]  # 老年护理、康复护理
        
        caregiver2 = Caregiver(
            name="王芳",
            phone="13700137002",
            gender="女",
            age=38,
            avatar_url="https://picsum.photos/id/91/120/120",
            id_card="1101021985XXXX5678",
            qualification="高级母婴护理师证书",
            introduction="专业母婴护理师，擅长新生儿照料、产后恢复指导，服务细致周到。",
            experience_years=8,
            hourly_rate=220.0,
            rating=4.9,
            review_count=98,
            status="approved",
            available=True,
            is_approved=True,
            approved_at=datetime.now(timezone.utc)
        )
        caregiver2.set_password("123456")
        caregiver2.service_types = [service_types[1]]  # 母婴护理
        
        caregiver3 = Caregiver(
            name="张伟",
            phone="13700137003",
            gender="男",
            age=50,
            avatar_url="https://picsum.photos/id/177/120/120",
            id_card="1101031973XXXX9012",
            qualification="护师资格证",
            introduction="原医院护士，擅长术后护理、医疗辅助，熟悉各种医疗设备使用。",
            experience_years=10,
            hourly_rate=260.0,
            rating=4.7,
            review_count=76,
            status="approved",
            available=True,
            is_approved=True,
            approved_at=datetime.now(timezone.utc)
        )
        caregiver3.set_password("123456")
        caregiver3.service_types = [service_types[2], service_types[3]]  # 医疗护理、康复护理
        
        db.session.add_all([caregiver1, caregiver2, caregiver3])
        db.session.commit()
        print(f"已添加 {3} 名护工")
        
        # 添加示例预约
        appointment1 = Appointment(
            user_id=user.id,
            caregiver_id=caregiver1.id,
            service_type="老年护理",
            date=date(2023, 10, 15),
            start_time=datetime.strptime("09:00", "%H:%M").time(),
            end_time=datetime.strptime("11:00", "%H:%M").time(),
            notes="请携带血压计",
            status="confirmed"
        )
        
        appointment2 = Appointment(
            user_id=user.id,
            caregiver_id=caregiver2.id,
            service_type="母婴护理咨询",
            date=date(2023, 10, 18),
            start_time=datetime.strptime("14:00", "%H:%M").time(),
            end_time=datetime.strptime("16:00", "%H:%M").time(),
            status="pending"
        )
        
        appointment3 = Appointment(
            user_id=user.id,
            caregiver_id=caregiver3.id,
            service_type="术后护理",
            date=date(2023, 10, 8),
            start_time=datetime.strptime("10:00", "%H:%M").time(),
            end_time=datetime.strptime("13:00", "%H:%M").time(),
            status="completed"
        )
        
        db.session.add_all([appointment1, appointment2, appointment3])
        db.session.commit()
        print(f"已添加 {3} 条预约记录")
        
        # 添加示例长期聘用
        employment = Employment(
            user_id=user.id,
            caregiver_id=caregiver1.id,
            service_type="老年护理",
            start_date=date(2023, 9, 1),
            frequency="每周3次",
            duration_per_session="2小时",
            status="active",
            notes="主要提供日常照料和简单康复训练"
        )
        
        db.session.add(employment)
        db.session.commit()
        print(f"已添加 {1} 条长期聘用记录")
        
        # 添加示例消息
        message1 = Message(
            sender_id=caregiver1.id,
            sender_type="caregiver",
            recipient_id=user.id,
            recipient_type="user",
            content="您好，我看到了您的预约请求，10月15日上午9点可以为您提供服务",
            created_at=datetime(2023, 10, 10, 9, 15, tzinfo=timezone.utc)
        )
        
        message2 = Message(
            sender_id=user.id,
            sender_type="user",
            recipient_id=caregiver1.id,
            recipient_type="caregiver",
            content="好的，非常感谢！到时候需要准备什么吗？",
            is_read=True,
            created_at=datetime(2023, 10, 10, 9, 20, tzinfo=timezone.utc)
        )
        
        message3 = Message(
            sender_id=caregiver1.id,
            sender_type="caregiver",
            recipient_id=user.id,
            recipient_type="user",
            content="已确认您10月15日的预约，我会准时到达。请准备好您的医保卡和既往病史资料即可。",
            created_at=datetime(2023, 10, 10, 9, 23, tzinfo=timezone.utc)
        )
        
        db.session.add_all([message1, message2, message3])
        db.session.commit()
        print(f"已添加 {3} 条消息记录")
        
        print("示例数据初始化完成")

# 创建数据库表并初始化示例数据
with app.app_context():
    db.create_all()
    # 初始化示例数据（仅在首次运行时执行）
    initialize_sample_data()

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
