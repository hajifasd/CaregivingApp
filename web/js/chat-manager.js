/**
 * 聊天管理器 - 实现用户与护工的实时通信
 */

class ChatManager {
    constructor() {
        this.socket = null;
        this.currentChat = null;
        this.chatWindows = new Map();
        this.messageHistory = new Map();
        this.userId = null;
        this.userName = null;
        
        this.init();
    }
    
    init() {
        // 获取用户信息
        this.getUserInfo();
        
        // 初始化Socket.IO连接
        this.initSocket();
        
        // 绑定事件
        this.bindEvents();
    }
    
    getUserInfo() {
        // 从localStorage或session获取用户信息
        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
        this.userId = userInfo.id;
        this.userName = userInfo.name || '用户';
        
        if (!this.userId) {
            console.warn('用户未登录，部分功能可能受限');
        }
    }
    
    initSocket() {
        try {
            // 连接Socket.IO服务器
            this.socket = io('http://localhost:8000');
            
            this.socket.on('connect', () => {
                console.log('✅ 聊天服务器连接成功');
                this.updateConnectionStatus(true);
            });
            
            this.socket.on('disconnect', () => {
                console.log('❌ 聊天服务器连接断开');
                this.updateConnectionStatus(false);
            });
            
            this.socket.on('message_received', (data) => {
                this.handleIncomingMessage(data);
            });
            
            this.socket.on('user_online', (data) => {
                this.updateUserStatus(data.userId, 'online');
            });
            
            this.socket.on('user_offline', (data) => {
                this.updateUserStatus(data.userId, 'offline');
            });
            
        } catch (error) {
            console.error('❌ Socket.IO连接失败:', error);
            this.showNotification('聊天服务连接失败，请检查网络连接', 'error');
        }
    }
    
    bindEvents() {
        // 绑定新建对话按钮
        const newChatBtn = document.getElementById('new-chat-btn');
        if (newChatBtn) {
            newChatBtn.addEventListener('click', () => this.showNewChatModal());
        }
        
        // 绑定搜索消息按钮
        const searchBtn = document.getElementById('search-messages-btn');
        if (searchBtn) {
            searchBtn.addEventListener('click', () => this.showSearchModal());
        }
    }
    
    // 打开聊天窗口
    openChat(contactId, contactName, contactAvatar) {
        if (this.chatWindows.has(contactId)) {
            // 如果聊天窗口已存在，直接显示
            this.showChatWindow(contactId);
            return;
        }
        
        // 创建新的聊天窗口
        this.createChatWindow(contactId, contactName, contactAvatar);
        
        // 加载聊天历史
        this.loadChatHistory(contactId);
        
        // 设置当前聊天
        this.currentChat = contactId;
    }
    
