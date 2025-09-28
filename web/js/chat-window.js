/**
 * 聊天窗口管理器
 * 提供完整的聊天界面功能
 */

class ChatWindow {
    constructor() {
        this.isOpen = false;
        this.isMinimized = false;
        this.currentContact = null;
        this.messages = [];
        this.socket = null;
        this.isTyping = false;
        this.typingTimer = null;
        this.unreadCount = 0;
        
        this.init();
    }
    
    /**
     * 初始化聊天窗口
     */
    init() {
        this.createChatWindow();
        this.bindEvents();
        this.initSocket();
        this.loadUserInfo();
        this.initNotificationManager();
    }
    
    /**
     * 初始化通知管理器
     */
    initNotificationManager() {
        if (window.NotificationManager) {
            this.notificationManager = new NotificationManager();
            console.log('✅ 通知管理器已初始化');
        }
    }
    
    /**
     * 创建聊天窗口HTML
     */
    createChatWindow() {
        // 如果聊天窗口已存在，直接返回
        if (document.getElementById('chat-window')) {
            return;
        }
        
        // 创建聊天窗口容器
        const chatContainer = document.createElement('div');
        chatContainer.innerHTML = `
            <!-- 聊天窗口组件 -->
            <div id="chat-window" class="chat-window hidden">
                <!-- 聊天窗口头部 -->
                <div class="chat-header">
                    <div class="chat-contact-info">
                        <img id="chat-contact-avatar" src="/uploads/avatars/default-user.png" alt="联系人头像" class="contact-avatar">
                        <div class="contact-details">
                            <h3 id="chat-contact-name" class="contact-name">联系人</h3>
                            <span id="chat-contact-status" class="contact-status offline">离线</span>
                        </div>
                    </div>
                    <div class="chat-actions">
                        <button id="chat-minimize-btn" class="chat-action-btn" title="最小化">
                            <i class="fa fa-minus"></i>
                        </button>
                        <button id="chat-close-btn" class="chat-action-btn" title="关闭">
                            <i class="fa fa-times"></i>
                        </button>
                    </div>
                </div>

                <!-- 消息显示区域 -->
                <div class="chat-messages" id="chat-messages">
                    <div class="messages-container" id="messages-container">
                        <div class="empty-messages">
                            <i class="fa fa-comments"></i>
                            <p>开始聊天吧</p>
                        </div>
                    </div>
                    <div id="typing-indicator" class="typing-indicator hidden">
                        <div class="typing-dots">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                        <span class="typing-text">正在输入...</span>
                    </div>
                </div>

                <!-- 消息输入区域 -->
                <div class="chat-input-area">
                    <div class="input-tools">
                        <button id="attach-file-btn" class="input-tool-btn" title="附件">
                            <i class="fa fa-paperclip"></i>
                        </button>
                        <button id="send-image-btn" class="input-tool-btn" title="图片">
                            <i class="fa fa-image"></i>
                        </button>
                        <button id="emoji-btn" class="input-tool-btn" title="表情">
                            <i class="fa fa-smile-o"></i>
                        </button>
                    </div>
                    <div class="input-wrapper">
                        <textarea id="message-input" placeholder="输入消息..." rows="1" maxlength="1000"></textarea>
                        <button id="send-message-btn" class="send-btn" disabled>
                            <i class="fa fa-paper-plane"></i>
                        </button>
                    </div>
                </div>

                <!-- 文件上传区域 -->
                <div id="file-upload-area" class="file-upload-area hidden">
                    <div class="upload-content">
                        <i class="fa fa-cloud-upload upload-icon"></i>
                        <p class="upload-text">拖拽文件到此处或点击选择文件</p>
                        <input type="file" id="file-input" multiple accept="image/*,.pdf,.doc,.docx,.txt">
                    </div>
                </div>
            </div>

            <!-- 聊天窗口最小化后的浮动按钮 -->
            <div id="chat-float-btn" class="chat-float-btn hidden">
                <button id="open-chat-btn" class="float-btn">
                    <i class="fa fa-comments"></i>
                    <span id="unread-count" class="unread-badge hidden">0</span>
                </button>
            </div>
        `;
        
        // 添加到页面
        document.body.appendChild(chatContainer);
        
        // 添加CSS样式
        this.addChatStyles();
    }
    
