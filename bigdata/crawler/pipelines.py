"""
护工资源管理系统 - 爬虫数据管道
====================================

处理爬虫数据的存储和清洗
"""

import logging
import pymongo
from itemadapter import ItemAdapter
from bigdata_config import MONGODB_CONFIG

logger = logging.getLogger(__name__)

class MongoDBPipeline:
    """MongoDB数据存储管道"""
    
    def __init__(self):
        self.mongo_client = None
        self.db = None
        self.collection = None
    
    def open_spider(self, spider):
        """爬虫开始时初始化数据库连接"""
        try:
            self.mongo_client = pymongo.MongoClient(
                f"mongodb://{MONGODB_CONFIG['MONGODB_HOST']}:{MONGODB_CONFIG['MONGODB_PORT']}/"
            )
            self.db = self.mongo_client[MONGODB_CONFIG['MONGODB_DATABASE']]
            
            # 根据爬虫类型选择不同的集合
            if spider.name == 'caregiver_spider':
                self.collection = self.db['caregiver_jobs']
            elif spider.name == 'news_spider':
                self.collection = self.db['caregiver_news']
            else:
                self.collection = self.db['crawled_data']
            
            logger.info(f"✅ MongoDB连接成功: {spider.name}")
            
        except Exception as e:
            logger.error(f"❌ MongoDB连接失败: {str(e)}")
    
    def close_spider(self, spider):
        """爬虫结束时关闭数据库连接"""
        if self.mongo_client:
            self.mongo_client.close()
            logger.info(f"✅ MongoDB连接已关闭: {spider.name}")
    
    def process_item(self, item, spider):
        """处理爬取的数据项"""
        try:
            adapter = ItemAdapter(item)
            
            # 数据验证和清洗
            cleaned_item = self.clean_item(adapter.asdict())
            
            # 检查是否已存在（避免重复）
            if self.is_duplicate(cleaned_item):
                logger.info(f"跳过重复数据: {cleaned_item.get('title', 'Unknown')}")
                return item
            
            # 插入数据
            result = self.collection.insert_one(cleaned_item)
            logger.info(f"✅ 数据插入成功: {result.inserted_id}")
            
            return item
            
        except Exception as e:
            logger.error(f"❌ 数据处理失败: {str(e)}")
            return item
    
    def clean_item(self, item):
        """清洗数据项"""
        # 移除空值
        cleaned = {k: v for k, v in item.items() if v is not None and v != ''}
        
        # 标准化字段
        if 'title' in cleaned:
            cleaned['title'] = cleaned['title'].strip()
        
        if 'company' in cleaned:
            cleaned['company'] = cleaned['company'].strip()
        
        if 'location' in cleaned:
            cleaned['location'] = cleaned['location'].strip()
        
        # 添加数据质量标记
        cleaned['data_quality'] = self.assess_data_quality(cleaned)
        
        return cleaned
    
    def assess_data_quality(self, item):
        """评估数据质量"""
        score = 0
        required_fields = ['title', 'crawl_time']
        
        # 检查必需字段
        for field in required_fields:
            if field in item and item[field]:
                score += 1
        
        # 检查可选字段
        optional_fields = ['company', 'salary', 'location']
        for field in optional_fields:
            if field in item and item[field]:
                score += 0.5
        
        return min(score / len(required_fields + optional_fields), 1.0)
    
    def is_duplicate(self, item):
        """检查是否为重复数据"""
        try:
            # 基于标题和公司名称检查重复
            query = {
                'title': item.get('title'),
                'company': item.get('company')
            }
            
            existing = self.collection.find_one(query)
            return existing is not None
            
        except Exception as e:
            logger.error(f"检查重复数据失败: {str(e)}")
            return False

class DataValidationPipeline:
    """数据验证管道"""
    
    def process_item(self, item, spider):
        """验证数据项"""
        adapter = ItemAdapter(item)
        
        # 验证必需字段
        if not adapter.get('title'):
            raise DropItem("缺少标题字段")
        
        if not adapter.get('crawl_time'):
            raise DropItem("缺少爬取时间字段")
        
        # 验证数据格式
        if adapter.get('salary_min') and not isinstance(adapter.get('salary_min'), (int, float)):
            adapter['salary_min'] = None
        
        if adapter.get('salary_max') and not isinstance(adapter.get('salary_max'), (int, float)):
            adapter['salary_max'] = None
        
        return item

class DuplicatesPipeline:
    """去重管道"""
    
    def __init__(self):
        self.seen = set()
    
    def process_item(self, item, spider):
        """去重处理"""
        adapter = ItemAdapter(item)
        
        # 创建唯一标识
        identifier = f"{adapter.get('title', '')}_{adapter.get('company', '')}"
        
        if identifier in self.seen:
            raise DropItem(f"重复数据: {identifier}")
        else:
            self.seen.add(identifier)
            return item
