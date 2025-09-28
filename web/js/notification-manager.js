/**
 * 通知管理器
 * 处理浏览器通知和页面内通知
 */

class NotificationManager {
    constructor() {
        this.permission = 'default';
        this.notifications = [];
        this.soundEnabled = true;
        this.vibrationEnabled = true;
        
        this.init();
    }
    
    /**
     * 初始化通知管理器
     */
    init() {
        this.checkNotificationPermission();
        this.createNotificationContainer();
        this.bindEvents();
    }
    
    /**
     * 检查通知权限
     */
    async checkNotificationPermission() {
        if ('Notification' in window) {
            this.permission = Notification.permission;
            
            if (this.permission === 'default') {
                try {
                    this.permission = await Notification.requestPermission();
                } catch (error) {
                    console.warn('请求通知权限失败:', error);
                }
            }
        } else {
            console.warn('浏览器不支持通知功能');
        }
    }
    
    /**
     * 创建通知容器
     */
    createNotificationContainer() {
        if (document.getElementById('notification-container')) {
            return;
        }
        
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'fixed top-4 right-4 z-50 space-y-2';
        container.style.cssText = `
            position: fixed;
            top: 16px;
            right: 16px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 8px;
            pointer-events: none;
        `;
        
        document.body.appendChild(container);
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        // 监听页面可见性变化
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.onPageHidden();
            } else {
                this.onPageVisible();
            }
        });
        
        // 监听窗口焦点变化
        window.addEventListener('focus', () => this.onWindowFocus());
        window.addEventListener('blur', () => this.onWindowBlur());
    }
    
    /**
     * 显示通知
     */
    showNotification(options) {
        const {
            title = '新消息',
            message = '',
            type = 'info',
            duration = 5000,
            actions = [],
            sound = true,
            vibration = true,
            icon = '/uploads/avatars/default-user.png',
            tag = null
        } = options;
        
        // 创建页面内通知
        this.showInPageNotification({
            title,
            message,
            type,
            duration,
            actions,
            icon
        });
        
        // 创建浏览器通知
        if (this.permission === 'granted') {
            this.showBrowserNotification({
                title,
                message,
                icon,
                tag
            });
        }
        
        // 播放声音
        if (sound && this.soundEnabled) {
            this.playNotificationSound();
        }
        
        // 震动
        if (vibration && this.vibrationEnabled && 'vibrate' in navigator) {
            navigator.vibrate([200, 100, 200]);
        }
    }
    
    /**
     * 显示页面内通知
     */
    showInPageNotification(options) {
        const container = document.getElementById('notification-container');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${options.type}`;
        notification.style.cssText = `
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            padding: 16px;
            max-width: 320px;
            pointer-events: auto;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            border-left: 4px solid ${this.getTypeColor(options.type)};
        `;
        
        notification.innerHTML = `
            <div style="display: flex; align-items: flex-start; gap: 12px;">
                <img src="${options.icon}" alt="头像" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;">
                <div style="flex: 1; min-width: 0;">
                    <h4 style="margin: 0 0 4px 0; font-size: 14px; font-weight: 600; color: #1f2937;">${this.escapeHtml(options.title)}</h4>
                    <p style="margin: 0; font-size: 13px; color: #6b7280; line-height: 1.4;">${this.escapeHtml(options.message)}</p>
                    ${options.actions.length > 0 ? `
                        <div style="margin-top: 8px; display: flex; gap: 8px;">
                            ${options.actions.map(action => `
                                <button onclick="${action.onclick}" style="
                                    background: ${this.getTypeColor(options.type)};
                                    color: white;
                                    border: none;
                                    border-radius: 4px;
                                    padding: 4px 8px;
                                    font-size: 12px;
                                    cursor: pointer;
                                ">${action.text}</button>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
                <button onclick="this.parentElement.parentElement.remove()" style="
                    background: none;
                    border: none;
                    color: #9ca3af;
                    cursor: pointer;
                    padding: 4px;
                    font-size: 16px;
                ">×</button>
            </div>
        `;
        
        container.appendChild(notification);
        
        // 动画显示
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);
        
        // 自动移除
        if (options.duration > 0) {
            setTimeout(() => {
                this.removeNotification(notification);
            }, options.duration);
        }
        
        return notification;
    }
    
    /**
     * 显示浏览器通知
     */
    showBrowserNotification(options) {
        if (this.permission !== 'granted') return;
        
        const notification = new Notification(options.title, {
            body: options.message,
            icon: options.icon,
            tag: options.tag,
            requireInteraction: false,
            silent: false
        });
        
        // 点击通知时聚焦窗口
        notification.onclick = () => {
            window.focus();
            notification.close();
        };
        
        // 自动关闭
        setTimeout(() => {
            notification.close();
        }, 5000);
        
        return notification;
    }
    
    /**
     * 移除通知
     */
    removeNotification(notification) {
        if (notification && notification.parentNode) {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }
    }
    
    /**
     * 播放通知声音
     */
    playNotificationSound() {
        try {
            // 创建简单的提示音
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            // 创建悦耳的提示音
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime + 0.2);
            
            gainNode.gain.setValueAtTime(0, audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(0.1, audioContext.currentTime + 0.01);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.3);
        } catch (error) {
            console.warn('播放通知声音失败:', error);
        }
    }
    
    /**
     * 显示消息通知
     */
    showMessageNotification(message) {
        this.showNotification({
            title: `${message.sender_name} 发来消息`,
            message: message.content,
            type: 'message',
            icon: message.sender_avatar || '/uploads/avatars/default-user.png',
            tag: `message_${message.sender_id}`,
            actions: [
                {
                    text: '查看',
                    onclick: `window.chatWindow && window.chatWindow.open({
                        id: '${message.sender_id}',
                        contactId: '${message.sender_type}_${message.sender_id}',
                        name: '${message.sender_name}',
                        avatar: '${message.sender_avatar || '/uploads/avatars/default-user.png'}',
                        type: '${message.sender_type}',
                        online: true
                    })`
                }
            ]
        });
    }
    
    /**
     * 显示系统通知
     */
    showSystemNotification(title, message, type = 'info') {
        this.showNotification({
            title,
            message,
            type,
            icon: '/uploads/avatars/system.png',
            duration: 8000
        });
    }
    
    /**
     * 页面隐藏时的处理
     */
    onPageHidden() {
        // 页面隐藏时，增加通知的持续时间
        console.log('页面隐藏，通知将保持更长时间');
    }
    
    /**
     * 页面可见时的处理
     */
    onPageVisible() {
        // 页面可见时，清除所有通知
        this.clearAllNotifications();
    }
    
    /**
     * 窗口获得焦点时的处理
     */
    onWindowFocus() {
        // 窗口获得焦点时，清除所有通知
        this.clearAllNotifications();
    }
    
    /**
     * 窗口失去焦点时的处理
     */
    onWindowBlur() {
        // 窗口失去焦点时，可以增加通知的优先级
        console.log('窗口失去焦点');
    }
    
    /**
     * 清除所有通知
     */
    clearAllNotifications() {
        const container = document.getElementById('notification-container');
        if (container) {
            container.innerHTML = '';
        }
    }
    
    /**
     * 获取类型颜色
     */
    getTypeColor(type) {
        const colors = {
            info: '#3b82f6',
            success: '#10b981',
            warning: '#f59e0b',
            error: '#ef4444',
            message: '#8b5cf6'
        };
        return colors[type] || colors.info;
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
     * 设置声音开关
     */
    setSoundEnabled(enabled) {
        this.soundEnabled = enabled;
        localStorage.setItem('notification_sound_enabled', enabled);
    }
    
    /**
     * 设置震动开关
     */
    setVibrationEnabled(enabled) {
        this.vibrationEnabled = enabled;
        localStorage.setItem('notification_vibration_enabled', enabled);
    }
    
    /**
     * 加载设置
     */
    loadSettings() {
        this.soundEnabled = localStorage.getItem('notification_sound_enabled') !== 'false';
        this.vibrationEnabled = localStorage.getItem('notification_vibration_enabled') !== 'false';
    }
    
    /**
     * 检查是否支持通知
     */
    isSupported() {
        return 'Notification' in window;
    }
    
    /**
     * 获取权限状态
     */
    getPermission() {
        return this.permission;
    }
}

// 全局通知管理器实例
window.NotificationManager = NotificationManager;



