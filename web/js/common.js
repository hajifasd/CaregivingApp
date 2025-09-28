/**
 * 通用JavaScript功能
 */

// 配置Tailwind CSS主题
if (typeof tailwind !== 'undefined') {
    tailwind.config = {
        theme: {
            extend: {
                colors: {
                    primary: '#165DFF',
                    secondary: '#36CFC9',
                    accent: '#722ED1',
                    neutral: '#F5F7FA',
                    'neutral-dark': '#4E5969',
                    success: '#52C41A',
                    warning: '#FAAD14',
                    danger: '#FF4D4F',
                },
                fontFamily: {
                    inter: ['Inter', 'system-ui', 'sans-serif'],
                },
            }
        }
    };
}

// 通用工具函数
const Utils = {
    /**
     * 格式化日期
     * @param {Date|string} date 日期
     * @param {string} format 格式
     * @returns {string} 格式化后的日期
     */
    formatDate(date, format = 'YYYY-MM-DD') {
        const d = new Date(date);
        if (isNaN(d.getTime())) return '';
        
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        const seconds = String(d.getSeconds()).padStart(2, '0');
        
        return format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day)
            .replace('HH', hours)
            .replace('mm', minutes)
            .replace('ss', seconds);
    },
    
    /**
     * 格式化时间
     * @param {Date|string} date 日期
     * @returns {string} 相对时间
     */
    formatRelativeTime(date) {
        const now = new Date();
        const target = new Date(date);
        const diff = now - target;
        
        const minute = 60 * 1000;
        const hour = 60 * minute;
        const day = 24 * hour;
        const week = 7 * day;
        const month = 30 * day;
        const year = 365 * day;
        
        if (diff < minute) return '刚刚';
        if (diff < hour) return `${Math.floor(diff / minute)}分钟前`;
        if (diff < day) return `${Math.floor(diff / hour)}小时前`;
        if (diff < week) return `${Math.floor(diff / day)}天前`;
        if (diff < month) return `${Math.floor(diff / week)}周前`;
        if (diff < year) return `${Math.floor(diff / month)}个月前`;
        return `${Math.floor(diff / year)}年前`;
    },
    
    /**
     * 格式化数字
     * @param {number} num 数字
     * @param {number} decimals 小数位数
     * @returns {string} 格式化后的数字
     */
    formatNumber(num, decimals = 0) {
        if (typeof num !== 'number' || isNaN(num)) return '0';
        
        if (decimals > 0) {
            return num.toFixed(decimals);
        }
        
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        
        return num.toString();
    },
    
    /**
     * 防抖函数
     * @param {Function} func 函数
     * @param {number} wait 等待时间
     * @returns {Function} 防抖后的函数
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * 节流函数
     * @param {Function} func 函数
     * @param {number} limit 限制时间
     * @returns {Function} 节流后的函数
     */
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    /**
     * 深拷贝对象
     * @param {*} obj 要拷贝的对象
     * @returns {*} 拷贝后的对象
     */
    deepClone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj.getTime());
        if (obj instanceof Array) return obj.map(item => this.deepClone(item));
        if (typeof obj === 'object') {
            const clonedObj = {};
            for (const key in obj) {
                if (obj.hasOwnProperty(key)) {
                    clonedObj[key] = this.deepClone(obj[key]);
                }
            }
            return clonedObj;
        }
    },
    
    /**
     * 生成唯一ID
     * @returns {string} 唯一ID
     */
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    },
    
    /**
     * 验证邮箱格式
     * @param {string} email 邮箱
     * @returns {boolean} 是否有效
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },
    
    /**
     * 验证手机号格式
     * @param {string} phone 手机号
     * @returns {boolean} 是否有效
     */
    isValidPhone(phone) {
        const phoneRegex = /^1[3-9]\d{9}$/;
        return phoneRegex.test(phone);
    },
    
    /**
     * 获取文件扩展名
     * @param {string} filename 文件名
     * @returns {string} 扩展名
     */
    getFileExtension(filename) {
        return filename.slice((filename.lastIndexOf('.') - 1 >>> 0) + 2);
    },
    
    /**
     * 格式化文件大小
     * @param {number} bytes 字节数
     * @returns {string} 格式化后的大小
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
};

// 本地存储管理
const Storage = {
    /**
     * 设置本地存储
     * @param {string} key 键
     * @param {*} value 值
     * @param {number} ttl 过期时间（秒）
     */
    set(key, value, ttl = null) {
        const item = {
            value: value,
            timestamp: Date.now()
        };
        
        if (ttl) {
            item.expires = Date.now() + (ttl * 1000);
        }
        
        localStorage.setItem(key, JSON.stringify(item));
    },
    
    /**
     * 获取本地存储
     * @param {string} key 键
     * @param {*} defaultValue 默认值
     * @returns {*} 存储的值
     */
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            if (!item) return defaultValue;
            
            const data = JSON.parse(item);
            
            // 检查是否过期
            if (data.expires && Date.now() > data.expires) {
                localStorage.removeItem(key);
                return defaultValue;
            }
            
            return data.value;
        } catch (error) {
            console.error('Error reading from localStorage:', error);
            return defaultValue;
        }
    },
    
    /**
     * 删除本地存储
     * @param {string} key 键
     */
    remove(key) {
        localStorage.removeItem(key);
    },
    
    /**
     * 清空本地存储
     */
    clear() {
        localStorage.clear();
    },
    
    /**
     * 检查键是否存在
     * @param {string} key 键
     * @returns {boolean} 是否存在
     */
    has(key) {
        return localStorage.getItem(key) !== null;
    }
};

