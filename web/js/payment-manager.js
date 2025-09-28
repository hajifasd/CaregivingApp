/**
 * 支付管理系统
 * ====================================
 * 
 * 处理用户支付相关功能
 */

class PaymentManager {
    constructor() {
        this.paymentMethods = [];
        this.currentPayment = null;
        this.paymentStatus = 'idle';
    }
    
    /**
     * 初始化支付系统
     */
    init() {
        this.loadPaymentMethods();
        this.setupEventListeners();
    }
    
    /**
     * 加载支付方式
     */
    loadPaymentMethods() {
        this.paymentMethods = [
            {
                id: 'wechat',
                name: '微信支付',
                icon: 'fa-wechat',
                enabled: true
            },
            {
                id: 'alipay',
                name: '支付宝',
                icon: 'fa-alipay',
                enabled: true
            },
            {
                id: 'bank',
                name: '银行卡',
                icon: 'fa-credit-card',
                enabled: true
            }
        ];
    }
    
    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 支付按钮事件
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-payment-action]')) {
                const action = e.target.getAttribute('data-payment-action');
                this.handlePaymentAction(action, e.target);
            }
        });
    }
    
    /**
     * 处理支付操作
     */
    handlePaymentAction(action, element) {
        switch (action) {
            case 'create-payment':
                this.createPayment(element);
                break;
            case 'process-payment':
                this.processPayment(element);
                break;
            case 'cancel-payment':
                this.cancelPayment(element);
                break;
            case 'refund-payment':
                this.refundPayment(element);
                break;
        }
    }
    
    /**
     * 创建支付订单
     */
    async createPayment(element) {
        try {
            const orderData = this.extractOrderData(element);
            
            const response = await fetch('/api/payment/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getUserToken()}`
                },
                body: JSON.stringify(orderData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.currentPayment = result.data;
                this.showPaymentModal(result.data);
            } else {
                this.showError(result.message || '创建支付订单失败');
            }
        } catch (error) {
            console.error('创建支付订单失败:', error);
            this.showError('网络错误，请稍后重试');
        }
    }
    
    /**
     * 处理支付
     */
    async processPayment(element) {
        const paymentMethod = element.getAttribute('data-payment-method');
        const paymentId = element.getAttribute('data-payment-id');
        
        try {
            this.paymentStatus = 'processing';
            this.updatePaymentUI(element, 'processing');
            
            const response = await fetch('/api/payment/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getUserToken()}`
                },
                body: JSON.stringify({
                    payment_id: paymentId,
                    payment_method: paymentMethod
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.paymentStatus = 'success';
                this.updatePaymentUI(element, 'success');
                this.showSuccess('支付成功！');
                this.handlePaymentSuccess(result.data);
            } else {
                this.paymentStatus = 'failed';
                this.updatePaymentUI(element, 'failed');
                this.showError(result.message || '支付失败');
            }
        } catch (error) {
            console.error('支付处理失败:', error);
            this.paymentStatus = 'failed';
            this.updatePaymentUI(element, 'failed');
            this.showError('支付失败，请稍后重试');
        }
    }
    
    /**
     * 取消支付
     */
    async cancelPayment(element) {
        const paymentId = element.getAttribute('data-payment-id');
        
        try {
            const response = await fetch('/api/payment/cancel', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getUserToken()}`
                },
                body: JSON.stringify({ payment_id: paymentId })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('支付已取消');
                this.handlePaymentCancel(result.data);
            } else {
                this.showError(result.message || '取消支付失败');
            }
        } catch (error) {
            console.error('取消支付失败:', error);
            this.showError('取消支付失败，请稍后重试');
        }
    }
    
    /**
     * 退款
     */
    async refundPayment(element) {
        const paymentId = element.getAttribute('data-payment-id');
        
        if (!confirm('确定要申请退款吗？')) {
            return;
        }
        
        try {
            const response = await fetch('/api/payment/refund', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getUserToken()}`
                },
                body: JSON.stringify({ payment_id: paymentId })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('退款申请已提交，请等待处理');
                this.handlePaymentRefund(result.data);
            } else {
                this.showError(result.message || '申请退款失败');
            }
        } catch (error) {
            console.error('申请退款失败:', error);
            this.showError('申请退款失败，请稍后重试');
        }
    }
    
    /**
     * 显示支付模态框
     */
    showPaymentModal(paymentData) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-semibold">选择支付方式</h3>
                    <button onclick="this.closest('.fixed').remove()" class="text-gray-400 hover:text-gray-600">
                        <i class="fa fa-times"></i>
                    </button>
                </div>
                
                <div class="mb-4">
                    <p class="text-sm text-gray-600">订单金额</p>
                    <p class="text-2xl font-bold text-primary">¥${paymentData.amount}</p>
                </div>
                
                <div class="space-y-3 mb-6">
                    ${this.paymentMethods.map(method => `
                        <button class="w-full flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:border-primary hover:bg-primary/5 transition-colors"
                                data-payment-method="${method.id}" 
                                data-payment-id="${paymentData.id}"
                                data-payment-action="process-payment">
                            <div class="flex items-center gap-3">
                                <i class="fa ${method.icon} text-xl"></i>
                                <span>${method.name}</span>
                            </div>
                            <i class="fa fa-arrow-right text-gray-400"></i>
                        </button>
                    `).join('')}
                </div>
                
                <div class="flex gap-3">
                    <button onclick="this.closest('.fixed').remove()" 
                            class="flex-1 border border-gray-300 text-gray-700 hover:bg-gray-50 px-4 py-2 rounded-lg transition-colors">
                        取消
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    /**
     * 更新支付UI状态
     */
    updatePaymentUI(element, status) {
        const button = element;
        const originalText = button.textContent;
        
        switch (status) {
            case 'processing':
                button.disabled = true;
                button.innerHTML = '<i class="fa fa-spinner fa-spin mr-2"></i>处理中...';
                button.classList.add('opacity-50');
                break;
            case 'success':
                button.innerHTML = '<i class="fa fa-check mr-2"></i>支付成功';
                button.classList.remove('bg-primary', 'hover:bg-primary/90');
                button.classList.add('bg-success');
                break;
            case 'failed':
                button.innerHTML = '<i class="fa fa-times mr-2"></i>支付失败';
                button.classList.remove('bg-primary', 'hover:bg-primary/90');
                button.classList.add('bg-danger');
                break;
        }
    }
    
    /**
     * 提取订单数据
     */
    extractOrderData(element) {
        const form = element.closest('form');
        if (!form) return {};
        
        const formData = new FormData(form);
        return {
            amount: formData.get('amount') || element.getAttribute('data-amount'),
            description: formData.get('description') || element.getAttribute('data-description'),
            appointment_id: formData.get('appointment_id') || element.getAttribute('data-appointment-id'),
            employment_id: formData.get('employment_id') || element.getAttribute('data-employment-id')
        };
    }
    
    /**
     * 获取用户令牌
     */
    getUserToken() {
        return localStorage.getItem('user_token') || 
               document.cookie.split('; ').find(row => row.startsWith('user_token='))?.split('=')[1];
    }
    
    /**
     * 支付成功处理
     */
    handlePaymentSuccess(paymentData) {
        // 更新页面状态
        this.updatePaymentStatus(paymentData);
        
        // 发送成功通知
        this.sendPaymentNotification('success', paymentData);
        
        // 刷新相关数据
        setTimeout(() => {
            if (window.loadAppointmentsData) {
                window.loadAppointmentsData();
            }
            if (window.loadEmploymentsData) {
                window.loadEmploymentsData();
            }
        }, 1000);
    }
    
    /**
     * 支付取消处理
     */
    handlePaymentCancel(paymentData) {
        this.updatePaymentStatus(paymentData);
        this.sendPaymentNotification('cancelled', paymentData);
    }
    
    /**
     * 支付退款处理
     */
    handlePaymentRefund(paymentData) {
        this.updatePaymentStatus(paymentData);
        this.sendPaymentNotification('refunded', paymentData);
    }
    
    /**
     * 更新支付状态
     */
    updatePaymentStatus(paymentData) {
        // 更新页面中的支付状态显示
        const statusElements = document.querySelectorAll(`[data-payment-id="${paymentData.id}"]`);
        statusElements.forEach(element => {
            const statusSpan = element.querySelector('.payment-status');
            if (statusSpan) {
                statusSpan.textContent = this.getStatusText(paymentData.status);
                statusSpan.className = `payment-status ${this.getStatusClass(paymentData.status)}`;
            }
        });
    }
    
    /**
     * 获取状态文本
     */
    getStatusText(status) {
        const statusMap = {
            'pending': '待支付',
            'processing': '处理中',
            'success': '支付成功',
            'failed': '支付失败',
            'cancelled': '已取消',
            'refunded': '已退款'
        };
        return statusMap[status] || status;
    }
    
    /**
     * 获取状态样式
     */
    getStatusClass(status) {
        const statusMap = {
            'pending': 'text-warning',
            'processing': 'text-blue-600',
            'success': 'text-success',
            'failed': 'text-danger',
            'cancelled': 'text-gray-500',
            'refunded': 'text-orange-500'
        };
        return statusMap[status] || 'text-gray-500';
    }
    
    /**
     * 发送支付通知
     */
    sendPaymentNotification(type, paymentData) {
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-white border border-gray-200 rounded-lg shadow-lg p-4 z-50 max-w-sm';
        
        const messages = {
            success: '支付成功！',
            cancelled: '支付已取消',
            refunded: '退款申请已提交'
        };
        
        notification.innerHTML = `
            <div class="flex items-center gap-3">
                <i class="fa fa-${type === 'success' ? 'check-circle text-success' : 'info-circle text-blue-500'}"></i>
                <span>${messages[type] || '支付状态更新'}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
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
}

// 创建全局实例
window.PaymentManager = new PaymentManager();

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    window.PaymentManager.init();
});
