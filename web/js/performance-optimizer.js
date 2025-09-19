/**
 * 前端性能优化工具
 * 包含图片懒加载、代码分割、缓存策略等优化功能
 */

class PerformanceOptimizer {
    constructor() {
        this.imageObserver = null;
        this.initialized = false;
    }

    /**
     * 初始化性能优化
     */
    init() {
        if (this.initialized) return;
        
        this.initImageLazyLoading();
        this.initCodeSplitting();
        this.initCaching();
        this.initDebouncing();
        this.initVirtualScrolling();
        
        this.initialized = true;
        console.log('✅ 前端性能优化已初始化');
    }

    /**
     * 图片懒加载
     */
    initImageLazyLoading() {
        if ('IntersectionObserver' in window) {
            this.imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        const src = img.dataset.src;
                        
                        if (src) {
                            img.src = src;
                            img.classList.remove('lazy');
                            img.classList.add('loaded');
                            this.imageObserver.unobserve(img);
                        }
                    }
                });
            }, {
                rootMargin: '50px 0px',
                threshold: 0.01
            });

            // 观察所有懒加载图片
            document.querySelectorAll('img[data-src]').forEach(img => {
                this.imageObserver.observe(img);
            });
        }
    }

    /**
     * 代码分割 - 动态加载模块
     */
    initCodeSplitting() {
        // 为按钮添加动态加载功能
        document.addEventListener('click', (e) => {
            const target = e.target.closest('[data-module]');
            if (target) {
                const moduleName = target.dataset.module;
                this.loadModule(moduleName);
            }
        });
    }

    /**
     * 加载模块
     */
    async loadModule(moduleName) {
        try {
            const module = await import(`./modules/${moduleName}.js`);
            if (module.default) {
                module.default.init();
            }
        } catch (error) {
            console.error(`加载模块 ${moduleName} 失败:`, error);
        }
    }

    /**
     * 缓存策略
     */
    initCaching() {
        // 本地存储缓存
        this.cache = new Map();
        
        // 为API请求添加缓存
        this.originalFetch = window.fetch;
        window.fetch = this.cachedFetch.bind(this);
    }

    /**
     * 带缓存的fetch
     */
    async cachedFetch(url, options = {}) {
        const cacheKey = `${url}_${JSON.stringify(options)}`;
        
        // 检查缓存
        if (this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < 300000) { // 5分钟缓存
                return new Response(JSON.stringify(cached.data), {
                    headers: { 'Content-Type': 'application/json' }
                });
            }
        }

        // 发起请求
        const response = await this.originalFetch(url, options);
        const data = await response.json();

        // 缓存响应
        this.cache.set(cacheKey, {
            data: data,
            timestamp: Date.now()
        });

        return new Response(JSON.stringify(data), {
            headers: { 'Content-Type': 'application/json' }
        });
    }

    /**
     * 防抖功能
     */
    initDebouncing() {
        // 为搜索输入框添加防抖
        document.querySelectorAll('input[type="search"], input[placeholder*="搜索"]').forEach(input => {
            let timeout;
            input.addEventListener('input', (e) => {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    // 触发搜索
                    if (typeof performSearch === 'function') {
                        performSearch(e.target.value);
                    }
                }, 300);
            });
        });
    }

    /**
     * 虚拟滚动
     */
    initVirtualScrolling() {
        // 为长列表添加虚拟滚动
        document.querySelectorAll('.virtual-scroll-container').forEach(container => {
            this.setupVirtualScroll(container);
        });
    }

    /**
     * 设置虚拟滚动
     */
    setupVirtualScroll(container) {
        const itemHeight = 50; // 每个项目的高度
        const visibleCount = Math.ceil(container.clientHeight / itemHeight);
        const buffer = 5; // 缓冲区

        let scrollTop = 0;
        let data = [];

        const updateVisibleItems = () => {
            const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - buffer);
            const endIndex = Math.min(data.length, startIndex + visibleCount + buffer * 2);

            // 更新可见项目
            const visibleItems = data.slice(startIndex, endIndex);
            this.renderVisibleItems(container, visibleItems, startIndex);
        };

        container.addEventListener('scroll', (e) => {
            scrollTop = e.target.scrollTop;
            updateVisibleItems();
        });
    }

    /**
     * 渲染可见项目
     */
    renderVisibleItems(container, items, startIndex) {
        const content = container.querySelector('.virtual-scroll-content');
        if (!content) return;

        content.innerHTML = items.map((item, index) => `
            <div class="virtual-scroll-item" style="height: 50px;">
                ${this.renderItem(item, startIndex + index)}
            </div>
        `).join('');
    }

    /**
     * 渲染单个项目
     */
    renderItem(item, index) {
        // 根据数据类型渲染不同的内容
        if (item.name) {
            return `<div class="item-name">${item.name}</div>`;
        } else if (item.content) {
            return `<div class="item-content">${item.content}</div>`;
        }
        return `<div class="item-default">项目 ${index + 1}</div>`;
    }

    /**
     * 预加载关键资源
     */
    preloadCriticalResources() {
        const criticalResources = [
            '/css/style.css',
            '/js/common.js',
            '/js/chat-manager.js'
        ];

        criticalResources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.href = resource;
            link.as = resource.endsWith('.css') ? 'style' : 'script';
            document.head.appendChild(link);
        });
    }

    /**
     * 压缩图片
     */
    compressImage(file, maxWidth = 800, quality = 0.8) {
        return new Promise((resolve) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();

            img.onload = () => {
                // 计算新尺寸
                let { width, height } = img;
                if (width > maxWidth) {
                    height = (height * maxWidth) / width;
                    width = maxWidth;
                }

                canvas.width = width;
                canvas.height = height;

                // 绘制压缩后的图片
                ctx.drawImage(img, 0, 0, width, height);

                // 转换为blob
                canvas.toBlob(resolve, 'image/jpeg', quality);
            };

            img.src = URL.createObjectURL(file);
        });
    }

    /**
     * 批量处理DOM操作
     */
    batchDOMOperations(operations) {
        requestAnimationFrame(() => {
            operations.forEach(operation => {
                if (typeof operation === 'function') {
                    operation();
                }
            });
        });
    }

    /**
     * 内存清理
     */
    cleanup() {
        if (this.imageObserver) {
            this.imageObserver.disconnect();
        }
        
        this.cache.clear();
        
        // 清理事件监听器
        document.removeEventListener('click', this.handleClick);
        
        this.initialized = false;
        console.log('🧹 性能优化器已清理');
    }
}