    // 创建聊天窗口
    createChatWindow(contactId, contactName, contactAvatar) {
        const chatWindow = document.createElement('div');
        chatWindow.id = `chat-${contactId}`;
        chatWindow.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        
        chatWindow.innerHTML = `
            <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl h-5/6 flex flex-col">
                <!-- 聊天窗口头部 -->
                <div class="flex items-center justify-between p-4 border-b border-gray-200 bg-primary text-white rounded-t-xl">
                    <div class="flex items-center gap-3">
                        <img src="${contactAvatar}" alt="${contactName}" class="w-10 h-10 rounded-full object-cover">
                        <div>
                            <h3 class="font-bold text-lg">${contactName}</h3>
                            <span class="text-sm opacity-90" id="status-${contactId}">在线</span>
                        </div>
                    </div>
                    <div class="flex items-center gap-2">
                        <button class="p-2 hover:bg-white/20 rounded-lg transition-colors" onclick="chatManager.toggleChatWindow('${contactId}')">
                            <i class="fa fa-minus"></i>
                        </button>
                        <button class="p-2 hover:bg-white/20 rounded-lg transition-colors" onclick="chatManager.closeChatWindow('${contactId}')">
                            <i class="fa fa-times"></i>
                        </button>
                    </div>
                </div>
                
                <!-- 聊天消息区域 -->
                <div class="flex-1 overflow-y-auto p-4 space-y-4" id="messages-${contactId}">
                    <!-- 消息内容将在这里动态生成 -->
                </div>
                
                <!-- 消息输入区域 -->
                <div class="p-4 border-t border-gray-200">
                    <div class="flex items-center gap-3">
                        <button class="p-2 text-gray-500 hover:text-primary transition-colors" onclick="chatManager.toggleEmojiPicker('${contactId}')">
                            <i class="fa fa-smile-o"></i>
                        </button>
                        <div class="flex-1 relative">
                            <textarea 
                                id="input-${contactId}" 
                                placeholder="输入消息..." 
                                class="w-full p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary/50"
                                rows="2"
                                onkeydown="if(event.keyCode===13&&!event.shiftKey){event.preventDefault();chatManager.sendMessage('${contactId}')}"
                            ></textarea>
                        </div>
                        <button class="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors" onclick="chatManager.sendMessage('${contactId}')">
                            <i class="fa fa-paper-plane mr-2"></i>发送
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(chatWindow);
        this.chatWindows.set(contactId, chatWindow);
        
        // 绑定输入框事件
        const input = chatWindow.querySelector(`#input-${contactId}`);
        input.addEventListener('input', () => {
            this.autoResizeTextarea(input);
        });
        
        // 聚焦输入框
        input.focus();
    }
    
    // 显示聊天窗口
    showChatWindow(contactId) {
        const chatWindow = this.chatWindows.get(contactId);
        if (chatWindow) {
            chatWindow.style.display = 'block';
            chatWindow.style.zIndex = '50';
            
            // 聚焦到输入框
            const input = chatWindow.querySelector(`#input-${contactId}`);
            if (input) {
                input.focus();
            }
        }
    }
    
    // 隐藏聊天窗口
    toggleChatWindow(contactId) {
        const chatWindow = this.chatWindows.get(contactId);
        if (chatWindow) {
            if (chatWindow.classList.contains('hidden')) {
                chatWindow.classList.remove('hidden');
                chatWindow.classList.add('flex');
            } else {
                chatWindow.classList.add('hidden');
                chatWindow.classList.remove('flex');
            }
        }
    }
    
    // 关闭聊天窗口
    closeChatWindow(contactId) {
        const chatWindow = this.chatWindows.get(contactId);
        if (chatWindow) {
            document.body.removeChild(chatWindow);
            this.chatWindows.delete(contactId);
            
            if (this.currentChat === contactId) {
                this.currentChat = null;
            }
        }
    }
    
    // 发送消息
    sendMessage(contactId) {
        const input = document.getElementById(`input-${contactId}`);
        const message = input.value.trim();
        
        if (!message) return;
        
        // 获取真实的用户ID
        let userId = this.userId;
        if (!userId) {
            const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
            userId = userInfo.id || '1';
        }
        
        // 处理contactId格式 - 支持多种ID格式
        let numericContactId = contactId;
        let receiverType = 'caregiver';
        
        if (typeof contactId === 'string') {
            if (contactId.startsWith('caregiver_')) {
                numericContactId = contactId.replace('caregiver_', '');
                receiverType = 'caregiver';
            } else if (contactId.startsWith('user_')) {
                numericContactId = contactId.replace('user_', '');
                receiverType = 'user';
            } else if (contactId.isdigit()) {
                numericContactId = contactId;
                receiverType = 'caregiver'; // 默认假设是护工
            }
        }
        
        // 创建消息对象 - 使用后端期望的字段格式
        const messageData = {
            id: Date.now(),
            sender_id: userId,
            sender_name: this.userName || '用户',
            sender_type: 'user', // 明确指定发送者类型
            recipient_id: numericContactId,
            recipient_type: receiverType, // 明确指定接收者类型
            content: message,
            timestamp: new Date().toISOString(),
            type: 'text'
        };
        
        console.log('发送消息:', messageData);
        
        // 发送到服务器
        if (this.socket && this.socket.connected) {
            this.socket.emit('send_message', messageData);
        }
        
        // 添加到本地消息历史（使用原始contactId作为key）
        this.addMessageToHistory(contactId, messageData);
        
        // 显示消息
        this.displayMessage(contactId, messageData);
        
        // 清空输入框
        input.value = '';
        this.autoResizeTextarea(input);
        
        // 更新消息列表
        this.updateMessageList(contactId, messageData);
    }
    
