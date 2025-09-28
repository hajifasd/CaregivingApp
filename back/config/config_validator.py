"""
护工资源管理系统 - 配置验证器
====================================

提供配置验证、环境检查和安全提醒功能
"""

import os
import secrets
import string
from typing import Dict, List, Tuple
from datetime import datetime
from dotenv import load_dotenv

# 加载.env文件
try:
    load_dotenv(override=True, encoding='utf-8')
except Exception as e:
    print(f"⚠️  警告：加载.env文件失败: {e}")
    # 尝试其他编码
    try:
        load_dotenv(override=True, encoding='gbk')
    except Exception as e2:
        print(f"⚠️  警告：使用GBK编码加载.env文件也失败: {e2}")
        # 最后尝试默认编码
        load_dotenv(override=True)

class ConfigValidator:
    """配置验证器"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.suggestions = []
    
    def validate_environment(self) -> Dict[str, any]:
        """验证环境配置"""
        print("🔍 开始配置验证...")
        
        # 验证安全配置
        self._validate_security_config()
        
        # 验证数据库配置
        self._validate_database_config()
        
        # 验证管理员配置
        self._validate_admin_config()
        
        # 验证其他配置
        self._validate_other_config()
        
        return {
            'errors': self.errors,
            'warnings': self.warnings,
            'suggestions': self.suggestions,
            'is_valid': len(self.errors) == 0,
            'has_warnings': len(self.warnings) > 0
        }
    
    def _validate_security_config(self):
        """验证安全配置"""
        print("  🔐 验证安全配置...")
        
        # 检查APP_SECRET
        app_secret = os.getenv("APP_SECRET")
        print(f"    APP_SECRET: {'已设置' if app_secret else '未设置'}")
        if not app_secret:
            self.errors.append("❌ APP_SECRET 环境变量未设置")
        elif app_secret == "dev-secret-key-change-in-production":
            self.warnings.append("⚠️  APP_SECRET 使用默认值，生产环境不安全")
        elif len(app_secret) < 32:
            self.warnings.append("⚠️  APP_SECRET 长度不足32位，建议使用更长的密钥")
        else:
            print(f"    ✅ APP_SECRET 配置正确 (长度: {len(app_secret)})")
        
        # 检查FLASK_SECRET_KEY
        flask_secret = os.getenv("FLASK_SECRET_KEY")
        print(f"    FLASK_SECRET_KEY: {'已设置' if flask_secret else '未设置'}")
        if not flask_secret:
            self.errors.append("❌ FLASK_SECRET_KEY 环境变量未设置")
        elif flask_secret == "dev-flask-secret-key-change-in-production":
            self.warnings.append("⚠️  FLASK_SECRET_KEY 使用默认值，生产环境不安全")
        elif len(flask_secret) < 32:
            self.warnings.append("⚠️  FLASK_SECRET_KEY 长度不足32位，建议使用更长的密钥")
        else:
            print(f"    ✅ FLASK_SECRET_KEY 配置正确 (长度: {len(flask_secret)})")
    
    def _validate_database_config(self):
        """验证数据库配置"""
        print("  🗄️ 验证数据库配置...")
        
        # 检查数据库密码
        db_password = os.getenv("MYSQL_PASSWORD")
        if not db_password:
            self.errors.append("❌ MYSQL_PASSWORD 环境变量未设置")
        elif db_password == "20040924":
            self.warnings.append("⚠️  MYSQL_PASSWORD 使用默认值，生产环境不安全")
        elif len(db_password) < 8:
            self.warnings.append("⚠️  数据库密码长度不足8位，建议使用更强的密码")
        
        # 检查其他数据库配置
        required_db_vars = ["MYSQL_HOST", "MYSQL_PORT", "MYSQL_USERNAME", "MYSQL_DATABASE"]
        for var in required_db_vars:
            if not os.getenv(var):
                self.warnings.append(f"⚠️  {var} 环境变量未设置，将使用默认值")
    
    def _validate_admin_config(self):
        """验证管理员配置"""
        print("  👤 验证管理员配置...")
        
        # 检查管理员密码
        admin_password = os.getenv("ADMIN_PASSWORD")
        if not admin_password:
            self.errors.append("❌ ADMIN_PASSWORD 环境变量未设置")
        elif admin_password == "admin123":
            self.warnings.append("⚠️  ADMIN_PASSWORD 使用默认值，生产环境不安全")
        elif len(admin_password) < 8:
            self.warnings.append("⚠️  管理员密码长度不足8位，建议使用更强的密码")
        
        # 检查管理员用户名
        admin_username = os.getenv("ADMIN_USERNAME")
        if not admin_username:
            self.warnings.append("⚠️  ADMIN_USERNAME 环境变量未设置，将使用默认值")
        elif admin_username == "admin":
            self.warnings.append("⚠️  管理员用户名使用默认值，建议修改")
    
    def _validate_other_config(self):
        """验证其他配置"""
        print("  ⚙️ 验证其他配置...")
        
        # 检查JWT配置
        jwt_hours = os.getenv("JWT_EXPIRATION_HOURS")
        if jwt_hours:
            try:
                hours = int(jwt_hours)
                if hours < 1 or hours > 24:
                    self.warnings.append("⚠️  JWT_EXPIRATION_HOURS 建议设置为1-24小时之间")
            except ValueError:
                self.warnings.append("⚠️  JWT_EXPIRATION_HOURS 必须是数字")
    
    def generate_secure_config(self) -> str:
        """生成安全的配置建议"""
        print("  🔧 生成安全配置建议...")
        
        config_template = f"""# 护工资源管理系统 - 安全配置建议
# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# 安全配置 - 请替换为您的实际值
APP_SECRET={self._generate_secret_key()}
FLASK_SECRET_KEY={self._generate_secret_key()}

# 数据库配置 - 请替换为您的实际值
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USERNAME=your_mysql_username
MYSQL_PASSWORD={self._generate_password()}
MYSQL_DATABASE=caregiving_db

# 管理员配置 - 请替换为您的实际值
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD={self._generate_password()}

# JWT配置
JWT_EXPIRATION_HOURS=2

# 邮件配置 - 新增
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your_email@example.com
SMTP_PASSWORD=your_email_password
TEMP_EMAIL_DOMAIN=temp.caregiving.com
"""
        return config_template
    
    def _generate_secret_key(self, length: int = 64) -> str:
        """生成安全密钥"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def _generate_password(self, length: int = 16) -> str:
        """生成安全密码"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def print_validation_report(self, result: Dict[str, any]):
        """打印验证报告"""
        print("\n" + "="*60)
        print("📋 配置验证报告")
        print("="*60)
        
        if result['errors']:
            print("\n❌ 错误 (必须修复):")
            for error in result['errors']:
                print(f"  {error}")
        
        if result['warnings']:
            print("\n⚠️  警告 (建议修复):")
            for warning in result['warnings']:
                print(f"  {warning}")
        
        if result['suggestions']:
            print("\n💡 建议:")
            for suggestion in result['suggestions']:
                print(f"  {suggestion}")
        
        if result['is_valid']:
            if result['has_warnings']:
                print("\n✅ 配置基本可用，但建议修复警告项")
            else:
                print("\n🎉 配置验证通过！")
        else:
            print("\n❌ 配置验证失败，请修复错误项")
        
        print("="*60)

def validate_config():
    """验证配置的主函数"""
    validator = ConfigValidator()
    result = validator.validate_environment()
    validator.print_validation_report(result)
    return result

if __name__ == "__main__":
    validate_config()