// 网络请求管理
const Http = {
    /**
     * 发送GET请求
     * @param {string} url 请求URL
     * @param {Object} options 请求选项
     * @returns {Promise} 请求结果
     */
    async get(url, options = {}) {
        return this.request(url, { ...options, method: 'GET' });
    },
    
    /**
     * 发送POST请求
     * @param {string} url 请求URL
     * @param {Object} data 请求数据
     * @param {Object} options 请求选项
     * @returns {Promise} 请求结果
     */
    async post(url, data = {}, options = {}) {
        return this.request(url, { ...options, method: 'POST', body: JSON.stringify(data) });
    },
    
    /**
     * 发送PUT请求
     * @param {string} url 请求URL
     * @param {Object} data 请求数据
     * @param {Object} options 请求选项
     * @returns {Promise} 请求结果
     */
    async put(url, data = {}, options = {}) {
        return this.request(url, { ...options, method: 'PUT', body: JSON.stringify(data) });
    },
    
    /**
     * 发送DELETE请求
     * @param {string} url 请求URL
     * @param {Object} options 请求选项
     * @returns {Promise} 请求结果
     */
    async delete(url, options = {}) {
        return this.request(url, { ...options, method: 'DELETE' });
    },
    
    /**
     * 发送请求
     * @param {string} url 请求URL
     * @param {Object} options 请求选项
     * @returns {Promise} 请求结果
     */
    async request(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include'
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        
        // 添加认证token
        const token = AuthManager?.getToken();
        if (token) {
            finalOptions.headers['Authorization'] = `Bearer ${token}`;
        }
        
        try {
            const response = await fetch(url, finalOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();
        } catch (error) {
            console.error('Request failed:', error);
            throw error;
        }
    }
};

// 页面初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化UI管理器
    if (typeof UIManager !== 'undefined') {
        UIManager.init();
    }
    
    // 初始化导航管理器
    if (typeof NavigationManager !== 'undefined') {
        NavigationManager.onPageLoad();
    }
    
    // 设置当前日期
    const currentDateElement = document.getElementById('current-date');
    if (currentDateElement) {
        const now = new Date();
        const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };
        currentDateElement.textContent = now.toLocaleDateString('zh-CN', options);
    }
    
    // 检查用户登录状态
    if (typeof AuthManager !== 'undefined') {
        AuthManager.checkLogin();
        AuthManager.updateUI();
    }
    
    // 绑定全局事件
    bindGlobalEvents();
});

// 绑定全局事件
function bindGlobalEvents() {
    // 返回顶部按钮
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        backToTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
        
        // 滚动时显示/隐藏按钮
        window.addEventListener('scroll', Utils.throttle(() => {
            if (window.pageYOffset > 300) {
                backToTopBtn.classList.remove('hidden');
            } else {
                backToTopBtn.classList.add('hidden');
            }
        }, 100));
    }
    
    // 搜索功能
    const searchInput = document.querySelector('input[placeholder*="搜索"]');
    if (searchInput) {
        searchInput.addEventListener('input', Utils.debounce((e) => {
            const query = e.target.value.trim();
            if (query.length > 0) {
                performSearch(query);
            } else {
                clearSearchResults();
            }
        }, 300));
    }
}

// 搜索功能实现
async function performSearch(query) {
    try {
        console.log('正在搜索:', query);
        
        // 根据当前页面类型执行不同的搜索
        const currentPath = window.location.pathname;
        
        if (currentPath.includes('/user/caregivers') || currentPath.includes('/caregiver')) {
            await searchCaregivers(query);
        } else if (currentPath.includes('/user/messages')) {
            await searchMessages(query);
        } else if (currentPath.includes('/admin')) {
            await searchAdminData(query);
        } else {
            // 通用搜索
            await performGeneralSearch(query);
        }
    } catch (error) {
        console.error('搜索失败:', error);
        showSearchError('搜索失败，请稍后重试');
    }
}

