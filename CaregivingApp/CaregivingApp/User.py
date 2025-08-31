from typing import List
from caregiver import Caregiver


class User:
    """用户类，提供查看护工列表和为护工评分的功能"""
    
    def __init__(self, username: str, password: str) -> None:
        """
        初始化用户对象
        
        参数:
            username: 用户名
            password: 用户密码（实际应用中应存储加密后的密码）
        """
        self._username = username
        self._password = password
    
    @property
    def username(self) -> str:
        """获取用户名"""
        return self._username
    
    def view_caregivers(self, caregivers: List[Caregiver]) -> None:
        """
        查看所有已审核通过的护工列表
        
        参数:
            caregivers: 护工对象列表
        """
        print("\n--- 可用的护工列表 ---")
        
        # 筛选已审核通过的护工
        approved_caregivers = [c for c in caregivers if c.is_approved]
        
        if not approved_caregivers:
            print("当前没有可用的护工")
            return
            
        for caregiver in approved_caregivers:
            caregiver.display_profile()
    
    def rate_caregiver(self, caregiver: Caregiver, rating: int) -> None:
        """
        为指定护工评分
        
        参数:
            caregiver: 要评分的护工对象
            rating: 评分值（1-5之间）
            
        异常:
            ValueError: 如果评分不在1-5范围内会被传播
        """
        if not caregiver.is_approved:
            print(f"无法为护工 {caregiver.name} 评分，该护工尚未通过审核")
            return
            
        try:
            caregiver.add_rating(rating)
            print(f"用户 {self._username} 已成功为 {caregiver.name} 评分。")
        except ValueError as e:
            print(f"评分失败: {e}")
    