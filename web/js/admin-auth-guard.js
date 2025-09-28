/**
 * 管理端专用认证守卫
 * 简化版本，专门处理管理端页面的认证问题
 */

class AdminAuthGuard {
    constructor() {
        this.init();
    }

    init() {
        // 页面加载完成后立即检查认证
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.checkAdminAuth();
            });
        } else {
            this.checkAdminAuth();
        }
    }

    checkAdminAuth() {
        console.log('🔍 管理端认证检查开始...');
        console.log('当前路径:', window.location.pathname);
        
        // 检查是否有admin_token
        const adminToken = localStorage.getItem('admin_token');
        console.log('admin_token存在:', !!adminToken);
        
        if (!adminToken) {
            console.log('❌ 未找到admin_token，重定向到登录页面');
            this.redirectToLogin();
            return;
        }

        // 验证token格式（简单检查）
        try {
            const parts = adminToken.split('.');
            if (parts.length !== 3) {
                throw new Error('Token格式错误');
            }
            
            // 解析payload
            const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));
            console.log('Token payload:', payload);
            
            // 检查用户类型
            if (payload.user_type !== 'admin') {
                console.log('❌ 用户类型不是admin，重定向到登录页面');
                this.redirectToLogin();
                return;
            }
            
            // 检查是否过期
            if (payload.exp && payload.exp * 1000 < Date.now()) {
                console.log('❌ Token已过期，重定向到登录页面');
                this.redirectToLogin();
                return;
            }
            
            console.log('✅ 管理端认证检查通过');
            
        } catch (error) {
            console.log('❌ Token验证失败:', error.message);
            this.redirectToLogin();
        }
    }

    redirectToLogin() {
        console.log('重定向到管理端登录页面...');
        window.location.href = '/admin/admin-login.html';
    }
}

// 创建全局实例
window.adminAuthGuard = new AdminAuthGuard();