// 搜索护工
async function searchCaregivers(query) {
    try {
        const response = await fetch(`/api/caregiver/search?keyword=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.success) {
            displaySearchResults(data.data, 'caregiver');
        } else {
            showSearchError(data.message || '搜索失败');
        }
    } catch (error) {
        console.error('护工搜索失败:', error);
        showSearchError('护工搜索失败');
    }
}

// 搜索消息
async function searchMessages(query) {
    try {
        const token = localStorage.getItem('user_token') || getCookie('user_token');
        if (!token) {
            showSearchError('请先登录');
            return;
        }
        
        const response = await fetch(`/api/chat/search?keyword=${encodeURIComponent(query)}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        const data = await response.json();
        
        if (data.success) {
            displaySearchResults(data.data, 'message');
        } else {
            showSearchError(data.message || '消息搜索失败');
        }
    } catch (error) {
        console.error('消息搜索失败:', error);
        showSearchError('消息搜索失败');
    }
}

// 管理员数据搜索
async function searchAdminData(query) {
    try {
        const token = localStorage.getItem('admin_token') || getCookie('admin_token');
        if (!token) {
            showSearchError('请先登录管理员账户');
            return;
        }
        
        const response = await fetch(`/api/admin/search?keyword=${encodeURIComponent(query)}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        const data = await response.json();
        
        if (data.success) {
            displaySearchResults(data.data, 'admin');
        } else {
            showSearchError(data.message || '搜索失败');
        }
    } catch (error) {
        console.error('管理员搜索失败:', error);
        showSearchError('搜索失败');
    }
}

// 通用搜索
async function performGeneralSearch(query) {
    try {
        const response = await fetch(`/api/search?keyword=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.success) {
            displaySearchResults(data.data, 'general');
        } else {
            showSearchError(data.message || '搜索失败');
        }
    } catch (error) {
        console.error('通用搜索失败:', error);
        showSearchError('搜索失败');
    }
}

// 显示搜索结果
function displaySearchResults(results, type) {
    // 移除现有的搜索结果
    clearSearchResults();
    
    if (!results || results.length === 0) {
        showSearchMessage('未找到相关结果');
        return;
    }
    
    // 创建搜索结果容器
    const searchContainer = document.createElement('div');
    searchContainer.id = 'search-results';
    searchContainer.className = 'search-results-container';
    
    // 根据类型显示不同的结果
    switch (type) {
        case 'caregiver':
            searchContainer.innerHTML = results.map(caregiver => `
                <div class="search-result-item caregiver-result">
                    <div class="result-avatar">
                        <img src="${window.AvatarManager.getAvatarUrl(caregiver.avatar_url, 'caregiver', 'small')}" alt="${caregiver.name}">
                    </div>
                    <div class="result-info">
                        <h4>${caregiver.name}</h4>
                        <p>${caregiver.phone}</p>
                        <p>${caregiver.experience_years}年经验</p>
                        <span class="result-rating">评分: ${caregiver.rating || '5.0'}</span>
                    </div>
                    <div class="result-actions">
                        <button onclick="viewCaregiver(${caregiver.id})" class="btn-primary">查看详情</button>
                    </div>
                </div>
            `).join('');
            break;
            
        case 'message':
            searchContainer.innerHTML = results.map(message => `
                <div class="search-result-item message-result">
                    <div class="result-info">
                        <h4>${message.sender_name}</h4>
                        <p>${message.content}</p>
                        <span class="result-time">${formatTime(message.created_at)}</span>
                    </div>
                </div>
            `).join('');
            break;
            
        default:
            searchContainer.innerHTML = results.map(item => `
                <div class="search-result-item general-result">
                    <div class="result-info">
                        <h4>${item.title || item.name || '搜索结果'}</h4>
                        <p>${item.description || item.content || ''}</p>
                    </div>
                </div>
            `).join('');
    }
    
    // 插入到页面中
    const searchInput = document.querySelector('input[placeholder*="搜索"]');
    if (searchInput) {
        searchInput.parentNode.appendChild(searchContainer);
    }
}

// 清除搜索结果
function clearSearchResults() {
    const existingResults = document.getElementById('search-results');
    if (existingResults) {
        existingResults.remove();
    }
}

// 显示搜索消息
function showSearchMessage(message) {
    clearSearchResults();
    
    const messageDiv = document.createElement('div');
    messageDiv.id = 'search-results';
    messageDiv.className = 'search-results-container';
    messageDiv.innerHTML = `
        <div class="search-message">
            <p>${message}</p>
        </div>
    `;
    
    const searchInput = document.querySelector('input[placeholder*="搜索"]');
    if (searchInput) {
        searchInput.parentNode.appendChild(messageDiv);
    }
}

// 显示搜索错误
function showSearchError(message) {
    showSearchMessage(`<span class="error">${message}</span>`);
}

// 格式化时间
function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN');
}

// 获取cookie值
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// 导出到全局
window.Utils = Utils;
window.Storage = Storage;
window.Http = Http;
window.performSearch = performSearch;
window.clearSearchResults = clearSearchResults;