// 图片优化工具
class ImageOptimizer {
    /**
     * 创建响应式图片
     */
    static createResponsiveImage(src, alt, sizes = [320, 640, 1024]) {
        const picture = document.createElement('picture');
        
        sizes.forEach(size => {
            const source = document.createElement('source');
            source.media = `(max-width: ${size}px)`;
            source.srcset = `${src}?w=${size}`;
            picture.appendChild(source);
        });
        
        const img = document.createElement('img');
        img.src = src;
        img.alt = alt;
        img.loading = 'lazy';
        img.classList.add('responsive-image');
        
        picture.appendChild(img);
        return picture;
    }

    /**
     * 添加图片占位符
     */
    static addImagePlaceholder(container, width = 200, height = 200) {
        const placeholder = document.createElement('div');
        placeholder.className = 'image-placeholder';
        placeholder.style.cssText = `
            width: ${width}px;
            height: ${height}px;
            background: #f0f0f0;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
        `;
        placeholder.innerHTML = '<i class="fa fa-image"></i>';
        
        container.appendChild(placeholder);
        return placeholder;
    }
}

// 网络优化工具
class NetworkOptimizer {
    /**
     * 检测网络状态
     */
    static detectNetworkStatus() {
        if ('connection' in navigator) {
            const connection = navigator.connection;
            return {
                effectiveType: connection.effectiveType,
                downlink: connection.downlink,
                rtt: connection.rtt,
                saveData: connection.saveData
            };
        }
        return null;
    }

    /**
     * 根据网络状态调整策略
     */
    static adjustForNetworkStatus() {
        const networkInfo = this.detectNetworkStatus();
        
        if (networkInfo) {
            if (networkInfo.effectiveType === 'slow-2g' || networkInfo.effectiveType === '2g') {
                // 慢网络：减少图片质量，禁用动画
                document.body.classList.add('slow-network');
                this.enableDataSaver();
            } else if (networkInfo.saveData) {
                // 数据节省模式
                this.enableDataSaver();
            }
        }
    }

    /**
     * 启用数据节省模式
     */
    static enableDataSaver() {
        // 降低图片质量
        document.querySelectorAll('img').forEach(img => {
            if (img.src.includes('?')) {
                img.src += '&quality=50';
            } else {
                img.src += '?quality=50';
            }
        });

        // 禁用非关键动画
        document.body.classList.add('data-saver');
    }
}

// 初始化性能优化
document.addEventListener('DOMContentLoaded', () => {
    const optimizer = new PerformanceOptimizer();
    optimizer.init();
    
    // 预加载关键资源
    optimizer.preloadCriticalResources();
    
    // 网络优化
    NetworkOptimizer.adjustForNetworkStatus();
    
    // 导出到全局
    window.PerformanceOptimizer = optimizer;
    window.ImageOptimizer = ImageOptimizer;
    window.NetworkOptimizer = NetworkOptimizer;
});

// 页面卸载时清理
window.addEventListener('beforeunload', () => {
    if (window.PerformanceOptimizer) {
        window.PerformanceOptimizer.cleanup();
    }
});
