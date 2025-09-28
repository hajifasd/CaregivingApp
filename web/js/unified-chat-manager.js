/**
 * 统一聊天管理器
 * 整合了ChatWindow、ChatManager和EnhancedChatManager的所有功能
 * 提供完整的聊天解决方案
 */

class UnifiedChatManager {
    constructor() {
        // 基础属性
        this.socket = null;
        this.isConnected = false;
        this.isOpen = false;
        this.isMinimized = false;
        
        // 用户信息
        this.userInfo = null;
        this.userType = null;
        this.userToken = null;
        
        // 聊天状态
        this.currentContact = null;
        this.currentRoom = null;
        this.messages = [];
        this.messageHistory = new Map();
        this.chatWindows = new Map();
        
        // 连接管理
        this.connectionRetries = 0;
        this.maxRetries = 5;
        this.retryDelay = 1000;
        
        // 输入状态
        this.isTyping = false;
        this.typingTimer = null;
        this.typingUsers = new Set();
        this.unreadCount = 0;
        
        // 初始化
        this.init();
    }
    
    /**
     * 初始化聊天管理器
     */
    init() {
        console.log('🚀 初始化统一聊天管理器...');
        
        // 加载用户信息
        this.loadUserInfo();
        
        // 初始化Socket连接
        this.initSocket();
        
        // 绑定事件
        this.bindEvents();
        
        // 创建聊天窗口
        this.createChatWindow();
        
        console.log('✅ 统一聊天管理器初始化完成');
    }
    
    /**
     * 加载用户信息
     */
    loadUserInfo() {
        try {
            // 统一使用 user_info 和 caregiver_info 字段名
            let userInfo = JSON.parse(localStorage.getItem('user_info') || '{}');
            let token = localStorage.getItem('user_token');
            let userType = 'user';
            
            // 如果用户端没有信息，尝试护工端
            if (!userInfo.id) {
                userInfo = JSON.parse(localStorage.getItem('caregiver_info') || '{}');
                token = localStorage.getItem('caregiver_token');
                userType = 'caregiver';
            }
            
            // 如果护工端也没有信息，尝试管理端
            if (!userInfo.id) {
                userInfo = JSON.parse(localStorage.getItem('admin_info') || '{}');
                token = localStorage.getItem('admin_token');
                userType = 'admin';
            }
            
            if (userInfo.id && token) {
                this.userInfo = userInfo;
                this.userToken = token;
                this.userType = userType;
                console.log('✅ 用户信息加载成功:', { userType, userId: userInfo.id });
            } else {
                console.warn('⚠️ 用户信息或token缺失');
            }
        } catch (error) {
            console.error('❌ 加载用户信息失败:', error);
        }
    }
    
    /**
     * 初始化Socket连接
     */
    initSocket() {
        try {
            // 优先使用全局Socket管理器
            if (window.SocketManager && window.SocketManager.socket) {
                this.socket = window.SocketManager.socket;
                console.log('✅ 使用全局Socket管理器');
            } else {
                // 备用方案：创建新连接
                const serverConfig = window.SERVER_CONFIG || window.SERVER_CONFIG;
                const socketUrl = serverConfig ? serverConfig.socketUrl : 'http://localhost:8000';
                const config = serverConfig ? serverConfig.socketConfig : {
                    transports: ['websocket', 'polling'],
                    timeout: 10000,
                    reconnection: true,
                    reconnectionAttempts: 5,
                    reconnectionDelay: 1000
                };
                
                // 添加认证信息
                if (this.userToken) {
                    config.auth = { token: this.userToken };
                }
                
                this.socket = io(socketUrl, config);
                console.log('🔌 创建新的Socket连接:', socketUrl);
            }
            
            this.setupSocketEvents();
            
        } catch (error) {
            console.error('❌ Socket初始化失败:', error);
            this.handleSocketError(error);
        }
    }
    
    /**
     * 设置Socket事件监听
     */
    setupSocketEvents() {
        if (!this.socket) return;
        
        // 连接事件
        this.socket.on('connect', () => this.onSocketConnect());
        this.socket.on('disconnect', () => this.onSocketDisconnect());
        this.socket.on('connect_error', (error) => this.handleSocketError(error));
        
        // 消息事件
        this.socket.on('new_message', (data) => this.handleNewMessage(data));
        this.socket.on('message_sent', (data) => this.handleMessageSent(data));
        this.socket.on('typing', (data) => this.handleTyping(data));
        this.socket.on('stop_typing', (data) => this.handleStopTyping(data));
        
        // 错误事件
        this.socket.on('error', (error) => this.handleSocketError(error));
    }
    