    // 处理接收到的消息
    handleIncomingMessage(data) {
        const { senderId, content, timestamp, senderType } = data;
        
        // 确定联系人ID（可能是数字ID，需要转换为前端格式）
        let contactId = senderId;
        
        // 如果senderId是数字，需要找到对应的护工ID或用户ID
        if (typeof senderId === 'string' && senderId.match(/^\d+$/)) {
            // 查找当前打开的聊天窗口，确定contactId
            for (let [key, window] of this.chatWindows) {
                if (key.startsWith('caregiver_')) {
                    // 提取数字部分进行比较
                    const numericKey = key.replace('caregiver_', '');
                    if (numericKey === senderId) {
                        contactId = key;
                        break;
                    }
                } else if (key.startsWith('user_')) {
                    // 提取数字部分进行比较
                    const numericKey = key.replace('user_', '');
                    if (numericKey === senderId) {
                        contactId = key;
                        break;
                    }
                }
            }
            
            // 如果没找到对应的聊天窗口，根据发送者类型构造ID
            if (contactId === senderId) {
                if (senderType === 'caregiver') {
                    contactId = `caregiver_${senderId}`;
                } else if (senderType === 'user') {
                    contactId = `user_${senderId}`;
                }
            }
        }
        
        console.log(`收到消息，联系人ID: ${contactId}, 原始senderId: ${senderId}, 发送者类型: ${senderType}`);
        
        // 添加到消息历史（使用前端格式的contactId）
        this.addMessageToHistory(contactId, data);
        
        // 如果聊天窗口打开，显示消息
        if (this.chatWindows.has(contactId)) {
            this.displayMessage(contactId, data);
        }
        
        // 更新消息列表
        this.updateMessageList(contactId, data);
        
        // 显示通知
        if (this.currentChat !== contactId) {
            const senderName = data.senderName || '联系人';
            this.showNotification(`收到来自${senderName}的新消息: ${content.substring(0, 30)}...`, 'info');
        }
    }
    
    // 添加消息到历史记录
    addMessageToHistory(contactId, message) {
        if (!this.messageHistory.has(contactId)) {
            this.messageHistory.set(contactId, []);
        }
        
        // 确保消息有完整的字段信息
        const enrichedMessage = {
            ...message,
            // 如果缺少字段，提供默认值
            senderType: message.senderType || 'user',
            receiverType: message.receiverType || 'caregiver',
            timestamp: message.timestamp || new Date().toISOString(),
            type: message.type || 'text'
        };
        
        this.messageHistory.get(contactId).push(enrichedMessage);
        
        // 限制历史记录数量
        if (this.messageHistory.get(contactId).length > 100) {
            this.messageHistory.get(contactId).shift();
        }
    }
    
