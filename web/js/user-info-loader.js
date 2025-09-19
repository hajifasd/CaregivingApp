/**
 * 用户信息加载器
 * 用于在所有用户页面中统一加载和显示用户信息
 */

class UserInfoLoader {
    constructor() {
        this.userInfo = null;
    }
    
    /**
     * 初始化用户信息显示
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
            // 尝试从多个可能的localStorage键获取用户信息
            let userInfo = null;
            
            // 首先尝试 user_info (用户信息管理模块的键)
            const userInfoFromManager = localStorage.getItem('user_info');
            if (userInfoFromManager) {
                userInfo = JSON.parse(userInfoFromManager);
            } else {
                // 然后尝试 userInfo (旧版本的键)
                const userInfoOld = localStorage.getItem('userInfo');
                if (userInfoOld) {
                    userInfo = JSON.parse(userInfoOld);
                }
            }
            
            // 如果localStorage中没有用户信息，尝试从JWT token解析
            if (!userInfo || !userInfo.name) {
                userInfo = this.getUserInfoFromToken();
                
                // 如果从token解析成功，保存到localStorage
                if (userInfo && userInfo.name) {
                    localStorage.setItem('user_info', JSON.stringify(userInfo));
                }
            }
            
            // 如果仍然没有用户信息，尝试从API获取
            if (!userInfo || !userInfo.name) {
                userInfo = await this.fetchUserInfoFromAPI();
            }
            
            this.userInfo = userInfo;
            return userInfo;
            
        } catch (error) {
            console.error('加载用户信息失败:', error);
            return null;
        }
    }
    
    /**
     * 从JWT token解析用户信息
     */
    getUserInfoFromToken() {
        try {
            const token = localStorage.getItem('user_token') || this.getCookie('user_token');
            if (!token) return null;
            
            const payload = token.split('.')[1];
            if (payload) {
                const decoded = JSON.parse(decodeURIComponent(escape(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))));
                return {
                    id: decoded.user_id,
                    name: decoded.name || decoded.username || '用户',
                    role: decoded.role || '普通用户'
                };
            }
        } catch (e) {
            console.error('解析token失败:', e);
        }
        return null;
    }
    
    /**
     * 从API获取用户信息
     */
    async fetchUserInfoFromAPI() {
        try {
            const token = localStorage.getItem('user_token') || this.getCookie('user_token');
            if (!token) {
                console.warn('未找到用户token');
                return null;
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
                    const userInfo = result.data;
                    // 保存用户信息到localStorage
                    localStorage.setItem('user_info', JSON.stringify(userInfo));
                    return userInfo;
                }
            }
        } catch (error) {
            console.error('从API获取用户信息失败:', error);
        }
        return null;
    }
    
    /**
     * 更新用户显示
     */
    updateUserDisplay() {
        if (!this.userInfo) {
            console.warn('未找到用户信息，显示默认值');
            return;
        }
        
        // 更新用户名显示
        const userNameElement = document.getElementById('user-name');
        if (userNameElement) {
            const userName = this.userInfo.name || this.userInfo.fullname || '用户';
            userNameElement.textContent = userName;
        }
        
        // 更新用户角色显示
        const userRoleElement = document.getElementById('user-role');
        if (userRoleElement) {
            userRoleElement.textContent = this.userInfo.role || '普通用户';
        }
        
        // 更新欢迎标题中的用户名
        const welcomeUserNameElement = document.getElementById('welcome-user-name');
        if (welcomeUserNameElement) {
            const userName = this.userInfo.name || this.userInfo.fullname || '用户';
            welcomeUserNameElement.textContent = userName;
        }
        
        console.log('用户信息显示更新成功:', this.userInfo.name || this.userInfo.fullname);
    }
    
    /**
     * 获取Cookie
     */
    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
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
        return this.userInfo ? (this.userInfo.name || this.userInfo.fullname || '用户') : '用户';
    }
}

// 创建全局实例
window.userInfoLoader = new UserInfoLoader();

// 页面加载完成后自动初始化
document.addEventListener('DOMContentLoaded', function() {
    // 检查用户登录状态
    const token = localStorage.getItem('user_token');
    if (token) {
        // 如果已登录，初始化用户信息
        window.userInfoLoader.init();
    } else {
        // 如果未登录，跳转到登录页面
        if (window.location.pathname !== '/' && !window.location.pathname.includes('login')) {
            window.location.href = '/';
        }
    }
});

// 导出到全局
window.UserInfoLoader = UserInfoLoader;
