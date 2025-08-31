from typing import List, Optional


class Caregiver:
    """护工类，包含护工的基本信息、审核状态和评分管理"""
    
    def __init__(self, name: str, phone: str, id_info: str, cert_info: str) -> None:
        """
        初始化护工对象
        
        参数:
            name: 护工姓名
            phone: 护工电话号码
            id_info: 护工身份信息
            cert_info: 护工资质证书信息
        """
        self._name = name
        self._phone_number = phone
        self._identity_info = id_info
        self._certification_info = cert_info
        self._approved = False
        self._ratings: List[int] = []
        self._average_rating = 0.0
    
    @property
    def name(self) -> str:
        """获取护工姓名"""
        return self._name
    
    @property
    def phone_number(self) -> str:
        """获取护工电话号码"""
        return self._phone_number
    
    @property
    def id_info(self) -> str:
        """获取护工身份信息"""
        return self._identity_info
    
    @property
    def cert_info(self) -> str:
        """获取护工资质证书信息"""
        return self._certification_info
    
    @property
    def is_approved(self) -> bool:
        """获取护工审核状态"""
        return self._approved
    
    @is_approved.setter
    def is_approved(self, status: bool) -> None:
        """设置护工审核状态"""
        self._approved = status
    
    @property
    def average_rating(self) -> float:
        """获取护工的平均评分"""
        return self._average_rating
    
    def display_profile(self) -> None:
        """显示护工的基本资料和平均评分"""
        print(f"姓名: {self._name}, 平均评分: {self._average_rating:.1f}/5")
    
    def add_rating(self, rating: int) -> None:
        """
        添加对护工的评分并更新平均评分
        
        参数:
            rating: 评分值，应在1-5之间
            
        异常:
            ValueError: 如果评分不在1-5范围内则抛出
        """
        if not (1 <= rating <= 5):
            raise ValueError("评分必须在1到5之间")
        
        self._ratings.append(rating)
        self._update_average_rating()
    
    def _update_average_rating(self) -> None:
        """更新平均评分（私有方法）"""
        if not self._ratings:
            self._average_rating = 0.0
        else:
            total = sum(self._ratings)
            self._average_rating = total / len(self._ratings)
    