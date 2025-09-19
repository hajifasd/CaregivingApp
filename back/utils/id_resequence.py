"""
ID重新排序工具
用于在删除记录后重新设置自增ID，保持连续的自增序列
"""

from extensions import db
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

class IDResequenceManager:
    """ID重新排序管理器"""
    
    @staticmethod
    def resequence_table(table_name, id_column='id'):
        """
        重新排序指定表的ID（简化版本）
        只重置自增ID计数器，不重新分配现有记录的ID
        
        Args:
            table_name (str): 表名
            id_column (str): ID列名，默认为'id'
        """
        try:
            with db.engine.connect() as conn:
                try:
                    # 获取当前最大ID
                    max_id_query = text(f"SELECT MAX({id_column}) FROM {table_name}")
                    result = conn.execute(max_id_query)
                    max_id = result.fetchone()[0]
                    
                    if max_id is None:
                        # 如果没有数据，重置自增ID为1
                        next_id = 1
                    else:
                        # 设置下一个自增ID为最大ID+1
                        next_id = max_id + 1
                    
                    # 重置自增ID
                    conn.execute(text(f"ALTER TABLE {table_name} AUTO_INCREMENT = {next_id}"))
                    
                    logger.info(f"表 {table_name} 的自增ID已重置为 {next_id}")
                    return True
                    
                except Exception as e:
                    logger.error(f"重置表 {table_name} 的自增ID失败: {e}")
                    return False
                    
        except Exception as e:
            logger.error(f"重置表 {table_name} 的自增ID失败: {e}")
            return False
    
    @staticmethod
    def resequence_caregivers():
        """重新排序护工表ID"""
        return IDResequenceManager.resequence_table('caregiver')
    
    @staticmethod
    def resequence_users():
        """重新排序用户表ID"""
        return IDResequenceManager.resequence_table('user')
    
    @staticmethod
    def resequence_employment_contracts():
        """重新排序就业合同表ID"""
        return IDResequenceManager.resequence_table('employment_contract')
    
    @staticmethod
    def resequence_caregiver_hire_info():
        """重新排序护工聘用信息表ID"""
        return IDResequenceManager.resequence_table('caregiver_hire_info')
    
    @staticmethod
    def resequence_messages():
        """重新排序消息表ID"""
        return IDResequenceManager.resequence_table('message')
    
    @staticmethod
    def resequence_notifications():
        """重新排序通知表ID"""
        return IDResequenceManager.resequence_table('notification')

# 导出到全局
__all__ = ['IDResequenceManager']
