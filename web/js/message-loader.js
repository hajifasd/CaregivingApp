/**
 * 统一消息加载工具
 * 提供统一的消息历史加载和错误处理
 */

class MessageLoader {
    constructor() {
        this.baseUrl = '/api/chat';
        this.retryCount = 3;
        this.retryDelay = 1000;
    }
    
    /**
     * 获取用户信息
     */
    getCurrentUserInfo() {
        // 尝试从localStorage获取用户信息
        let userInfo = JSON.parse(localStorage.getItem('user_info') || '{}');
        let userType = 'user';
        let token = localStorage.getItem('user_token');
        
        // 如果用户端没有信息，尝试护工端
        if (!userInfo.id) {
            userInfo = JSON.parse(localStorage.getItem('caregiver_info') || '{}');
            userType = 'caregiver';
            token = localStorage.getItem('caregiver_token');
        }
        
        // 如果护工端也没有信息，尝试管理端
        if (!userInfo.id) {
            userInfo = JSON.parse(localStorage.getItem('admin_info') || '{}');
            userType = 'admin';
            token = localStorage.getItem('admin_token');
        }
        
        return {
            id: userInfo.id,
            name: userInfo.name || userInfo.username || userInfo.real_name || '用户',
            type: userType,
            token: token
        };
    }
    
