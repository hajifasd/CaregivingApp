"""
护工资源管理系统 - 服务层模块
====================================

包含所有业务逻辑服务，连接数据模型和API接口
"""

from .user_service import UserService
from .caregiver_service import CaregiverService
from .appointment_service import AppointmentService
from .employment_service import EmploymentService
from .message_service import MessageService

__all__ = [
    'UserService',
    'CaregiverService', 
    'AppointmentService',
    'EmploymentService',
    'MessageService'
] 