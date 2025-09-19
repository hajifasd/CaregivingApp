#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库索引优化脚本
为常用查询字段添加索引，提高查询性能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_indexes():
    """创建数据库索引"""
    try:
        logger.info("开始创建数据库索引...")
        
        with app.app_context():
            with db.engine.connect() as connection:
                # 用户表索引
                logger.info("创建用户表索引...")
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);"))
                
                # 护工表索引
                logger.info("创建护工表索引...")
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_caregivers_phone ON caregivers(phone);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_caregivers_status ON caregivers(status);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_caregivers_is_approved ON caregivers(is_approved);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_caregivers_created_at ON caregivers(created_at);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_caregivers_experience_years ON caregivers(experience_years);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_caregivers_rating ON caregivers(rating);"))
                
                # 消息表索引
                logger.info("创建消息表索引...")
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON messages(sender_id);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_messages_recipient_id ON messages(recipient_id);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_messages_sender_type ON messages(sender_type);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_messages_recipient_type ON messages(recipient_type);"))
                
                # 通知表索引
                logger.info("创建通知表索引...")
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);"))
                
                # 预约表索引
                logger.info("创建预约表索引...")
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_appointments_user_id ON appointments(user_id);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_appointments_caregiver_id ON appointments(caregiver_id);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_appointments_start_time ON appointments(start_time);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_appointments_created_at ON appointments(created_at);"))
                
                # 就业申请表索引
                logger.info("创建就业申请表索引...")
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_employment_applications_user_id ON employment_applications(user_id);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_employment_applications_caregiver_id ON employment_applications(caregiver_id);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_employment_applications_status ON employment_applications(status);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_employment_applications_created_at ON employment_applications(created_at);"))
                
                # 就业合同表索引
                logger.info("创建就业合同表索引...")
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_employment_contracts_user_id ON employment_contracts(user_id);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_employment_contracts_caregiver_id ON employment_contracts(caregiver_id);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_employment_contracts_status ON employment_contracts(status);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_employment_contracts_created_at ON employment_contracts(created_at);"))
                
                # 护工招聘信息表索引
                logger.info("创建护工招聘信息表索引...")
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_caregiver_hire_info_caregiver_id ON caregiver_hire_info(caregiver_id);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_caregiver_hire_info_service_type ON caregiver_hire_info(service_type);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_caregiver_hire_info_status ON caregiver_hire_info(status);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_caregiver_hire_info_created_at ON caregiver_hire_info(created_at);"))
                
                # 聊天对话表索引
                logger.info("创建聊天对话表索引...")
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_chat_conversations_user_id ON chat_conversations(user_id);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_chat_conversations_caregiver_id ON chat_conversations(caregiver_id);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_chat_conversations_created_at ON chat_conversations(created_at);"))
                
                # 服务记录表索引
                logger.info("创建服务记录表索引...")
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_service_records_contract_id ON service_records(contract_id);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_service_records_service_date ON service_records(service_date);"))
                connection.execute(db.text("CREATE INDEX IF NOT EXISTS idx_service_records_created_at ON service_records(created_at);"))
                
                connection.commit()
                logger.info("✅ 所有数据库索引创建完成")
                
    except Exception as e:
        logger.error(f"❌ 创建索引失败: {str(e)}")
        raise

def analyze_tables():
    """分析表性能"""
    try:
        logger.info("开始分析表性能...")
        
        with app.app_context():
            with db.engine.connect() as connection:
                # 获取所有表名
                result = connection.execute(db.text("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_SCHEMA = DATABASE()
                """))
                
                tables = [row[0] for row in result]
                
                for table in tables:
                    logger.info(f"分析表: {table}")
                    try:
                        # 分析表
                        connection.execute(db.text(f"ANALYZE TABLE {table}"))
                        logger.info(f"✅ 表 {table} 分析完成")
                    except Exception as e:
                        logger.warning(f"⚠️ 表 {table} 分析失败: {str(e)}")
                
                logger.info("✅ 所有表性能分析完成")
                
    except Exception as e:
        logger.error(f"❌ 分析表性能失败: {str(e)}")
        raise

def show_index_info():
    """显示索引信息"""
    try:
        logger.info("显示数据库索引信息...")
        
        with app.app_context():
            with db.engine.connect() as connection:
                result = connection.execute(db.text("""
                    SELECT 
                        TABLE_NAME,
                        INDEX_NAME,
                        COLUMN_NAME,
                        NON_UNIQUE
                    FROM INFORMATION_SCHEMA.STATISTICS 
                    WHERE TABLE_SCHEMA = DATABASE()
                    ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX
                """))
                
                current_table = None
                for row in result:
                    table_name, index_name, column_name, non_unique = row
                    
                    if table_name != current_table:
                        current_table = table_name
                        logger.info(f"\n📋 表: {table_name}")
                    
                    unique_text = "唯一" if non_unique == 0 else "非唯一"
                    logger.info(f"  📌 {index_name} ({column_name}) - {unique_text}")
                
                logger.info("\n✅ 索引信息显示完成")
                
    except Exception as e:
        logger.error(f"❌ 显示索引信息失败: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        logger.info("🚀 开始数据库索引优化...")
        
        # 创建索引
        create_indexes()
        
        # 分析表性能
        analyze_tables()
        
        # 显示索引信息
        show_index_info()
        
        logger.info("🎉 数据库索引优化完成！")
        
    except Exception as e:
        logger.error(f"💥 数据库索引优化失败: {str(e)}")
        sys.exit(1)