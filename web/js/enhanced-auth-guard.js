/**
 * 增强版认证守卫模块
 * 用于检查用户登录状态，防止未授权访问
 * 支持用户端、护工端、管理端三种角色
 */

class EnhancedAuthGuard {
    constructor() {
        this.loginPages = [
            '/',
            '/index.html',
            '/admin/admin-login.html'
        ];
        
        this.userPages = [
            '/user/',
            '/user/user-dashboard.html',
            '/user/user-profile.html',
            '/user/user-caregivers.html',
            '/user/user-appointments.html',
            '/user/user-employments.html',
            '/user/user-hire-caregiver.html',
            '/user/user-messages.html',
            '/user/user-review.html'
        ];
        
        this.caregiverPages = [
            '/caregiver/caregiver-dashboard.html',
            '/caregiver/caregiver-profile.html',
            '/caregiver/caregiver-appointments.html',
            '/caregiver/caregiver-messages.html',
            '/caregiver/caregiver-jobs.html',
            '/caregiver/caregiver-job-opportunities.html',
            '/caregiver/caregiver-hire-info.html',
            '/caregiver/caregiver-reviews.html',
            '/caregiver/caregiver-schedule.html',
            '/caregiver/caregiver-settings.html',
            '/caregiver/caregiver-earnings.html',
            '/caregiver/caregiver-location.html'
        ];
        
        this.adminPages = [
            '/admin/admin-dashboard.html',
            '/admin/admin-users.html',
            '/admin/admin-caregivers.html',
            '/admin/admin-settings.html',
            '/admin/admin-monitoring.html',
            '/admin/admin-job-analysis.html',
            '/admin/admin-bigdata-dashboard.html'
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
        if (this.loginPages.some(page => currentPath.endsWith(page))) {
            return false;
        }
        
        // 静态资源不需要认证
        if (currentPath.startsWith('/css/') || 
            currentPath.startsWith('/js/') || 
            currentPath.startsWith('/uploads/') ||
            currentPath.endsWith('.css') ||
            currentPath.endsWith('.js') ||
            currentPath.endsWith('.png') ||
            currentPath.endsWith('.jpg') ||
            currentPath.endsWith('.jpeg') ||
            currentPath.endsWith('.gif') ||
            currentPath.endsWith('.ico')) {
            return false;
        }
        
        // 其他页面都需要认证
        return true;
    }

    /**
     * 获取当前用户类型
     */
    getUserType() {
        // 检查护工端token
        if (localStorage.getItem('caregiver_token')) {
            return 'caregiver';
        }
        
        // 检查用户端token
        if (localStorage.getItem('user_token')) {
            return 'user';
        }
        
        // 检查管理端token
        if (localStorage.getItem('admin_token')) {
            return 'admin';
        }
        
        return null;
    }

    /**
     * 检查用户是否有权限访问当前页面
     */
    hasPermission() {
        const currentPath = window.location.pathname;
        const userType = this.getUserType();
        
        if (!userType) {
            return false;
        }
        
        // 根据用户类型检查页面权限
        switch (userType) {
            case 'user':
                return this.userPages.some(page => currentPath.endsWith(page)) || 
                       currentPath.startsWith('/user/');
                       
            case 'caregiver':
                return this.caregiverPages.some(page => currentPath.endsWith(page)) || 
                       currentPath.startsWith('/caregiver/');
                       
            case 'admin':
                // 管理端可以访问所有管理页面
                return this.adminPages.some(page => currentPath.endsWith(page)) || 
                       currentPath.startsWith('/admin/') ||
                       currentPath === '/admin-dashboard.html' ||
                       currentPath === '/admin-users.html' ||
                       currentPath === '/admin-caregivers.html' ||
                       currentPath === '/admin-settings.html' ||
                       currentPath === '/admin-monitoring.html' ||
                       currentPath === '/admin-job-analysis.html' ||
                       currentPath === '/admin-bigdata-dashboard.html';
                       
            default:
                return false;
        }
    }

    /**
     * 验证token有效性
     */
    isTokenValid() {
        const userType = this.getUserType();
        if (!userType) return false;
        
        const tokenKey = `${userType}_token`;
        const token = localStorage.getItem(tokenKey);
        
        if (!token) return false;
        
        try {
            // 解析JWT token
            const payload = token.split('.')[1];
            if (!payload) return false;
            
            const decoded = JSON.parse(decodeURIComponent(escape(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))));
            
            // 检查token是否过期
            if (decoded.exp && decoded.exp * 1000 < Date.now()) {
                return false;
            }
            
            // 检查用户类型是否匹配
            if (decoded.user_type !== userType) {
                return false;
            }
            
            return true;
        } catch (error) {
            console.error('Token验证失败:', error);
            return false;
        }
    }

    /**
     * 重定向到对应的登录页面
     */
    redirectToLogin() {
        const currentPath = window.location.pathname;
        
        if (currentPath.startsWith('/admin/')) {
            window.location.href = '/admin/admin-login.html';
        } else if (currentPath.startsWith('/caregiver/')) {
            window.location.href = '/';
        } else {
            window.location.href = '/';
        }
    }

    /**
     * 清除认证信息
     */
    clearAuth() {
        localStorage.removeItem('user_token');
        localStorage.removeItem('user_info');
        localStorage.removeItem('caregiver_token');
        localStorage.removeItem('caregiver_info');
        localStorage.removeItem('admin_token');
        localStorage.removeItem('admin_info');
    }

    /**
     * 主要认证检查方法
     */
    checkAuth() {
        console.log('🔍 开始增强认证检查...');
        console.log('当前路径:', window.location.pathname);
        console.log('当前URL:', window.location.href);
        
        // 如果当前页面不需要认证，直接返回
        if (!this.needsAuth()) {
            console.log('✅ 页面不需要认证，跳过检查');
            return;
        }

        console.log('🔑 检查token...');
        const userType = this.getUserType();
        console.log('检测到的用户类型:', userType);
        
        // 如果没有检测到用户类型，等待一下再检查（可能是localStorage还没更新）
        if (!userType) {
            console.log('⏳ 未检测到用户类型，等待localStorage更新...');
            setTimeout(() => {
                const retryUserType = this.getUserType();
                if (retryUserType) {
                    console.log('🔄 重试检测到用户类型:', retryUserType);
                    this.checkAuth();
                } else {
                    console.log('❌ 重试后仍未检测到用户类型，重定向到登录页面');
                    this.redirectToLogin();
                }
            }, 300);
            return;
        }
        
        // 检查是否有有效的token
        if (!this.isTokenValid()) {
            console.log('❌ Token无效或已过期，重定向到登录页面');
            console.log('Token详情:', {
                admin_token: localStorage.getItem('admin_token'),
                user_token: localStorage.getItem('user_token'),
                caregiver_token: localStorage.getItem('caregiver_token')
            });
            this.clearAuth();
            this.redirectToLogin();
            return;
        }

        console.log('👤 检查用户权限...');
        console.log('用户类型:', userType);
        
        // 检查用户权限
        if (!this.hasPermission()) {
            console.log('❌ 用户权限不足，重定向到登录页面');
            console.log('权限检查详情:', {
                currentPath: window.location.pathname,
                userType: userType,
                hasPermission: this.hasPermission()
            });
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
window.enhancedAuthGuard = new EnhancedAuthGuard();
