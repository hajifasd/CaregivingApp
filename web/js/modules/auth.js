/**
 * 认证管理模块
 */
class AuthManager {
    static TOKEN_KEY = 'user_token';
    static USER_INFO_KEY = 'user_info';
    
    /**
     * 检查用户登录状态
     * @returns {boolean} 是否已登录
     */
    static checkLogin() {
        const token = localStorage.getItem(this.TOKEN_KEY);
        if (!token) {
            this.redirectToLogin();
            return false;
        }
        
        // 验证token有效性（这里简化处理，实际应该调用验证API）
        if (this.isTokenExpired(token)) {
            this.logout();
            return false;
        }
        
        return true;
    }
    
    /**
     * 用户登录
     * @param {string} username 用户名
     * @param {string} password 密码
     * @returns {Promise<boolean>} 登录是否成功
     */
    static async login(username, password) {
        try {
            // 这里应该调用实际的登录API
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.setToken(data.token);
                    this.setUserInfo(data.user);
                    return true;
                }
            }
            
            return false;
        } catch (error) {
            console.error('Login failed:', error);
            return false;
        }
    }
    
    /**
     * 用户登出
     */
    static logout() {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_INFO_KEY);
        this.redirectToLogin();
    }
    
    /**
     * 获取用户信息
     * @returns {Object|null} 用户信息
     */
    static getUserInfo() {
        const userInfo = localStorage.getItem(this.USER_INFO_KEY);
        return userInfo ? JSON.parse(userInfo) : null;
    }
    
    /**
     * 获取认证token
     * @returns {string|null} 认证token
     */
    static getToken() {
        return localStorage.getItem(this.TOKEN_KEY);
    }
    
    /**
     * 设置认证token
     * @param {string} token 认证token
     */
    static setToken(token) {
        localStorage.setItem(this.TOKEN_KEY, token);
    }
    
    /**
     * 设置用户信息
     * @param {Object} userInfo 用户信息
     */
    static setUserInfo(userInfo) {
        localStorage.setItem(this.USER_INFO_KEY, JSON.stringify(userInfo));
    }
    
    /**
     * 检查token是否过期
     * @param {string} token 认证token
     * @returns {boolean} 是否过期
     */
    static isTokenExpired(token) {
        try {
            // 这里应该解析JWT token并检查过期时间
            // 简化处理：检查token长度
            return token.length < 10;
        } catch (error) {
            return true;
        }
    }
    
    /**
     * 重定向到登录页面
     */
    static redirectToLogin() {
        if (window.location.pathname !== '/') {
            window.location.href = '/';
        }
    }
    
    /**
     * 更新用户头像
     * @param {string} avatarUrl 头像URL
     */
    static updateAvatar(avatarUrl) {
        const userInfo = this.getUserInfo();
        if (userInfo) {
            userInfo.avatar = avatarUrl;
            this.setUserInfo(userInfo);
            this.updateUI();
        }
    }
    
    /**
     * 更新用户信息
     * @param {Object} updates 更新的信息
     */
    static updateUserInfo(updates) {
        const userInfo = this.getUserInfo();
        if (userInfo) {
            Object.assign(userInfo, updates);
            this.setUserInfo(userInfo);
            this.updateUI();
        }
    }
    
    /**
     * 更新UI显示
     */
    static updateUI() {
        const userInfo = this.getUserInfo();
        if (userInfo) {
            // 更新用户名显示
            const userNameElement = document.getElementById('user-name');
            if (userNameElement) {
                userNameElement.textContent = userInfo.name || '用户';
            }
            
            // 更新用户角色显示
            const userRoleElement = document.getElementById('user-role');
            if (userRoleElement) {
                userRoleElement.textContent = userInfo.role || '普通用户';
            }
            
            // 更新头像显示
            const avatarElement = document.querySelector('#user-avatar img');
            if (avatarElement && userInfo.avatar) {
                avatarElement.src = userInfo.avatar;
            }
        }
    }
}

// 导出到全局
window.AuthManager = AuthManager;
