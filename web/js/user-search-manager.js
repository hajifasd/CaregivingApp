/**
 * 用户端搜索管理器
 * ====================================
 * 
 * 处理用户端的全局搜索功能
 */

class UserSearchManager {
    constructor() {
        this.searchInput = null;
        this.searchResults = [];
        this.searchHistory = [];
        this.currentQuery = '';
        this.searchTimeout = null;
        this.isSearching = false;
    }
    
    /**
     * 初始化搜索管理器
     */
    init() {
        this.setupSearchInput();
        this.setupEventListeners();
        this.loadSearchHistory();
    }
    
    /**
     * 设置搜索输入框
     */
    setupSearchInput() {
        // 查找所有搜索输入框
        this.searchInput = document.querySelector('input[placeholder*="搜索护工、服务"]');
        
        if (!this.searchInput) {
            console.warn('未找到搜索输入框');
            return;
        }
        
        // 添加搜索功能属性
        this.searchInput.setAttribute('id', 'global-search-input');
        this.searchInput.setAttribute('autocomplete', 'off');
        
        console.log('✅ 搜索输入框已初始化');
    }
    
    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        if (!this.searchInput) return;
        
        // 输入事件
        this.searchInput.addEventListener('input', (e) => {
            this.handleSearchInput(e.target.value);
        });
        
        // 键盘事件
        this.searchInput.addEventListener('keydown', (e) => {
            this.handleKeyDown(e);
        });
        
        // 焦点事件
        this.searchInput.addEventListener('focus', () => {
            this.showSearchSuggestions();
        });
        
