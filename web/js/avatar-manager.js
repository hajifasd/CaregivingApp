/**
 * 头像管理器 - 统一处理头像URL
 * ====================================
 * 
 * 避免硬编码头像URL，提供默认头像和头像处理功能
 */

class AvatarManager {
    constructor() {
        // 默认头像配置
        this.defaultAvatars = {
            user: '/uploads/avatars/default-user.png',
            caregiver: '/uploads/avatars/default-caregiver.png',
            admin: '/uploads/avatars/default-admin.png',
            placeholder: '/uploads/avatars/default-placeholder.png'
        };
        
        // 头像尺寸配置
        this.avatarSizes = {
            small: { width: 40, height: 40 },
            medium: { width: 80, height: 80 },
            large: { width: 120, height: 120 },
            xlarge: { width: 200, height: 200 }
        };
    }
    
    /**
     * 获取头像URL，如果为空则返回默认头像
     * @param {string} avatarUrl 原始头像URL
     * @param {string} userType 用户类型 (user, caregiver, admin)
     * @param {string} size 头像尺寸 (small, medium, large, xlarge)
     * @returns {string} 处理后的头像URL
     */
    getAvatarUrl(avatarUrl, userType = 'user', size = 'medium') {
        // 如果有真实头像URL，直接返回
        if (avatarUrl && avatarUrl.trim() && !this.isPlaceholderUrl(avatarUrl)) {
            return avatarUrl;
        }
        
        // 返回默认头像
        const defaultAvatar = this.defaultAvatars[userType] || this.defaultAvatars.placeholder;
        return defaultAvatar;
    }
    
    /**
     * 检查是否为占位符URL
     * @param {string} url 头像URL
     * @returns {boolean} 是否为占位符
     */
    isPlaceholderUrl(url) {
        if (!url) return true;
        
        // 检查常见的占位符URL
        const placeholderPatterns = [
            'picsum.photos',
            'placeholder.com',
            'via.placeholder.com',
            'dummyimage.com',
            'lorempixel.com'
        ];
        
        return placeholderPatterns.some(pattern => url.includes(pattern));
    }
    
    /**
     * 生成头像HTML
     * @param {string} avatarUrl 头像URL
     * @param {string} alt 替代文本
     * @param {string} userType 用户类型
     * @param {string} size 尺寸
     * @param {string} cssClass 额外的CSS类
     * @returns {string} 头像HTML
     */
    generateAvatarHtml(avatarUrl, alt = '头像', userType = 'user', size = 'medium', cssClass = '') {
        const url = this.getAvatarUrl(avatarUrl, userType, size);
        const sizeConfig = this.avatarSizes[size];
        
        return `<img src="${url}" alt="${alt}" class="rounded-full object-cover ${cssClass}" 
                style="width: ${sizeConfig.width}px; height: ${sizeConfig.height}px;"
                onerror="this.src='${this.defaultAvatars.placeholder}'">`;
    }
    
