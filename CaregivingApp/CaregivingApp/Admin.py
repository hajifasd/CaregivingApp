from __future__ import annotations
from typing import List
from caregiver import Caregiver


class Admin:
    """管理员类，负责管理和审核护工信息"""
    
    def __init__(self, username: str, password: str) -> None:
        """
        初始化管理员对象
        
        参数:
            username: 管理员用户名
            password: 管理员密码
        """
        self._username = username
        self._password = password  # 实际应用中应存储加密后的密码
    
    @property
    def username(self) -> str:
        """获取管理员用户名"""
        return self._username
    
    def review_caregivers(self, caregivers: List[Caregiver]) -> None:
        """
        审核护工列表中的未通过审核的护工
        
        参数:
            caregivers: 护工对象列表
        """
        print("\n--- 待审核的护工列表 ---")
        
        # 筛选出未通过审核的护工
        pending_caregivers = [c for c in caregivers if not c.is_approved]
        
        if not pending_caregivers:
            print("当前没有待审核的护工")
            return
            
        for caregiver in pending_caregivers:
            print(f"护工姓名: {caregiver.name}")
            print(f"身份信息: {caregiver.id_info}")
            print(f"资质证书: {caregiver.cert_info}")
            
            # 获取用户输入并处理
            while True:
                try:
                    choice = input("审核通过 (y/n)? ").strip().lower()
                    if choice in ('y', 'n'):
                        break
                    raise ValueError("请输入 'y' 或 'n'")
                except ValueError as e:
                    print(f"输入错误: {e}")
            
            if choice == 'y':
                caregiver.is_approved = True
                print(f"护工 {caregiver.name} 已通过审核。")
            else:
                print(f"护工 {caregiver.name} 未通过审核。")
