/**
 * 护工端通用功能模块
 * 提供护工端页面通用的功能函数
 */

// 用户端通用功能
window.CaregiverCommon = {
    /**
     * 加载用户信息
     * 在所有护工端页面中统一调用
     */
    loadUserInfo: function() {
        try {
            const caregiverInfo = JSON.parse(localStorage.getItem('caregiver_info') || '{}');
            console.log('CaregiverCommon.loadUserInfo 开始执行:', caregiverInfo);
            
            if (!caregiverInfo || !caregiverInfo.id) {
                console.warn('护工信息不存在或无效');
                return null;
            }
            
            // 更新各种可能的用户名显示元素
            const nameSelectors = [
                'caregiver-name',
                'caregiver-name-display',
                'dashboard-name', 
                'user-name',
                'profile-name',
                'header-name'
            ];
            
            nameSelectors.forEach(selector => {
                const element = document.getElementById(selector);
                if (element) {
                    element.textContent = caregiverInfo.name || '护工';
                    console.log(`更新元素 ${selector}:`, caregiverInfo.name);
                }
            });
            
            // 更新所有包含"用户"文本的元素（可能是用户名显示）
            const userTextElements = document.querySelectorAll('*');
            userTextElements.forEach(element => {
                if (element.textContent && element.textContent.trim() === '用户' && 
                    !element.querySelector('*')) { // 确保是叶子节点
                    element.textContent = caregiverInfo.name || '护工';
                }
            });
            
            // 更新头像（如果有的话）
            const avatarSelectors = [
                'img[alt="用户头像"]',
                'img[alt="护工头像"]',
                'img[alt="头像"]',
                '.avatar img',
                '#avatar img'
            ];
            
            avatarSelectors.forEach(selector => {
                const avatarElement = document.querySelector(selector);
                if (avatarElement && caregiverInfo.avatar) {
                    avatarElement.src = caregiverInfo.avatar;
                }
            });
            
            // 更新表单中的护工信息
            this.updateFormFields(caregiverInfo);
            
            console.log('护工用户信息加载成功:', caregiverInfo);
            return caregiverInfo;
        } catch (error) {
            console.error('加载护工用户信息失败:', error);
            return null;
        }
    },

    /**
     * 更新表单字段中的护工信息
     */
    updateFormFields: function(caregiverInfo) {
        // 更新姓名输入框
        const nameInputs = document.querySelectorAll('input[name="name"], input[name="caregiver_name"]');
        nameInputs.forEach(input => {
            if (!input.value || input.value === '用户' || input.value === '护工') {
                input.value = caregiverInfo.name || '';
            }
        });
        
        // 更新手机号输入框
        const phoneInputs = document.querySelectorAll('input[name="phone"], input[name="caregiver_phone"]');
        phoneInputs.forEach(input => {
            if (!input.value) {
                input.value = caregiverInfo.phone || '';
            }
        });
        
        // 更新邮箱输入框
        const emailInputs = document.querySelectorAll('input[name="email"], input[name="caregiver_email"]');
        emailInputs.forEach(input => {
            if (!input.value) {
                input.value = caregiverInfo.email || '';
            }
        });
        
        // 更新年龄输入框
        const ageInputs = document.querySelectorAll('input[name="age"], input[name="caregiver_age"]');
        ageInputs.forEach(input => {
            if (!input.value) {
                input.value = caregiverInfo.age || '';
            }
        });
        
        // 更新性别选择
        const genderSelects = document.querySelectorAll('select[name="gender"], select[name="caregiver_gender"]');
        genderSelects.forEach(select => {
            if (!select.value) {
                select.value = caregiverInfo.gender || '';
            }
        });
        
        // 更新介绍文本域
        const introTextareas = document.querySelectorAll('textarea[name="introduction"], textarea[name="caregiver_introduction"]');
        introTextareas.forEach(textarea => {
            if (!textarea.value) {
                textarea.value = caregiverInfo.introduction || '';
            }
        });
    },

    /**
     * 检查认证状态
     * 在所有护工端页面中统一调用
     */
    checkAuth: function() {
        const caregiverInfo = localStorage.getItem('caregiver_info');
        if (!caregiverInfo) {
            window.location.href = '/';
            return false;
        }
        return true;
    },

    /**
     * 显示通知
     * 统一的通知显示函数
     */
    showNotification: function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 ${
            type === 'success' ? 'bg-success text-white' :
            type === 'error' ? 'bg-danger text-white' :
            type === 'warning' ? 'bg-warning text-white' :
            'bg-primary text-white'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    },

    /**
     * 设置退出登录事件
     * 在所有护工端页面中统一调用
     */
    setupLogout: function() {
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', function() {
                localStorage.removeItem('caregiver_info');
                localStorage.removeItem('caregiver_token');
                window.location.href = '/';
            });
        }
    },

    /**
     * 初始化护工端页面
     * 在页面DOMContentLoaded事件中调用
     */
    initPage: function() {
        // 检查认证状态
        if (!this.checkAuth()) {
            return;
        }
        
        // 加载用户信息
        this.loadUserInfo();
        
        // 设置退出登录
        this.setupLogout();
        
        console.log('护工端页面初始化完成');
    }
};

// 页面加载完成后自动初始化
document.addEventListener('DOMContentLoaded', function() {
    window.CaregiverCommon.initPage();
});
