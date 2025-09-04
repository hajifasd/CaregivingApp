/**
 * 用户端通用登出功能
 * 所有用户页面都可以使用这个文件
 */

// 绑定登出按钮
function bindUserLogoutButton() {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            if (confirm('确定要登出吗？')) {
                logoutUser();
            }
        });
    }
}

// 执行用户登出
function logoutUser() {
    try {
        // 清除localStorage中的用户数据
        localStorage.removeItem('user_token');
        localStorage.removeItem('user_info');
        localStorage.removeItem('user_id');
        
        // 清除cookie中的用户数据
        document.cookie = 'user_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
        document.cookie = 'user_info=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
        
        // 显示登出成功消息
        showLogoutMessage();
        
        // 延迟跳转到首页，让用户看到登出消息
        setTimeout(() => {
            window.location.href = '/';
        }, 1500);
        
    } catch (error) {
        console.error('登出过程中出现错误:', error);
        // 即使出错也要跳转到首页
        window.location.href = '/';
    }
}

// 显示登出成功消息
function showLogoutMessage() {
    // 创建登出成功提示
    const logoutMessage = document.createElement('div');
    logoutMessage.id = 'logout-message';
    logoutMessage.className = 'fixed top-4 right-4 bg-success text-white px-6 py-3 rounded-lg shadow-lg z-50';
    logoutMessage.innerHTML = `
        <div class="flex items-center">
            <i class="fa fa-check-circle mr-2"></i>
            <span>登出成功，正在跳转到首页...</span>
        </div>
    `;
    
    document.body.appendChild(logoutMessage);
    
    // 3秒后自动移除消息
    setTimeout(() => {
        if (logoutMessage.parentNode) {
            logoutMessage.parentNode.removeChild(logoutMessage);
        }
    }, 3000);
}

// 检查用户登录状态
function checkUserLoginStatus() {
    const token = localStorage.getItem('user_token') || getCookie('user_token');
    if (!token) {
        // 如果没有token，跳转到首页
        window.location.href = '/';
        return false;
    }
    
    try {
        // 解析JWT token验证有效性
        const payload = token.split('.')[1];
        if (payload) {
            const decoded = JSON.parse(decodeURIComponent(escape(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))));
            
            // 检查token是否过期
            if (decoded.exp && decoded.exp * 1000 < Date.now()) {
                // token已过期，清除并跳转
                logoutUser();
                return false;
            }
            
            // 检查用户类型
            if (decoded.user_type !== 'user') {
                // 不是用户类型，清除并跳转
                logoutUser();
                return false;
            }
            
            return true;
        }
    } catch (error) {
        console.error('Token验证失败:', error);
        logoutUser();
        return false;
    }
    
    return false;
}

// 获取cookie值
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// 自动绑定登出按钮（页面加载完成后）
document.addEventListener('DOMContentLoaded', function() {
    bindUserLogoutButton();
    
    // 检查登录状态
    if (!checkUserLoginStatus()) {
        return;
    }
});

// 导出函数供其他脚本使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        bindUserLogoutButton,
        logoutUser,
        checkUserLoginStatus
    };
}
