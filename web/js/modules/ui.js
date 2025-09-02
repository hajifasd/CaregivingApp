/**
 * UI管理模块
 */
class UIManager {
    static notificationContainer = null;
    static loadingOverlay = null;
    
    /**
     * 初始化UI管理器
     */
    static init() {
        this.createNotificationContainer();
        this.createLoadingOverlay();
        this.bindGlobalEvents();
    }
    
    /**
     * 创建通知容器
     */
    static createNotificationContainer() {
        if (!this.notificationContainer) {
            this.notificationContainer = document.createElement('div');
            this.notificationContainer.id = 'notification-container';
            this.notificationContainer.className = 'fixed top-4 right-4 z-50 space-y-2';
            document.body.appendChild(this.notificationContainer);
        }
    }
    
    /**
     * 创建加载遮罩
     */
    static createLoadingOverlay() {
        if (!this.loadingOverlay) {
            this.loadingOverlay = document.createElement('div');
            this.loadingOverlay.id = 'loading-overlay';
            this.loadingOverlay.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 hidden';
            this.loadingOverlay.innerHTML = `
                <div class="bg-white rounded-lg p-6 flex flex-col items-center">
                    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
                    <p class="text-gray-600">加载中...</p>
                </div>
            `;
            document.body.appendChild(this.loadingOverlay);
        }
    }
    