    /**
     * Socket连接成功
     */
    onSocketConnect() {
        console.log('✅ Socket连接成功');
        this.isConnected = true;
        this.connectionRetries = 0;
        
        // 加入用户房间
        if (this.userInfo && this.userType) {
            this.socket.emit('join', {
                user_id: this.userInfo.id,
                user_type: this.userType,
                user_name: this.userInfo.name || this.userInfo.username || '用户'
            });
        }
        
        this.updateConnectionStatus(true);
    }
    
    /**
     * Socket连接断开
     */
    onSocketDisconnect() {
        console.log('⚠️ Socket连接断开');
        this.isConnected = false;
        this.updateConnectionStatus(false);
        
        // 尝试重连
        if (this.connectionRetries < this.maxRetries) {
            this.connectionRetries++;
            console.log(`🔄 尝试重连 (${this.connectionRetries}/${this.maxRetries})...`);
            setTimeout(() => this.initSocket(), this.retryDelay * this.connectionRetries);
        }
    }
    
    /**
     * 处理Socket错误
     */
    handleSocketError(error) {
        console.error('❌ Socket错误:', error);
        this.isConnected = false;
        this.updateConnectionStatus(false);
    }
    
    /**
     * 更新连接状态显示
     */
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = connected ? '已连接' : '连接断开';
            statusElement.className = connected ? 'text-green-600' : 'text-red-600';
        }
    }
    
    /**
     * 创建聊天窗口
     */
    createChatWindow() {
        // 检查是否已存在聊天窗口
        if (document.getElementById('chat-window')) {
            console.log('⚠️ 聊天窗口已存在，跳过创建');
            return;
        }
        
        console.log('🔨 开始创建聊天窗口...');
        
        const chatWindowHTML = `
            <div id="chat-window" class="fixed bottom-4 right-4 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50 hidden">
                <!-- 聊天窗口头部 -->
                <div class="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50 rounded-t-lg">
                    <div class="flex items-center space-x-3">
                        <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                            <span class="text-white text-sm font-medium" id="contact-initial">U</span>
                        </div>
                        <div>
                            <h3 class="font-medium text-gray-900" id="contact-name">选择联系人</h3>
                            <p class="text-xs text-gray-500" id="contact-status">离线</p>
                        </div>
                    </div>
                    <div class="flex items-center space-x-2">
                        <button id="minimize-chat" class="p-1 hover:bg-gray-200 rounded">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path>
                            </svg>
                        </button>
                        <button id="close-chat" class="p-1 hover:bg-gray-200 rounded">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <!-- 消息显示区域 -->
                <div id="chat-messages" class="h-64 overflow-y-auto p-4 space-y-3">
                    <div class="text-center text-gray-500 text-sm">
                        开始聊天...
                    </div>
                </div>
                
                <!-- 输入区域 -->
                <div class="p-4 border-t border-gray-200">
                    <div class="flex space-x-2">
                        <input 
                            type="text" 
                            id="message-input" 
                            placeholder="输入消息..." 
                            class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                        <button 
                            id="send-message-btn" 
                            class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
                        >
                            发送
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // 确保document.body存在
        if (document.body) {
            document.body.insertAdjacentHTML('beforeend', chatWindowHTML);
            this.bindChatWindowEvents();
            console.log('✅ 聊天窗口HTML已插入');
        } else {
            console.error('❌ document.body不存在，延迟创建聊天窗口');
            // 延迟创建，等待DOM加载完成
            setTimeout(() => {
                if (document.body) {
                    document.body.insertAdjacentHTML('beforeend', chatWindowHTML);
                    this.bindChatWindowEvents();
                    console.log('✅ 聊天窗口HTML已延迟插入');
                } else {
                    console.error('❌ 延迟后document.body仍然不存在');
                }
            }, 100);
        }
    }
    
    /**
     * 绑定聊天窗口事件
     */
    bindChatWindowEvents() {
        console.log('🔗 绑定聊天窗口事件...');
        
        // 使用事件委托，避免重复绑定
        const chatWindow = document.getElementById('chat-window');
        if (!chatWindow) {
            console.error('❌ 聊天窗口元素不存在，无法绑定事件');
            return;
        }
        
        // 移除之前的事件监听器（如果存在）
        chatWindow.removeEventListener('click', this.handleChatWindowClick);
        
        // 绑定点击事件委托
        this.handleChatWindowClick = (e) => {
            console.log('🖱️ 聊天窗口点击事件:', e.target, e.target.id);
            
            // 检查点击的元素或其父元素
            let target = e.target;
            while (target && target !== chatWindow) {
                if (target.id === 'close-chat' || target.closest('#close-chat')) {
                    console.log('🔴 关闭按钮被点击');
                    e.preventDefault();
                    e.stopPropagation();
                    this.closeChat();
                    return;
                } else if (target.id === 'minimize-chat' || target.closest('#minimize-chat')) {
                    console.log('🔽 最小化按钮被点击');
                    e.preventDefault();
                    e.stopPropagation();
                    this.toggleMinimize();
                    return;
                } else if (target.id === 'send-message-btn') {
                    console.log('📤 发送按钮被点击');
                    e.preventDefault();
                    e.stopPropagation();
                    this.sendMessage();
                    return;
                }
                target = target.parentElement;
            }
        };
        
        chatWindow.addEventListener('click', this.handleChatWindowClick);
        
        // 输入框事件
        const messageInput = document.getElementById('message-input');
        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    console.log('⌨️ 回车键发送消息');
                    this.sendMessage();
                }
            });
            
            messageInput.addEventListener('input', () => {
                this.sendTypingStatus(true);
            });
        }
        
        console.log('✅ 聊天窗口事件绑定完成');
    }
    
    /**
     * 绑定全局事件
     */
    bindEvents() {
        // 监听存储变化
        window.addEventListener('storage', (e) => {
            if (e.key === 'user_token' || e.key === 'caregiver_token' || e.key === 'admin_token') {
                this.loadUserInfo();
                this.initSocket();
            }
        });
    }
    
    /**
     * 打开聊天窗口
     */
    openChat(contact) {
        console.log('🚀 openChat被调用:', contact);
        
        if (!contact) {
            console.error('❌ contact参数为空');
            return;
        }
        
        this.currentContact = contact;
        this.isOpen = true;
        
        // 确保聊天窗口存在
        let chatWindow = document.getElementById('chat-window');
        console.log('🔍 聊天窗口元素:', chatWindow);
        
        if (!chatWindow) {
            console.log('🔧 聊天窗口不存在，重新创建...');
            this.createChatWindow();
            chatWindow = document.getElementById('chat-window');
            console.log('🔍 重新创建后的聊天窗口元素:', chatWindow);
        }
        
        if (chatWindow) {
            chatWindow.classList.remove('hidden');
            console.log('✅ 聊天窗口已显示');
            
            // 更新联系人信息
            const contactName = document.getElementById('contact-name');
            const contactInitial = document.getElementById('contact-initial');
            
            if (contactName) {
                contactName.textContent = contact.name || contact.username || '联系人';
                console.log('✅ 联系人姓名已更新:', contact.name);
            }
            
            if (contactInitial) {
                contactInitial.textContent = (contact.name || contact.username || 'U').charAt(0).toUpperCase();
                console.log('✅ 联系人首字母已更新');
            }
            
            // 加载消息历史
            this.loadMessageHistory(contact);
        } else {
            console.error('❌ 找不到聊天窗口元素');
        }
        
        console.log('✅ 聊天窗口打开完成:', contact);
    }
    
    /**
     * 关闭聊天窗口
     */
    closeChat() {
        this.isOpen = false;
        this.currentContact = null;
        
        const chatWindow = document.getElementById('chat-window');
        if (chatWindow) {
            chatWindow.classList.add('hidden');
        }
        
        console.log('✅ 聊天窗口已关闭');
    }
    
    /**
     * 切换最小化状态
     */
    toggleMinimize() {
        this.isMinimized = !this.isMinimized;
        
        const chatWindow = document.getElementById('chat-window');
        if (chatWindow) {
            if (this.isMinimized) {
                chatWindow.style.height = '60px';
                document.getElementById('chat-messages').style.display = 'none';
                document.querySelector('.p-4.border-t').style.display = 'none';
            } else {
                chatWindow.style.height = 'auto';
                document.getElementById('chat-messages').style.display = 'block';
                document.querySelector('.p-4.border-t').style.display = 'block';
            }
        }
    }
    
    /**
     * 发送消息
     */
    async sendMessage() {
        const input = document.getElementById('message-input');
        const content = input.value.trim();
        
        if (!content || !this.currentContact || !this.socket) {
            return;
        }
        
        try {
            const contactId = this.currentContact.id || this.currentContact.contactId?.replace(/^(user_|caregiver_)/, '');
            const contactType = this.currentContact.type || (this.currentContact.contactId?.startsWith('user_') ? 'user' : 'caregiver');
            
            // 使用标准化的消息格式
            const messageData = MessageFormatUtils.buildSendMessageData(
                contactId,
                content,
                {
                    recipientType: contactType,
                    messageType: 'text',
                    conversationId: MessageFormatUtils.generateConversationId(
                        this.userInfo.id,
                        this.userType,
                        contactId,
                        contactType
                    )
                }
            );
            
            // 验证消息数据
            const validation = MessageFormatUtils.validateMessageData(messageData);
            if (!validation.isValid) {
                console.error('❌ 消息数据验证失败:', validation.errors);
                this.showNotification('消息格式错误: ' + validation.errors.join(', '), 'error');
                return;
            }
            
            // 发送到服务器
            this.socket.emit('send_message', messageData);
            
            // 清空输入框
            input.value = '';
            input.style.height = 'auto';
            document.getElementById('send-message-btn').disabled = true;
            
            console.log('✅ 消息发送成功:', messageData);
            
        } catch (error) {
            console.error('❌ 发送消息失败:', error);
            this.showNotification('发送消息失败: ' + error.message, 'error');
        }
        
        // 停止输入状态
        this.sendTypingStatus(false);
    }
    
    /**
     * 处理新消息
     */
    handleNewMessage(data) {
        console.log('📨 收到新消息:', data);
        
        // 添加到消息历史
        if (this.currentContact) {
            this.addMessageToUI(data);
        }
        
        // 更新未读计数
        this.unreadCount++;
        this.updateUnreadCount();
    }
    
    /**
     * 处理消息发送确认
     */
    handleMessageSent(data) {
        console.log('✅ 消息发送确认:', data);
        this.addMessageToUI(data);
    }
    
    /**
     * 添加消息到UI
     */
    addMessageToUI(message) {
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return;
        
        // 清除"开始聊天..."提示
        const emptyMessage = messagesContainer.querySelector('.text-center.text-gray-500');
        if (emptyMessage) {
            emptyMessage.remove();
        }
        
        const messageElement = document.createElement('div');
        messageElement.className = `flex ${message.sender_id == this.userInfo.id ? 'justify-end' : 'justify-start'}`;
        
        messageElement.innerHTML = `
            <div class="max-w-xs px-4 py-2 rounded-lg ${message.sender_id == this.userInfo.id ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-900'}">
                <div class="text-sm">${message.content}</div>
                <div class="text-xs opacity-75 mt-1">${new Date(message.timestamp || Date.now()).toLocaleTimeString()}</div>
            </div>
        `;
        
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    /**
     * 加载消息历史
     */
    async loadMessageHistory(contact) {
        console.log('📚 开始加载消息历史:', contact);
        console.log('👤 用户信息:', this.userInfo);
        
        if (!contact || !this.userInfo) {
            console.log('❌ 缺少必要参数，跳过消息历史加载');
            return;
        }
        
        try {
            const contactId = contact.id || contact.contactId?.replace(/^(user_|caregiver_)/, '');
            const contactType = contact.type || (contact.contactId?.startsWith('user_') ? 'user' : 'caregiver');
            
            console.log('🔍 联系人ID:', contactId, '类型:', contactType);
            
            // 使用统一的消息加载工具
            if (window.messageLoader) {
                console.log('📦 使用messageLoader加载消息');
                const messages = await window.messageLoader.getMessageHistory(contactId, contactType, {
                    limit: 20,
                    offset: 0
                });
                
                // 清空当前消息
                const messagesContainer = document.getElementById('chat-messages');
                console.log('📦 消息容器:', messagesContainer);
                console.log('📊 消息数量:', messages ? messages.length : 0);
                
                if (messagesContainer) {
                    messagesContainer.innerHTML = '';
                    
                    if (messages && messages.length > 0) {
                        console.log('📝 显示历史消息:', messages);
                        // 显示历史消息
                        messages.reverse().forEach(message => {
                            this.addMessageToUI(message);
                        });
                    } else {
                        console.log('📭 没有历史消息');
                        messagesContainer.innerHTML = '<div class="text-center text-gray-500 text-sm">暂无消息，开始聊天吧！</div>';
                    }
                } else {
                    console.error('❌ 找不到消息容器');
                }
            } else {
                // 备用方案：直接调用API
                const response = await fetch(`/api/chat/messages?user_id=${this.userInfo.id}&user_type=${this.userType}&contact_id=${contactId}&contact_type=${contactType}&limit=20`);
                const data = await response.json();
                
                if (data.success && data.data) {
                    // 清空当前消息
                    const messagesContainer = document.getElementById('chat-messages');
                    if (messagesContainer) {
                        messagesContainer.innerHTML = '';
                        
                        // 显示历史消息
                        data.data.reverse().forEach(message => {
                            this.addMessageToUI(message);
                        });
                    }
                }
            }
        } catch (error) {
            console.error('❌ 加载消息历史失败:', error);
            this.showNotification('加载消息历史失败: ' + error.message, 'error');
        }
    }
    
    /**
     * 发送输入状态
     */
    sendTypingStatus(isTyping) {
        if (!this.socket || !this.currentContact) return;
        
        if (isTyping) {
            if (!this.isTyping) {
                this.isTyping = true;
                this.socket.emit('typing', {
                    contact_id: this.currentContact.id,
                    contact_type: this.currentContact.type || 'user'
                });
            }
            
            // 清除之前的定时器
            if (this.typingTimer) {
                clearTimeout(this.typingTimer);
            }
            
            // 3秒后停止输入状态
            this.typingTimer = setTimeout(() => {
                this.sendTypingStatus(false);
            }, 3000);
        } else {
            if (this.isTyping) {
                this.isTyping = false;
                this.socket.emit('stop_typing', {
                    contact_id: this.currentContact.id,
                    contact_type: this.currentContact.type || 'user'
                });
            }
            
            if (this.typingTimer) {
                clearTimeout(this.typingTimer);
                this.typingTimer = null;
            }
        }
    }
    
    /**
     * 处理输入状态
     */
    handleTyping(data) {
        console.log('⌨️ 对方正在输入:', data);
        // 可以在这里显示"对方正在输入..."的提示
    }
    
    /**
     * 处理停止输入状态
     */
    handleStopTyping(data) {
        console.log('⌨️ 对方停止输入:', data);
        // 可以在这里隐藏"对方正在输入..."的提示
    }
    
    /**
     * 更新未读计数
     */
    updateUnreadCount() {
        // 可以在这里更新未读消息计数显示
        console.log('📊 未读消息数:', this.unreadCount);
    }
    
    /**
     * 显示通知
     */
    showNotification(message, type = 'info') {
        // 简单的通知实现
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
            type === 'error' ? 'bg-red-500 text-white' : 
            type === 'success' ? 'bg-green-500 text-white' : 
            'bg-blue-500 text-white'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// 等待DOM加载完成后创建全局实例
function initUnifiedChatManager() {
    if (window.unifiedChatManager) {
        console.log('⚠️ 统一聊天管理器已存在，跳过初始化');
        return;
    }
    
    if (document.body) {
        window.unifiedChatManager = new UnifiedChatManager();
        window.UnifiedChatManager = UnifiedChatManager;
        console.log('✅ 统一聊天管理器已初始化');
    } else {
        console.log('⏳ 等待DOM加载完成...');
        setTimeout(initUnifiedChatManager, 50);
    }
}

// 立即尝试初始化
initUnifiedChatManager();

// 也监听DOMContentLoaded事件作为备用
document.addEventListener('DOMContentLoaded', function() {
    if (!window.unifiedChatManager) {
        console.log('🔄 DOMContentLoaded时重新初始化聊天管理器');
        initUnifiedChatManager();
    }
});
