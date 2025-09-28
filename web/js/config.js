/**
 * 用户资源管理系统 - 前端配置
 * ====================================
 * 
 * 统一管理前端配置，避免硬编码
 */

// 服务器配置
const SERVER_CONFIG = {
    // 根据环境自动选择服务器地址
    get baseUrl() {
        // 开发环境
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:8000';
        }
        // 生产环境 - 使用当前域名
        return window.location.origin;
    },
    
    // WebSocket地址
    get socketUrl() {
        return this.baseUrl;
    },
    
    // API基础地址
    get apiUrl() {
        return this.baseUrl;
    },
    
    // Socket.IO连接配置
    get socketConfig() {
        return {
            transports: ['websocket', 'polling'],
            timeout: 10000,
            forceNew: true,
            reconnection: true,
            reconnectionAttempts: 5,
            reconnectionDelay: 1000,
            maxReconnectionAttempts: 5
        };
    },
    
    // 环境检测
    get isDevelopment() {
        return window.location.hostname === 'localhost' || 
               window.location.hostname === '127.0.0.1' ||
               window.location.hostname === '0.0.0.0';
    },
    
    get isProduction() {
        return !this.isDevelopment;
    },
    
    // 调试模式
    get debugMode() {
        return this.isDevelopment || localStorage.getItem('debug_mode') === 'true';
    },
    
    // 获取完整API URL
    getApiUrl(endpoint) {
        const baseUrl = this.apiUrl;
        const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
        return `${baseUrl}${cleanEndpoint}`;
    },
    
    // 获取完整Socket URL
    getSocketUrl() {
        return this.socketUrl;
    },
    
    // 连接状态检测
    checkConnection() {
        return new Promise((resolve) => {
            const testUrl = this.getApiUrl('/api/health');
            fetch(testUrl, { method: 'HEAD' })
                .then(() => resolve(true))
                .catch(() => resolve(false));
        });
    }
};

// Socket.IO连接管理器
class SocketManager {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = SERVER_CONFIG.socketConfig.maxReconnectionAttempts;
        this.reconnectInterval = null;
    }
    
    // 初始化连接
    init() {
        if (this.socket) {
            this.disconnect();
        }
        
        const socketUrl = SERVER_CONFIG.getSocketUrl();
        const config = SERVER_CONFIG.socketConfig;
        
        if (SERVER_CONFIG.debugMode) {
            console.log('🔌 初始化Socket.IO连接:', socketUrl);
            console.log('⚙️ 连接配置:', config);
        }
        
        this.socket = io(socketUrl, config);
        this.setupEventListeners();
    }
    
    // 设置事件监听器
    setupEventListeners() {
        this.socket.on('connect', () => {
            this.isConnected = true;
            this.reconnectAttempts = 0;
            if (SERVER_CONFIG.debugMode) {
                console.log('✅ Socket.IO连接成功');
            }
            this.onConnect();
        });
        
        this.socket.on('disconnect', (reason) => {
            this.isConnected = false;
            if (SERVER_CONFIG.debugMode) {
                console.log('❌ Socket.IO连接断开:', reason);
            }
            this.onDisconnect(reason);
        });
        
        this.socket.on('connect_error', (error) => {
            if (SERVER_CONFIG.debugMode) {
                console.error('❌ Socket.IO连接错误:', error);
            }
            this.onConnectError(error);
        });
        
        this.socket.on('reconnect', (attemptNumber) => {
            if (SERVER_CONFIG.debugMode) {
                console.log('🔄 Socket.IO重连成功，尝试次数:', attemptNumber);
            }
            this.onReconnect(attemptNumber);
        });
        
        this.socket.on('reconnect_error', (error) => {
            if (SERVER_CONFIG.debugMode) {
                console.error('❌ Socket.IO重连失败:', error);
            }
            this.onReconnectError(error);
        });
    }
    
    // 连接成功回调
    onConnect() {
        // 可以在这里添加连接成功后的逻辑
        if (window.ChatManager && window.ChatManager.socket === this.socket) {
            // 如果ChatManager使用同一个socket实例，通知它连接成功
            window.ChatManager.onSocketConnect();
        }
    }
    
    // 连接断开回调
    onDisconnect(reason) {
        // 可以在这里添加连接断开后的逻辑
        if (window.ChatManager && window.ChatManager.socket === this.socket) {
            // 如果ChatManager使用同一个socket实例，通知它连接断开
            window.ChatManager.onSocketDisconnect(reason);
        }
    }
    
    // 连接错误回调
    onConnectError(error) {
        // 可以在这里添加连接错误后的逻辑
    }
    
    // 重连成功回调
    onReconnect(attemptNumber) {
        this.reconnectAttempts = 0;
    }
    
    // 重连失败回调
    onReconnectError(error) {
        this.reconnectAttempts++;
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            if (SERVER_CONFIG.debugMode) {
                console.error('❌ Socket.IO重连失败次数过多，停止重连');
            }
        }
    }
    
    // 获取连接状态
    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            reconnectAttempts: this.reconnectAttempts,
            socketId: this.socket ? this.socket.id : null
        };
    }
    
    // 手动重连
    reconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
        this.init();
    }
    
    // 断开连接
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
        this.isConnected = false;
    }
    
    // 发送消息
    emit(event, data) {
        if (this.socket && this.isConnected) {
            this.socket.emit(event, data);
            return true;
        }
        return false;
    }
    
    // 监听事件
    on(event, callback) {
        if (this.socket) {
            this.socket.on(event, callback);
        }
    }
    
    // 移除事件监听
    off(event, callback) {
        if (this.socket) {
            this.socket.off(event, callback);
        }
    }
}

// 创建全局实例
window.SERVER_CONFIG = SERVER_CONFIG;
window.SocketManager = new SocketManager();

// 自动初始化Socket连接
if (typeof io !== 'undefined') {
    window.SocketManager.init();
} else {
    // 如果Socket.IO还未加载，等待加载完成后再初始化
    document.addEventListener('DOMContentLoaded', () => {
        if (typeof io !== 'undefined') {
            window.SocketManager.init();
        }
    });
}
