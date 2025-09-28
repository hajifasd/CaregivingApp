/**
 * 紧急呼叫管理系统
 * ====================================
 * 
 * 处理紧急情况下的快速呼叫功能
 */

class EmergencyManager {
    constructor() {
        this.emergencyContacts = [];
        this.isEmergencyMode = false;
        this.emergencyTimer = null;
        this.emergencyCountdown = 0;
    }
    
    /**
     * 初始化紧急呼叫系统
     */
    init() {
        this.loadEmergencyContacts();
        this.setupEventListeners();
        this.setupKeyboardShortcuts();
    }
    
    /**
     * 加载紧急联系人
     */
    async loadEmergencyContacts() {
        try {
            // 首先尝试从API加载紧急联系人
            const response = await fetch('/api/emergency/contacts');
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.emergencyContacts = data.data || [];
                    return;
                }
            }
        } catch (error) {
            console.log('从API加载紧急联系人失败，使用本地存储');
        }
        
        // 从本地存储加载
        const savedContacts = localStorage.getItem('emergency_contacts');
        if (savedContacts) {
            this.emergencyContacts = JSON.parse(savedContacts);
        } else {
            // 默认紧急联系人（仅作为最后备选）
            this.emergencyContacts = [
                {
                    id: 1,
                    name: '紧急服务中心',
                    phone: '120',
                    type: 'medical',
                    priority: 1
                },
                {
                    id: 2,
                    name: '报警电话',
                    phone: '110',
                    type: 'police',
                    priority: 1
                },
                {
                    id: 3,
                    name: '火警电话',
                    phone: '119',
                    type: 'fire',
                    priority: 1
                }
            ];
        }
    }
    
    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 紧急呼叫按钮事件
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-emergency-action]')) {
                const action = e.target.getAttribute('data-emergency-action');
                this.handleEmergencyAction(action, e.target);
            }
        });
        
        // 页面可见性变化事件
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && this.isEmergencyMode) {
                this.handlePageHidden();
            }
        });
    }
    
    /**
     * 设置键盘快捷键
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl + E 触发紧急呼叫
            if (e.ctrlKey && e.key === 'e') {
                e.preventDefault();
                this.triggerEmergencyCall();
            }
            
            // ESC 取消紧急呼叫
            if (e.key === 'Escape' && this.isEmergencyMode) {
                this.cancelEmergencyCall();
            }
        });
    }
    
    /**
     * 处理紧急操作
     */
    handleEmergencyAction(action, element) {
        switch (action) {
            case 'trigger-emergency':
                this.triggerEmergencyCall();
                break;
            case 'call-emergency':
                this.callEmergencyContact(element);
                break;
            case 'cancel-emergency':
                this.cancelEmergencyCall();
                break;
            case 'add-emergency-contact':
                this.addEmergencyContact();
                break;
            case 'edit-emergency-contact':
                this.editEmergencyContact(element);
                break;
            case 'delete-emergency-contact':
                this.deleteEmergencyContact(element);
                break;
        }
    }
    
    /**
     * 触发紧急呼叫
     */
    triggerEmergencyCall() {
        if (this.isEmergencyMode) {
            return;
        }
        
        this.isEmergencyMode = true;
        this.showEmergencyModal();
        this.startEmergencyCountdown();
        this.sendEmergencyNotification();
    }
    
    /**
     * 显示紧急呼叫模态框
     */
    showEmergencyModal() {
        const modal = document.createElement('div');
        modal.id = 'emergency-modal';
        modal.className = 'fixed inset-0 bg-red-600 bg-opacity-90 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-8 max-w-md w-full mx-4 text-center">
                <div class="mb-6">
                    <i class="fa fa-exclamation-triangle text-red-500 text-6xl mb-4"></i>
                    <h2 class="text-2xl font-bold text-red-600 mb-2">紧急呼叫</h2>
                    <p class="text-gray-600">请选择紧急联系人</p>
                </div>
                
                <div class="space-y-3 mb-6" id="emergency-contacts-list">
                    ${this.emergencyContacts.map(contact => `
                        <button class="w-full flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-red-500 hover:bg-red-50 transition-colors"
                                data-emergency-contact-id="${contact.id}"
                                data-emergency-action="call-emergency">
                            <div class="flex items-center gap-3">
                                <i class="fa fa-${this.getContactIcon(contact.type)} text-xl"></i>
                                <div class="text-left">
                                    <div class="font-semibold">${contact.name}</div>
                                    <div class="text-sm text-gray-600">${contact.phone}</div>
                                </div>
                            </div>
                            <i class="fa fa-phone text-red-500"></i>
                        </button>
                    `).join('')}
                </div>
                
                <div class="flex gap-3">
                    <button onclick="window.EmergencyManager.cancelEmergencyCall()" 
                            class="flex-1 border border-gray-300 text-gray-700 hover:bg-gray-50 px-4 py-2 rounded-lg transition-colors">
                        取消
                    </button>
                    <button onclick="window.EmergencyManager.addEmergencyContact()" 
                            class="flex-1 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors">
                        添加联系人
                    </button>
                </div>
                
                <div class="mt-4 text-sm text-gray-500">
                    <p>快捷键：Ctrl+E 触发紧急呼叫，ESC 取消</p>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 添加紧急样式
        document.body.classList.add('emergency-mode');
    }
    
    /**
     * 开始紧急倒计时
     */
    startEmergencyCountdown() {
        this.emergencyCountdown = 30; // 30秒倒计时
        
        const countdownElement = document.createElement('div');
        countdownElement.id = 'emergency-countdown';
        countdownElement.className = 'fixed top-4 left-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
        countdownElement.innerHTML = `
            <i class="fa fa-clock mr-2"></i>
            <span>紧急模式：${this.emergencyCountdown}秒</span>
        `;
        
        document.body.appendChild(countdownElement);
        
        this.emergencyTimer = setInterval(() => {
            this.emergencyCountdown--;
            countdownElement.innerHTML = `
                <i class="fa fa-clock mr-2"></i>
                <span>紧急模式：${this.emergencyCountdown}秒</span>
            `;
            
            if (this.emergencyCountdown <= 0) {
                this.autoCallEmergency();
            }
        }, 1000);
    }
    
    /**
     * 自动拨打紧急电话
     */
    autoCallEmergency() {
        const primaryContact = this.emergencyContacts.find(c => c.priority === 1);
        if (primaryContact) {
            this.callEmergencyContact({ getAttribute: () => primaryContact.id });
        }
    }
    
    /**
     * 拨打紧急联系人
     */
    callEmergencyContact(element) {
        const contactId = element.getAttribute('data-emergency-contact-id');
        const contact = this.emergencyContacts.find(c => c.id == contactId);
        
        if (!contact) {
            this.showError('联系人不存在');
            return;
        }
        
        // 记录紧急呼叫
        this.logEmergencyCall(contact);
        
        // 尝试拨打电话
        this.initiateCall(contact.phone);
        
        // 关闭紧急模态框
        this.cancelEmergencyCall();
        
        this.showSuccess(`正在拨打 ${contact.name} (${contact.phone})`);
    }
    
    /**
     * 发起电话呼叫
     */
    initiateCall(phoneNumber) {
        // 尝试使用 tel: 协议拨打电话
        const phoneLink = document.createElement('a');
        phoneLink.href = `tel:${phoneNumber}`;
        phoneLink.click();
        
        // 如果支持，也可以尝试使用 WebRTC 或其他方式
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            // 这里可以添加更高级的呼叫功能
            console.log('支持高级呼叫功能');
        }
    }
    
    /**
     * 取消紧急呼叫
     */
    cancelEmergencyCall() {
        this.isEmergencyMode = false;
        
        // 清除倒计时
        if (this.emergencyTimer) {
            clearInterval(this.emergencyTimer);
            this.emergencyTimer = null;
        }
        
        // 移除紧急模态框
        const modal = document.getElementById('emergency-modal');
        if (modal) {
            modal.remove();
        }
        
        // 移除倒计时显示
        const countdown = document.getElementById('emergency-countdown');
        if (countdown) {
            countdown.remove();
        }
        
        // 移除紧急样式
        document.body.classList.remove('emergency-mode');
        
        this.showSuccess('紧急呼叫已取消');
    }
    
    /**
     * 添加紧急联系人
     */
    addEmergencyContact() {
        const name = prompt('请输入联系人姓名：');
        if (!name) return;
        
        const phone = prompt('请输入电话号码：');
        if (!phone) return;
        
        const type = prompt('请输入联系人类型 (medical/police/fire/other)：', 'other');
        
        const newContact = {
            id: Date.now(),
            name: name,
            phone: phone,
            type: type,
            priority: 2
        };
        
        this.emergencyContacts.push(newContact);
        this.saveEmergencyContacts();
        this.refreshEmergencyModal();
        
        this.showSuccess('紧急联系人已添加');
    }
    
    /**
     * 编辑紧急联系人
     */
    editEmergencyContact(element) {
        const contactId = element.getAttribute('data-emergency-contact-id');
        const contact = this.emergencyContacts.find(c => c.id == contactId);
        
        if (!contact) return;
        
        const newName = prompt('请输入新的联系人姓名：', contact.name);
        if (newName) contact.name = newName;
        
        const newPhone = prompt('请输入新的电话号码：', contact.phone);
        if (newPhone) contact.phone = newPhone;
        
        this.saveEmergencyContacts();
        this.refreshEmergencyModal();
        
        this.showSuccess('紧急联系人已更新');
    }
    
    /**
     * 删除紧急联系人
     */
    deleteEmergencyContact(element) {
        const contactId = element.getAttribute('data-emergency-contact-id');
        
        if (confirm('确定要删除这个紧急联系人吗？')) {
            this.emergencyContacts = this.emergencyContacts.filter(c => c.id != contactId);
            this.saveEmergencyContacts();
            this.refreshEmergencyModal();
            
            this.showSuccess('紧急联系人已删除');
        }
    }
    
    /**
     * 刷新紧急模态框
     */
    refreshEmergencyModal() {
        const modal = document.getElementById('emergency-modal');
        if (modal) {
            const contactsList = modal.querySelector('#emergency-contacts-list');
            if (contactsList) {
                contactsList.innerHTML = this.emergencyContacts.map(contact => `
                    <button class="w-full flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-red-500 hover:bg-red-50 transition-colors"
                            data-emergency-contact-id="${contact.id}"
                            data-emergency-action="call-emergency">
                        <div class="flex items-center gap-3">
                            <i class="fa fa-${this.getContactIcon(contact.type)} text-xl"></i>
                            <div class="text-left">
                                <div class="font-semibold">${contact.name}</div>
                                <div class="text-sm text-gray-600">${contact.phone}</div>
                            </div>
                        </div>
                        <i class="fa fa-phone text-red-500"></i>
                    </button>
                `).join('');
            }
        }
    }
    
    /**
     * 获取联系人图标
     */
    getContactIcon(type) {
        const iconMap = {
            'medical': 'ambulance',
            'police': 'shield',
            'fire': 'fire',
            'other': 'phone'
        };
        return iconMap[type] || 'phone';
    }
    
    /**
     * 保存紧急联系人
     */
    saveEmergencyContacts() {
        localStorage.setItem('emergency_contacts', JSON.stringify(this.emergencyContacts));
    }
    
    /**
     * 记录紧急呼叫
     */
    logEmergencyCall(contact) {
        const log = {
            timestamp: new Date().toISOString(),
            contact: contact,
            location: window.LocationManager ? window.LocationManager.currentLocation : null
        };
        
        // 保存到本地存储
        const logs = JSON.parse(localStorage.getItem('emergency_logs') || '[]');
        logs.push(log);
        localStorage.setItem('emergency_logs', JSON.stringify(logs));
        
        // 发送到服务器
        this.sendEmergencyLog(log);
    }
    
    /**
     * 发送紧急日志到服务器
     */
    async sendEmergencyLog(log) {
        try {
            await fetch('/api/emergency/log', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getUserToken()}`
                },
                body: JSON.stringify(log)
            });
        } catch (error) {
            console.error('发送紧急日志失败:', error);
        }
    }
    
    /**
     * 发送紧急通知
     */
    sendEmergencyNotification() {
        // 发送浏览器通知
        if (Notification.permission === 'granted') {
            new Notification('紧急呼叫已激活', {
                body: '请选择紧急联系人',
                icon: '/favicon.ico'
            });
        }
        
        // 发送到服务器
        this.notifyServer();
    }
    
    /**
     * 通知服务器紧急状态
     */
    async notifyServer() {
        try {
            await fetch('/api/emergency/notify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getUserToken()}`
                },
                body: JSON.stringify({
                    status: 'emergency_activated',
                    location: window.LocationManager ? window.LocationManager.currentLocation : null
                })
            });
        } catch (error) {
            console.error('发送紧急通知失败:', error);
        }
    }
    
    /**
     * 处理页面隐藏
     */
    handlePageHidden() {
        if (this.isEmergencyMode) {
            // 页面隐藏时继续紧急模式
            console.log('页面隐藏，紧急模式继续');
        }
    }
    
    /**
     * 显示错误信息
     */
    showError(message) {
        this.showMessage(message, 'error');
    }
    
    /**
     * 显示成功信息
     */
    showSuccess(message) {
        this.showMessage(message, 'success');
    }
    
    /**
     * 显示消息
     */
    showMessage(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 max-w-sm ${
            type === 'error' ? 'bg-red-500 text-white' :
            type === 'success' ? 'bg-green-500 text-white' :
            'bg-blue-500 text-white'
        }`;
        
        notification.innerHTML = `
            <div class="flex items-center gap-2">
                <i class="fa fa-${type === 'error' ? 'times-circle' : type === 'success' ? 'check-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    /**
     * 获取用户令牌
     */
    getUserToken() {
        return localStorage.getItem('user_token') || 
               document.cookie.split('; ').find(row => row.startsWith('user_token='))?.split('=')[1];
    }
}

// 创建全局实例
window.EmergencyManager = new EmergencyManager();

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    window.EmergencyManager.init();
});

// 添加紧急模式样式
const emergencyStyles = document.createElement('style');
emergencyStyles.textContent = `
    .emergency-mode {
        animation: emergencyPulse 1s infinite;
    }
    
    @keyframes emergencyPulse {
        0% { background-color: rgba(239, 68, 68, 0.1); }
        50% { background-color: rgba(239, 68, 68, 0.2); }
        100% { background-color: rgba(239, 68, 68, 0.1); }
    }
`;
document.head.appendChild(emergencyStyles);