    /**
     * 添加聊天样式
     */
    addChatStyles() {
        if (document.getElementById('chat-styles')) {
            return;
        }
        
        const link = document.createElement('link');
        link.id = 'chat-styles';
        link.rel = 'stylesheet';
        link.href = '/css/chat.css';
        document.head.appendChild(link);
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        // 窗口控制按钮
        document.getElementById('chat-minimize-btn')?.addEventListener('click', () => this.minimize());
        document.getElementById('chat-close-btn')?.addEventListener('click', () => this.close());
        document.getElementById('open-chat-btn')?.addEventListener('click', () => this.open());
        
        // 消息输入
        const messageInput = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-message-btn');
        
        messageInput?.addEventListener('input', (e) => {
            this.handleInputChange(e);
        });
        
        messageInput?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        sendBtn?.addEventListener('click', () => this.sendMessage());
        
        // 工具按钮
        document.getElementById('attach-file-btn')?.addEventListener('click', () => this.showFileUpload());
        document.getElementById('send-image-btn')?.addEventListener('click', () => this.selectImage());
        document.getElementById('emoji-btn')?.addEventListener('click', () => this.showEmojiPicker());
        
        // 文件上传
        document.getElementById('file-input')?.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // 点击外部关闭文件上传区域
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#file-upload-area') && !e.target.closest('#attach-file-btn')) {
                this.hideFileUpload();
            }
        });
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
        
        this.socket.on('connect', () => {
            console.log('✅ 聊天Socket连接成功');
            this.onSocketConnect();
        });
        
        this.socket.on('new_message', (message) => {
            this.handleNewMessage(message);
        });
        
        this.socket.on('message_sent', (message) => {
            this.handleMessageSent(message);
        });
        
        this.socket.on('user_typing', (data) => {
            this.handleUserTyping(data);
        });
        
        this.socket.on('disconnect', (reason) => {
            console.log('❌ 聊天Socket连接断开:', reason);
            this.onSocketDisconnect(reason);
        });
        
        this.socket.on('connect_error', (error) => {
            console.error('❌ 聊天Socket连接错误:', error);
            this.handleSocketError(error);
        });
    }
    
    /**
     * Socket连接成功处理
     */
    onSocketConnect() {
        // 可以在这里添加连接成功后的逻辑
        if (this.currentContact) {
            this.joinRoom(this.currentContact.id);
        }
    }
    
    /**
     * Socket连接断开处理
     */
    onSocketDisconnect(reason) {
        // 可以在这里添加连接断开后的逻辑
        console.log('Socket断开原因:', reason);
    }
    
    /**
     * Socket错误处理
     */
    handleSocketError(error) {
        console.error('Socket错误:', error);
        // 可以显示用户友好的错误提示
        this.showNotification('连接服务器失败，请检查网络连接', 'error');
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
     * 打开聊天窗口
     */
    open(contact = null) {
        if (contact) {
            this.setContact(contact);
        }
        
        if (!this.currentContact) {
            console.warn('请先选择聊天对象');
            return;
        }
        
        this.isOpen = true;
        this.isMinimized = false;
        
        const chatWindow = document.getElementById('chat-window');
        const floatBtn = document.getElementById('chat-float-btn');
        
        chatWindow?.classList.remove('hidden');
        floatBtn?.classList.add('hidden');
        
        // 加载消息历史
        this.loadMessageHistory();
        
        // 加入房间
        this.joinRoom();
        
        // 聚焦输入框
        setTimeout(() => {
            document.getElementById('message-input')?.focus();
        }, 100);
    }
    
    /**
     * 关闭聊天窗口
     */
    close() {
        this.isOpen = false;
        this.isMinimized = false;
        
        const chatWindow = document.getElementById('chat-window');
        const floatBtn = document.getElementById('chat-float-btn');
        
        chatWindow?.classList.add('hidden');
        
        if (this.unreadCount > 0) {
            floatBtn?.classList.remove('hidden');
        }
        
        // 离开房间
        this.leaveRoom();
    }
    
    /**
     * 最小化聊天窗口
     */
    minimize() {
        this.isMinimized = true;
        
        const chatWindow = document.getElementById('chat-window');
        const floatBtn = document.getElementById('chat-float-btn');
        
        chatWindow?.classList.add('minimized');
        floatBtn?.classList.remove('hidden');
    }
    
    /**
     * 设置聊天对象
     */
    setContact(contact) {
        this.currentContact = contact;
        
        // 更新头部信息
        const avatar = document.getElementById('chat-contact-avatar');
        const name = document.getElementById('chat-contact-name');
        const status = document.getElementById('chat-contact-status');
        
        if (avatar) avatar.src = contact.avatar || '/uploads/avatars/default-user.png';
        if (name) name.textContent = contact.name || contact.sender || '联系人';
        if (status) {
            status.textContent = contact.online ? '在线' : '离线';
            status.className = `contact-status ${contact.online ? 'online' : 'offline'}`;
        }
        
        // 清空消息列表
        this.messages = [];
        this.renderMessages();
    }
    
    /**
     * 加载消息历史
     */
    async loadMessageHistory() {
        if (!this.currentContact || !this.userInfo) {
            return;
        }
        
        try {
            const contactId = this.currentContact.id || this.currentContact.contactId?.replace(/^(user_|caregiver_)/, '');
            const contactType = this.currentContact.type || (this.currentContact.contactId?.startsWith('user_') ? 'user' : 'caregiver');
            
            const response = await fetch(`/api/${this.userType}/messages/history?contact_id=${contactId}&contact_type=${contactType}`, {
                headers: {
                    'Authorization': `Bearer ${this.userToken}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.messages = data.data.messages || [];
                    this.renderMessages();
                }
            }
        } catch (error) {
            console.error('加载消息历史失败:', error);
        }
    }
    
    /**
     * 渲染消息列表
     */
    renderMessages() {
        const container = document.getElementById('messages-container');
        if (!container) return;
        
        if (this.messages.length === 0) {
            container.innerHTML = `
                <div class="empty-messages">
                    <i class="fa fa-comments"></i>
                    <p>开始聊天吧</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.messages.map(message => this.createMessageHTML(message)).join('');
        
        // 滚动到底部
        this.scrollToBottom();
    }
    
    /**
     * 创建消息HTML
     */
    createMessageHTML(message) {
        const isSent = message.sender_id == this.userInfo.id && message.sender_type === this.userType;
        const time = new Date(message.created_at).toLocaleTimeString('zh-CN', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        return `
            <div class="message ${isSent ? 'sent' : 'received'}">
                <div class="message-bubble">
                    <div class="message-content">${this.escapeHtml(message.content)}</div>
                    <div class="message-time">
                        ${time}
                        ${isSent ? `<span class="message-status ${message.is_read ? 'read' : 'delivered'}">${message.is_read ? '已读' : '已送达'}</span>` : ''}
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * 处理输入变化
     */
    handleInputChange(e) {
        const input = e.target;
        const sendBtn = document.getElementById('send-message-btn');
        
        // 自动调整高度
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 120) + 'px';
        
        // 更新发送按钮状态
        const hasText = input.value.trim().length > 0;
        sendBtn.disabled = !hasText;
        
        // 发送正在输入状态
        if (hasText && !this.isTyping) {
            this.sendTypingStatus(true);
        } else if (!hasText && this.isTyping) {
            this.sendTypingStatus(false);
        }
        
        // 重置输入定时器
        clearTimeout(this.typingTimer);
        this.typingTimer = setTimeout(() => {
            this.sendTypingStatus(false);
        }, 1000);
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
    handleNewMessage(message) {
        this.messages.push(message);
        this.renderMessages();
        
        // 如果窗口未打开，增加未读计数
        if (!this.isOpen) {
            this.unreadCount++;
            this.updateUnreadCount();
        }
        
        // 显示通知
        if (this.notificationManager) {
            this.notificationManager.showMessageNotification(message);
        } else {
            // 备用提示音
            this.playNotificationSound();
        }
    }
    
    /**
     * 处理消息发送确认
     */
    handleMessageSent(message) {
        // 消息已添加到列表中，无需重复添加
        this.scrollToBottom();
    }
    
    /**
     * 处理用户输入状态
     */
    handleUserTyping(data) {
        const indicator = document.getElementById('typing-indicator');
        if (!indicator) return;
        
        if (data.is_typing) {
            indicator.classList.remove('hidden');
        } else {
            indicator.classList.add('hidden');
        }
    }
    
    /**
     * 发送输入状态
     */
    sendTypingStatus(isTyping) {
        if (!this.socket || !this.currentContact || this.isTyping === isTyping) {
            return;
        }
        
        this.isTyping = isTyping;
        
        const contactId = this.currentContact.id || this.currentContact.contactId?.replace(/^(user_|caregiver_)/, '');
        const contactType = this.currentContact.type || (this.currentContact.contactId?.startsWith('user_') ? 'user' : 'caregiver');
        
        this.socket.emit('typing', {
            user_id: this.userInfo.id,
            user_type: this.userType,
            contact_id: contactId,
            contact_type: contactType,
            is_typing: isTyping
        });
    }
    
    /**
     * 加入房间
     */
    joinRoom() {
        if (!this.socket || !this.userInfo) return;
        
        const room = `${this.userType}_${this.userInfo.id}`;
        this.socket.emit('join', { room: room });
    }
    
    /**
     * 离开房间
     */
    leaveRoom() {
        if (!this.socket || !this.userInfo) return;
        
        const room = `${this.userType}_${this.userInfo.id}`;
        this.socket.emit('leave', { room: room });
    }
    
    /**
     * 滚动到底部
     */
    scrollToBottom() {
        const container = document.getElementById('messages-container');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }
    
    /**
     * 更新未读计数
     */
    updateUnreadCount() {
        const badge = document.getElementById('unread-count');
        if (badge) {
            if (this.unreadCount > 0) {
                badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
                badge.classList.remove('hidden');
            } else {
                badge.classList.add('hidden');
            }
        }
    }
    
    /**
     * 显示文件上传区域
     */
    showFileUpload() {
        const uploadArea = document.getElementById('file-upload-area');
        if (uploadArea) {
            uploadArea.classList.remove('hidden');
        }
    }
    
    /**
     * 隐藏文件上传区域
     */
    hideFileUpload() {
        const uploadArea = document.getElementById('file-upload-area');
        if (uploadArea) {
            uploadArea.classList.add('hidden');
        }
    }
    
    /**
     * 选择图片
     */
    selectImage() {
        const fileInput = document.getElementById('file-input');
        if (fileInput) {
            fileInput.accept = 'image/*';
            fileInput.click();
        }
    }
    
    /**
     * 显示表情选择器
     */
    showEmojiPicker() {
        // TODO: 实现表情选择器
        console.log('表情选择器功能待实现');
    }
    
    /**
     * 处理文件选择
     */
    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            console.log('选择了文件:', files);
            // TODO: 实现文件上传
        }
        this.hideFileUpload();
    }
    
    /**
     * 播放通知音
     */
    playNotificationSound() {
        // 创建简单的提示音
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.1);
    }
    
    /**
     * HTML转义
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// 全局聊天窗口实例
window.ChatWindow = ChatWindow;