    // 显示消息
    displayMessage(contactId, message) {
        const messagesContainer = document.getElementById(`messages-${contactId}`);
        if (!messagesContainer) return;
        
        // 处理消息发送者ID - 支持多种格式
        let messageSenderId = message.senderId;
        if (typeof message.senderId === 'string' && message.senderId.match(/^\d+$/)) {
            // 如果是数字ID，需要转换为前端格式
            if (message.senderType === 'caregiver') {
                messageSenderId = `caregiver_${message.senderId}`;
            } else if (message.senderType === 'user') {
                messageSenderId = `user_${message.senderId}`;
            }
        }
        
        const isOwnMessage = messageSenderId === this.userId || 
                           (this.userId && messageSenderId === `user_${this.userId}`) ||
                           (this.userId && messageSenderId === this.userId.toString());
        
        const messageElement = document.createElement('div');
        messageElement.className = `flex ${isOwnMessage ? 'justify-end' : 'justify-start'}`;
        
        messageElement.innerHTML = `
            <div class="max-w-xs lg:max-w-md ${isOwnMessage ? 'bg-primary text-white' : 'bg-gray-100 text-gray-800'} rounded-lg p-3 shadow-sm">
                <div class="text-sm">${message.content}</div>
                <div class="text-xs ${isOwnMessage ? 'text-white/70' : 'text-gray-500'} mt-1">
                    ${this.formatTime(message.timestamp)}
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // 加载聊天历史
    async loadChatHistory(contactId) {
        try {
            console.log(`正在加载与 ${contactId} 的聊天历史...`);
            
            // 获取真实的用户ID，如果没有则使用默认值
            let userId = this.userId;
            if (!userId) {
                // 尝试从localStorage获取
                const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
                userId = userInfo.id;
                
                // 如果还是没有，使用默认值
                if (!userId) {
                    userId = '1'; // 使用数字ID，与数据库中的用户ID匹配
                    console.warn('未找到用户ID，使用默认值:', userId);
                }
            }
            
            // 处理contactId格式 - 支持多种ID格式
            let numericContactId = contactId;
            if (typeof contactId === 'string') {
                if (contactId.startsWith('caregiver_')) {
                    numericContactId = contactId.replace('caregiver_', '');
                } else if (contactId.startsWith('user_')) {
                    numericContactId = contactId.replace('user_', '');
                } else if (contactId.isdigit()) {
                    numericContactId = contactId;
                }
            }
            
            console.log(`使用用户ID: ${userId}, 联系人ID: ${numericContactId}`);
            
            // 构建请求URL，包含用户ID参数
            const url = `/api/chat/history/${numericContactId}?user_id=${userId}&limit=100`;
            
            const response = await fetch(url);
            
            if (response.ok) {
                const result = await response.json();
                
                if (result.success) {
                    const messages = result.data.messages || [];
                    // 使用原始的contactId作为key，这样前端ID格式保持一致
                    this.messageHistory.set(contactId, messages);
                    
                    console.log(`成功加载 ${messages.length} 条聊天记录`);
                    
                    // 显示历史消息
                    const messagesContainer = document.getElementById(`messages-${contactId}`);
                    if (messagesContainer) {
                        messagesContainer.innerHTML = '';
                        messages.forEach(message => {
                            this.displayMessage(contactId, message);
                        });
                        
                        // 滚动到底部
                        messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    }
                } else {
                    console.warn('加载聊天历史失败:', result.message);
                    // 如果API失败，尝试从本地历史记录加载
                    this.loadLocalHistory(contactId);
                }
            } else {
                console.error('加载聊天历史HTTP错误:', response.status);
                // 如果HTTP请求失败，尝试从本地历史记录加载
                this.loadLocalHistory(contactId);
            }
        } catch (error) {
            console.error('加载聊天历史失败:', error);
            // 如果出现异常，尝试从本地历史记录加载
            this.loadLocalHistory(contactId);
        }
    }
    
    // 从本地历史记录加载（备用方案）
    loadLocalHistory(contactId) {
        const localMessages = this.messageHistory.get(contactId) || [];
        console.log(`从本地历史记录加载 ${localMessages.length} 条消息`);
        
        if (localMessages.length > 0) {
            const messagesContainer = document.getElementById(`messages-${contactId}`);
            if (messagesContainer) {
                messagesContainer.innerHTML = '';
                localMessages.forEach(message => {
                    // 确保消息有完整的字段信息
                    const enrichedMessage = {
                        ...message,
                        senderType: message.senderType || 'user',
                        receiverType: message.receiverType || 'caregiver',
                        timestamp: message.timestamp || new Date().toISOString(),
                        type: message.type || 'text'
                    };
                    this.displayMessage(contactId, enrichedMessage);
                });
                
                // 滚动到底部
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        } else {
            // 显示欢迎消息
            this.displayWelcomeMessage(contactId);
        }
    }
    
    // 显示欢迎消息
    displayWelcomeMessage(contactId) {
        const messagesContainer = document.getElementById(`messages-${contactId}`);
        if (!messagesContainer) return;
        
        const welcomeMessage = {
            id: 'welcome',
            senderId: 'system',
            senderName: '系统',
            senderType: 'system',
            receiverId: contactId,
            receiverType: 'user',
            content: '欢迎开始新的对话！您可以在这里与护工进行交流。',
            timestamp: new Date().toISOString(),
            type: 'system'
        };
        
        this.displayMessage(contactId, welcomeMessage);
    }
    
    // 更新消息列表
    updateMessageList(contactId, message) {
        // 更新左侧消息列表中的最新消息
        const messageItem = document.querySelector(`[data-contact-id="${contactId}"]`);
        if (messageItem) {
            const contentElement = messageItem.querySelector('.text-sm.text-gray-600');
            if (contentElement) {
                contentElement.textContent = message.content || '';
            }
            
            const timeElement = messageItem.querySelector('.text-xs.text-gray-500');
            if (timeElement) {
                timeElement.textContent = this.formatTime(message.timestamp || new Date().toISOString());
            }
        }
    }
    
    // 更新用户状态
    updateUserStatus(userId, status) {
        const statusElement = document.getElementById(`status-${userId}`);
        if (statusElement) {
            statusElement.textContent = status === 'online' ? '在线' : '离线';
            statusElement.className = `text-sm ${status === 'online' ? 'text-green-400' : 'text-gray-400'}`;
        }
    }
    
    // 更新连接状态
    updateConnectionStatus(connected) {
        const statusIndicator = document.getElementById('connection-status');
        if (statusIndicator) {
            statusIndicator.textContent = connected ? '已连接' : '未连接';
            statusIndicator.className = `text-xs px-2 py-1 rounded ${connected ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`;
        }
    }
    
    // 显示新建对话模态框
    showNewChatModal() {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        
        modal.innerHTML = `
            <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-96 overflow-hidden">
                <div class="flex items-center justify-between p-4 border-b border-gray-200 bg-primary text-white">
                    <h3 class="font-bold text-lg">新建对话</h3>
                    <button onclick="this.closest('.fixed').remove()" class="p-2 hover:bg-white/20 rounded-lg transition-colors">
                        <i class="fa fa-times"></i>
                    </button>
                </div>
                <div class="p-6">
                    <div class="mb-4">
                        <label class="block text-sm font-medium text-gray-700 mb-2">选择护工</label>
                        <select id="caregiver-select" class="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50">
                            <option value="">正在加载护工列表...</option>
                        </select>
                    </div>
                    <div class="mb-4">
                        <label class="block text-sm font-medium text-gray-700 mb-2">初始消息</label>
                        <textarea id="initial-message" placeholder="输入初始消息（可选）..." 
                                  class="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50" rows="3"></textarea>
                    </div>
                    <div class="flex justify-end gap-3">
                        <button onclick="this.closest('.fixed').remove()" class="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50">
                            取消
                        </button>
                        <button onclick="chatManager.startNewChat()" class="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90">
                            开始聊天
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 点击背景关闭
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        // 加载护工列表
        this.loadCaregiversForSelect(modal);
        
        // 聚焦选择框
        setTimeout(() => {
            const select = modal.querySelector('#caregiver-select');
            if (select) {
                select.focus();
            }
        }, 100);
    }
    
    // 加载护工列表到选择框
    async loadCaregiversForSelect(modal) {
        try {
            const response = await fetch('/api/caregivers/hire-info');
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    const select = modal.querySelector('#caregiver-select');
                    select.innerHTML = '<option value="">请选择护工...</option>';
                    
                    result.data.forEach(caregiver => {
                        const option = document.createElement('option');
                        option.value = caregiver.caregiver_id;
                        option.textContent = `${caregiver.name} - ${caregiver.service_type || '护理服务'}`;
                        select.appendChild(option);
                    });
                } else {
                    const select = modal.querySelector('#caregiver-select');
                    select.innerHTML = '<option value="">加载护工列表失败</option>';
                }
            } else {
                const select = modal.querySelector('#caregiver-select');
                select.innerHTML = '<option value="">网络错误，请稍后重试</option>';
            }
        } catch (error) {
            console.error('加载护工列表失败:', error);
            const select = modal.querySelector('#caregiver-select');
            select.innerHTML = '<option value="">加载护工列表失败</option>';
        }
    }
    
    // 开始新聊天
    startNewChat() {
        const select = document.getElementById('caregiver-select');
        const initialMessage = document.getElementById('initial-message');
        const selectedValue = select.value;
        
        if (!selectedValue) {
            this.showNotification('请选择护工', 'warning');
            return;
        }
        
        // 从后端API获取护工信息
        this.loadCaregiversForNewChat(selectedValue, initialMessage);
    }
    
    // 从后端加载护工信息
    async loadCaregiversForNewChat(selectedValue, initialMessage) {
        try {
            const response = await fetch('/api/caregivers/hire-info');
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    const caregivers = result.data;
                    const caregiver = caregivers.find(c => c.caregiver_id.toString() === selectedValue);
                    
                    if (caregiver) {
                        // 打开聊天窗口
                        this.openChat(`caregiver_${caregiver.caregiver_id}`, caregiver.name, caregiver.avatar);
                        
                        // 如果有初始消息，发送它
                        if (initialMessage.value.trim()) {
                            setTimeout(() => {
                                const input = document.getElementById(`input-caregiver_${caregiver.caregiver_id}`);
                                if (input) {
                                    input.value = initialMessage.value.trim();
                                    this.sendMessage(`caregiver_${caregiver.caregiver_id}`);
                                }
                            }, 500);
                        }
                        
                        // 关闭模态框
                        document.querySelector('.fixed').remove();
                    } else {
                        this.showNotification('未找到选中的护工', 'error');
                    }
                } else {
                    this.showNotification('加载护工信息失败', 'error');
                }
            } else {
                this.showNotification('网络错误，请稍后重试', 'error');
            }
        } catch (error) {
            console.error('加载护工信息失败:', error);
            this.showNotification('加载护工信息失败', 'error');
        }
    }
    
    // 显示搜索模态框
    showSearchModal() {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        
        modal.innerHTML = `
            <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-96 overflow-hidden">
                <div class="flex items-center justify-between p-4 border-b border-gray-200 bg-primary text-white">
                    <h3 class="font-bold text-lg">搜索消息</h3>
                    <button onclick="this.closest('.fixed').remove()" class="p-2 hover:bg-white/20 rounded-lg transition-colors">
                        <i class="fa fa-times"></i>
                    </button>
                </div>
                <div class="p-6">
                    <div class="mb-4">
                        <label class="block text-sm font-medium text-gray-700 mb-2">搜索关键词</label>
                        <input type="text" id="search-input" placeholder="输入要搜索的内容..." 
                               class="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50">
                    </div>
                    <div class="mb-4">
                        <label class="block text-sm font-medium text-gray-700 mb-2">搜索范围</label>
                        <div class="space-y-2">
                            <label class="flex items-center">
                                <input type="checkbox" value="caregiver" checked class="mr-2">
                                <span>护工消息</span>
                            </label>
                            <label class="flex items-center">
                                <input type="checkbox" value="system" checked class="mr-2">
                                <span>系统通知</span>
                            </label>
                        </div>
                    </div>
                    <div class="flex justify-end gap-3">
                        <button onclick="this.closest('.fixed').remove()" class="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50">
                            取消
                        </button>
                        <button onclick="chatManager.searchMessages()" class="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90">
                            搜索
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 点击背景关闭
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        // 聚焦搜索输入框
        setTimeout(() => {
            const searchInput = modal.querySelector('#search-input');
            if (searchInput) {
                searchInput.focus();
            }
        }, 100);
    }
    
    // 搜索消息
    async searchMessages() {
        const keyword = document.getElementById('search-input').value;
        if (!keyword.trim()) {
            this.showNotification('请输入搜索关键词', 'warning');
            return;
        }
        
        try {
            // 这里可以调用后端搜索API
            // const response = await fetch(`/api/chat/search?keyword=${encodeURIComponent(keyword)}`);
            // const result = await response.json();
            
            // 暂时使用本地搜索
            const searchResults = this.searchLocalMessages(keyword);
            
            if (searchResults.length > 0) {
                this.showSearchResults(searchResults);
            } else {
                this.showNotification('未找到相关消息', 'info');
            }
            
            // 关闭搜索模态框
            document.querySelector('.fixed').remove();
            
        } catch (error) {
            console.error('搜索消息失败:', error);
            this.showNotification('搜索失败，请稍后重试', 'error');
        }
    }
    
    // 本地搜索消息
    searchLocalMessages(keyword) {
        const results = [];
        const lowerKeyword = keyword.toLowerCase();
        
        this.messageHistory.forEach((messages, contactId) => {
            messages.forEach(message => {
                if (message.content.toLowerCase().includes(lowerKeyword)) {
                    results.push({
                        ...message,
                        contactId: contactId
                    });
                }
            });
        });
        
        return results;
    }
    
    // 显示搜索结果
    showSearchResults(results) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        
        modal.innerHTML = `
            <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-96 overflow-hidden">
                <div class="flex items-center justify-between p-4 border-b border-gray-200 bg-primary text-white">
                    <h3 class="font-bold text-lg">搜索结果 (${results.length})</h3>
                    <button onclick="this.closest('.fixed').remove()" class="p-2 hover:bg-white/20 rounded-lg transition-colors">
                        <i class="fa fa-times"></i>
                    </button>
                </div>
                <div class="p-6 overflow-y-auto max-h-80">
                    ${results.map(result => `
                        <div class="border-b border-gray-200 py-3 last:border-b-0">
                            <div class="flex items-start gap-3">
                                <div class="flex-1">
                                    <div class="flex items-center gap-2 mb-1">
                                        <span class="font-medium text-sm">${result.senderName}</span>
                                        <span class="text-xs text-gray-500">${this.formatTime(result.timestamp)}</span>
                                    </div>
                                    <p class="text-sm text-gray-700">${result.content}</p>
                                </div>
                                <button onclick="chatManager.openChat('${result.contactId}', '联系人', '')" 
                                        class="px-3 py-1 text-xs bg-primary text-white rounded hover:bg-primary/90">
                                    查看对话
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 点击背景关闭
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }
    
    // 自动调整文本框高度
    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
    
    // 格式化时间
    formatTime(timestamp) {
        try {
            if (!timestamp) return '刚刚';
            
            const date = new Date(timestamp);
            if (isNaN(date.getTime())) return '刚刚';
            
            const now = new Date();
            const diff = now - date;
            
            if (diff < 60000) { // 1分钟内
                return '刚刚';
            } else if (diff < 3600000) { // 1小时内
                return `${Math.floor(diff / 60000)}分钟前`;
            } else if (diff < 86400000) { // 1天内
                return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
            } else {
                return date.toLocaleDateString('zh-CN');
            }
        } catch (error) {
            console.error('时间格式化失败:', error, timestamp);
            return '刚刚';
        }
    }
    
    // 显示通知
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
            type === 'error' ? 'bg-red-500 text-white' :
            type === 'success' ? 'bg-green-500 text-white' :
            type === 'warning' ? 'bg-yellow-500 text-white' :
            'bg-blue-500 text-white'
        }`;
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
}

// 全局聊天管理器实例
let chatManager;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    chatManager = new ChatManager();
});
