"""
护工资源管理系统 - 文件上传工具函数
====================================

包含文件格式验证、文件保存等文件上传相关功能
"""

import os
import uuid
from typing import Optional
from config.settings import ALLOWED_EXTENSIONS

def allowed_file(filename: str) -> bool:
    """检查文件是否为允许的格式
    
    Args:
        filename: 文件名
        
    Returns:
        bool: 是否为允许的文件格式
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename: str, prefix: str = "") -> str:
    """生成唯一的文件名
    
    Args:
        original_filename: 原始文件名
        prefix: 文件名前缀
        
    Returns:
        str: 生成的唯一文件名
    """
    if not original_filename:
        return ""
    
    file_ext = original_filename.rsplit('.', 1)[1].lower()
    unique_id = uuid.uuid4().hex
    prefix = f"{prefix}_" if prefix else ""
    
    return f"{prefix}{unique_id}.{file_ext}"

def save_uploaded_file(file, upload_folder: str, filename: str) -> Optional[str]:
    """保存上传的文件
    
    Args:
        file: 上传的文件对象
        upload_folder: 上传目录
        filename: 保存的文件名
        
    Returns:
        Optional[str]: 保存成功返回文件路径，失败返回None
    """
    try:
        # 确保上传目录存在
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # 验证文件是否保存成功
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path
        else:
            return None
            
    except Exception as e:
        print(f"文件保存失败: {e}")
        return None

def delete_file(file_path: str) -> bool:
    """删除文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 删除是否成功
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"文件删除失败: {e}")
        return False 