    /**
     * 显示加载状态
     */
    showLoadingState(containerId, message = '加载中...') {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="flex items-center justify-center p-8">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    <span class="ml-3 text-gray-600">${message}</span>
                </div>
            `;
        }
    }
    
    /**
     * 显示错误状态
     */
    showErrorState(containerId, error, retryCallback = null) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="flex flex-col items-center justify-center p-8 text-center">
                    <div class="text-red-500 text-6xl mb-4">⚠️</div>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">加载失败</h3>
                    <p class="text-gray-600 mb-4">${error}</p>
                    ${retryCallback ? `
                        <button onclick="${retryCallback}" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                            重试
                        </button>
                    ` : ''}
                </div>
            `;
        }
    }
    
    /**
     * 显示空状态
     */
    showEmptyState(containerId, message = '暂无消息') {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="flex flex-col items-center justify-center p-8 text-center">
                    <div class="text-gray-400 text-6xl mb-4">💬</div>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">${message}</h3>
                    <p class="text-gray-600">开始与护工交流吧</p>
                </div>
            `;
        }
    }
    
    /**
     * 显示通知
     */
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
            notification.remove();
        }, 3000);
    }
    
    /**
     * 获取消息历史
     */
    async getMessageHistory(contactId, contactType, options = {}) {
        const userInfo = this.getCurrentUserInfo();
        
        if (!userInfo.id) {
            throw new Error('用户未登录，无法加载消息');
        }
        
        const params = new URLSearchParams({
            user_id: userInfo.id,
            user_type: userInfo.type,
            contact_id: contactId,
            contact_type: contactType,
            limit: options.limit || 50,
            offset: options.offset || 0
        });
        
        const url = `${this.baseUrl}/messages?${params}`;
        
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${userInfo.token}`
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.message || '获取消息失败');
            }
            
            return data.data || [];
            
        } catch (error) {
            console.error('获取消息历史失败:', error);
            throw error;
        }
    }
    
    /**
     * 获取对话列表
     */
    async getConversations(options = {}) {
        const userInfo = this.getCurrentUserInfo();
        
        if (!userInfo.id) {
            throw new Error('用户未登录，无法加载对话');
        }
        
        const params = new URLSearchParams({
            user_id: userInfo.id,
            user_type: userInfo.type,
            limit: options.limit || 20,
            offset: options.offset || 0
        });
        
        const url = `${this.baseUrl}/conversations?${params}`;
        
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${userInfo.token}`
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.message || '获取对话列表失败');
            }
            
            // 确保返回的是数组
            const conversations = data.data || [];
            return Array.isArray(conversations) ? conversations : [];
            
        } catch (error) {
            console.error('获取对话列表失败:', error);
            throw error;
        }
    }
    
    /**
     * 带重试的消息加载
     */
    async loadWithRetry(loadFunction, retryCount = null) {
        const maxRetries = retryCount || this.retryCount;
        let lastError = null;
        
        for (let i = 0; i <= maxRetries; i++) {
            try {
                return await loadFunction();
            } catch (error) {
                lastError = error;
                console.warn(`加载失败 (${i + 1}/${maxRetries + 1}):`, error.message);
                
                if (i < maxRetries) {
                    // 等待后重试
                    await new Promise(resolve => setTimeout(resolve, this.retryDelay * (i + 1)));
                }
            }
        }
        
        throw lastError;
    }
    
    /**
     * 加载消息历史并显示
     */
    async loadMessageHistory(contactId, contactType, containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error('容器元素不存在:', containerId);
            return;
        }
        
        // 显示加载状态
        this.showLoadingState(containerId, '加载消息历史...');
        
        try {
            const messages = await this.loadWithRetry(() => 
                this.getMessageHistory(contactId, contactType, options)
            );
            
            if (messages.length === 0) {
                this.showEmptyState(containerId, '暂无消息记录');
                return;
            }
            
            // 渲染消息
            this.renderMessages(containerId, messages);
            
        } catch (error) {
            console.error('加载消息历史失败:', error);
            this.showErrorState(containerId, error.message, () => {
                this.loadMessageHistory(contactId, contactType, containerId, options);
            });
            this.showNotification('加载消息失败: ' + error.message, 'error');
        }
    }
    
    /**
     * 加载对话列表并显示
     */
    async loadConversations(containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error('容器元素不存在:', containerId);
            return;
        }
        
        // 显示加载状态
        this.showLoadingState(containerId, '加载对话列表...');
        
        try {
            const conversations = await this.loadWithRetry(() => 
                this.getConversations(options)
            );
            
            if (conversations.length === 0) {
                this.showEmptyState(containerId, '暂无对话');
                return;
            }
            
            // 渲染对话列表
            this.renderConversations(containerId, conversations);
            
        } catch (error) {
            console.error('加载对话列表失败:', error);
            this.showErrorState(containerId, error.message, () => {
                this.loadConversations(containerId, options);
            });
            this.showNotification('加载对话列表失败: ' + error.message, 'error');
        }
    }
    
    /**
     * 渲染消息列表
     */
    renderMessages(containerId, messages) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const userInfo = this.getCurrentUserInfo();
        
        const messagesHTML = messages.map(message => {
            const isOwn = message.sender_id == userInfo.id && message.sender_type === userInfo.type;
            const time = new Date(message.timestamp || message.created_at || Date.now()).toLocaleTimeString();
            
            return `
                <div class="flex ${isOwn ? 'justify-end' : 'justify-start'} mb-4">
                    <div class="max-w-xs px-4 py-2 rounded-lg ${
                        isOwn ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-900'
                    }">
                        <div class="text-sm">${message.content}</div>
                        <div class="text-xs opacity-75 mt-1">${time}</div>
                    </div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = `
            <div class="space-y-3">
                ${messagesHTML}
            </div>
        `;
    }
    
    /**
     * 渲染对话列表
     */
    renderConversations(containerId, conversations) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        // 确保conversations是数组
        if (!Array.isArray(conversations)) {
            console.error('conversations不是数组:', conversations);
            this.showErrorState(containerId, '对话数据格式错误');
            return;
        }
        
        const conversationsHTML = conversations.map(conversation => {
            return `
                <div class="flex items-center p-4 border-b border-gray-200 hover:bg-gray-50 cursor-pointer" 
                     onclick="openConversation('${conversation.contactId}', '${conversation.name}', '${conversation.avatar}')">
                    <div class="flex-shrink-0">
                        <img src="${conversation.avatar}" alt="${conversation.name}" 
                             class="w-12 h-12 rounded-full object-cover">
                    </div>
                    <div class="ml-4 flex-1 min-w-0">
                        <div class="flex items-center justify-between">
                            <h3 class="text-sm font-medium text-gray-900 truncate">${conversation.name}</h3>
                            <span class="text-xs text-gray-500">${conversation.time}</span>
                        </div>
                        <p class="text-sm text-gray-600 truncate">${conversation.content}</p>
                    </div>
                    ${conversation.unread ? '<div class="w-2 h-2 bg-red-500 rounded-full"></div>' : ''}
                </div>
            `;
        }).join('');
        
        container.innerHTML = `
            <div class="divide-y divide-gray-200">
                ${conversationsHTML}
            </div>
        `;
    }
}

// 创建全局实例
window.messageLoader = new MessageLoader();

// 导出到全局
window.MessageLoader = MessageLoader;
