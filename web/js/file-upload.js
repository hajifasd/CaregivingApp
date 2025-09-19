/**
 * 文件上传组件
 * 支持头像上传、文档上传、聊天图片上传
 */

class FileUploader {
    constructor(options = {}) {
        this.maxFileSize = options.maxFileSize || 5 * 1024 * 1024; // 5MB
        this.allowedTypes = options.allowedTypes || ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        this.uploadUrl = options.uploadUrl || '/api/upload/avatar';
        this.onSuccess = options.onSuccess || (() => {});
        this.onError = options.onError || (() => {});
        this.onProgress = options.onProgress || (() => {});
    }

    /**
     * 创建文件上传输入框
     */
    createUploadInput(containerId, buttonText = '选择文件') {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error('容器不存在:', containerId);
            return;
        }

        const uploadHTML = `
            <div class="file-upload-container">
                <input type="file" id="file-input-${containerId}" accept="${this.allowedTypes.join(',')}" style="display: none;">
                <button type="button" class="upload-btn" onclick="document.getElementById('file-input-${containerId}').click()">
                    <i class="fa fa-upload"></i> ${buttonText}
                </button>
                <div class="upload-progress" id="progress-${containerId}" style="display: none;">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progress-fill-${containerId}"></div>
                    </div>
                    <span class="progress-text" id="progress-text-${containerId}">0%</span>
                </div>
                <div class="upload-preview" id="preview-${containerId}"></div>
            </div>
        `;

        container.innerHTML = uploadHTML;

        // 绑定文件选择事件
        const fileInput = document.getElementById(`file-input-${containerId}`);
        fileInput.addEventListener('change', (e) => {
            this.handleFileSelect(e, containerId);
        });
    }

    /**
     * 处理文件选择
     */
    handleFileSelect(event, containerId) {
        const file = event.target.files[0];
        if (!file) return;

        // 验证文件
        const validation = this.validateFile(file);
        if (!validation.valid) {
            this.onError(validation.message);
            return;
        }

        // 显示预览
        this.showPreview(file, containerId);

        // 开始上传
        this.uploadFile(file, containerId);
    }

    /**
     * 验证文件
     */
    validateFile(file) {
        // 检查文件大小
        if (file.size > this.maxFileSize) {
            return {
                valid: false,
                message: `文件大小不能超过 ${this.formatFileSize(this.maxFileSize)}`
            };
        }

        // 检查文件类型
        if (!this.allowedTypes.includes(file.type)) {
            return {
                valid: false,
                message: '不支持的文件格式'
            };
        }

        return { valid: true };
    }

    /**
     * 显示文件预览
     */
    showPreview(file, containerId) {
        const preview = document.getElementById(`preview-${containerId}`);
        if (!preview) return;

        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                preview.innerHTML = `
                    <div class="preview-image">
                        <img src="${e.target.result}" alt="预览">
                        <div class="preview-info">
                            <p>${file.name}</p>
                            <p>${this.formatFileSize(file.size)}</p>
                        </div>
                    </div>
                `;
            };
            reader.readAsDataURL(file);
        } else {
            preview.innerHTML = `
                <div class="preview-file">
                    <i class="fa fa-file"></i>
                    <div class="preview-info">
                        <p>${file.name}</p>
                        <p>${this.formatFileSize(file.size)}</p>
                    </div>
                </div>
            `;
        }
    }

    /**
     * 上传文件
     */
    async uploadFile(file, containerId) {
        const formData = new FormData();
        formData.append('file', file);

        // 显示进度条
        this.showProgress(containerId);

        try {
            const response = await fetch(this.uploadUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('user_token') || localStorage.getItem('admin_token')}`
                }
            });

            const result = await response.json();

            if (result.success) {
                this.hideProgress(containerId);
                this.onSuccess(result.data);
                this.showSuccess(containerId, '上传成功');
            } else {
                this.hideProgress(containerId);
                this.onError(result.message);
                this.showError(containerId, result.message);
            }
        } catch (error) {
            this.hideProgress(containerId);
            this.onError('上传失败: ' + error.message);
            this.showError(containerId, '上传失败');
        }
    }

    /**
     * 显示进度条
     */
    showProgress(containerId) {
        const progress = document.getElementById(`progress-${containerId}`);
        if (progress) {
            progress.style.display = 'block';
        }
    }

    /**
     * 隐藏进度条
     */
    hideProgress(containerId) {
        const progress = document.getElementById(`progress-${containerId}`);
        if (progress) {
            progress.style.display = 'none';
        }
    }

    /**
     * 显示成功消息
     */
    showSuccess(containerId, message) {
        const preview = document.getElementById(`preview-${containerId}`);
        if (preview) {
            const successDiv = document.createElement('div');
            successDiv.className = 'upload-success';
            successDiv.innerHTML = `<i class="fa fa-check"></i> ${message}`;
            preview.appendChild(successDiv);
        }
    }

    /**
     * 显示错误消息
     */
    showError(containerId, message) {
        const preview = document.getElementById(`preview-${containerId}`);
        if (preview) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'upload-error';
            errorDiv.innerHTML = `<i class="fa fa-times"></i> ${message}`;
            preview.appendChild(errorDiv);
        }
    }

    /**
     * 格式化文件大小
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// 头像上传器
class AvatarUploader extends FileUploader {
    constructor(options = {}) {
        super({
            maxFileSize: 5 * 1024 * 1024, // 5MB
            allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
            uploadUrl: '/api/upload/avatar',
            ...options
        });
    }
}

// 文档上传器
class DocumentUploader extends FileUploader {
    constructor(options = {}) {
        super({
            maxFileSize: 10 * 1024 * 1024, // 10MB
            allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'],
            uploadUrl: '/api/upload/document',
            ...options
        });
    }
}

// 聊天图片上传器
class ChatImageUploader extends FileUploader {
    constructor(options = {}) {
        super({
            maxFileSize: 3 * 1024 * 1024, // 3MB
            allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
            uploadUrl: '/api/upload/chat-image',
            ...options
        });
    }
}

// 导出到全局
window.FileUploader = FileUploader;
window.AvatarUploader = AvatarUploader;
window.DocumentUploader = DocumentUploader;
window.ChatImageUploader = ChatImageUploader;
