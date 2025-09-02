/**
 * 导航管理模块
 */
class NavigationManager {
    /**
     * 导航到指定页面
     * @param {string} page 页面路径
     * @param {Object} params 查询参数
     */
    static navigateTo(page, params = {}) {
        const url = new URL(page, window.location.origin);
        Object.keys(params).forEach(key => {
            if (params[key] !== undefined && params[key] !== null) {
                url.searchParams.set(key, params[key]);
            }
        });
        window.location.href = url.toString();
    }
    
    /**
     * 获取当前页面
     * @returns {string} 当前页面路径
     */
    static getCurrentPage() {
        return window.location.pathname.split('/').pop() || 'user-home.html';
    }
    
    /**
     * 获取URL查询参数
     * @returns {Object} 查询参数对象
     */
    static getQueryParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const params = {};
        for (const [key, value] of urlParams) {
            params[key] = value;
        }
        return params;
    }
    
    /**
     * 获取特定查询参数
     * @param {string} key 参数名
     * @param {*} defaultValue 默认值
     * @returns {*} 参数值
     */
    static getQueryParam(key, defaultValue = null) {
        const params = this.getQueryParams();
        return params[key] !== undefined ? params[key] : defaultValue;
    }
    
    /**
     * 设置查询参数
     * @param {string} key 参数名
     * @param {*} value 参数值
     */
    static setQueryParam(key, value) {
        const url = new URL(window.location);
        if (value === null || value === undefined) {
            url.searchParams.delete(key);
        } else {
            url.searchParams.set(key, value);
        }
        window.history.replaceState({}, '', url);
    }
    
    /**
     * 移除查询参数
     * @param {string} key 参数名
     */
    static removeQueryParam(key) {
        this.setQueryParam(key, null);
    }
    
    /**
     * 清除所有查询参数
     */
    static clearQueryParams() {
        const url = new URL(window.location);
        url.search = '';
        window.history.replaceState({}, '', url);
    }
    
    /**
     * 返回上一页
     */
    static goBack() {
        if (window.history.length > 1) {
            window.history.back();
        } else {
            this.navigateTo('user-home.html');
        }
    }
    
    /**
     * 刷新当前页面
     */
    static refresh() {
        window.location.reload();
    }
    
    /**
     * 在新标签页中打开链接
     * @param {string} url 链接地址
     */
    static openInNewTab(url) {
        window.open(url, '_blank');
    }
    
    /**
     * 滚动到页面顶部
     */
    static scrollToTop() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    /**
     * 滚动到指定元素
     * @param {string} selector 元素选择器
     * @param {Object} options 滚动选项
     */
    static scrollToElement(selector, options = {}) {
        const element = document.querySelector(selector);
        if (element) {
            element.scrollIntoView({
                behavior: 'smooth',
                block: 'start',
                ...options
            });
        }
    }
    
    /**
     * 处理页面内锚点导航
     * @param {string} anchor 锚点名称
     */
    static scrollToAnchor(anchor) {
        const element = document.getElementById(anchor) || document.querySelector(`[data-anchor="${anchor}"]`);
        if (element) {
            this.scrollToElement(`#${anchor}`);
        }
    }
    
    /**
     * 更新页面标题
     * @param {string} title 页面标题
     */
    static updatePageTitle(title) {
        document.title = `护理助手 - ${title}`;
    }
    
    /**
     * 更新面包屑导航
     * @param {Array} breadcrumbs 面包屑数组
     */
    static updateBreadcrumbs(breadcrumbs) {
        const breadcrumbContainer = document.getElementById('breadcrumbs');
        if (breadcrumbContainer && breadcrumbs) {
            breadcrumbContainer.innerHTML = breadcrumbs.map((item, index) => {
                if (index === breadcrumbs.length - 1) {
                    return `<span class="text-gray-500">${item.name}</span>`;
                } else {
                    return `<a href="${item.url}" class="text-primary hover:text-primary/80">${item.name}</a> <i class="fa fa-angle-right mx-2 text-gray-400"></i>`;
                }
            }).join('');
        }
    }
    
    /**
     * 处理页面加载完成后的导航相关操作
     */
    static onPageLoad() {
        // 检查是否有锚点参数
        const anchor = this.getQueryParam('anchor');
        if (anchor) {
            setTimeout(() => this.scrollToAnchor(anchor), 100);
        }
        
        // 更新页面标题
        const currentPage = this.getCurrentPage();
        const pageTitles = {
            'user-home.html': '首页',
            'user-profile.html': '个人信息',
            'user-caregivers.html': '寻找护工',
            'user-appointments.html': '我的预约',
            'user-employments.html': '我的聘用',
            'user-messages.html': '消息中心'
        };
        
        if (pageTitles[currentPage]) {
            this.updatePageTitle(pageTitles[currentPage]);
        }
        
        // 更新面包屑
        this.updateBreadcrumbs([
            { name: '首页', url: 'user-home.html' },
            { name: pageTitles[currentPage] || '页面' }
        ]);
    }
}

// 导出到全局
window.NavigationManager = NavigationManager;