        // 失焦事件
        this.searchInput.addEventListener('blur', () => {
            // 延迟隐藏，允许点击建议项
            setTimeout(() => {
                this.hideSearchSuggestions();
            }, 200);
        });
    }
    
    /**
     * 处理搜索输入
     */
    handleSearchInput(query) {
        this.currentQuery = query.trim();
        
        // 清除之前的搜索超时
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        
        if (this.currentQuery.length === 0) {
            this.hideSearchSuggestions();
            return;
        }
        
        if (this.currentQuery.length < 2) {
            return;
        }
        
        // 延迟搜索，避免频繁请求
        this.searchTimeout = setTimeout(() => {
            this.performSearch(this.currentQuery);
        }, 300);
    }
    
    /**
     * 处理键盘事件
     */
    handleKeyDown(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            this.performSearch(this.currentQuery);
        } else if (e.key === 'Escape') {
            this.hideSearchSuggestions();
            this.searchInput.blur();
        }
    }
    
    /**
     * 执行搜索
     */
    async performSearch(query) {
        if (this.isSearching) return;
        
        this.isSearching = true;
        this.showSearchLoading();
        
        try {
            const results = await this.searchAll(query);
            this.displaySearchResults(results);
            this.addToSearchHistory(query);
        } catch (error) {
            console.error('搜索失败:', error);
            this.showSearchError('搜索失败，请稍后重试');
        } finally {
            this.isSearching = false;
        }
    }
    
    /**
     * 搜索所有内容
     */
    async searchAll(query) {
        const searchPromises = [
            this.searchCaregivers(query),
            this.searchServices(query),
            this.searchAppointments(query),
            this.searchEmployments(query)
        ];
        
        const results = await Promise.all(searchPromises);
        
        return {
            caregivers: results[0],
            services: results[1],
            appointments: results[2],
            employments: results[3],
            total: results.reduce((sum, arr) => sum + arr.length, 0)
        };
    }
    
    /**
     * 搜索护工
     */
    async searchCaregivers(query) {
        try {
            const token = this.getUserToken();
            if (!token) return [];
            
            const response = await fetch(`/api/caregivers/search?q=${encodeURIComponent(query)}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                return data.success ? data.data : [];
            }
        } catch (error) {
            console.error('搜索护工失败:', error);
        }
        return [];
    }
    
    /**
     * 搜索服务
     */
    async searchServices(query) {
        try {
            const token = this.getUserToken();
            if (!token) return [];
            
            const response = await fetch(`/api/services/search?q=${encodeURIComponent(query)}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                return data.success ? data.data : [];
            }
        } catch (error) {
            console.error('搜索服务失败:', error);
        }
        return [];
    }
    
    /**
     * 搜索预约
     */
    async searchAppointments(query) {
        try {
            const token = this.getUserToken();
            if (!token) return [];
            
            const response = await fetch(`/api/user/appointments/search?q=${encodeURIComponent(query)}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                return data.success ? data.data : [];
            }
        } catch (error) {
            console.error('搜索预约失败:', error);
        }
        return [];
    }
    
    /**
     * 搜索聘用
     */
    async searchEmployments(query) {
        try {
            const token = this.getUserToken();
            if (!token) return [];
            
            const response = await fetch(`/api/user/employments/search?q=${encodeURIComponent(query)}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                return data.success ? data.data : [];
            }
        } catch (error) {
            console.error('搜索聘用失败:', error);
        }
        return [];
    }
    
    /**
     * 显示搜索结果
     */
    displaySearchResults(results) {
        this.hideSearchSuggestions();
        
        if (results.total === 0) {
            this.showNoResults();
            return;
        }
        
        // 创建搜索结果模态框
        this.showSearchResultsModal(results);
    }
    
    /**
     * 显示搜索结果模态框
     */
    showSearchResultsModal(results) {
        const modal = document.createElement('div');
        modal.id = 'search-results-modal';
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[80vh] overflow-hidden">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-semibold">搜索结果</h3>
                    <button onclick="this.closest('.fixed').remove()" class="text-gray-400 hover:text-gray-600">
                        <i class="fa fa-times"></i>
                    </button>
                </div>
                
                <div class="mb-4">
                    <p class="text-sm text-gray-600">找到 ${results.total} 个相关结果</p>
                </div>
                
                <div class="overflow-y-auto max-h-96">
                    ${this.generateSearchResultsHTML(results)}
                </div>
                
                <div class="flex gap-3 mt-4">
                    <button onclick="this.closest('.fixed').remove()" 
                            class="flex-1 border border-gray-300 text-gray-700 hover:bg-gray-50 px-4 py-2 rounded-lg transition-colors">
                        关闭
                    </button>
                    <button onclick="window.UserSearchManager.clearSearch()" 
                            class="flex-1 bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-lg transition-colors">
                        清空搜索
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    /**
     * 生成搜索结果HTML
     */
    generateSearchResultsHTML(results) {
        let html = '';
        
        // 用户结果
        if (results.caregivers.length > 0) {
            html += `
                <div class="mb-6">
                    <h4 class="font-semibold text-gray-800 mb-3">护工 (${results.caregivers.length})</h4>
                    <div class="space-y-3">
                        ${results.caregivers.map(caregiver => `
                            <div class="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                                 onclick="window.UserSearchManager.viewCaregiver(${caregiver.id})">
                                <img src="${window.AvatarManager ? window.AvatarManager.getAvatarUrl(caregiver.avatar_url, 'caregiver', 'small') : '/uploads/avatars/default-caregiver.png'}" 
                                     alt="${caregiver.name}" 
                                     class="w-10 h-10 rounded-full object-cover">
                                <div class="flex-1">
                                    <div class="font-medium">${caregiver.name}</div>
                                    <div class="text-sm text-gray-500">${caregiver.experience_years}年经验 · ¥${caregiver.hourly_rate}/小时</div>
                                </div>
                                <i class="fa fa-arrow-right text-gray-400"></i>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        // 服务结果
        if (results.services.length > 0) {
            html += `
                <div class="mb-6">
                    <h4 class="font-semibold text-gray-800 mb-3">服务 (${results.services.length})</h4>
                    <div class="space-y-3">
                        ${results.services.map(service => `
                            <div class="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                                 onclick="window.UserSearchManager.viewService('${service.id}')">
                                <div class="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                                    <i class="fa fa-heart text-primary"></i>
                                </div>
                                <div class="flex-1">
                                    <div class="font-medium">${service.name}</div>
                                    <div class="text-sm text-gray-500">${service.description}</div>
                                </div>
                                <i class="fa fa-arrow-right text-gray-400"></i>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        // 预约结果
        if (results.appointments.length > 0) {
            html += `
                <div class="mb-6">
                    <h4 class="font-semibold text-gray-800 mb-3">预约 (${results.appointments.length})</h4>
                    <div class="space-y-3">
                        ${results.appointments.map(appointment => `
                            <div class="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                                 onclick="window.UserSearchManager.viewAppointment(${appointment.id})">
                                <div class="w-10 h-10 bg-secondary/10 rounded-full flex items-center justify-center">
                                    <i class="fa fa-calendar text-secondary"></i>
                                </div>
                                <div class="flex-1">
                                    <div class="font-medium">${appointment.service_type}</div>
                                    <div class="text-sm text-gray-500">${appointment.date} ${appointment.start_time}</div>
                                </div>
                                <i class="fa fa-arrow-right text-gray-400"></i>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        // 聘用结果
        if (results.employments.length > 0) {
            html += `
                <div class="mb-6">
                    <h4 class="font-semibold text-gray-800 mb-3">聘用 (${results.employments.length})</h4>
                    <div class="space-y-3">
                        ${results.employments.map(employment => `
                            <div class="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                                 onclick="window.UserSearchManager.viewEmployment(${employment.id})">
                                <div class="w-10 h-10 bg-accent/10 rounded-full flex items-center justify-center">
                                    <i class="fa fa-handshake text-accent"></i>
                                </div>
                                <div class="flex-1">
                                    <div class="font-medium">${employment.caregiver_name}</div>
                                    <div class="text-sm text-gray-500">${employment.service_type} · ${employment.status}</div>
                                </div>
                                <i class="fa fa-arrow-right text-gray-400"></i>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        return html;
    }
    
    /**
     * 显示搜索建议
     */
    showSearchSuggestions() {
        if (this.searchHistory.length === 0) return;
        
        const suggestions = document.createElement('div');
        suggestions.id = 'search-suggestions';
        suggestions.className = 'absolute top-full left-0 right-0 bg-white border border-gray-200 rounded-lg shadow-lg z-50 mt-1';
        
        suggestions.innerHTML = `
            <div class="p-2">
                <div class="text-xs text-gray-500 mb-2">搜索历史</div>
                ${this.searchHistory.slice(0, 5).map(query => `
                    <div class="px-3 py-2 hover:bg-gray-50 cursor-pointer rounded text-sm"
                         onclick="window.UserSearchManager.searchFromHistory('${query}')">
                        <i class="fa fa-history text-gray-400 mr-2"></i>${query}
                    </div>
                `).join('')}
            </div>
        `;
        
        this.searchInput.parentElement.appendChild(suggestions);
    }
    
    /**
     * 隐藏搜索建议
     */
    hideSearchSuggestions() {
        const suggestions = document.getElementById('search-suggestions');
        if (suggestions) {
            suggestions.remove();
        }
    }
    
    /**
     * 显示搜索加载状态
     */
    showSearchLoading() {
        // 可以在这里添加加载指示器
        console.log('正在搜索...');
    }
    
    /**
     * 显示搜索错误
     */
    showSearchError(message) {
        this.showNotification(message, 'error');
    }
    
    /**
     * 显示无结果
     */
    showNoResults() {
        this.showNotification('未找到相关结果', 'info');
    }
    
    /**
     * 从历史记录搜索
     */
    searchFromHistory(query) {
        this.searchInput.value = query;
        this.performSearch(query);
        this.hideSearchSuggestions();
    }
    
    /**
     * 清空搜索
     */
    clearSearch() {
        this.searchInput.value = '';
        this.hideSearchSuggestions();
        this.searchInput.focus();
    }
    
    /**
     * 查看护工详情
     */
    viewCaregiver(caregiverId) {
        window.location.href = `/user/caregivers?id=${caregiverId}&view=detail`;
    }
    
    /**
     * 查看服务详情
     */
    viewService(serviceId) {
        window.location.href = `/user/services?id=${serviceId}`;
    }
    
    /**
     * 查看预约详情
     */
    viewAppointment(appointmentId) {
        window.location.href = `/user/appointments?id=${appointmentId}&view=detail`;
    }
    
    /**
     * 查看聘用详情
     */
    viewEmployment(employmentId) {
        window.location.href = `/user/employments?id=${employmentId}&view=detail`;
    }
    
    /**
     * 添加到搜索历史
     */
    addToSearchHistory(query) {
        if (!query || query.length < 2) return;
        
        // 移除重复项
        this.searchHistory = this.searchHistory.filter(item => item !== query);
        
        // 添加到开头
        this.searchHistory.unshift(query);
        
        // 限制历史记录数量
        if (this.searchHistory.length > 10) {
            this.searchHistory = this.searchHistory.slice(0, 10);
        }
        
        // 保存到本地存储
        localStorage.setItem('user_search_history', JSON.stringify(this.searchHistory));
    }
    
    /**
     * 加载搜索历史
     */
    loadSearchHistory() {
        try {
            const history = localStorage.getItem('user_search_history');
            if (history) {
                this.searchHistory = JSON.parse(history);
            }
        } catch (error) {
            console.error('加载搜索历史失败:', error);
        }
    }
    
    /**
     * 获取用户令牌
     */
    getUserToken() {
        return localStorage.getItem('user_token') || 
               document.cookie.split('; ').find(row => row.startsWith('user_token='))?.split('=')[1];
    }
    
    /**
     * 显示通知
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 max-w-sm ${
            type === 'error' ? 'bg-red-500 text-white' :
            type === 'success' ? 'bg-green-500 text-white' :
            'bg-blue-500 text-white'
        }`;
        
        notification.innerHTML = `
            <div class="flex items-center gap-2">
                <i class="fa fa-${type === 'error' ? 'times-circle' : type === 'success' ? 'check-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// 创建全局实例
window.UserSearchManager = new UserSearchManager();

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    window.UserSearchManager.init();
});
