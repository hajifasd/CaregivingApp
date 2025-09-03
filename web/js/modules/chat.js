/**
 * 护工资源管理系统 - 聊天模块
 * ====================================
 * 
 * 实现用户和护工之间的实时聊天功能
 */

class ChatManager {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.currentRoom = null;
        this.currentContact = null;
        this.typingTimer = null;
        this.messageHistory = [];
        
        // 绑定事件
        this.bindEvents();
    }
    
    /**
     * 绑定聊天相关事件
     */
    bindEvents() {
        // 发送消息按钮
        document.addEventListener('click', (e) => {
            if (e.target.matches('.send-message-btn')) {
                this.sendMessage();
            }
        });
        
        // 消息输入框
        document.addEventListener('input', (e) => {
            if (e.target.matches('.message-input')) {
                this.handleTyping();
            }
        });
        
        // 回车发送消息
        document.addEventListener('keypress', (e) => {
            if (e.target.matches('.message-input') && e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }
    
    /**
     * 初始化WebSocket连接
     */
    initSocket() {
        try {
            // 检查是否支持WebSocket
            if (!window.io) {
                console.warn('Socket.IO客户端库未加载，聊天功能将不可用');
                return false;
            }
            
            // 连接到服务器
            this.socket = io();
            
            // 绑定Socket事件
            this.bindSocketEvents();
            
            return true;
        } catch (error) {
            console.error('初始化WebSocket失败:', error);
            return false;
        }
    }
    
    /**
     * 绑定Socket事件
     */
    bindSocketEvents() {
        if (!this.socket) return;
        
        // 连接成功
        this.socket.on('connect', () => {
            console.log('WebSocket连接成功');
            this.isConnected = true;
            this.authenticate();
        });
        
        // 连接断开
        this.socket.on('disconnect', () => {
            console.log('WebSocket连接断开');
            this.isConnected = false;
            this.showConnectionStatus('连接已断开');
        });
        
        // 认证成功
        this.socket.on('authenticated', (data) => {
            console.log('认证成功:', data);
            this.showConnectionStatus('已连接');
        });
        
        // 认证失败
        this.socket.on('auth_error', (data) => {
            console.error('认证失败:', data);
            this.showConnectionStatus('认证失败');
        });
        
        // 新消息
        this.socket.on('new_message', (message) => {
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
        
        // 消息已读
        this.socket.on('message_read', (data) => {
            this.handleMessageRead(data);
        });
        
        // 错误处理
        this.socket.on('error', (data) => {
            console.error('Socket错误:', data);
            this.showError(data.message);
        });
    }
    
    /**
     * 认证用户
     */
    authenticate() {
        if (!this.socket || !this.isConnected) return;
        
        const token = localStorage.getItem('user_token') || localStorage.getItem('caregiver_token');
        const userType = localStorage.getItem('user_token') ? 'user' : 'caregiver';
        
        if (!token) {
            console.warn('未找到认证令牌');
            return;
        }
        
        this.socket.emit('authenticate', {
            token: token,
            user_type: userType
        });
    }
    
    /**
     * 加入聊天房间
     */
    joinChat(contactId, contactType) {
        if (!this.socket || !this.isConnected) {
            console.warn('WebSocket未连接');
            return;
        }
        
        this.currentContact = { id: contactId, type: contactType };
        
        this.socket.emit('join_chat', {
            contact_id: contactId,
            contact_type: contactType
        });
        
        // 加载聊天历史
        this.loadChatHistory(contactId, contactType);
    }
    
    /**
     * 发送消息
     */
    sendMessage() {
        if (!this.socket || !this.isConnected || !this.currentContact) {
            this.showError('无法发送消息，请检查连接状态');
            return;
        }
        
        const messageInput = document.querySelector('.message-input');
        if (!messageInput) return;
        
        const content = messageInput.value.trim();
        if (!content) return;
        
        // 发送消息
        this.socket.emit('send_message', {
            recipient_id: this.currentContact.id,
            recipient_type: this.currentContact.type,
            content: content
        });
        
        // 清空输入框
        messageInput.value = '';
        
        // 添加消息到本地显示（临时）
        this.addMessageToChat({
            id: Date.now(), // 临时ID
            sender_id: this.getCurrentUserId(),
            sender_type: this.getCurrentUserType(),
            recipient_id: this.currentContact.id,
            recipient_type: this.currentContact.type,
            content: content,
            created_at: new Date().toISOString(),
            is_read: false,
            is_temp: true
        });
    }
    
    /**
     * 处理新消息
     */
    handleNewMessage(message) {
        // 检查是否是当前聊天窗口的消息
        if (this.currentContact && 
            ((message.sender_id === this.currentContact.id && message.sender_type === this.currentContact.type) ||
             (message.recipient_id === this.currentContact.id && message.recipient_type === this.currentContact.type))) {
            
            this.addMessageToChat(message);
            
            // 标记消息为已读
            this.markMessageAsRead(message.id);
        }
        
        // 更新未读消息数量
        this.updateUnreadCount();
        
        // 播放提示音（可选）
        this.playNotificationSound();
    }
    
    /**
     * 处理消息发送成功
     */
    handleMessageSent(data) {
        // 移除临时消息标记
        const tempMessage = document.querySelector(`[data-temp-id="${data.message_id}"]`);
        if (tempMessage) {
            tempMessage.removeAttribute('data-temp-id');
            tempMessage.classList.remove('temp-message');
        }
        
        // 显示成功提示
        this.showSuccess('消息发送成功');
    }
    
    /**
     * 处理用户正在输入
     */
    handleUserTyping(data) {
        if (this.currentContact && 
            data.user_id === this.currentContact.id && 
            data.user_type === this.currentContact.type) {
            
            this.showTypingIndicator(data.is_typing);
        }
    }
    
    /**
     * 处理消息已读
     */
    handleMessageRead(data) {
        const messageElement = document.querySelector(`[data-message-id="${data.message_id}"]`);
        if (messageElement) {
            messageElement.classList.add('read');
        }
    }
    
    /**
     * 处理正在输入状态
     */
    handleTyping() {
        if (!this.socket || !this.isConnected || !this.currentContact) return;
        
        // 清除之前的定时器
        if (this.typingTimer) {
            clearTimeout(this.typingTimer);
        }
        
        // 发送正在输入状态
        this.socket.emit('typing', {
            recipient_id: this.currentContact.id,
            recipient_type: this.currentContact.type,
            is_typing: true
        });
        
        // 3秒后停止输入状态
        this.typingTimer = setTimeout(() => {
            this.socket.emit('typing', {
                recipient_id: this.currentContact.id,
                recipient_type: this.currentContact.type,
                is_typing: false
            });
        }, 3000);
    }
    
    /**
     * 标记消息为已读
     */
    markMessageAsRead(messageId) {
        if (!this.socket || !this.isConnected) return;
        
        this.socket.emit('mark_read', {
            message_id: messageId
        });
    }
    
    /**
     * 加载聊天历史
     */
    async loadChatHistory(contactId, contactType) {
        try {
            const userType = this.getCurrentUserType();
            const response = await fetch(`/api/chat/messages?contact_id=${contactId}&contact_type=${contactType}&user_type=${userType}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('user_token') || localStorage.getItem('caregiver_token')}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.messageHistory = data.data.messages || [];
                    this.renderChatHistory();
                }
            }
        } catch (error) {
            console.error('加载聊天历史失败:', error);
        }
    }
    
    /**
     * 渲染聊天历史
     */
    renderChatHistory() {
        const chatContainer = document.querySelector('.chat-messages');
        if (!chatContainer) return;
        
        chatContainer.innerHTML = '';
        
        this.messageHistory.forEach(message => {
            this.addMessageToChat(message, false);
        });
        
        // 滚动到底部
        this.scrollToBottom();
    }
    
    /**
     * 添加消息到聊天窗口
     */
    addMessageToChat(message, scrollToBottom = true) {
        const chatContainer = document.querySelector('.chat-messages');
        if (!chatContainer) return;
        
        const messageElement = this.createMessageElement(message);
        chatContainer.appendChild(messageElement);
        
        if (scrollToBottom) {
            this.scrollToBottom();
        }
    }
    
    /**
     * 创建消息元素
     */
    createMessageElement(message) {
        const isOwnMessage = message.sender_id === this.getCurrentUserId() && 
                           message.sender_type === this.getCurrentUserType();
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isOwnMessage ? 'own-message' : 'other-message'}`;
        messageDiv.setAttribute('data-message-id', message.id);
        
        if (message.is_temp) {
            messageDiv.classList.add('temp-message');
            messageDiv.setAttribute('data-temp-id', message.id);
        }
        
        const time = new Date(message.created_at).toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">${this.escapeHtml(message.content)}</div>
                <div class="message-time">${time}</div>
                ${isOwnMessage ? `<div class="message-status">${message.is_read ? '已读' : '未读'}</div>` : ''}
            </div>
        `;
        
        return messageDiv;
    }
    
    /**
     * 显示正在输入指示器
     */
    showTypingIndicator(isTyping) {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (!typingIndicator) return;
        
        if (isTyping) {
            typingIndicator.style.display = 'block';
        } else {
            typingIndicator.style.display = 'none';
        }
    }
    
    /**
     * 滚动到底部
     */
    scrollToBottom() {
        const chatContainer = document.querySelector('.chat-messages');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }
    
    /**
     * 更新未读消息数量
     */
    async updateUnreadCount() {
        try {
            const userType = this.getCurrentUserType();
            const response = await fetch(`/api/chat/unread_count?user_type=${userType}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('user_token') || localStorage.getItem('caregiver_token')}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.updateUnreadBadge(data.data.unread_count);
                }
            }
        } catch (error) {
            console.error('更新未读消息数量失败:', error);
        }
    }
    
    /**
     * 更新未读消息徽章
     */
    updateUnreadBadge(count) {
        const badge = document.querySelector('.unread-badge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : count;
                badge.style.display = 'block';
            } else {
                badge.style.display = 'none';
            }
        }
    }
    
    /**
     * 获取当前用户ID
     */
    getCurrentUserId() {
        const userInfo = JSON.parse(localStorage.getItem('user_info') || localStorage.getItem('caregiver_info') || '{}');
        return userInfo.id;
    }
    
    /**
     * 获取当前用户类型
     */
    getCurrentUserType() {
        return localStorage.getItem('user_token') ? 'user' : 'caregiver';
    }
    
    /**
     * 显示连接状态
     */
    showConnectionStatus(status) {
        const statusElement = document.querySelector('.connection-status');
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.className = `connection-status ${status.includes('已连接') ? 'connected' : 'disconnected'}`;
        }
    }
    
    /**
     * 显示成功提示
     */
    showSuccess(message) {
        // 这里可以使用Toast或其他提示组件
        console.log('成功:', message);
    }
    
    /**
     * 显示错误提示
     */
    showError(message) {
        // 这里可以使用Toast或其他提示组件
        console.error('错误:', message);
    }
    
    /**
     * 播放通知音
     */
    playNotificationSound() {
        // 这里可以播放提示音
        // const audio = new Audio('/sounds/notification.mp3');
        // audio.play();
    }
    
    /**
     * HTML转义
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
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
window.ChatManager = new ChatManager();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    // 初始化聊天功能
    if (window.ChatManager) {
        window.ChatManager.initSocket();
    }
});
