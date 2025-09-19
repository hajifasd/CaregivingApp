/**
 * 用户信息管理模块
 * 用于在所有用户页面中统一管理用户信息的显示
 */

class UserInfoManager {
    constructor() {
        this.userInfo = null;
    }
    
    /**
     * 初始化用户信息
     */
    async init() {
        await this.loadUserInfo();
        this.updateUserDisplay();
    }
    
    /**
     * 加载用户信息
     */
    async loadUserInfo() {
        try {
            // 首先尝试从localStorage获取
            const userInfo = localStorage.getItem('user_info');
            if (userInfo) {
                this.userInfo = JSON.parse(userInfo);
                return;
            }
            
            // 如果localStorage中没有，从API获取
            await this.fetchUserInfoFromAPI();
        } catch (error) {
            console.error('加载用户信息失败:', error);
            // 如果解析失败，从API获取
            await this.fetchUserInfoFromAPI();
        }
    }
    
    /**
     * 从API获取用户信息
     */
    async fetchUserInfoFromAPI() {
        try {
            const token = localStorage.getItem('user_token');
            if (!token) {
                console.warn('未找到用户token');
                return;
            }
            
            const response = await fetch('/api/user/profile', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    this.userInfo = result.data;
                    // 保存用户信息到localStorage
                    localStorage.setItem('user_info', JSON.stringify(result.data));
                }
            }
        } catch (error) {
            console.error('从API获取用户信息失败:', error);
        }
    }
    
    /**
     * 更新用户显示
     */
    updateUserDisplay() {
        if (!this.userInfo) {
            return;
        }
        
        // 更新用户名显示
        const userNameElement = document.getElementById('user-name');
        if (userNameElement && this.userInfo.name) {
            userNameElement.textContent = this.userInfo.name;
        }
        
        // 更新用户角色显示
        const userRoleElement = document.getElementById('user-role');
        if (userRoleElement) {
            userRoleElement.textContent = '普通用户';
        }
        
        // 更新头像显示（如果有的话）
        const avatarElement = document.querySelector('#user-avatar img');
        if (avatarElement && this.userInfo.avatar_url) {
            avatarElement.src = this.userInfo.avatar_url;
        }
    }
    
    /**
     * 获取当前用户信息
     */
    getUserInfo() {
        return this.userInfo;
    }
    
    /**
     * 获取当前用户ID
     */
    getCurrentUserId() {
        return this.userInfo ? this.userInfo.id : null;
    }
    
    /**
     * 获取当前用户名
     */
    getCurrentUserName() {
        return this.userInfo ? this.userInfo.name : '用户';
    }
    
    /**
     * 更新用户信息
     */
    updateUserInfo(newUserInfo) {
        this.userInfo = { ...this.userInfo, ...newUserInfo };
        localStorage.setItem('user_info', JSON.stringify(this.userInfo));
        this.updateUserDisplay();
    }
    
    /**
     * 清除用户信息
     */
    clearUserInfo() {
        this.userInfo = null;
        localStorage.removeItem('user_info');
        localStorage.removeItem('user_token');
    }
}

// 创建全局实例
window.userInfoManager = new UserInfoManager();

// 页面加载完成后自动初始化
document.addEventListener('DOMContentLoaded', function() {
    // 检查用户登录状态
    const token = localStorage.getItem('user_token');
    if (token) {
        // 如果已登录，初始化用户信息
        window.userInfoManager.init();
    } else {
        // 如果未登录，跳转到登录页面
        if (window.location.pathname !== '/' && !window.location.pathname.includes('login')) {
            window.location.href = '/';
        }
    }
});

// 导出到全局
window.UserInfoManager = UserInfoManager;
