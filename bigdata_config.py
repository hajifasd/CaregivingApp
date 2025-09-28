"""
护工资源管理系统 - 大数据配置
====================================

大数据技术栈配置文件
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ==================== 大数据技术栈配置 ====================

# Hadoop配置
HADOOP_CONFIG = {
    'HDFS_NAMENODE': os.getenv('HDFS_NAMENODE', 'hdfs://localhost:9000'),
    'HDFS_USER': os.getenv('HDFS_USER', 'hadoop'),
    'HDFS_DATA_DIR': '/caregiver_data',
    'HDFS_LOG_DIR': '/caregiver_logs'
}

# Hive配置
HIVE_CONFIG = {
    'HIVE_HOST': os.getenv('HIVE_HOST', 'localhost'),
    'HIVE_PORT': os.getenv('HIVE_PORT', '10000'),
    'HIVE_DATABASE': os.getenv('HIVE_DATABASE', 'caregiver_warehouse'),
    'HIVE_USER': os.getenv('HIVE_USER', 'hive'),
    'HIVE_PASSWORD': os.getenv('HIVE_PASSWORD', 'hive')
}

# Spark配置
SPARK_CONFIG = {
    'SPARK_MASTER': os.getenv('SPARK_MASTER', 'local[*]'),
    'SPARK_APP_NAME': 'CaregiverDataAnalysis',
    'SPARK_DRIVER_MEMORY': '4g',
    'SPARK_EXECUTOR_MEMORY': '2g',
    'SPARK_EXECUTOR_CORES': '2',
    'SPARK_SQL_ADAPTIVE_ENABLED': 'true',
    'SPARK_SQL_ADAPTIVE_COALESCE_PARTITIONS_ENABLED': 'true'
}

# MongoDB配置
MONGODB_CONFIG = {
    'MONGODB_HOST': os.getenv('MONGODB_HOST', 'localhost'),
    'MONGODB_PORT': int(os.getenv('MONGODB_PORT', '27017')),
    'MONGODB_DATABASE': os.getenv('MONGODB_DATABASE', 'caregiver_analytics'),
    'MONGODB_USER': os.getenv('MONGODB_USER', ''),
    'MONGODB_PASSWORD': os.getenv('MONGODB_PASSWORD', '')
}

# Redis配置
REDIS_CONFIG = {
    'REDIS_HOST': os.getenv('REDIS_HOST', 'localhost'),
    'REDIS_PORT': int(os.getenv('REDIS_PORT', '6379')),
    'REDIS_DB': int(os.getenv('REDIS_DB', '0')),
    'REDIS_PASSWORD': os.getenv('REDIS_PASSWORD', '')
}

# 爬虫配置
CRAWLER_CONFIG = {
    'CRAWLER_DELAY': 1,  # 爬取延迟（秒）
    'CRAWLER_CONCURRENT_REQUESTS': 16,
    'CRAWLER_USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'CRAWLER_TARGET_SITES': [
        'https://www.zhaopin.com',
        'https://www.51job.com',
        'https://www.liepin.com',
        'https://www.bosszhipin.com'
    ]
}

# 机器学习配置
ML_CONFIG = {
    'MODEL_SAVE_PATH': './models',
    'TRAINING_DATA_PATH': './data/training',
    'TEST_DATA_PATH': './data/test',
    'FEATURE_COLUMNS': [
        'age', 'experience_years', 'hourly_rate', 'rating',
        'service_type', 'location', 'gender'
    ],
    'TARGET_COLUMN': 'success_rate'
}

# 数据可视化配置
VISUALIZATION_CONFIG = {
    'CHART_THEME': 'plotly_white',
    'COLOR_PALETTE': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
    'DASHBOARD_REFRESH_INTERVAL': 30,  # 秒
    'MAX_DATA_POINTS': 10000
}

# 数据存储路径配置
DATA_PATHS = {
    'RAW_DATA': './data/raw',
    'PROCESSED_DATA': './data/processed',
    'ANALYSIS_RESULTS': './data/analysis',
    'MODELS': './models',
    'LOGS': './logs',
    'UPLOADS': './web/uploads'
}

# 创建必要的目录
def create_directories():
    """创建必要的目录结构"""
    import os
    for path in DATA_PATHS.values():
        os.makedirs(path, exist_ok=True)
        print(f"✅ 创建目录: {path}")

if __name__ == "__main__":
    create_directories()
