from typing import List
from admin import Admin
from user import User
from caregiver import Caregiver
import logging

# 全局数据存储（为简化示例）
users: List[User] = []
caregivers: List[Caregiver] = []
admin = Admin("admin", "password")  # 系统管理员

def initialize_sample_data() -> None:
    logging.info("开始初始化示例数据")
    # 原初始化逻辑...
    logging.info("示例数据初始化完成")

    
def initialize_sample_data() -> None:
    """初始化示例数据用于测试"""
    # 添加示例用户
    users.append(User("user1", "pass123"))
    users.append(User("user2", "pass456"))
    
    # 添加示例护工
    caregivers.append(
        Caregiver(
            "张三", 
            "13800138000", 
            "身份证: 110101XXXXXXXX1234", 
            "护理证书: 护证XXXXXXXX号"
        )
    )
    caregivers.append(
        Caregiver(
            "李四", 
            "13900139000", 
            "身份证: 310101XXXXXXXX5678", 
            "护理证书: 护证YYYYYYYY号"
        )
    )
    
    print("已初始化示例数据")

def start_web_server() -> None:
    """启动Web服务器（示例实现）"""
    # 实际应用中可以使用Flask或FastAPI等框架
    print("\n=== 护理服务应用 ===")
    print("Web服务器已启动，访问地址: http://localhost:8080")
    print("请在浏览器中打开Web界面进行操作")
    
    # 这里可以添加Web框架的初始化和启动代码
    # 例如使用Flask:
    # from flask import Flask
    # app = Flask(__name__)
    # # 注册路由和API端点
    # app.run(host="0.0.0.0", port=8080)

def main() -> None:
    """应用程序主函数"""
    # 初始化示例数据
    initialize_sample_data()
    
    # 启动Web服务器
    start_web_server()

if __name__ == "__main__":
    main()
    