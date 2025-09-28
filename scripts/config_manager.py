#!/usr/bin/env python3
"""
护工资源管理系统 - 配置管理工具
====================================

提供配置检查、生成、验证等功能
"""

import os
import sys
import argparse
import secrets
import string
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / 'back'))

from back.config.config_validator import ConfigValidator

def generate_secure_config():
    """生成安全配置"""
    print("🔧 生成安全配置...")
    
    validator = ConfigValidator()
    config_content = validator.generate_secure_config()
    
    # 保存到文件
    config_file = project_root / '.env.secure'
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"✅ 安全配置已生成: {config_file}")
    print("📝 请检查配置内容并重命名为 .env")
    
    return config_file

def validate_current_config():
    """验证当前配置"""
    print("🔍 验证当前配置...")
    
    validator = ConfigValidator()
    result = validator.validate_environment()
    validator.print_validation_report(result)
    
    return result['is_valid']

def check_env_file():
    """检查环境变量文件"""
    print("📄 检查环境变量文件...")
    
    env_file = project_root / '.env'
    env_example = project_root / 'env.example'
    
    if not env_file.exists():
        print("❌ .env 文件不存在")
        if env_example.exists():
            print("💡 请复制 env.example 为 .env 并填入实际值")
            print(f"   命令: copy {env_example} {env_file}")
        return False
    
    print("✅ .env 文件存在")
    
    # 检查关键配置
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_vars = ['APP_SECRET', 'FLASK_SECRET_KEY', 'MYSQL_PASSWORD', 'ADMIN_PASSWORD']
    missing_vars = []
    
    for var in required_vars:
        if f"{var}=" not in content or f"{var}=your_" in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  以下配置项需要设置: {', '.join(missing_vars)}")
        return False
    
    print("✅ 关键配置项已设置")
    return True

def create_production_config():
    """创建生产环境配置"""
    print("🏭 创建生产环境配置...")
    
    # 生成强密码和密钥
    def generate_password(length=16):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def generate_secret(length=64):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    production_config = f"""# 护工资源管理系统 - 生产环境配置
# 生成时间: {os.popen('date /t & time /t').read().strip()}

# ==================== 安全配置 ====================
APP_SECRET={generate_secret()}
FLASK_SECRET_KEY={generate_secret()}

# ==================== 数据库配置 ====================
MYSQL_HOST=your_production_mysql_host
MYSQL_PORT=3306
MYSQL_USERNAME=your_production_mysql_user
MYSQL_PASSWORD={generate_password()}
MYSQL_DATABASE=caregiving_production

# ==================== 管理员配置 ====================
ADMIN_USERNAME=admin_{secrets.token_hex(4)}
ADMIN_PASSWORD={generate_password()}

# ==================== JWT配置 ====================
JWT_EXPIRATION_HOURS=2

# ==================== 邮件配置 ====================
SMTP_HOST=your_smtp_host
SMTP_PORT=587
SMTP_USERNAME=your_email@yourdomain.com
SMTP_PASSWORD={generate_password()}
SMTP_USE_TLS=true
TEMP_EMAIL_DOMAIN=temp.yourdomain.com

# ==================== 部署配置 ====================
FLASK_ENV=production
DEBUG=false
LOG_LEVEL=INFO
"""
    
    config_file = project_root / '.env.production'
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(production_config)
    
    print(f"✅ 生产环境配置已生成: {config_file}")
    print("📝 请根据实际情况修改数据库和邮件配置")
    
    return config_file

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='护工资源管理系统配置管理工具')
    parser.add_argument('action', choices=['validate', 'generate', 'check', 'production'], 
                       help='执行的操作')
    
    args = parser.parse_args()
    
    print("🚀 护工资源管理系统 - 配置管理工具")
    print("=" * 50)
    
    if args.action == 'validate':
        success = validate_current_config()
        sys.exit(0 if success else 1)
    
    elif args.action == 'generate':
        generate_secure_config()
    
    elif args.action == 'check':
        success = check_env_file()
        sys.exit(0 if success else 1)
    
    elif args.action == 'production':
        create_production_config()
    
    print("\n✅ 操作完成！")

if __name__ == "__main__":
    main()