    /**
     * 更新页面中的头像
     * @param {string} selector 选择器
     * @param {string} avatarUrl 新头像URL
     * @param {string} userType 用户类型
     */
    updateAvatar(selector, avatarUrl, userType = 'user') {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            const newUrl = this.getAvatarUrl(avatarUrl, userType);
            element.src = newUrl;
        });
    }
    
    /**
     * 批量处理头像URL
     * @param {Array} items 包含avatar_url字段的对象数组
     * @param {string} userType 用户类型
     * @returns {Array} 处理后的数组
     */
    processAvatarUrls(items, userType = 'user') {
        return items.map(item => ({
            ...item,
            avatar_url: this.getAvatarUrl(item.avatar_url, userType),
            avatar: this.getAvatarUrl(item.avatar_url, userType) // 兼容不同字段名
        }));
    }
    
    /**
     * 上传头像
     * @param {File} file 头像文件
     * @param {string} userType 用户类型
     * @param {string} userId 用户ID
     * @returns {Promise} 上传结果
     */
    async uploadAvatar(file, userType = 'user', userId = null) {
        try {
            // 验证文件类型
            if (!this.validateImageFile(file)) {
                throw new Error('不支持的文件类型');
            }
            
            // 压缩图片
            const compressedFile = await this.compressImage(file);
            
            // 创建FormData
            const formData = new FormData();
            formData.append('avatar', compressedFile);
            formData.append('user_type', userType);
            if (userId) formData.append('user_id', userId);
            
            // 上传文件
            const response = await fetch('/api/upload/avatar', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                return {
                    success: true,
                    avatarUrl: result.data.avatar_url,
                    message: '头像上传成功'
                };
            } else {
                throw new Error(result.message || '上传失败');
            }
            
        } catch (error) {
            console.error('头像上传失败:', error);
            return {
                success: false,
                message: error.message || '头像上传失败'
            };
        }
    }
    
    /**
     * 验证图片文件
     * @param {File} file 文件对象
     * @returns {boolean} 是否有效
     */
    validateImageFile(file) {
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
        const maxSize = 5 * 1024 * 1024; // 5MB
        
        if (!allowedTypes.includes(file.type)) {
            return false;
        }
        
        if (file.size > maxSize) {
            return false;
        }
        
        return true;
    }
    
    /**
     * 压缩图片
     * @param {File} file 原始文件
     * @param {number} maxWidth 最大宽度
     * @param {number} maxHeight 最大高度
     * @param {number} quality 压缩质量
     * @returns {Promise<File>} 压缩后的文件
     */
    async compressImage(file, maxWidth = 400, maxHeight = 400, quality = 0.8) {
        return new Promise((resolve) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            img.onload = () => {
                // 计算压缩后的尺寸
                let { width, height } = img;
                
                if (width > height) {
                    if (width > maxWidth) {
                        height = (height * maxWidth) / width;
                        width = maxWidth;
                    }
                } else {
                    if (height > maxHeight) {
                        width = (width * maxHeight) / height;
                        height = maxHeight;
                    }
                }
                
                canvas.width = width;
                canvas.height = height;
                
                // 绘制压缩后的图片
                ctx.drawImage(img, 0, 0, width, height);
                
                // 转换为Blob
                canvas.toBlob((blob) => {
                    const compressedFile = new File([blob], file.name, {
                        type: file.type,
                        lastModified: Date.now()
                    });
                    resolve(compressedFile);
                }, file.type, quality);
            };
            
            img.src = URL.createObjectURL(file);
        });
    }
    
    /**
     * 设置默认头像
     * @param {string} userType 用户类型
     * @param {string} avatarUrl 头像URL
     */
    setDefaultAvatar(userType, avatarUrl) {
        if (this.defaultAvatars[userType]) {
            this.defaultAvatars[userType] = avatarUrl;
        }
    }
    
    /**
     * 获取头像缓存键
     * @param {string} avatarUrl 头像URL
     * @returns {string} 缓存键
     */
    getCacheKey(avatarUrl) {
        return `avatar_${btoa(avatarUrl).replace(/[^a-zA-Z0-9]/g, '')}`;
    }
    
    /**
     * 缓存头像
     * @param {string} avatarUrl 头像URL
     * @param {string} dataUrl 头像数据URL
     */
    cacheAvatar(avatarUrl, dataUrl) {
        try {
            const cacheKey = this.getCacheKey(avatarUrl);
            localStorage.setItem(cacheKey, dataUrl);
        } catch (error) {
            console.warn('头像缓存失败:', error);
        }
    }
    
    /**
     * 获取缓存的头像
     * @param {string} avatarUrl 头像URL
     * @returns {string|null} 缓存的头像数据URL
     */
    getCachedAvatar(avatarUrl) {
        try {
            const cacheKey = this.getCacheKey(avatarUrl);
            return localStorage.getItem(cacheKey);
        } catch (error) {
            return null;
        }
    }
    
    /**
     * 清除头像缓存
     * @param {string} avatarUrl 头像URL（可选）
     */
    clearAvatarCache(avatarUrl = null) {
        try {
            if (avatarUrl) {
                const cacheKey = this.getCacheKey(avatarUrl);
                localStorage.removeItem(cacheKey);
            } else {
                // 清除所有头像缓存
                const keys = Object.keys(localStorage);
                keys.forEach(key => {
                    if (key.startsWith('avatar_')) {
                        localStorage.removeItem(key);
                    }
                });
            }
        } catch (error) {
            console.warn('清除头像缓存失败:', error);
        }
    }
    
    /**
     * 预加载头像
     * @param {string} avatarUrl 头像URL
     * @returns {Promise} 预加载结果
     */
    async preloadAvatar(avatarUrl) {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => {
                // 缓存头像
                this.cacheAvatar(avatarUrl, img.src);
                resolve(true);
            };
            img.onerror = () => resolve(false);
            img.src = avatarUrl;
        });
    }
    
    /**
     * 批量预加载头像
     * @param {Array} avatarUrls 头像URL数组
     */
    async preloadAvatars(avatarUrls) {
        const promises = avatarUrls.map(url => this.preloadAvatar(url));
        await Promise.all(promises);
    }
    
    /**
     * 创建头像上传组件
     * @param {Object} options 配置选项
     * @returns {AvatarUpload} 上传组件实例
     */
    createUploadComponent(options = {}) {
        if (typeof window.AvatarUpload === 'undefined') {
            console.error('AvatarUpload组件未加载，请先引入avatar-upload.js');
            return null;
        }
        
        return new window.AvatarUpload({
            userType: this.options.userType || 'user',
            userId: this.options.userId || null,
            size: this.options.size || 'medium',
            ...options
        });
    }
    
    /**
     * 批量更新页面中的头像
     * @param {Array} selectors 选择器数组
     * @param {string} avatarUrl 新头像URL
     * @param {string} userType 用户类型
     */
    batchUpdateAvatars(selectors, avatarUrl, userType = 'user') {
        selectors.forEach(selector => {
            this.updateAvatar(selector, avatarUrl, userType);
        });
    }
    
    /**
     * 获取头像统计信息
     * @returns {Object} 统计信息
     */
    getAvatarStats() {
        const keys = Object.keys(localStorage);
        const avatarKeys = keys.filter(key => key.startsWith('avatar_'));
        
        return {
            cachedCount: avatarKeys.length,
            cacheSize: this.calculateCacheSize(avatarKeys),
            defaultAvatars: Object.keys(this.defaultAvatars).length
        };
    }
    
    /**
     * 计算缓存大小
     * @param {Array} keys 缓存键数组
     * @returns {number} 缓存大小（字节）
     */
    calculateCacheSize(keys) {
        let totalSize = 0;
        keys.forEach(key => {
            const value = localStorage.getItem(key);
            if (value) {
                totalSize += key.length + value.length;
            }
        });
        return totalSize;
    }
    
    /**
     * 优化缓存（清理过期或无效的缓存）
     */
    optimizeCache() {
        const keys = Object.keys(localStorage);
        const avatarKeys = keys.filter(key => key.startsWith('avatar_'));
        let cleanedCount = 0;
        
        avatarKeys.forEach(key => {
            const value = localStorage.getItem(key);
            if (!value || value.length < 100) { // 太小的数据可能是无效的
                localStorage.removeItem(key);
                cleanedCount++;
            }
        });
        
        return cleanedCount;
    }
    
    /**
     * 获取所有默认头像
     * @returns {Object} 默认头像对象
     */
    getAllDefaultAvatars() {
        return { ...this.defaultAvatars };
    }
    
    /**
     * 设置自定义默认头像
     * @param {Object} customAvatars 自定义头像对象
     */
    setCustomDefaultAvatars(customAvatars) {
        Object.assign(this.defaultAvatars, customAvatars);
    }
    
    /**
     * 导出头像配置
     * @returns {Object} 配置对象
     */
    exportConfig() {
        return {
            defaultAvatars: this.defaultAvatars,
            avatarSizes: this.avatarSizes,
            stats: this.getAvatarStats()
        };
    }
    
    /**
     * 导入头像配置
     * @param {Object} config 配置对象
     */
    importConfig(config) {
        if (config.defaultAvatars) {
            this.setCustomDefaultAvatars(config.defaultAvatars);
        }
        
        if (config.avatarSizes) {
            Object.assign(this.avatarSizes, config.avatarSizes);
        }
    }
}

// 创建全局实例
window.AvatarManager = new AvatarManager();
