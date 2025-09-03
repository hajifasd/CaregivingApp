#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建聊天记录数据库表脚本
用于在现有数据库中创建聊天记录相关的表结构
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_chat_tables():
    """创建聊天记录相关的数据库表"""
    try:
        print("🚀 开始创建聊天记录数据库表...")
        
        # 导入必要的模块
        from extensions import db
        from models.chat import ChatMessage, ChatConversation
        
        # 创建应用上下文
        from app import app
        
        with app.app_context():
            print("📋 正在创建聊天消息表...")
            ChatMessageModel = ChatMessage.get_model(db)
            
            print("📋 正在创建聊天对话表...")
            ChatConversationModel = ChatConversation.get_model(db)
            
            # 创建表
            db.create_all()
            
            print("✅ 聊天记录表创建完成！")
            
            # 显示表结构信息
            print("\n📊 表结构信息:")
            print(f"- chat_message: 聊天消息表")
            print(f"- chat_conversation: 聊天对话表")
            
            # 检查表是否创建成功
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'chat_message' in tables:
                print("✅ chat_message 表创建成功")
            else:
                print("❌ chat_message 表创建失败")
                
            if 'chat_conversation' in tables:
                print("✅ chat_conversation 表创建成功")
            else:
                print("❌ chat_conversation 表创建失败")
            
            return True
            
    except Exception as e:
        print(f"❌ 创建聊天记录表失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def insert_sample_data():
    """插入示例聊天数据"""
    try:
        print("\n📝 正在插入示例聊天数据...")
        
        from extensions import db
        from models.chat import ChatMessage, ChatConversation
        from datetime import datetime, timezone
        
        # 重新导入app以避免作用域问题
        from app import app
        
        with app.app_context():
            # 首先确保所有基础模型都被正确初始化
            print("📋 正在初始化基础模型...")
            from models.user import User
            from models.caregiver import Caregiver
            
            # 初始化基础模型
            UserModel = User.get_model(db)
            CaregiverModel = Caregiver.get_model(db)
            
            # 获取聊天模型
            ChatMessageModel = ChatMessage.get_model(db)
            ChatConversationModel = ChatConversation.get_model(db)
            
            # 检查基础表是否存在数据
            user_count = UserModel.query.count()
            caregiver_count = CaregiverModel.query.count()
            
            print(f"📊 数据库状态检查:")
            print(f"   - 用户表记录数: {user_count}")
            print(f"   - 护工表记录数: {caregiver_count}")
            
            # 如果没有基础数据，先创建一些测试数据
            if user_count == 0:
                print("📝 创建测试用户...")
                test_user = UserModel(
                    phone='17661895382',
                    name='张阿姨',
                    is_approved=True
                )
                db.session.add(test_user)
                db.session.flush()  # 获取ID但不提交
                user_id = test_user.id
                print(f"   - 创建测试用户: ID={user_id}")
            else:
                # 使用第一个用户
                user_id = UserModel.query.first().id
                print(f"   - 使用现有用户: ID={user_id}")
            
            if caregiver_count == 0:
                print("📝 创建测试护工...")
                test_caregiver = CaregiverModel(
                    phone='17661895381',
                    name='李敏',
                    is_approved=True
                )
                db.session.add(test_caregiver)
                db.session.flush()  # 获取ID但不提交
                caregiver_id = test_caregiver.id
                print(f"   - 创建测试护工: ID={caregiver_id}")
            else:
                # 使用第一个护工
                caregiver_id = CaregiverModel.query.first().id
                print(f"   - 使用现有护工: ID={caregiver_id}")
            
            # 创建示例对话
            conversation_id = f"{user_id}_{caregiver_id}"
            
            # 检查对话是否已存在
            existing_conversation = ChatConversationModel.query.filter_by(
                conversation_id=conversation_id
            ).first()
            
            if not existing_conversation:
                print(f"📝 创建聊天对话: {conversation_id}")
                # 创建对话记录
                conversation = ChatConversationModel(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    caregiver_id=caregiver_id,
                    last_message_content="您好，我想咨询一下老年护理服务",
                    last_message_time=datetime.now(timezone.utc),
                    unread_count=1,
                    is_active=True,
                    created_at=datetime.now(timezone.utc)
                )
                db.session.add(conversation)
                
                # 创建示例消息
                messages = [
                    {
                        'conversation_id': conversation_id,
                        'sender_id': user_id,
                        'sender_type': 'user',
                        'sender_name': '张阿姨',
                        'recipient_id': caregiver_id,
                        'recipient_type': 'caregiver',
                        'content': '您好，我想咨询一下老年护理服务',
                        'message_type': 'text',
                        'is_read': False,
                        'created_at': datetime.now(timezone.utc)
                    },
                    {
                        'conversation_id': conversation_id,
                        'sender_id': caregiver_id,
                        'sender_type': 'caregiver',
                        'sender_name': '李敏',
                        'recipient_id': user_id,
                        'recipient_type': 'user',
                        'content': '您好张阿姨，很高兴为您服务。请问您需要什么类型的护理服务？',
                        'message_type': 'text',
                        'is_read': True,
                        'created_at': datetime.now(timezone.utc)
                    },
                    {
                        'conversation_id': conversation_id,
                        'sender_id': user_id,
                        'sender_type': 'user',
                        'sender_name': '张阿姨',
                        'recipient_id': caregiver_id,
                        'recipient_type': 'caregiver',
                        'content': '我需要日常护理，包括生活照料和康复训练',
                        'message_type': 'text',
                        'is_read': False,
                        'created_at': datetime.now(timezone.utc)
                    }
                ]
                
                for msg_data in messages:
                    message = ChatMessageModel(**msg_data)
                    db.session.add(message)
                
                # 提交所有数据
                db.session.commit()
                print("✅ 示例聊天数据插入成功！")
                print(f"   - 创建了1个对话")
                print(f"   - 插入了{len(messages)}条消息")
            else:
                print("ℹ️ 示例数据已存在，跳过插入")
            
            return True
            
    except Exception as e:
        print(f"❌ 插入示例数据失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 护工资源管理系统 - 聊天记录表创建脚本")
    print("=" * 60)
    
    # 创建表
    if create_chat_tables():
        print("\n🎯 表创建完成！")
        
        # 询问是否插入示例数据
        try:
            choice = input("\n是否插入示例聊天数据？(y/n): ").strip().lower()
            if choice in ['y', 'yes', '是']:
                insert_sample_data()
        except KeyboardInterrupt:
            print("\n\n👋 用户取消操作")
        except Exception as e:
            print(f"\n❌ 插入示例数据时出错: {e}")
    else:
        print("\n💥 表创建失败！")
        sys.exit(1)
    
    print("\n🎉 脚本执行完成！")
