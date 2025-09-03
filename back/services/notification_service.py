"""
护工资源管理系统 - 通知服务
====================================

处理系统内各种通知的创建、发送、查询和管理
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from models.notification import Notification

class NotificationService:
    """通知管理服务"""
    
    def __init__(self, db=None):
        self.db = db
        self.notification_model = None
    
    def set_db(self, db):
        """设置数据库连接"""
        self.db = db
        self.notification_model = Notification.get_model(db)
    
    def create_notification(self, recipient_id: int, recipient_type: str,
                           notification_type: str, title: str, content: str,
                           sender_id: Optional[int] = None, sender_type: Optional[str] = None,
                           related_id: Optional[int] = None, related_type: Optional[str] = None,
                           priority: str = 'normal') -> Dict[str, Any]:
        """创建通知"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            notification = self.notification_model(
                recipient_id=recipient_id,
                recipient_type=recipient_type,
                sender_id=sender_id,
                sender_type=sender_type,
                notification_type=notification_type,
                title=title,
                content=content,
                related_id=related_id,
                related_type=related_type,
                priority=priority
            )
            
            self.db.session.add(notification)
            self.db.session.commit()
            
            return {
                "success": True,
                "message": "通知创建成功",
                "data": notification.to_dict()
            }
            
        except Exception as e:
            self.db.session.rollback()
            return {"success": False, "message": f"创建通知失败: {str(e)}"}
    
    def create_job_opportunity_notification(self, caregiver_id: int, user_id: int, 
                                          application_id: int, service_type: str) -> Dict[str, Any]:
        """为护工创建工作机会通知"""
        title = "新的工作机会"
        content = f"您收到了一个{service_type}服务的工作机会，请及时查看并回复。"
        
        return self.create_notification(
            recipient_id=caregiver_id,
            recipient_type='caregiver',
            notification_type='job_opportunity',
            title=title,
            content=content,
            sender_id=user_id,
            sender_type='user',
            related_id=application_id,
            related_type='contract_application',
            priority='high'
        )
    
    def create_application_response_notification(self, user_id: int, caregiver_id: int,
                                              application_id: int, response: str, status: str) -> Dict[str, Any]:
        """为用户创建申请回复通知"""
        if status == 'accepted':
            title = "护工接受了您的工作申请"
            content = f"护工已接受您的{response}服务申请，请查看详情。"
            priority = 'high'
        else:
            title = "护工回复了您的工作申请"
            content = f"护工回复了您的申请：{response}"
            priority = 'normal'
        
        return self.create_notification(
            recipient_id=user_id,
            recipient_type='user',
            notification_type='application_response',
            title=title,
            content=content,
            sender_id=caregiver_id,
            sender_type='caregiver',
            related_id=application_id,
            related_type='contract_application',
            priority=priority
        )
    
    def get_user_notifications(self, user_id: int, user_type: str, 
                             limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """获取用户通知列表"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            notifications = self.notification_model.query.filter_by(
                recipient_id=user_id,
                recipient_type=user_type
            ).order_by(self.notification_model.created_at.desc()).offset(offset).limit(limit).all()
            
            total = self.notification_model.query.filter_by(
                recipient_id=user_id,
                recipient_type=user_type
            ).count()
            
            return {
                "success": True,
                "data": {
                    "notifications": [n.to_dict() for n in notifications],
                    "total": total,
                    "unread_count": self.get_unread_count(user_id, user_type)
                }
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取通知失败: {str(e)}"}
    
    def get_unread_count(self, user_id: int, user_type: str) -> int:
        """获取未读通知数量"""
        try:
            if not self.db:
                return 0
            
            return self.notification_model.query.filter_by(
                recipient_id=user_id,
                recipient_type=user_type,
                is_read=False
            ).count()
            
        except Exception:
            return 0
    
    def mark_as_read(self, notification_id: int, user_id: int, user_type: str) -> Dict[str, Any]:
        """标记通知为已读"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            notification = self.notification_model.query.filter_by(
                id=notification_id,
                recipient_id=user_id,
                recipient_type=user_type
            ).first()
            
            if not notification:
                return {"success": False, "message": "通知不存在"}
            
            notification.mark_as_read()
            self.db.session.commit()
            
            return {"success": True, "message": "通知已标记为已读"}
            
        except Exception as e:
            self.db.session.rollback()
            return {"success": False, "message": f"操作失败: {str(e)}"}
    
    def mark_all_as_read(self, user_id: int, user_type: str) -> Dict[str, Any]:
        """标记所有通知为已读"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            notifications = self.notification_model.query.filter_by(
                recipient_id=user_id,
                recipient_type=user_type,
                is_read=False
            ).all()
            
            for notification in notifications:
                notification.mark_as_read()
            
            self.db.session.commit()
            
            return {"success": True, "message": f"已标记 {len(notifications)} 条通知为已读"}
            
        except Exception as e:
            self.db.session.rollback()
            return {"success": False, "message": f"操作失败: {str(e)}"}

# 创建全局实例
notification_service = NotificationService()
