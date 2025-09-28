/**
 * 系统监控管理器
 * ====================================
 * 
 * 实时监控系统状态和性能指标
 */

class SystemMonitor {
    constructor() {
        this.metrics = {
            server: { status: 'unknown', responseTime: 0, uptime: 0 },
            database: { status: 'unknown', connections: 0, queries: 0 },
            redis: { status: 'unknown', memory: 0, keys: 0 },
            spark: { status: 'unknown', jobs: 0, executors: 0 },
            hadoop: { status: 'unknown', nodes: 0, storage: 0 }
        };
        this.updateInterval = null;
        this.alerts = [];
    }
    
    /**
     * 初始化系统监控
     */
    init() {
        this.setupEventListeners();
        this.startMonitoring();
        this.loadSystemStatus();
    }
    
    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 监控相关按钮事件
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-monitor-action]')) {
                const action = e.target.getAttribute('data-monitor-action');
                this.handleMonitorAction(action, e.target);
            }
        });
    }
    
    /**
     * 处理监控操作
     */
    handleMonitorAction(action, element) {
        switch (action) {
            case 'refresh-status':
                this.refreshSystemStatus();
                break;
            case 'restart-service':
                this.restartService(element);
                break;
            case 'view-logs':
                this.viewServiceLogs(element);
                break;
            case 'clear-alerts':
                this.clearAlerts();
                break;
        }
    }
    
    /**
     * 开始监控
     */
    startMonitoring() {
        // 每30秒更新一次系统状态
        this.updateInterval = setInterval(() => {
            this.updateSystemMetrics();
        }, 30000);
        
        // 立即执行一次
        this.updateSystemMetrics();
    }
    
    /**
     * 停止监控
     */
    stopMonitoring() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
    
    /**
     * 更新系统指标
     */
    async updateSystemMetrics() {
        try {
            const response = await fetch('/api/admin/system/metrics', {
                headers: {
                    'Authorization': `Bearer ${this.getAdminToken()}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.metrics = data.metrics;
                this.updateSystemStatusDisplay();
                this.checkAlerts();
            }
        } catch (error) {
            console.error('获取系统指标失败:', error);
            this.handleConnectionError();
        }
    }
    
    /**
     * 加载系统状态
     */
    async loadSystemStatus() {
        try {
            const response = await fetch('/api/admin/system/status', {
                headers: {
                    'Authorization': `Bearer ${this.getAdminToken()}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateSystemStatusDisplay(data);
            }
        } catch (error) {
            console.error('加载系统状态失败:', error);
        }
    }
    
    /**
     * 更新系统状态显示
     */
    updateSystemStatusDisplay(data = null) {
        const metrics = data || this.metrics;
        
        // 更新服务器状态
        this.updateServiceStatus('server', metrics.server);
        this.updateServiceStatus('database', metrics.database);
        this.updateServiceStatus('redis', metrics.redis);
        this.updateServiceStatus('spark', metrics.spark);
        this.updateServiceStatus('hadoop', metrics.hadoop);
        
        // 更新性能图表
        this.updatePerformanceCharts(metrics);
        
        // 更新告警信息
        this.updateAlertsDisplay();
    }
    
    /**
     * 更新服务状态
     */
    updateServiceStatus(serviceName, serviceData) {
        const statusElement = document.getElementById(`${serviceName}-status`);
        if (statusElement) {
            const statusClass = this.getStatusClass(serviceData.status);
            statusElement.className = `stat-value ${statusClass}`;
            statusElement.textContent = this.getStatusText(serviceData.status);
        }
        
        // 更新详细信息
        this.updateServiceDetails(serviceName, serviceData);
    }
    
    /**
     * 更新服务详细信息
     */
    updateServiceDetails(serviceName, serviceData) {
        const detailsContainer = document.getElementById(`${serviceName}-details`);
        if (!detailsContainer) return;
        
        let detailsHTML = '';
        
        switch (serviceName) {
            case 'server':
                detailsHTML = `
                    <div class="text-sm space-y-1">
                        <div>响应时间: ${serviceData.responseTime}ms</div>
                        <div>运行时间: ${this.formatUptime(serviceData.uptime)}</div>
                    </div>
                `;
                break;
            case 'database':
                detailsHTML = `
                    <div class="text-sm space-y-1">
                        <div>连接数: ${serviceData.connections}</div>
                        <div>查询数: ${serviceData.queries}</div>
                    </div>
                `;
                break;
            case 'redis':
                detailsHTML = `
                    <div class="text-sm space-y-1">
                        <div>内存使用: ${serviceData.memory}MB</div>
                        <div>键数量: ${serviceData.keys}</div>
                    </div>
                `;
                break;
            case 'spark':
                detailsHTML = `
                    <div class="text-sm space-y-1">
                        <div>活跃作业: ${serviceData.jobs}</div>
                        <div>执行器: ${serviceData.executors}</div>
                    </div>
                `;
                break;
            case 'hadoop':
                detailsHTML = `
                    <div class="text-sm space-y-1">
                        <div>节点数: ${serviceData.nodes}</div>
                        <div>存储: ${serviceData.storage}GB</div>
                    </div>
                `;
                break;
        }
        
        detailsContainer.innerHTML = detailsHTML;
    }
    
    /**
     * 更新性能图表
     */
    updatePerformanceCharts(metrics) {
        // 更新CPU使用率图表
        this.updateChart('cpu-chart', metrics.server.cpu || 0);
        
        // 更新内存使用率图表
        this.updateChart('memory-chart', metrics.server.memory || 0);
        
        // 更新磁盘使用率图表
        this.updateChart('disk-chart', metrics.server.disk || 0);
        
        // 更新网络流量图表
        this.updateChart('network-chart', metrics.server.network || 0);
    }
    
    /**
     * 更新图表
     */
    updateChart(chartId, value) {
        const chartElement = document.getElementById(chartId);
        if (!chartElement) return;
        
        const percentage = Math.min(100, Math.max(0, value));
        const color = this.getPerformanceColor(percentage);
        
        chartElement.innerHTML = `
            <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="h-2 rounded-full transition-all duration-500" 
                     style="width: ${percentage}%; background-color: ${color};"></div>
            </div>
            <div class="text-sm text-gray-600 mt-1">${percentage.toFixed(1)}%</div>
        `;
    }
    
    /**
     * 检查告警
     */
    checkAlerts() {
        const newAlerts = [];
        
        // 检查服务器状态
        if (this.metrics.server.status !== 'running') {
            newAlerts.push({
                type: 'error',
                service: 'server',
                message: '服务器状态异常',
                timestamp: new Date().toISOString()
            });
        }
        
        // 检查数据库连接
        if (this.metrics.database.connections > 80) {
            newAlerts.push({
                type: 'warning',
                service: 'database',
                message: '数据库连接数过高',
                timestamp: new Date().toISOString()
            });
        }
        
        // 检查Redis内存
        if (this.metrics.redis.memory > 1000) {
            newAlerts.push({
                type: 'warning',
                service: 'redis',
                message: 'Redis内存使用过高',
                timestamp: new Date().toISOString()
            });
        }
        
        // 添加新告警
        newAlerts.forEach(alert => {
            if (!this.alerts.find(a => a.message === alert.message)) {
                this.alerts.unshift(alert);
                this.showAlert(alert);
            }
        });
        
        // 限制告警数量
        if (this.alerts.length > 50) {
            this.alerts = this.alerts.slice(0, 50);
        }
    }
    
    /**
     * 显示告警
     */
    showAlert(alert) {
        const alertElement = document.createElement('div');
        alertElement.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 max-w-sm ${
            alert.type === 'error' ? 'bg-red-500 text-white' :
            alert.type === 'warning' ? 'bg-yellow-500 text-white' :
            'bg-blue-500 text-white'
        }`;
        
        alertElement.innerHTML = `
            <div class="flex items-center gap-2">
                <i class="fa fa-${alert.type === 'error' ? 'times-circle' : 'exclamation-triangle'}"></i>
                <span>${alert.message}</span>
            </div>
        `;
        
        document.body.appendChild(alertElement);
        
        setTimeout(() => {
            alertElement.remove();
        }, 5000);
    }
    
    /**
     * 更新告警显示
     */
    updateAlertsDisplay() {
        const alertsContainer = document.getElementById('system-alerts');
        if (!alertsContainer) return;
        
        if (this.alerts.length === 0) {
            alertsContainer.innerHTML = `
                <div class="text-center py-8">
                    <i class="fa fa-check-circle text-green-500 text-4xl mb-4"></i>
                    <p class="text-gray-500">系统运行正常，无告警</p>
                </div>
            `;
            return;
        }
        
        alertsContainer.innerHTML = `
            <div class="space-y-3">
                ${this.alerts.slice(0, 10).map(alert => `
                    <div class="flex items-center gap-3 p-3 border border-gray-200 rounded-lg ${
                        alert.type === 'error' ? 'border-red-200 bg-red-50' :
                        alert.type === 'warning' ? 'border-yellow-200 bg-yellow-50' :
                        'border-blue-200 bg-blue-50'
                    }">
                        <i class="fa fa-${alert.type === 'error' ? 'times-circle text-red-500' : 'exclamation-triangle text-yellow-500'}"></i>
                        <div class="flex-1">
                            <div class="font-medium">${alert.message}</div>
                            <div class="text-sm text-gray-500">${new Date(alert.timestamp).toLocaleString()}</div>
                        </div>
                        <button onclick="this.parentElement.remove()" class="text-gray-400 hover:text-gray-600">
                            <i class="fa fa-times"></i>
                        </button>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    /**
     * 刷新系统状态
     */
    async refreshSystemStatus() {
        this.showMessage('正在刷新系统状态...', 'info');
        await this.updateSystemMetrics();
        this.showMessage('系统状态已刷新', 'success');
    }
    
    /**
     * 重启服务
     */
    async restartService(element) {
        const serviceName = element.getAttribute('data-service');
        
        if (!confirm(`确定要重启 ${serviceName} 服务吗？`)) {
            return;
        }
        
        try {
            const response = await fetch('/api/admin/system/restart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAdminToken()}`
                },
                body: JSON.stringify({ service: serviceName })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showMessage(`${serviceName} 服务重启成功`, 'success');
                setTimeout(() => {
                    this.updateSystemMetrics();
                }, 5000);
            } else {
                this.showMessage(result.message || '服务重启失败', 'error');
            }
        } catch (error) {
            console.error('重启服务失败:', error);
            this.showMessage('服务重启失败', 'error');
        }
    }
    
    /**
     * 查看服务日志
     */
    async viewServiceLogs(element) {
        const serviceName = element.getAttribute('data-service');
        
        try {
            const response = await fetch(`/api/admin/system/logs/${serviceName}`, {
                headers: {
                    'Authorization': `Bearer ${this.getAdminToken()}`
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showLogsModal(serviceName, result.data);
            } else {
                this.showMessage(result.message || '获取日志失败', 'error');
            }
        } catch (error) {
            console.error('获取日志失败:', error);
            this.showMessage('获取日志失败', 'error');
        }
    }
    
    /**
     * 显示日志模态框
     */
    showLogsModal(serviceName, logs) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[80vh] overflow-hidden">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-semibold">${serviceName} 服务日志</h3>
                    <button onclick="this.closest('.fixed').remove()" class="text-gray-400 hover:text-gray-600">
                        <i class="fa fa-times"></i>
                    </button>
                </div>
                
                <div class="bg-gray-900 text-green-400 p-4 rounded-lg h-96 overflow-y-auto font-mono text-sm">
                    <pre>${logs}</pre>
                </div>
                
                <div class="mt-4 flex gap-3">
                    <button onclick="this.closest('.fixed').remove()" 
                            class="flex-1 border border-gray-300 text-gray-700 hover:bg-gray-50 px-4 py-2 rounded-lg transition-colors">
                        关闭
                    </button>
                    <button onclick="window.EmergencyManager.refreshSystemStatus()" 
                            class="flex-1 bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-lg transition-colors">
                        刷新日志
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    /**
     * 清除告警
     */
    clearAlerts() {
        this.alerts = [];
        this.updateAlertsDisplay();
        this.showMessage('告警已清除', 'success');
    }
    
    /**
     * 处理连接错误
     */
    handleConnectionError() {
        this.showMessage('无法连接到监控服务', 'error');
    }
    
    /**
     * 获取状态样式类
     */
    getStatusClass(status) {
        const statusMap = {
            'running': 'text-green-600',
            'stopped': 'text-red-600',
            'warning': 'text-yellow-600',
            'unknown': 'text-gray-600'
        };
        return statusMap[status] || 'text-gray-600';
    }
    
    /**
     * 获取状态文本
     */
    getStatusText(status) {
        const statusMap = {
            'running': '运行中',
            'stopped': '已停止',
            'warning': '警告',
            'unknown': '未知'
        };
        return statusMap[status] || status;
    }
    
    /**
     * 获取性能颜色
     */
    getPerformanceColor(percentage) {
        if (percentage < 50) return '#10B981'; // 绿色
        if (percentage < 80) return '#F59E0B'; // 黄色
        return '#EF4444'; // 红色
    }
    
    /**
     * 格式化运行时间
     */
    formatUptime(seconds) {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        if (days > 0) return `${days}天 ${hours}小时`;
        if (hours > 0) return `${hours}小时 ${minutes}分钟`;
        return `${minutes}分钟`;
    }
    
    /**
     * 显示消息
     */
    showMessage(message, type = 'info') {
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
    
    /**
     * 获取管理员令牌
     */
    getAdminToken() {
        return localStorage.getItem('admin_token') || 
               document.cookie.split('; ').find(row => row.startsWith('admin_token='))?.split('=')[1];
    }
}

// 创建全局实例
window.SystemMonitor = new SystemMonitor();

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    window.SystemMonitor.init();
});
