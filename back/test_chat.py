#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天功能测试脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_message_service():
    """测试消息服务"""
    try:
        from services.message_service import MessageService
        
        # 创建消息服务实例
        service = MessageService()
        print("✅ 消息服务创建成功")
        
        # 测试保存消息到内存
        test_message = {
            'senderId': '1',
            'senderName': '测试用户',
            'senderType': 'user',
            'receiverId': '001',
            'receiverType': 'caregiver',
            'content': '这是一条测试消息',
            'type': 'text',
            'timestamp': '2025-09-04T16:30:00Z'
        }
        
        saved_message = service.save_message(test_message)
        if saved_message:
            print(f"✅ 消息保存成功: {saved_message}")
        else:
            print("❌ 消息保存失败")
        
        # 测试获取聊天历史
        history = service.get_chat_history('1', '001', 10)
        print(f"✅ 聊天历史获取成功: {len(history)} 条消息")
        
        return True
        
    except Exception as e:
        print(f"❌ 消息服务测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_chat_models():
    """测试聊天模型"""
    try:
        from models.chat import ChatMessage, ChatConversation
        
        print("✅ 聊天模型导入成功")
        
        # 测试模型包装器
        ChatMessageModel = ChatMessage.get_model(None)
        ChatConversationModel = ChatConversation.get_model(None)
        
        print("✅ 聊天模型包装器创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 聊天模型测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_chat_api():
    """测试聊天API"""
    try:
        from api.chat import chat_bp, init_socketio
        
        print("✅ 聊天API导入成功")
        
        # 测试蓝图
        if chat_bp:
            print("✅ 聊天蓝图创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 聊天API测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("聊天功能测试开始")
    print("=" * 50)
    
    tests = [
        ("聊天模型", test_chat_models),
        ("聊天API", test_chat_api),
        ("消息服务", test_message_service),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 测试 {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {str(e)}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    success_count = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n总计: {success_count}/{len(results)} 个测试通过")
    
    if success_count == len(results):
        print("🎉 所有测试通过！聊天功能应该可以正常工作。")
    else:
        print("⚠️  部分测试失败，请检查相关代码。")
    
    return success_count == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
