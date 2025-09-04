#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket连接测试脚本
用于测试用户和护工的WebSocket连接和消息路由
"""

import socketio
import time
import threading

# 创建SocketIO客户端
user_socket = socketio.Client()
caregiver_socket = socketio.Client()

def test_user_connection():
    """测试用户端连接"""
    try:
        print("🔗 用户端正在连接...")
        user_socket.connect('http://localhost:8000')
        print("✅ 用户端连接成功")
        
        # 加入用户房间
        user_socket.emit('join', {'user_id': 'test_user_001', 'user_type': 'user'})
        print("🔗 用户正在加入房间...")
        
        # 监听事件
        @user_socket.on('joined_room')
        def on_joined_room(data):
            print(f"✅ 用户已加入房间: {data}")
        
        @user_socket.on('message_sent')
        def on_message_sent(data):
            print(f"✅ 用户消息发送确认: {data}")
        
        @user_socket.on('error')
        def on_error(data):
            print(f"❌ 用户端错误: {data}")
        
        return True
        
    except Exception as e:
        print(f"❌ 用户端连接失败: {e}")
        return False

def test_caregiver_connection():
    """测试护工端连接"""
    try:
        print("🔗 护工端正在连接...")
        caregiver_socket.connect('http://localhost:8000')
        print("✅ 护工端连接成功")
        
        # 加入护工房间
        caregiver_socket.emit('join', {'user_id': 'test_caregiver_001', 'user_type': 'caregiver'})
        print("🔗 护工正在加入房间...")
        
        # 监听事件
        @caregiver_socket.on('joined_room')
        def on_joined_room(data):
            print(f"✅ 护工已加入房间: {data}")
        
        @caregiver_socket.on('message_received')
        def on_message_received(data):
            print(f"📨 护工收到消息: {data}")
        
        @caregiver_socket.on('message_sent')
        def on_message_sent(data):
            print(f"✅ 护工消息发送确认: {data}")
        
        @caregiver_socket.on('error')
        def on_error(data):
            print(f"❌ 护工端错误: {data}")
        
        return True
        
    except Exception as e:
        print(f"❌ 护工端连接失败: {e}")
        return False

def test_message_sending():
    """测试消息发送"""
    try:
        print("\n📤 测试用户发送消息...")
        
        # 用户发送消息给护工
        message_data = {
            'sender_id': 'test_user_001',
            'sender_type': 'user',
            'sender_name': '测试用户',
            'recipient_id': 'test_caregiver_001',
            'recipient_type': 'caregiver',
            'content': f'测试消息 - {time.strftime("%H:%M:%S")}',
            'type': 'text'
        }
        
        user_socket.emit('send_message', message_data)
        print("📤 用户消息已发送")
        
        # 等待一段时间让消息处理
        time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f"❌ 消息发送测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始WebSocket连接测试...")
    
    # 测试用户端连接
    user_connected = test_user_connection()
    if not user_connected:
        print("❌ 用户端连接测试失败，退出")
        return
    
    # 等待一下
    time.sleep(1)
    
    # 测试护工端连接
    caregiver_connected = test_caregiver_connection()
    if not caregiver_connected:
        print("❌ 护工端连接测试失败，退出")
        return
    
    # 等待连接稳定
    time.sleep(2)
    
    # 测试消息发送
    if test_message_sending():
        print("✅ 消息发送测试完成")
    else:
        print("❌ 消息发送测试失败")
    
    # 保持连接一段时间观察结果
    print("\n⏳ 保持连接10秒观察结果...")
    time.sleep(10)
    
    # 断开连接
    print("\n🔌 断开连接...")
    user_socket.disconnect()
    caregiver_socket.disconnect()
    
    print("✅ 测试完成")

if __name__ == '__main__':
    main()
