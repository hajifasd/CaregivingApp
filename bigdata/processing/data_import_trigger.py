"""
护工资源管理系统 - 数据导入触发器
====================================

当有新数据导入时自动触发动态分析
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd
from bigdata_config import DATA_PATHS

logger = logging.getLogger(__name__)

class DataImportTrigger:
    """数据导入触发器"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.import_log_file = os.path.join(DATA_PATHS['ANALYSIS_RESULTS'], 'dynamic', 'import_log.json')
        
        # 创建必要的目录
        os.makedirs(os.path.dirname(self.import_log_file), exist_ok=True)
    
    def trigger_analysis(self, source: str, data_count: int, data_type: str = "csv") -> bool:
        """触发动态分析"""
        try:
            # 调用API触发分析
            url = f"{self.api_base_url}/api/bigdata/dynamic/import-trigger"
            payload = {
                'source': source,
                'count': data_count,
                'type': data_type,
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info(f"✅ 数据导入分析触发成功: {source}, 数据量: {data_count}")
                    return True
                else:
                    logger.error(f"❌ 数据导入分析触发失败: {result.get('message')}")
                    return False
            else:
                logger.error(f"❌ API调用失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 触发分析失败: {str(e)}")
            return False
    
    def import_csv_data(self, file_path: str, source_name: str = None) -> bool:
        """导入CSV数据并触发分析"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"❌ 文件不存在: {file_path}")
                return False
            
            # 读取CSV文件
            df = pd.read_csv(file_path)
            data_count = len(df)
            
            if source_name is None:
                source_name = os.path.basename(file_path).replace('.csv', '')
            
            logger.info(f"📊 导入CSV数据: {source_name}, 数据量: {data_count}")
            
            # 保存到处理后的数据目录
            processed_file = os.path.join(DATA_PATHS['PROCESSED_DATA'], f"{source_name}_processed.parquet")
            df.to_parquet(processed_file, index=False)
            
            # 触发分析
            success = self.trigger_analysis(source_name, data_count, "csv")
            
            if success:
                # 记录导入日志
                self._log_import(source_name, data_count, "csv", file_path)
            
            return success
            
        except Exception as e:
            logger.error(f"❌ CSV数据导入失败: {str(e)}")
            return False
    
    def import_json_data(self, file_path: str, source_name: str = None) -> bool:
        """导入JSON数据并触发分析"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"❌ 文件不存在: {file_path}")
                return False
            
            # 读取JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                data_count = len(data)
                df = pd.DataFrame(data)
            else:
                data_count = 1
                df = pd.DataFrame([data])
            
            if source_name is None:
                source_name = os.path.basename(file_path).replace('.json', '')
            
            logger.info(f"📊 导入JSON数据: {source_name}, 数据量: {data_count}")
            
            # 保存到处理后的数据目录
            processed_file = os.path.join(DATA_PATHS['PROCESSED_DATA'], f"{source_name}_processed.parquet")
            df.to_parquet(processed_file, index=False)
            
            # 触发分析
            success = self.trigger_analysis(source_name, data_count, "json")
            
            if success:
                # 记录导入日志
                self._log_import(source_name, data_count, "json", file_path)
            
            return success
            
        except Exception as e:
            logger.error(f"❌ JSON数据导入失败: {str(e)}")
            return False
    
    def import_parquet_data(self, file_path: str, source_name: str = None) -> bool:
        """导入Parquet数据并触发分析"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"❌ 文件不存在: {file_path}")
                return False
            
            # 读取Parquet文件
            df = pd.read_parquet(file_path)
            data_count = len(df)
            
            if source_name is None:
                source_name = os.path.basename(file_path).replace('.parquet', '')
            
            logger.info(f"📊 导入Parquet数据: {source_name}, 数据量: {data_count}")
            
            # 保存到处理后的数据目录
            processed_file = os.path.join(DATA_PATHS['PROCESSED_DATA'], f"{source_name}_processed.parquet")
            df.to_parquet(processed_file, index=False)
            
            # 触发分析
            success = self.trigger_analysis(source_name, data_count, "parquet")
            
            if success:
                # 记录导入日志
                self._log_import(source_name, data_count, "parquet", file_path)
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Parquet数据导入失败: {str(e)}")
            return False
    
    def _log_import(self, source: str, count: int, data_type: str, file_path: str):
        """记录导入日志"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'source': source,
                'count': count,
                'type': data_type,
                'file_path': file_path,
                'status': 'success'
            }
            
            # 读取现有日志
            if os.path.exists(self.import_log_file):
                with open(self.import_log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # 添加新日志
            logs.append(log_entry)
            
            # 保存日志
            with open(self.import_log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 导入日志记录成功: {source}")
            
        except Exception as e:
            logger.error(f"❌ 导入日志记录失败: {str(e)}")
    
    def get_import_history(self) -> list:
        """获取导入历史"""
        try:
            if os.path.exists(self.import_log_file):
                with open(self.import_log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                return logs
            else:
                return []
                
        except Exception as e:
            logger.error(f"❌ 获取导入历史失败: {str(e)}")
            return []
    
    def monitor_data_directory(self, directory: str, file_patterns: list = None):
        """监控数据目录，自动导入新文件"""
        try:
            if file_patterns is None:
                file_patterns = ['*.csv', '*.json', '*.parquet']
            
            if not os.path.exists(directory):
                logger.warning(f"⚠️ 监控目录不存在: {directory}")
                return
            
            # 获取目录中的文件
            files = []
            for pattern in file_patterns:
                import glob
                files.extend(glob.glob(os.path.join(directory, pattern)))
            
            # 检查每个文件是否需要导入
            for file_path in files:
                file_name = os.path.basename(file_path)
                
                # 检查是否已经导入过
                history = self.get_import_history()
                already_imported = any(
                    log.get('file_path') == file_path and 
                    log.get('status') == 'success'
                    for log in history
                )
                
                if not already_imported:
                    # 根据文件类型导入
                    if file_name.endswith('.csv'):
                        self.import_csv_data(file_path)
                    elif file_name.endswith('.json'):
                        self.import_json_data(file_path)
                    elif file_name.endswith('.parquet'):
                        self.import_parquet_data(file_path)
            
            logger.info(f"✅ 目录监控完成: {directory}")
            
        except Exception as e:
            logger.error(f"❌ 目录监控失败: {str(e)}")

def main():
    """主函数 - 示例用法"""
    trigger = DataImportTrigger()
    
    # 示例1: 导入CSV文件
    csv_file = "caregiver_jobs_5000.csv"
    if os.path.exists(csv_file):
        trigger.import_csv_data(csv_file, "caregiver_jobs_5000")
    
    # 示例2: 导入JSON文件
    json_file = "data/raw/jobs_5000_20250919_180126.json"
    if os.path.exists(json_file):
        trigger.import_json_data(json_file, "jobs_5000_20250919_180126")
    
    # 示例3: 监控数据目录
    data_dir = "data/raw"
    if os.path.exists(data_dir):
        trigger.monitor_data_directory(data_dir)
    
    # 显示导入历史
    history = trigger.get_import_history()
    print(f"导入历史记录: {len(history)} 条")
    for log in history[-5:]:  # 显示最近5条
        print(f"- {log['timestamp']}: {log['source']} ({log['count']} 条记录)")

if __name__ == "__main__":
    main()

