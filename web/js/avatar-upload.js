/**
 * 头像上传组件
 * ====================================
 * 
 * 提供头像上传功能的UI组件
 */

class AvatarUpload {
    constructor(options = {}) {
        this.options = {
            container: options.container || document.body,
            userType: options.userType || 'user',
            userId: options.userId || null,
            size: options.size || 'medium',
            showPreview: options.showPreview !== false,
            onUpload: options.onUpload || null,
            onError: options.onError || null,
            ...options
        };
        
        this.element = null;
        this.fileInput = null;
        this.preview = null;
        this.uploading = false;
        
        this.init();
    }
    
    init() {
        this.createElement();
        this.bindEvents();
    }
    
    createElement() {
        const sizeConfig = window.AvatarManager.avatarSizes[this.options.size];
        const sizeClass = this.getSizeClass();
        
        this.element = document.createElement('div');
        this.element.className = `avatar-upload ${sizeClass}`;
        this.element.innerHTML = `
            <div class="avatar-upload-container">
                <div class="avatar-preview" id="avatar-preview-${Date.now()}">
                    <img src="${window.AvatarManager.getAvatarUrl('', this.options.userType, this.options.size)}" 
                         alt="头像预览" 
                         class="avatar-image"
                         style="width: ${sizeConfig.width}px; height: ${sizeConfig.height}px;">
                    <div class="avatar-overlay">
                        <i class="fa fa-camera"></i>
                        <span>点击上传</span>
                    </div>
                </div>
                <input type="file" 
                       id="avatar-input-${Date.now()}" 
                       accept="image/*" 
                       class="avatar-input"
                       style="display: none;">
                <div class="avatar-actions">
                    <button type="button" class="btn-upload" disabled>
                        <i class="fa fa-upload"></i>
                        上传头像
                    </button>
                    <button type="button" class="btn-remove" style="display: none;">
                        <i class="fa fa-trash"></i>
                        移除
                    </button>
                </div>
                <div class="upload-progress" style="display: none;">
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                    <span class="progress-text">上传中...</span>
                </div>
            </div>
        `;
        
        this.options.container.appendChild(this.element);
        
        // 获取子元素引用
        this.preview = this.element.querySelector('.avatar-preview');
        this.fileInput = this.element.querySelector('.avatar-input');
        this.uploadBtn = this.element.querySelector('.btn-upload');
        this.removeBtn = this.element.querySelector('.btn-remove');
        this.progress = this.element.querySelector('.upload-progress');
        this.progressFill = this.element.querySelector('.progress-fill');
        this.progressText = this.element.querySelector('.progress-text');
    }
    
    getSizeClass() {
        const sizeMap = {
            small: 'avatar-upload-sm',
            medium: 'avatar-upload-md',
            large: 'avatar-upload-lg',
            xlarge: 'avatar-upload-xl'
        };
        return sizeMap[this.options.size] || 'avatar-upload-md';
    }
    
