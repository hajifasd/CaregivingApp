/**
 * 地理位置管理系统
 * ====================================
 * 
 * 处理地理位置相关功能
 */

class LocationManager {
    constructor() {
        this.currentLocation = null;
        this.watchId = null;
        this.permissionGranted = false;
        this.caregiversNearby = [];
    }
    
    /**
     * 初始化位置服务
     */
    init() {
        this.checkGeolocationSupport();
        this.setupEventListeners();
    }
    
    /**
     * 检查地理位置支持
     */
    checkGeolocationSupport() {
        if (!navigator.geolocation) {
            console.warn('浏览器不支持地理位置功能');
            this.showLocationError('您的浏览器不支持地理位置功能');
            return false;
        }
        return true;
    }
    
    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 位置相关按钮事件
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-location-action]')) {
                const action = e.target.getAttribute('data-location-action');
                this.handleLocationAction(action, e.target);
            }
        });
    }
    
    /**
     * 处理位置操作
     */
    handleLocationAction(action, element) {
        switch (action) {
            case 'get-current-location':
                this.getCurrentLocation();
                break;
            case 'find-nearby-caregivers':
                this.findNearbyCaregivers();
                break;
            case 'share-location':
                this.shareLocation();
                break;
            case 'stop-location-sharing':
                this.stopLocationSharing();
                break;
        }
    }
    
    /**
     * 获取当前位置
     */
    getCurrentLocation() {
        if (!this.checkGeolocationSupport()) {
            return;
        }
        
        this.showLocationLoading();
        
        const options = {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 300000 // 5分钟缓存
        };
        
        navigator.geolocation.getCurrentPosition(
            (position) => {
                this.handleLocationSuccess(position);
            },
            (error) => {
                this.handleLocationError(error);
            },
            options
        );
    }
    
    /**
     * 开始位置监听
     */
    startLocationWatching() {
        if (!this.checkGeolocationSupport()) {
            return;
        }
        
        const options = {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 60000 // 1分钟缓存
        };
        
        this.watchId = navigator.geolocation.watchPosition(
            (position) => {
                this.handleLocationSuccess(position);
            },
            (error) => {
                this.handleLocationError(error);
            },
            options
        );
    }
    
    /**
     * 停止位置监听
     */
    stopLocationWatching() {
        if (this.watchId) {
            navigator.geolocation.clearWatch(this.watchId);
            this.watchId = null;
        }
    }
    
    /**
     * 处理位置获取成功
     */
    handleLocationSuccess(position) {
        this.currentLocation = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: new Date().toISOString()
        };
        
        this.hideLocationLoading();
        this.updateLocationDisplay();
        this.findNearbyCaregivers();
        
        console.log('位置获取成功:', this.currentLocation);
    }
    
    /**
     * 处理位置获取错误
     */
    handleLocationError(error) {
        this.hideLocationLoading();
        
        let errorMessage = '获取位置失败';
        
        switch (error.code) {
            case error.PERMISSION_DENIED:
                errorMessage = '用户拒绝了位置访问请求';
                break;
            case error.POSITION_UNAVAILABLE:
                errorMessage = '位置信息不可用';
                break;
            case error.TIMEOUT:
                errorMessage = '获取位置超时';
                break;
        }
        
        this.showLocationError(errorMessage);
        console.error('位置获取错误:', error);
    }
    
    /**
     * 查找附近的护工
     */
    async findNearbyCaregivers() {
        if (!this.currentLocation) {
            this.showLocationError('请先获取当前位置');
            return;
        }
        
        try {
            this.showNearbyLoading();
            
            const response = await fetch('/api/caregivers/nearby', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getUserToken()}`
                },
                body: JSON.stringify({
                    latitude: this.currentLocation.latitude,
                    longitude: this.currentLocation.longitude,
                    radius: 10 // 10公里半径
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.caregiversNearby = result.data;
                this.displayNearbyCaregivers(result.data);
            } else {
                this.showLocationError(result.message || '查找附近护工失败');
            }
        } catch (error) {
            console.error('查找附近护工失败:', error);
            this.showLocationError('网络错误，请稍后重试');
        } finally {
            this.hideNearbyLoading();
        }
    }
    
    /**
     * 分享位置
     */
    async shareLocation() {
        if (!this.currentLocation) {
            this.showLocationError('请先获取当前位置');
            return;
        }
        
        try {
            const response = await fetch('/api/location/share', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getUserToken()}`
                },
                body: JSON.stringify({
                    latitude: this.currentLocation.latitude,
                    longitude: this.currentLocation.longitude,
                    accuracy: this.currentLocation.accuracy
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('位置分享成功');
                this.updateLocationSharingStatus(true);
            } else {
                this.showLocationError(result.message || '位置分享失败');
            }
        } catch (error) {
            console.error('位置分享失败:', error);
            this.showLocationError('网络错误，请稍后重试');
        }
    }
    
    /**
     * 停止位置分享
     */
    async stopLocationSharing() {
        try {
            const response = await fetch('/api/location/stop-sharing', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getUserToken()}`
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('位置分享已停止');
                this.updateLocationSharingStatus(false);
            } else {
                this.showLocationError(result.message || '停止位置分享失败');
            }
        } catch (error) {
            console.error('停止位置分享失败:', error);
            this.showLocationError('网络错误，请稍后重试');
        }
    }
    
    /**
     * 更新位置显示
     */
    updateLocationDisplay() {
        const locationElements = document.querySelectorAll('[data-location-display]');
        locationElements.forEach(element => {
            if (this.currentLocation) {
                element.innerHTML = `
                    <div class="flex items-center gap-2">
                        <i class="fa fa-map-marker text-success"></i>
                        <span>位置已获取</span>
                    </div>
                `;
            } else {
                element.innerHTML = `
                    <div class="flex items-center gap-2">
                        <i class="fa fa-map-marker text-gray-400"></i>
                        <span>未获取位置</span>
                    </div>
                `;
            }
        });
    }
    
    /**
     * 显示附近的护工
     */
    displayNearbyCaregivers(caregivers) {
        const container = document.getElementById('nearby-caregivers');
        if (!container) return;
        
        if (caregivers.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8">
                    <i class="fa fa-map-marker text-gray-400 text-4xl mb-4"></i>
                    <p class="text-gray-500">附近暂无护工</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = `
            <div class="grid gap-4">
                ${caregivers.map(caregiver => `
                    <div class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                        <div class="flex items-start justify-between">
                            <div class="flex items-start gap-3">
                                <img src="${window.AvatarManager ? window.AvatarManager.getAvatarUrl(caregiver.avatar_url, 'caregiver', 'medium') : '/uploads/avatars/default-caregiver.png'}" 
                                     alt="${caregiver.name}" 
                                     class="w-12 h-12 rounded-full object-cover">
                                <div>
                                    <h4 class="font-semibold">${caregiver.name}</h4>
                                    <p class="text-sm text-gray-600">${caregiver.experience_years}年经验</p>
                                    <p class="text-sm text-gray-500">距离 ${caregiver.distance}km</p>
                                </div>
                            </div>
                            <div class="text-right">
                                <p class="text-lg font-bold text-primary">¥${caregiver.hourly_rate}/小时</p>
                                <button onclick="contactCaregiver(${caregiver.id})" 
                                        class="mt-2 bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-lg text-sm transition-colors">
                                    联系
                                </button>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    /**
     * 更新位置分享状态
     */
    updateLocationSharingStatus(isSharing) {
        const shareButton = document.querySelector('[data-location-action="share-location"]');
        const stopButton = document.querySelector('[data-location-action="stop-location-sharing"]');
        
        if (shareButton) {
            shareButton.style.display = isSharing ? 'none' : 'inline-block';
        }
        if (stopButton) {
            stopButton.style.display = isSharing ? 'inline-block' : 'none';
        }
    }
    
    /**
     * 显示位置加载状态
     */
    showLocationLoading() {
        const loadingElements = document.querySelectorAll('[data-location-loading]');
        loadingElements.forEach(element => {
            element.innerHTML = `
                <div class="flex items-center gap-2">
                    <i class="fa fa-spinner fa-spin text-primary"></i>
                    <span>获取位置中...</span>
                </div>
            `;
        });
    }
    
    /**
     * 隐藏位置加载状态
     */
    hideLocationLoading() {
        const loadingElements = document.querySelectorAll('[data-location-loading]');
        loadingElements.forEach(element => {
            element.innerHTML = '';
        });
    }
    
    /**
     * 显示附近护工加载状态
     */
    showNearbyLoading() {
        const container = document.getElementById('nearby-caregivers');
        if (container) {
            container.innerHTML = `
                <div class="text-center py-8">
                    <i class="fa fa-spinner fa-spin text-primary text-2xl mb-4"></i>
                    <p class="text-gray-500">查找附近护工中...</p>
                </div>
            `;
        }
    }
    
    /**
     * 隐藏附近护工加载状态
     */
    hideNearbyLoading() {
        // 加载状态会在显示结果时自动替换
    }
    
    /**
     * 显示位置错误
     */
    showLocationError(message) {
        this.showMessage(message, 'error');
    }
    
    /**
     * 显示成功信息
     */
    showSuccess(message) {
        this.showMessage(message, 'success');
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
     * 获取用户令牌
     */
    getUserToken() {
        return localStorage.getItem('user_token') || 
               document.cookie.split('; ').find(row => row.startsWith('user_token='))?.split('=')[1];
    }
    
    /**
     * 计算两点间距离
     */
    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // 地球半径（公里）
        const dLat = this.deg2rad(lat2 - lat1);
        const dLon = this.deg2rad(lon2 - lon1);
        const a = 
            Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(this.deg2rad(lat1)) * Math.cos(this.deg2rad(lat2)) * 
            Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        const distance = R * c;
        return Math.round(distance * 100) / 100;
    }
    
    /**
     * 角度转弧度
     */
    deg2rad(deg) {
        return deg * (Math.PI/180);
    }
}

// 创建全局实例
window.LocationManager = new LocationManager();

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    window.LocationManager.init();
});
