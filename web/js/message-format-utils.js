/**
 * 消息数据格式标准化工具
 * 统一处理消息数据的格式转换和验证
 */

class MessageFormatUtils {
    /**
     * 标准化消息数据格式
     * 将所有可能的字段名统一为标准格式
     */
    static standardizeMessageData(data) {
        if (!data || typeof data !== 'object') {
            throw new Error('消息数据必须是对象');
        }

        const standardized = {
            // 发送者信息
            sender_id: data.sender_id || data.senderId || data.sender_id,
            sender_type: data.sender_type || data.senderType || data.sender_type || 'user',
            sender_name: data.sender_name || data.senderName || data.sender_name || '',
            
            // 接收者信息
            recipient_id: data.recipient_id || data.recipientId || data.receiver_id || data.receiverId,
            recipient_type: data.recipient_type || data.recipientType || data.receiver_type || data.receiverType || 'user',
            
            // 消息内容
            content: data.content || data.message || data.text || '',
            message_type: data.message_type || data.messageType || data.type || 'text',
            
            // 时间戳
            timestamp: data.timestamp || data.created_at || data.createdAt || Date.now(),
            
            // 其他字段
            conversation_id: data.conversation_id || data.conversationId || data.room_id || data.roomId,
            is_read: data.is_read || data.isRead || data.read || false,
            message_id: data.message_id || data.messageId || data.id
        };

        return standardized;
    }

    /**
     * 验证消息数据
     */
    static validateMessageData(data) {
        const errors = [];

        // 必需字段检查
        if (!data.sender_id) {
            errors.push('缺少发送者ID (sender_id)');
        }
        if (!data.recipient_id) {
            errors.push('缺少接收者ID (recipient_id)');
        }
        if (!data.content || data.content.trim() === '') {
            errors.push('消息内容不能为空');
        }
        if (!data.sender_type) {
            errors.push('缺少发送者类型 (sender_type)');
        }
        if (!data.recipient_type) {
            errors.push('缺少接收者类型 (recipient_type)');
        }

        // 类型检查
        if (data.sender_id && typeof data.sender_id !== 'number' && typeof data.sender_id !== 'string') {
            errors.push('发送者ID必须是数字或字符串');
        }
        if (data.recipient_id && typeof data.recipient_id !== 'number' && typeof data.recipient_id !== 'string') {
            errors.push('接收者ID必须是数字或字符串');
        }
        if (data.sender_type && !['user', 'caregiver', 'admin'].includes(data.sender_type)) {
            errors.push('发送者类型必须是 user、caregiver 或 admin');
        }
        if (data.recipient_type && !['user', 'caregiver', 'admin'].includes(data.recipient_type)) {
            errors.push('接收者类型必须是 user、caregiver 或 admin');
        }
        if (data.message_type && !['text', 'image', 'file', 'system'].includes(data.message_type)) {
            errors.push('消息类型必须是 text、image、file 或 system');
        }

        return {
            isValid: errors.length === 0,
            errors: errors
        };
    }

    /**
     * 构建发送消息的数据格式
     */
    static buildSendMessageData(recipientId, content, options = {}) {
        // 获取当前用户信息
        const currentUser = this.getCurrentUserInfo();
        
        if (!currentUser.id) {
            throw new Error('用户未登录，无法发送消息');
        }

        const messageData = {
            sender_id: currentUser.id,
            sender_type: currentUser.type,
            sender_name: currentUser.name,
            recipient_id: recipientId,
            recipient_type: options.recipientType || 'user',
            content: content,
            message_type: options.messageType || 'text',
            timestamp: Date.now(),
            conversation_id: options.conversationId || `${currentUser.type}_${currentUser.id}_${options.recipientType || 'user'}_${recipientId}`
        };

        return messageData;
    }

    /**
     * 获取当前用户信息
     */
    static getCurrentUserInfo() {
        // 尝试从localStorage获取用户信息
        let userInfo = JSON.parse(localStorage.getItem('user_info') || '{}');
        let userType = 'user';
        let token = localStorage.getItem('user_token');

        // 如果用户端没有信息，尝试护工端
        if (!userInfo.id) {
            userInfo = JSON.parse(localStorage.getItem('caregiver_info') || '{}');
            userType = 'caregiver';
            token = localStorage.getItem('caregiver_token');
        }

        // 如果护工端也没有信息，尝试管理端
        if (!userInfo.id) {
            userInfo = JSON.parse(localStorage.getItem('admin_info') || '{}');
            userType = 'admin';
            token = localStorage.getItem('admin_token');
        }

        return {
            id: userInfo.id,
            name: userInfo.name || userInfo.username || userInfo.real_name || '用户',
            type: userType,
            token: token
        };
    }

    /**
     * 格式化消息显示
     */
    static formatMessageForDisplay(message) {
        const standardized = this.standardizeMessageData(message);
        
        return {
            id: standardized.message_id || Date.now(),
            senderId: standardized.sender_id,
            senderName: standardized.sender_name,
            senderType: standardized.sender_type,
            content: standardized.content,
            messageType: standardized.message_type,
            timestamp: standardized.timestamp,
            isRead: standardized.is_read,
            isOwn: this.isOwnMessage(standardized)
        };
    }

    /**
     * 判断是否是自己的消息
     */
    static isOwnMessage(message) {
        const currentUser = this.getCurrentUserInfo();
        return message.sender_id == currentUser.id && message.sender_type === currentUser.type;
    }

    /**
     * 生成对话ID
     */
    static generateConversationId(user1Id, user1Type, user2Id, user2Type) {
        // 确保ID顺序一致，避免重复对话
        const sorted = [
            { id: user1Id, type: user1Type },
            { id: user2Id, type: user2Type }
        ].sort((a, b) => {
            if (a.type !== b.type) {
                return a.type.localeCompare(b.type);
            }
            return a.id - b.id;
        });

        return `${sorted[0].type}_${sorted[0].id}_${sorted[1].type}_${sorted[1].id}`;
    }

    /**
     * 解析对话ID
     */
    static parseConversationId(conversationId) {
        const parts = conversationId.split('_');
        if (parts.length !== 4) {
            throw new Error('无效的对话ID格式');
        }

        return {
            user1Type: parts[0],
            user1Id: parts[1],
            user2Type: parts[2],
            user2Id: parts[3]
        };
    }
}

// 导出到全局
window.MessageFormatUtils = MessageFormatUtils;
