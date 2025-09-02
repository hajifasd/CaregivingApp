/**
 * 页面构建器 - 负责加载组件和构建页面
 */
class PageBuilder {
    constructor() {
        this.components = {};
        this.currentPage = '';
        this.init();
    }
    
    init() {
        // 初始化事件监听
        this.bindEvents();
        // 设置当前页面
        this.setCurrentPage();
        // 加载并插入组件
        this.loadAndInsertComponents();
        // 更新导航状态
        this.updateNavigation();
    }
    
    /**
     * 加载组件
     * @param {string} name 组件名称
     * @returns {Promise<string>} 组件HTML内容
     */
    async loadComponent(name) {
        if (this.components[name]) return this.components[name];
        
        try {
            const response = await fetch(`components/${name}.html`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const html = await response.text();
            this.components[name] = html;
            return html;
        } catch (error) {
            console.error(`Failed to load component: ${name}`, error);
            return '';
        }
    }
    
    /**
     * 加载并插入组件到页面
     */
    async loadAndInsertComponents() {
        try {
            // 在body开始处插入header
            const header = await this.loadComponent('header');
            if (header) {
                const headerElement = document.createElement('div');
                headerElement.innerHTML = header;
                document.body.insertBefore(headerElement.firstElementChild, document.body.firstChild);
            }
            
            // 在header后插入navigation
            const navigation = await this.loadComponent('navigation');
            if (navigation) {
                const navElement = document.createElement('div');
                navElement.innerHTML = navigation;
                const headerElement = document.querySelector('header');
                if (headerElement) {
                    headerElement.after(navElement.firstElementChild);
                }
            }
            
        } catch (error) {
            console.error('Failed to load components:', error);
        }
    }
    
    /**
     * 更新导航状态
     */
    updateNavigation() {
        document.querySelectorAll('[data-nav]').forEach(nav => {
            const isActive = nav.getAttribute('data-nav') === this.currentPage;
            nav.classList.toggle('border-b-2', isActive);
            nav.classList.toggle('border-primary', isActive);
            nav.classList.toggle('text-primary', isActive);
            nav.classList.toggle('font-medium', isActive);
            
            if (!isActive) {
                nav.classList.add('text-gray-500');
            }
        });
    }
    
    /**
     * 设置当前页面
     */
    setCurrentPage() {
        this.currentPage = window.location.pathname.split('/').pop() || 'user-home.html';
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        // 登出按钮
        document.addEventListener('click', (e) => {
            if (e.target.id === 'logout-btn') {
                if (typeof AuthManager !== 'undefined') {
                    AuthManager.logout();
                }
            }
        });
        
        // 搜索功能
        const searchInput = document.querySelector('input[placeholder*="搜索"]');
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.handleSearch(e.target.value);
                }
            });
        }
        
        // 通知按钮
        const notificationBtn = document.getElementById('notification-btn');
        if (notificationBtn) {
            notificationBtn.addEventListener('click', () => {
                this.showNotifications();
            });
        }
    }
    
    /**
     * 处理搜索
     * @param {string} query 搜索查询
     */
    handleSearch(query) {
        if (query.trim()) {
            if (typeof NavigationManager !== 'undefined') {
                NavigationManager.navigateTo('user-caregivers.html', { search: query });
            } else {
                window.location.href = `user-caregivers.html?search=${encodeURIComponent(query)}`;
            }
        }
    }
    
    /**
     * 显示通知
     */
    showNotifications() {
        if (typeof UIManager !== 'undefined') {
            UIManager.showNotification('暂无新通知', 'info');
        } else {
            alert('暂无新通知');
        }
    }
}

// 创建全局实例
window.pageBuilder = new PageBuilder();
