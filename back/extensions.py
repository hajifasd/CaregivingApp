"""
护工资源管理系统 - Flask扩展初始化
====================================

集中管理所有Flask扩展的初始化
"""

from flask_sqlalchemy import SQLAlchemy
import logging

logger = logging.getLogger(__name__)

# 初始化SQLAlchemy
db = SQLAlchemy()

def init_database(app):
    """初始化数据库连接"""
    try:
        with app.app_context():
            # 测试数据库连接
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
            logger.info("数据库连接成功")
            
            # 创建所有表
            db.create_all()
            logger.info("数据库表创建/更新完成")
            
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise

def test_database_connection():
    """测试数据库连接"""
    try:
        with db.engine.connect() as connection:
            connection.execute(db.text('SELECT 1'))
        return True
    except Exception as e:
        logger.error(f"数据库连接测试失败: {str(e)}")
        return False 