    bindEvents() {
        // 点击预览区域选择文件
        this.preview.addEventListener('click', () => {
            if (!this.uploading) {
                this.fileInput.click();
            }
        });
        
        // 文件选择事件
        this.fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleFileSelect(file);
            }
        });
        
        // 拖拽上传
        this.preview.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.preview.classList.add('drag-over');
        });
        
        this.preview.addEventListener('dragleave', (e) => {
            e.preventDefault();
            this.preview.classList.remove('drag-over');
        });
        
        this.preview.addEventListener('drop', (e) => {
            e.preventDefault();
            this.preview.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });
        
        // 上传按钮
        this.uploadBtn.addEventListener('click', () => {
            this.uploadAvatar();
        });
        
        // 移除按钮
        this.removeBtn.addEventListener('click', () => {
            this.removeAvatar();
        });
    }
    
    handleFileSelect(file) {
        // 验证文件
        if (!window.AvatarManager.validateImageFile(file)) {
            this.showError('请选择有效的图片文件（JPG、PNG、GIF、WebP，最大5MB）');
            return;
        }
        
        // 显示预览
        this.showPreview(file);
        
        // 启用上传按钮
        this.uploadBtn.disabled = false;
        this.removeBtn.style.display = 'inline-block';
    }
    
    showPreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = this.preview.querySelector('.avatar-image');
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
    
    async uploadAvatar() {
        if (this.uploading) return;
        
        const file = this.fileInput.files[0];
        if (!file) return;
        
        this.uploading = true;
        this.showProgress(0);
        
        try {
            const result = await window.AvatarManager.uploadAvatar(
                file, 
                this.options.userType, 
                this.options.userId
            );
            
            if (result.success) {
                this.showSuccess(result.avatarUrl);
                if (this.options.onUpload) {
                    this.options.onUpload(result.avatarUrl);
                }
            } else {
                this.showError(result.message);
                if (this.options.onError) {
                    this.options.onError(result.message);
                }
            }
        } catch (error) {
            this.showError('上传失败：' + error.message);
            if (this.options.onError) {
                this.options.onError(error.message);
            }
        } finally {
            this.uploading = false;
            this.hideProgress();
        }
    }
    
    removeAvatar() {
        // 重置到默认头像
        const img = this.preview.querySelector('.avatar-image');
        img.src = window.AvatarManager.getAvatarUrl('', this.options.userType, this.options.size);
        
        // 重置文件输入
        this.fileInput.value = '';
        
        // 隐藏按钮
        this.uploadBtn.disabled = true;
        this.removeBtn.style.display = 'none';
        
        // 隐藏错误信息
        this.hideError();
    }
    
    showProgress(percent) {
        this.progress.style.display = 'block';
        this.progressFill.style.width = `${percent}%`;
        this.progressText.textContent = `上传中... ${percent}%`;
    }
    
    hideProgress() {
        this.progress.style.display = 'none';
    }
    
    showSuccess(avatarUrl) {
        // 更新头像
        const img = this.preview.querySelector('.avatar-image');
        img.src = avatarUrl;
        
        // 显示成功提示
        this.showMessage('头像上传成功', 'success');
    }
    
    showError(message) {
        this.showMessage(message, 'error');
    }
    
    showMessage(message, type) {
        // 移除现有消息
        this.hideError();
        
        const messageEl = document.createElement('div');
        messageEl.className = `avatar-message avatar-message-${type}`;
        messageEl.textContent = message;
        
        this.element.appendChild(messageEl);
        
        // 自动隐藏
        setTimeout(() => {
            this.hideError();
        }, 3000);
    }
    
    hideError() {
        const messageEl = this.element.querySelector('.avatar-message');
        if (messageEl) {
            messageEl.remove();
        }
    }
    
    // 获取当前头像URL
    getAvatarUrl() {
        const img = this.preview.querySelector('.avatar-image');
        return img.src;
    }
    
    // 设置头像URL
    setAvatarUrl(avatarUrl) {
        const img = this.preview.querySelector('.avatar-image');
        img.src = window.AvatarManager.getAvatarUrl(avatarUrl, this.options.userType, this.options.size);
    }
    
    // 销毁组件
    destroy() {
        if (this.element && this.element.parentNode) {
            this.element.parentNode.removeChild(this.element);
        }
    }
}

// 添加样式
const style = document.createElement('style');
style.textContent = `
    .avatar-upload {
        display: inline-block;
    }
    
    .avatar-upload-container {
        text-align: center;
    }
    
    .avatar-preview {
        position: relative;
        display: inline-block;
        cursor: pointer;
        border-radius: 50%;
        overflow: hidden;
        border: 2px dashed #d1d5db;
        transition: all 0.3s ease;
    }
    
    .avatar-preview:hover {
        border-color: #3b82f6;
        background-color: #f3f4f6;
    }
    
    .avatar-preview.drag-over {
        border-color: #3b82f6;
        background-color: #dbeafe;
    }
    
    .avatar-image {
        display: block;
        object-fit: cover;
    }
    
    .avatar-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.5);
        color: white;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .avatar-preview:hover .avatar-overlay {
        opacity: 1;
    }
    
    .avatar-actions {
        margin-top: 10px;
    }
    
    .btn-upload, .btn-remove {
        padding: 8px 16px;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.3s ease;
    }
    
    .btn-upload {
        background-color: #3b82f6;
        color: white;
    }
    
    .btn-upload:hover:not(:disabled) {
        background-color: #2563eb;
    }
    
    .btn-upload:disabled {
        background-color: #9ca3af;
        cursor: not-allowed;
    }
    
    .btn-remove {
        background-color: #ef4444;
        color: white;
        margin-left: 8px;
    }
    
    .btn-remove:hover {
        background-color: #dc2626;
    }
    
    .upload-progress {
        margin-top: 10px;
    }
    
    .progress-bar {
        width: 100%;
        height: 4px;
        background-color: #e5e7eb;
        border-radius: 2px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background-color: #3b82f6;
        transition: width 0.3s ease;
    }
    
    .progress-text {
        display: block;
        margin-top: 5px;
        font-size: 12px;
        color: #6b7280;
    }
    
    .avatar-message {
        margin-top: 10px;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 14px;
    }
    
    .avatar-message-success {
        background-color: #d1fae5;
        color: #065f46;
        border: 1px solid #a7f3d0;
    }
    
    .avatar-message-error {
        background-color: #fee2e2;
        color: #991b1b;
        border: 1px solid #fca5a5;
    }
    
    .avatar-upload-sm .avatar-preview {
        width: 60px;
        height: 60px;
    }
    
    .avatar-upload-md .avatar-preview {
        width: 100px;
        height: 100px;
    }
    
    .avatar-upload-lg .avatar-preview {
        width: 150px;
        height: 150px;
    }
    
    .avatar-upload-xl .avatar-preview {
        width: 200px;
        height: 200px;
    }
`;

document.head.appendChild(style);

// 导出类
window.AvatarUpload = AvatarUpload;
