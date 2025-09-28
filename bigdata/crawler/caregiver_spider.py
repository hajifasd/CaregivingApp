"""
护工资源管理系统 - 网络爬虫
====================================

爬取护工相关的招聘信息和市场数据
"""

import scrapy
import json
import time
import logging
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import pymongo
from bigdata_config import MONGODB_CONFIG, CRAWLER_CONFIG

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CaregiverSpider(scrapy.Spider):
    """护工招聘信息爬虫"""
    
    name = 'caregiver_spider'
    allowed_domains = ['zhaopin.com', '51job.com', 'liepin.com', 'bosszhipin.com']
    
    def __init__(self):
        super().__init__()
        self.mongo_client = pymongo.MongoClient(
            f"mongodb://{MONGODB_CONFIG['MONGODB_HOST']}:{MONGODB_CONFIG['MONGODB_PORT']}/"
        )
        self.db = self.mongo_client[MONGODB_CONFIG['MONGODB_DATABASE']]
        self.collection = self.db['caregiver_jobs']
        
    def start_requests(self):
        """开始爬取请求"""
        urls = [
            'https://sou.zhaopin.com/?jl=北京&kw=护工&kt=3',
            'https://sou.zhaopin.com/?jl=上海&kw=护工&kt=3',
            'https://sou.zhaopin.com/?jl=广州&kw=护工&kt=3',
            'https://sou.zhaopin.com/?jl=深圳&kw=护工&kt=3',
            'https://search.51job.com/list/010000,000000,0000,00,9,99,护工,2,1.html',
            'https://search.51job.com/list/020000,000000,0000,00,9,99,护工,2,1.html',
        ]
        
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                headers={'User-Agent': CRAWLER_CONFIG['CRAWLER_USER_AGENT']},
                meta={'dont_cache': True}
            )
    
    def parse(self, response):
        """解析招聘信息页面"""
        try:
            # 智联招聘解析
            if 'zhaopin.com' in response.url:
                yield from self.parse_zhaopin(response)
            # 前程无忧解析
            elif '51job.com' in response.url:
                yield from self.parse_51job(response)
                
        except Exception as e:
            logger.error(f"解析页面失败: {response.url}, 错误: {str(e)}")
    
    def parse_zhaopin(self, response):
        """解析智联招聘页面"""
        job_items = response.css('.joblist-box .joblist-box-item')
        
        for job in job_items:
            try:
                job_data = {
                    'source': '智联招聘',
                    'title': job.css('.job-name a::text').get(),
                    'company': job.css('.company-name a::text').get(),
                    'salary': job.css('.job-salary::text').get(),
                    'location': job.css('.job-area::text').get(),
                    'experience': job.css('.job-require span:nth-child(1)::text').get(),
                    'education': job.css('.job-require span:nth-child(2)::text').get(),
                    'job_type': job.css('.job-require span:nth-child(3)::text').get(),
                    'publish_time': job.css('.job-time::text').get(),
                    'job_url': job.css('.job-name a::attr(href)').get(),
                    'crawl_time': datetime.now().isoformat(),
                    'crawl_url': response.url
                }
                
                # 清理数据
                job_data = self.clean_job_data(job_data)
                
                if job_data['title'] and '护工' in job_data['title']:
                    yield job_data
                    
            except Exception as e:
                logger.error(f"解析智联招聘职位失败: {str(e)}")
    
    def parse_51job(self, response):
        """解析前程无忧页面"""
        job_items = response.css('.el .t1')
        
        for job in job_items:
            try:
                job_data = {
                    'source': '前程无忧',
                    'title': job.css('.t1 a::text').get(),
                    'company': job.css('.t2 a::text').get(),
                    'location': job.css('.t3::text').get(),
                    'salary': job.css('.t4::text').get(),
                    'publish_time': job.css('.t5::text').get(),
                    'job_url': job.css('.t1 a::attr(href)').get(),
                    'crawl_time': datetime.now().isoformat(),
                    'crawl_url': response.url
                }
                
                # 清理数据
                job_data = self.clean_job_data(job_data)
                
                if job_data['title'] and '护工' in job_data['title']:
                    yield job_data
                    
            except Exception as e:
                logger.error(f"解析前程无忧职位失败: {str(e)}")
    
    def clean_job_data(self, job_data):
        """清理和标准化职位数据"""
        # 清理标题
        if job_data.get('title'):
            job_data['title'] = job_data['title'].strip()
        
        # 清理公司名称
        if job_data.get('company'):
            job_data['company'] = job_data['company'].strip()
        
        # 清理薪资信息
        if job_data.get('salary'):
            salary = job_data['salary'].strip()
            # 提取数字部分
            import re
            salary_numbers = re.findall(r'\d+', salary)
            if salary_numbers:
                job_data['salary_min'] = int(salary_numbers[0]) if len(salary_numbers) > 0 else None
                job_data['salary_max'] = int(salary_numbers[1]) if len(salary_numbers) > 1 else None
                job_data['salary_avg'] = (job_data['salary_min'] + job_data['salary_max']) / 2 if job_data['salary_min'] and job_data['salary_max'] else None
        
        # 清理地点信息
        if job_data.get('location'):
            job_data['location'] = job_data['location'].strip()
        
        return job_data
    
    def closed(self, reason):
        """爬虫关闭时的处理"""
        logger.info(f"爬虫关闭: {reason}")
        self.mongo_client.close()

class NewsSpider(scrapy.Spider):
    """护工行业新闻爬虫"""
    
    name = 'news_spider'
    allowed_domains = ['people.com.cn', 'xinhuanet.com', 'chinanews.com']
    
    def start_requests(self):
        """开始爬取新闻"""
        urls = [
            'http://health.people.com.cn/',
            'http://www.xinhuanet.com/health/',
            'http://www.chinanews.com/gn/',
        ]
        
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_news,
                headers={'User-Agent': CRAWLER_CONFIG['CRAWLER_USER_AGENT']}
            )
    
    def parse_news(self, response):
        """解析新闻页面"""
        news_items = response.css('a[href*="护工"], a[href*="护理"], a[href*="养老"]')
        
        for news in news_items:
            try:
                news_data = {
                    'title': news.css('::text').get(),
                    'url': news.css('::attr(href)').get(),
                    'source': response.url,
                    'crawl_time': datetime.now().isoformat()
                }
                
                if news_data['title'] and len(news_data['title'].strip()) > 10:
                    yield news_data
                    
            except Exception as e:
                logger.error(f"解析新闻失败: {str(e)}")

def run_spiders():
    """运行爬虫"""
    settings = get_project_settings()
    settings.update({
        'USER_AGENT': CRAWLER_CONFIG['CRAWLER_USER_AGENT'],
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': CRAWLER_CONFIG['CRAWLER_DELAY'],
        'CONCURRENT_REQUESTS': CRAWLER_CONFIG['CRAWLER_CONCURRENT_REQUESTS'],
        'ITEM_PIPELINES': {
            'bigdata.crawler.pipelines.MongoDBPipeline': 300,
        }
    })
    
    process = CrawlerProcess(settings)
    process.crawl(CaregiverSpider)
    process.crawl(NewsSpider)
    process.start()

if __name__ == "__main__":
    run_spiders()
