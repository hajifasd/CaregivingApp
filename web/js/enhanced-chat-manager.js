/**
 * 增强的聊天管理器 - 实现用户与护工的实时通信
 * ================================================
 */

class EnhancedChatManager {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.currentRoom = null;
        this.currentContact = null;
        this.messageHistory = new Map(); // 存储每个联系人的消息历史
        this.typingUsers = new Set();
        this.connectionRetries = 0;
        this.maxRetries = 5;
        this.retryDelay = 1000;
        
        // 绑定事件
        this.bindEvents();
        
        // 初始化连接
        this.initSocket();
    }
    
    /**
     * 初始化Socket.IO连接
     */
    initSocket() {
        try {
            console.log('🔌 初始化WebSocket连接...');
            
            // 优先使用全局Socket管理器
            if (window.SocketManager && window.SocketManager.socket) {
                this.socket = window.SocketManager.socket;
                console.log('✅ EnhancedChatManager使用全局Socket管理器');
            } else {
                // 备用方案：创建新连接
                const socketUrl = window.SERVER_CONFIG ? window.SERVER_CONFIG.socketUrl : 'http://localhost:8000';
                const config = window.SERVER_CONFIG ? window.SERVER_CONFIG.socketConfig : {
                    transports: ['websocket', 'polling'],
                    timeout: 10000,
                    reconnection: true,
                    reconnectionAttempts: 5,
                    reconnectionDelay: 1000
                };
                
                // 添加认证信息
                const token = localStorage.getItem('user_token') || localStorage.getItem('caregiver_token') || localStorage.getItem('admin_token');
                if (token) {
                    config.auth = { token: token };
                }
                
                this.socket = io(socketUrl, config);
                console.log('🔌 EnhancedChatManager创建新的Socket连接:', socketUrl);
            }
            
            this.bindSocketEvents();
            
        } catch (error) {
            console.error('❌ Socket.IO连接失败:', error);
            this.handleConnectionError();
        }
    }
    
    /**
     * 绑定Socket事件
     */
    bindSocketEvents() {
        if (!this.socket) return;
        
        // 连接成功
        this.socket.on('connect', () => {
            console.log('✅ WebSocket连接成功');
            this.isConnected = true;
            this.connectionRetries = 0;
            this.updateConnectionStatus(true);
            this.authenticate();
        });
        
        // 连接断开
        this.socket.on('disconnect', (reason) => {
            console.log('❌ WebSocket连接断开:', reason);
            this.isConnected = false;
            this.updateConnectionStatus(false);
            
            // 如果不是主动断开，尝试重连
            if (reason !== 'io client disconnect') {
                this.handleConnectionError();
            }
        });
        
        // 连接错误
        this.socket.on('connect_error', (error) => {
            console.error('❌ WebSocket连接错误:', error);
            this.handleConnectionError();
        });
        
        // 认证成功
        this.socket.on('authenticated', (data) => {
            console.log('✅ 认证成功:', data);
            this.showNotification('聊天服务已连接', 'success');
        });
        
        // 认证失败
        this.socket.on('auth_error', (data) => {
            console.error('❌ 认证失败:', data);
            this.showNotification('聊天服务认证失败', 'error');
        });
        
        // 新消息
        this.socket.on('message_received', (message) => {
            this.handleNewMessage(message);
        });
        
        // 消息发送成功
        this.socket.on('message_sent', (data) => {
            this.handleMessageSent(data);
        });
        
        // 用户正在输入
        this.socket.on('user_typing', (data) => {
            this.handleUserTyping(data);
        });
        
        // 用户停止输入
        this.socket.on('user_stopped_typing', (data) => {
            this.handleUserStoppedTyping(data);
        });
        
        // 消息已读
        this.socket.on('message_read', (data) => {
            this.handleMessageRead(data);
        });
        
        // 用户上线
        this.socket.on('user_online', (data) => {
            this.updateUserStatus(data.userId, 'online');
        });
        
        // 用户下线
        this.socket.on('user_offline', (data) => {
            this.updateUserStatus(data.userId, 'offline');
        });
        
        // 错误处理
        this.socket.on('error', (data) => {
            console.error('❌ Socket错误:', data);
            this.showNotification(data.message || '聊天服务错误', 'error');
        });
    }
    
    /**
     * 认证用户
     */
    authenticate() {
        if (!this.socket || !this.isConnected) return;
        
        try {
            const token = localStorage.getItem('user_token') || this.getCookie('user_token');
            if (!token) {
                console.warn('⚠️ 未找到用户token，无法认证');
                return;
            }
            
            // 解析token获取用户信息
            const payload = this.parseJWT(token);
            if (!payload) {
                console.error('❌ 无法解析用户token');
                return;
            }
            
            const userInfo = {
                userId: payload.user_id,
                userType: payload.user_type || 'user',
                userName: payload.username || '用户'
            };
            
            console.log('🔐 发送认证信息:', userInfo);
            this.socket.emit('authenticate', userInfo);
            
        } catch (error) {
            console.error('❌ 认证失败:', error);
        }
    }
    
    /**
     * 加入聊天房间
     */
    joinRoom(contactId, contactType = 'caregiver') {
        if (!this.socket || !this.isConnected) {
            console.warn('⚠️ WebSocket未连接，无法加入房间');
            return;
        }
        
        try {
            const roomId = `${contactType}_${contactId}`;
            console.log(`🚪 加入房间: ${roomId}`);
            
            this.socket.emit('join', {
                room: roomId,
                contactId: contactId,
                contactType: contactType
            });
            
            this.currentRoom = roomId;
            this.currentContact = { id: contactId, type: contactType };
            
        } catch (error) {
            console.error('❌ 加入房间失败:', error);
        }
    }
    
    /**
     * 离开聊天房间
     */
    leaveRoom() {
        if (!this.socket || !this.isConnected || !this.currentRoom) return;
        
        try {
            console.log(`🚪 离开房间: ${this.currentRoom}`);
            this.socket.emit('leave', { room: this.currentRoom });
            
            this.currentRoom = null;
            this.currentContact = null;
            
        } catch (error) {
            console.error('❌ 离开房间失败:', error);
        }
    }
    
    /**
     * 发送消息
     */
    sendMessage(content, type = 'text') {
        if (!this.socket || !this.isConnected) {
            console.warn('⚠️ WebSocket未连接，无法发送消息');
            this.showNotification('聊天服务未连接，请刷新页面重试', 'error');
            return false;
        }
        
        if (!this.currentContact) {
            console.warn('⚠️ 未选择聊天对象');
            return false;
        }
        
        try {
            const token = localStorage.getItem('user_token') || this.getCookie('user_token');
            const payload = this.parseJWT(token);
            
            if (!payload) {
                console.error('❌ 无法获取用户信息');
                return false;
            }
            
            const messageData = {
                sender_id: payload.user_id,
                sender_name: payload.username || '用户',
                sender_type: payload.user_type || 'user',
                recipient_id: this.currentContact.id,
                recipient_type: this.currentContact.type,
                content: content,
                type: type,
                timestamp: new Date().toISOString()
            };
            
            console.log('📤 发送消息:', messageData);
            this.socket.emit('send_message', messageData);
            
            // 添加消息到本地历史
            this.addMessageToHistory(messageData);
            
            return true;
            
        } catch (error) {
            console.error('❌ 发送消息失败:', error);
            this.showNotification('消息发送失败', 'error');
            return false;
        }
    }
    
    /**
     * 处理新消息
     */
    handleNewMessage(message) {
        console.log('📥 收到新消息:', message);
        
        // 添加消息到历史记录
        this.addMessageToHistory(message);
        
        // 更新UI
        this.updateMessageUI(message);
        
        // 播放提示音
        this.playNotificationSound();
        
        // 显示桌面通知
        this.showDesktopNotification(message);
    }
    
    /**
     * 处理消息发送成功
     */
    handleMessageSent(data) {
        console.log('✅ 消息发送成功:', data);
        this.updateMessageStatus(data.id, 'sent');
    }
    
    /**
     * 处理用户正在输入
     */
    handleUserTyping(data) {
        if (data.userId !== this.currentContact?.id) return;
        
        this.typingUsers.add(data.userId);
        this.updateTypingIndicator();
    }
    
    /**
     * 处理用户停止输入
     */
    handleUserStoppedTyping(data) {
        if (data.userId !== this.currentContact?.id) return;
        
        this.typingUsers.delete(data.userId);
        this.updateTypingIndicator();
    }
    
    /**
     * 处理消息已读
     */
    handleMessageRead(data) {
        console.log('👁️ 消息已读:', data);
        this.updateMessageStatus(data.messageId, 'read');
    }
    
    /**
     * 发送正在输入状态
     */
    sendTypingStatus() {
        if (!this.socket || !this.isConnected || !this.currentContact) return;
        
        this.socket.emit('typing', {
            contactId: this.currentContact.id,
            contactType: this.currentContact.type
        });
    }
    
    /**
     * 发送停止输入状态
     */
    sendStopTypingStatus() {
        if (!this.socket || !this.isConnected || !this.currentContact) return;
        
        this.socket.emit('stop_typing', {
            contactId: this.currentContact.id,
            contactType: this.currentContact.type
        });
    }
    
    /**
     * 添加消息到历史记录
     */
    addMessageToHistory(message) {
        const contactId = message.sender_id === this.getCurrentUserId() ? 
                         message.recipient_id : message.sender_id;
        
        if (!this.messageHistory.has(contactId)) {
            this.messageHistory.set(contactId, []);
        }
        
        this.messageHistory.get(contactId).push(message);
    }
    
    /**
     * 获取消息历史
     */
    getMessageHistory(contactId) {
        return this.messageHistory.get(contactId) || [];
    }
    
    /**
     * 更新消息UI
     */
    updateMessageUI(message) {
        // 如果当前正在查看这个联系人的消息，更新聊天界面
        if (this.currentContact && 
            (message.sender_id === this.currentContact.id || 
             message.recipient_id === this.currentContact.id)) {
            this.appendMessageToChat(message);
        }
        
        // 更新消息列表
        this.updateMessageList();
    }
    
    /**
     * 添加消息到聊天界面
     */
    appendMessageToChat(message) {
        const chatContainer = document.getElementById('chat-messages');
        if (!chatContainer) return;
        
        const isOwnMessage = message.sender_id === this.getCurrentUserId();
        const messageElement = this.createMessageElement(message, isOwnMessage);
        
        chatContainer.appendChild(messageElement);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    /**
     * 创建消息元素
     */
    createMessageElement(message, isOwnMessage) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isOwnMessage ? 'own' : 'other'}`;
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">${this.escapeHtml(message.content)}</div>
                <div class="message-time">${this.formatTime(message.timestamp)}</div>
            </div>
        `;
        
        return messageDiv;
    }
    
    /**
     * 更新消息列表
     */
    updateMessageList() {
        // 触发消息列表更新事件
        window.dispatchEvent(new CustomEvent('messageListUpdate'));
    }
    
    /**
     * 更新用户状态
     */
    updateUserStatus(userId, status) {
        console.log(`👤 用户 ${userId} 状态更新: ${status}`);
        
        // 更新在线状态指示器
        const statusElement = document.querySelector(`[data-user-id="${userId}"] .user-status`);
        if (statusElement) {
            statusElement.className = `user-status ${status}`;
            statusElement.textContent = status === 'online' ? '在线' : '离线';
        }
    }
    
    /**
     * 更新连接状态
     */
    updateConnectionStatus(isConnected) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.className = `connection-status ${isConnected ? 'connected' : 'disconnected'}`;
            statusElement.textContent = isConnected ? '已连接' : '连接断开';
        }
    }
    
    /**
     * 更新输入指示器
     */
    updateTypingIndicator() {
        const typingElement = document.getElementById('typing-indicator');
        if (!typingElement) return;
        
        if (this.typingUsers.size > 0) {
            typingElement.style.display = 'block';
            typingElement.textContent = '对方正在输入...';
        } else {
            typingElement.style.display = 'none';
        }
    }
    
    /**
     * 处理连接错误
     */
    handleConnectionError() {
        if (this.connectionRetries >= this.maxRetries) {
            console.error('❌ 达到最大重连次数，停止重连');
            this.showNotification('聊天服务连接失败，请刷新页面重试', 'error');
            return;
        }
        
        this.connectionRetries++;
        const delay = this.retryDelay * Math.pow(2, this.connectionRetries - 1);
        
        console.log(`🔄 ${delay}ms后尝试第${this.connectionRetries}次重连...`);
        
        setTimeout(() => {
            this.initSocket();
        }, delay);
    }
    
    /**
     * 播放提示音
     */
    playNotificationSound() {
        try {
            const audio = new Audio('/sounds/notification.mp3');
            audio.play().catch(e => console.log('无法播放提示音:', e));
        } catch (error) {
            console.log('提示音播放失败:', error);
        }
    }
    
    /**
     * 显示桌面通知
     */
    showDesktopNotification(message) {
        if (!('Notification' in window)) return;
        
        if (Notification.permission === 'granted') {
            new Notification('新消息', {
                body: `${message.sender_name}: ${message.content}`,
                icon: '/images/notification-icon.png'
            });
        } else if (Notification.permission !== 'denied') {
            Notification.requestPermission();
        }
    }
    
    /**
     * 显示通知
     */
    showNotification(message, type = 'info') {
        // 使用现有的通知系统
        if (window.showNotification) {
            window.showNotification(message, type);
        } else {
            console.log(`📢 ${type.toUpperCase()}: ${message}`);
        }
    }
    
    /**
     * 获取当前用户ID
     */
    getCurrentUserId() {
        try {
            const token = localStorage.getItem('user_token') || this.getCookie('user_token');
            const payload = this.parseJWT(token);
            return payload ? payload.user_id : null;
        } catch (error) {
            console.error('获取用户ID失败:', error);
            return null;
        }
    }
    
    /**
     * 解析JWT token
     */
    parseJWT(token) {
        try {
            const payload = token.split('.')[1];
            if (payload) {
                return JSON.parse(decodeURIComponent(escape(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))));
            }
        } catch (error) {
            console.error('解析JWT失败:', error);
        }
        return null;
    }
    
    /**
     * 获取Cookie
     */
    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }
    
    /**
     * 转义HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * 格式化时间
     */
    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) { // 1分钟内
            return '刚刚';
        } else if (diff < 3600000) { // 1小时内
            return `${Math.floor(diff / 60000)}分钟前`;
        } else if (diff < 86400000) { // 24小时内
            return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
        } else {
            return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' });
        }
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        // 绑定输入框事件
        document.addEventListener('input', (e) => {
            if (e.target.id === 'message-input') {
                this.sendTypingStatus();
                
                // 清除之前的定时器
                clearTimeout(this.typingTimer);
                
                // 设置停止输入定时器
                this.typingTimer = setTimeout(() => {
                    this.sendStopTypingStatus();
                }, 1000);
            }
        });
        
        // 绑定发送按钮事件
        document.addEventListener('click', (e) => {
            if (e.target.id === 'send-message-btn') {
                this.handleSendMessage();
            }
        });
        
        // 绑定回车发送
        document.addEventListener('keypress', (e) => {
            if (e.target.id === 'message-input' && e.key === 'Enter') {
                e.preventDefault();
                this.handleSendMessage();
            }
        });
    }
    
    /**
     * 处理发送消息
     */
    handleSendMessage() {
        const input = document.getElementById('message-input');
        if (!input) return;
        
        const content = input.value.trim();
        if (!content) return;
        
        if (this.sendMessage(content)) {
            input.value = '';
            this.sendStopTypingStatus();
        }
    }
    
    /**
     * 断开连接
     */
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
        
        this.isConnected = false;
        this.currentRoom = null;
        this.currentContact = null;
    }
}

// 创建全局聊天管理器实例
window.EnhancedChatManager = new EnhancedChatManager();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 增强聊天管理器已加载');
});