    /**
     * 绑定全局事件
     */
    static bindGlobalEvents() {
        // 点击外部关闭通知
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#notification-container')) {
                this.closeAllNotifications();
            }
        });
        
        // ESC键关闭通知
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllNotifications();
            }
        });
    }
    
    /**
     * 显示通知
     * @param {string} message 通知消息
     * @param {string} type 通知类型 (success, error, warning, info)
     * @param {number} duration 显示时长（毫秒）
     */
    static showNotification(message, type = 'info', duration = 5000) {
        this.createNotificationContainer();
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${type} transform transition-all duration-300 translate-x-full`;
        
        const iconMap = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        
        const colorMap = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500',
            info: 'bg-blue-500'
        };
        
        notification.innerHTML = `
            <div class="flex items-center p-4 bg-white rounded-lg shadow-lg border-l-4 ${colorMap[type]} min-w-80">
                <i class="fa ${iconMap[type]} text-white text-lg mr-3"></i>
                <div class="flex-1">
                    <p class="text-gray-800">${message}</p>
                </div>
                <button class="text-gray-400 hover:text-gray-600 ml-3" onclick="this.parentElement.parentElement.remove()">
                    <i class="fa fa-times"></i>
                </button>
            </div>
        `;
        
        this.notificationContainer.appendChild(notification);
        
        // 显示动画
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);
        
        // 自动关闭
        if (duration > 0) {
            setTimeout(() => {
                this.closeNotification(notification);
            }, duration);
        }
        
        return notification;
    }
    
    /**
     * 关闭指定通知
     * @param {HTMLElement} notification 通知元素
     */
    static closeNotification(notification) {
        notification.classList.add('translate-x-full');
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 300);
    }
    
    /**
     * 关闭所有通知
     */
    static closeAllNotifications() {
        if (this.notificationContainer) {
            this.notificationContainer.innerHTML = '';
        }
    }
    
    /**
     * 显示加载状态
     * @param {string} message 加载消息
     */
    static showLoading(message = '加载中...') {
        this.createLoadingOverlay();
        
        if (this.loadingOverlay) {
            const messageElement = this.loadingOverlay.querySelector('p');
            if (messageElement) {
                messageElement.textContent = message;
            }
            this.loadingOverlay.classList.remove('hidden');
        }
    }
    
    /**
     * 隐藏加载状态
     */
    static hideLoading() {
        if (this.loadingOverlay) {
            this.loadingOverlay.classList.add('hidden');
        }
    }
    
    /**
     * 显示确认对话框
     * @param {string} message 确认消息
     * @param {string} title 对话框标题
     * @returns {Promise<boolean>} 用户选择结果
     */
    static async showConfirm(message, title = '确认') {
        return new Promise((resolve) => {
            const modal = document.createElement('div');
            modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
            modal.innerHTML = `
                <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                    <h3 class="text-lg font-semibold mb-4">${title}</h3>
                    <p class="text-gray-600 mb-6">${message}</p>
                    <div class="flex justify-end space-x-3">
                        <button class="px-4 py-2 text-gray-500 hover:text-gray-700" id="cancel-btn">取消</button>
                        <button class="px-4 py-2 bg-primary text-white rounded hover:bg-primary/90" id="confirm-btn">确认</button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            // 绑定事件
            modal.querySelector('#confirm-btn').onclick = () => {
                modal.remove();
                resolve(true);
            };
            
            modal.querySelector('#cancel-btn').onclick = () => {
                modal.remove();
                resolve(false);
            };
            
            // 点击外部关闭
            modal.onclick = (e) => {
                if (e.target === modal) {
                    modal.remove();
                    resolve(false);
                }
            };
        });
    }
    
    /**
     * 显示输入对话框
     * @param {string} message 提示消息
     * @param {string} defaultValue 默认值
     * @param {string} placeholder 占位符
     * @returns {Promise<string|null>} 用户输入结果
     */
    static async showInput(message, defaultValue = '', placeholder = '') {
        return new Promise((resolve) => {
            const modal = document.createElement('div');
            modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
            modal.innerHTML = `
                <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                    <h3 class="text-lg font-semibold mb-4">输入</h3>
                    <p class="text-gray-600 mb-4">${message}</p>
                    <input type="text" class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/50" 
                           value="${defaultValue}" placeholder="${placeholder}" id="input-field">
                    <div class="flex justify-end space-x-3 mt-6">
                        <button class="px-4 py-2 text-gray-500 hover:text-gray-700" id="cancel-btn">取消</button>
                        <button class="px-4 py-2 bg-primary text-white rounded hover:bg-primary/90" id="confirm-btn">确认</button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            const inputField = modal.querySelector('#input-field');
            inputField.focus();
            inputField.select();
            
            // 绑定事件
            modal.querySelector('#confirm-btn').onclick = () => {
                const value = inputField.value.trim();
                modal.remove();
                resolve(value || null);
            };
            
            modal.querySelector('#cancel-btn').onclick = () => {
                modal.remove();
                resolve(null);
            };
            
            // 回车确认
            inputField.onkeypress = (e) => {
                if (e.key === 'Enter') {
                    modal.querySelector('#confirm-btn').click();
                }
            };
            
            // 点击外部关闭
            modal.onclick = (e) => {
                if (e.target === modal) {
                    modal.remove();
                    resolve(null);
                }
            };
        });
    }
    
    /**
     * 显示成功通知
     * @param {string} message 消息
     */
    static showSuccess(message) {
        return this.showNotification(message, 'success');
    }
    
    /**
     * 显示错误通知
     * @param {string} message 消息
     */
    static showError(message) {
        return this.showNotification(message, 'error');
    }
    
    /**
     * 显示警告通知
     * @param {string} message 消息
     */
    static showWarning(message) {
        return this.showNotification(message, 'warning');
    }
    
    /**
     * 显示信息通知
     * @param {string} message 消息
     */
    static showInfo(message) {
        return this.showNotification(message, 'info');
    }
    
    /**
     * 更新页面加载进度
     * @param {number} progress 进度百分比 (0-100)
     */
    static updateProgress(progress) {
        let progressBar = document.getElementById('progress-bar');
        if (!progressBar) {
            progressBar = document.createElement('div');
            progressBar.id = 'progress-bar';
            progressBar.className = 'fixed top-0 left-0 h-1 bg-primary z-50 transition-all duration-300';
            document.body.appendChild(progressBar);
        }
        
        progressBar.style.width = `${Math.min(100, Math.max(0, progress))}%`;
        
        if (progress >= 100) {
            setTimeout(() => {
                progressBar.style.opacity = '0';
                setTimeout(() => progressBar.remove(), 300);
            }, 500);
        }
    }
}

// 导出到全局
window.UIManager = UIManager;
