/**
 * 认证守卫模块
 * 用于检查用户登录状态，防止未授权访问
 */

class AuthGuard {
    constructor() {
        this.loginPages = [
            '/index.html',
            '/admin/login.html'
        ];
        this.init();
    }

    init() {
        // 页面加载时检查认证状态，添加延迟确保localStorage已更新
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                // 增加延迟时间，确保localStorage完全更新
                setTimeout(() => this.checkAuth(), 500);
            });
        } else {
            // 如果页面已经加载完成，立即检查但也要给一点延迟
            setTimeout(() => this.checkAuth(), 200);
        }
        
        // 监听localStorage变化，如果检测到token变化，重新检查认证
        window.addEventListener('storage', (e) => {
            if (e.key && e.key.endsWith('_token')) {
                console.log('检测到token变化，重新检查认证...');
                setTimeout(() => this.checkAuth(), 100);
            }
        });
    }

    /**
     * 检查当前页面是否需要认证
     */
    needsAuth() {
        const currentPath = window.location.pathname;
        
        // 登录页面不需要认证
        if (this.loginPages.some(page => currentPath.includes(page))) {
            return false;
        }
        
        // 静态资源不需要认证
        if (currentPath.match(/\.(css|js|png|jpg|jpeg|gif|ico|svg)$/)) {
            return false;
        }
        
        // 其他页面都需要认证
        return true;
    }

    /**
     * 获取用户类型
     */
    getUserType() {
        const token = this.getToken();
        if (!token) return null;

        try {
            const payload = token.split('.')[1];
            if (payload) {
                // 添加padding如果需要
                const paddedPayload = payload + '='.repeat((4 - payload.length % 4) % 4);
                const decoded = JSON.parse(atob(paddedPayload));
                return decoded.user_type;
            }
        } catch (e) {
            console.error('解析token失败:', e);
        }
        return null;
    }

    /**
     * 获取token
     */
    getToken() {
        return localStorage.getItem('user_token') || 
               localStorage.getItem('caregiver_token') || 
               localStorage.getItem('admin_token') ||
               this.getCookie('user_token') ||
               this.getCookie('caregiver_token') ||
               this.getCookie('admin_token');
    }

    /**
     * 获取cookie
     */
    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    /**
     * 检查token是否有效
     */
    isTokenValid() {
        const token = this.getToken();
        if (!token) return false;

        try {
            const payload = token.split('.')[1];
            if (payload) {
                // 添加padding如果需要
                const paddedPayload = payload + '='.repeat((4 - payload.length % 4) % 4);
                const decoded = JSON.parse(atob(paddedPayload));
                
                // 检查过期时间
                if (decoded.exp && decoded.exp < Date.now() / 1000) {
                    return false;
                }
                
                return true;
            }
        } catch (e) {
            console.error('解析token失败:', e);
        }
        return false;
    }

    /**
     * 检查用户是否有权限访问当前页面
     */
    hasPermission() {
        const userType = this.getUserType();
        const currentPath = window.location.pathname;
        
        // 用户端页面
        if (currentPath.includes('/user/')) {
            return userType === 'user';
        }
        
        // 护工端页面
        if (currentPath.includes('/caregiver/')) {
            return userType === 'caregiver';
        }
        
        // 管理端页面
        if (currentPath.includes('/admin/')) {
            return userType === 'admin';
        }
        
        return true;
    }

    /**
     * 重定向到登录页面
     */
    redirectToLogin() {
        const userType = this.getUserType();
        
        if (userType === 'admin') {
            window.location.href = '/admin/login.html';
        } else {
            window.location.href = '/index.html';
        }
    }

    /**
     * 清除认证信息
     */
    clearAuth() {
        localStorage.removeItem('user_token');
        localStorage.removeItem('caregiver_token');
        localStorage.removeItem('admin_token');
        localStorage.removeItem('user_info');
        localStorage.removeItem('caregiver_info');
        localStorage.removeItem('admin_info');
        
        // 清除cookie
        document.cookie = 'user_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
        document.cookie = 'caregiver_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
        document.cookie = 'admin_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    }

    /**
     * 主要认证检查方法
     */
    checkAuth() {
        console.log('🔍 开始认证检查...');
        console.log('当前路径:', window.location.pathname);
        
        // 如果当前页面不需要认证，直接返回
        if (!this.needsAuth()) {
            console.log('✅ 页面不需要认证，跳过检查');
            return;
        }

        console.log('🔑 检查token...');
        const token = this.getToken();
        console.log('获取到的token:', token ? '存在' : '不存在');
        
        // 检查是否有有效的token
        if (!this.isTokenValid()) {
            console.log('❌ Token无效或已过期，重定向到登录页面');
            this.clearAuth();
            this.redirectToLogin();
            return;
        }

        console.log('👤 检查用户权限...');
        const userType = this.getUserType();
        console.log('用户类型:', userType);
        
        // 检查用户权限
        if (!this.hasPermission()) {
            console.log('❌ 用户权限不足，重定向到登录页面');
            this.clearAuth();
            this.redirectToLogin();
            return;
        }

        console.log('✅ 认证检查通过');
    }

    /**
     * 登出方法
     */
    logout() {
        this.clearAuth();
        this.redirectToLogin();
    }
}

// 创建全局实例
window.authGuard = new AuthGuard();

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthGuard;
}
