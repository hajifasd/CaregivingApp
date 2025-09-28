"""
护工资源管理系统 - Spark数据处理
====================================

使用Spark进行大规模数据处理和分析
"""

import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml.feature import VectorAssembler, StringIndexer, OneHotEncoder
from pyspark.ml import Pipeline
import logging
from bigdata_config import SPARK_CONFIG, DATA_PATHS

logger = logging.getLogger(__name__)

class SparkDataProcessor:
    """Spark数据处理类"""
    
    def __init__(self):
        self.spark = None
        self.initialize_spark()
    
    def initialize_spark(self):
        """初始化Spark会话"""
        try:
            self.spark = SparkSession.builder \
                .appName(SPARK_CONFIG['SPARK_APP_NAME']) \
                .master(SPARK_CONFIG['SPARK_MASTER']) \
                .config("spark.driver.memory", SPARK_CONFIG['SPARK_DRIVER_MEMORY']) \
                .config("spark.executor.memory", SPARK_CONFIG['SPARK_EXECUTOR_MEMORY']) \
                .config("spark.executor.cores", SPARK_CONFIG['SPARK_EXECUTOR_CORES']) \
                .config("spark.sql.adaptive.enabled", SPARK_CONFIG['SPARK_SQL_ADAPTIVE_ENABLED']) \
                .config("spark.sql.adaptive.coalescePartitions.enabled", SPARK_CONFIG['SPARK_SQL_ADAPTIVE_COALESCE_PARTITIONS_ENABLED']) \
                .getOrCreate()
            
            logger.info("✅ Spark会话初始化成功")
            
        except Exception as e:
            logger.error(f"❌ Spark初始化失败: {str(e)}")
            raise
    
    def load_caregiver_data(self):
        """加载护工数据"""
        try:
            # 从MySQL加载护工数据
            caregiver_df = self.spark.read \
                .format("jdbc") \
                .option("url", "jdbc:mysql://localhost:3306/caregiving_db") \
                .option("dbtable", "caregiver") \
                .option("user", "root") \
                .option("password", "20040924") \
                .load()
            
            logger.info(f"✅ 护工数据加载成功: {caregiver_df.count()} 条记录")
            return caregiver_df
            
        except Exception as e:
            logger.error(f"❌ 护工数据加载失败: {str(e)}")
            return None
    
    def load_user_data(self):
        """加载用户数据"""
        try:
            user_df = self.spark.read \
                .format("jdbc") \
                .option("url", "jdbc:mysql://localhost:3306/caregiving_db") \
                .option("dbtable", "user") \
                .option("user", "root") \
                .option("password", "20040924") \
                .load()
            
            logger.info(f"✅ 用户数据加载成功: {user_df.count()} 条记录")
            return user_df
            
        except Exception as e:
            logger.error(f"❌ 用户数据加载失败: {str(e)}")
            return None
    
    def load_appointment_data(self):
        """加载预约数据"""
        try:
            appointment_df = self.spark.read \
                .format("jdbc") \
                .option("url", "jdbc:mysql://localhost:3306/caregiving_db") \
                .option("dbtable", "appointment") \
                .option("user", "root") \
                .option("password", "20040924") \
                .load()
            
            logger.info(f"✅ 预约数据加载成功: {appointment_df.count()} 条记录")
            return appointment_df
            
        except Exception as e:
            logger.error(f"❌ 预约数据加载失败: {str(e)}")
            return None
    
    def load_crawled_data(self):
        """加载爬虫数据"""
        try:
            # 从MongoDB加载爬虫数据
            crawled_df = self.spark.read \
                .format("mongo") \
                .option("uri", "mongodb://localhost:27017/caregiver_analytics.caregiver_jobs") \
                .load()
            
            logger.info(f"✅ 爬虫数据加载成功: {crawled_df.count()} 条记录")
            return crawled_df
            
        except Exception as e:
            logger.error(f"❌ 爬虫数据加载失败: {str(e)}")
            return None
    
    def clean_caregiver_data(self, df):
        """清洗护工数据"""
        try:
            # 移除空值
            cleaned_df = df.filter(col("name").isNotNull() & col("phone").isNotNull())
            
            # 标准化年龄字段
            cleaned_df = cleaned_df.withColumn(
                "age_clean", 
                when(col("age").isNull(), 0).otherwise(col("age"))
            )
            
            # 标准化时薪字段
            cleaned_df = cleaned_df.withColumn(
                "hourly_rate_clean",
                when(col("hourly_rate").isNull(), 0.0).otherwise(col("hourly_rate"))
            )
            
            # 标准化评分字段
            cleaned_df = cleaned_df.withColumn(
                "rating_clean",
                when(col("rating").isNull(), 0.0).otherwise(col("rating"))
            )
            
            # 添加数据质量标记
            cleaned_df = cleaned_df.withColumn(
                "data_quality",
                when(col("name").isNotNull() & col("phone").isNotNull() & 
                     col("age_clean") > 0 & col("hourly_rate_clean") > 0, 1.0)
                .otherwise(0.5)
            )
            
            logger.info("✅ 护工数据清洗完成")
            return cleaned_df
            
        except Exception as e:
            logger.error(f"❌ 护工数据清洗失败: {str(e)}")
            return df
    
    def clean_crawled_data(self, df):
        """清洗爬虫数据"""
        try:
            # 移除空值
            cleaned_df = df.filter(col("title").isNotNull())
            
            # 标准化薪资字段
            cleaned_df = cleaned_df.withColumn(
                "salary_avg_clean",
                when(col("salary_avg").isNull(), 0.0).otherwise(col("salary_avg"))
            )
            
            # 提取地点信息
            cleaned_df = cleaned_df.withColumn(
                "city",
                when(col("location").contains("北京"), "北京")
                .when(col("location").contains("上海"), "上海")
                .when(col("location").contains("广州"), "广州")
                .when(col("location").contains("深圳"), "深圳")
                .otherwise("其他")
            )
            
            # 提取服务类型
            cleaned_df = cleaned_df.withColumn(
                "service_type",
                when(col("title").contains("养老"), "养老护理")
                .when(col("title").contains("康复"), "康复护理")
                .when(col("title").contains("医疗"), "医疗护理")
                .otherwise("综合护理")
            )
            
            logger.info("✅ 爬虫数据清洗完成")
            return cleaned_df
            
        except Exception as e:
            logger.error(f"❌ 爬虫数据清洗失败: {str(e)}")
            return df
    
    def create_features(self, df):
        """创建特征工程"""
        try:
            # 字符串索引化
            string_indexer = StringIndexer(
                inputCols=["gender", "service_type", "city"],
                outputCols=["gender_index", "service_type_index", "city_index"]
            )
            
            # 独热编码
            one_hot_encoder = OneHotEncoder(
                inputCols=["gender_index", "service_type_index", "city_index"],
                outputCols=["gender_vec", "service_type_vec", "city_vec"]
            )
            
            # 特征向量化
            feature_columns = ["age_clean", "hourly_rate_clean", "rating_clean", 
                             "gender_vec", "service_type_vec", "city_vec"]
            
            vector_assembler = VectorAssembler(
                inputCols=feature_columns,
                outputCol="features"
            )
            
            # 创建管道
            pipeline = Pipeline(stages=[string_indexer, one_hot_encoder, vector_assembler])
            
            # 训练管道
            model = pipeline.fit(df)
            features_df = model.transform(df)
            
            logger.info("✅ 特征工程完成")
            return features_df
            
        except Exception as e:
            logger.error(f"❌ 特征工程失败: {str(e)}")
            return df
    
    def calculate_statistics(self, df):
        """计算统计信息"""
        try:
            stats = df.select(
                count("*").alias("total_count"),
                avg("age_clean").alias("avg_age"),
                avg("hourly_rate_clean").alias("avg_hourly_rate"),
                avg("rating_clean").alias("avg_rating"),
                min("hourly_rate_clean").alias("min_hourly_rate"),
                max("hourly_rate_clean").alias("max_hourly_rate")
            ).collect()[0]
            
            logger.info("✅ 统计信息计算完成")
            return stats
            
        except Exception as e:
            logger.error(f"❌ 统计信息计算失败: {str(e)}")
            return None
    
    def save_processed_data(self, df, table_name):
        """保存处理后的数据"""
        try:
            # 保存到HDFS
            df.write \
                .mode("overwrite") \
                .parquet(f"{DATA_PATHS['PROCESSED_DATA']}/{table_name}")
            
            logger.info(f"✅ 数据保存成功: {table_name}")
            
        except Exception as e:
            logger.error(f"❌ 数据保存失败: {str(e)}")
    
    def process_all_data(self):
        """处理所有数据"""
        try:
            logger.info("🚀 开始数据处理流程")
            
            # 加载数据
            caregiver_df = self.load_caregiver_data()
            user_df = self.load_user_data()
            appointment_df = self.load_appointment_data()
            crawled_df = self.load_crawled_data()
            
            if caregiver_df:
                # 清洗护工数据
                cleaned_caregiver_df = self.clean_caregiver_data(caregiver_df)
                
                # 创建特征
                features_caregiver_df = self.create_features(cleaned_caregiver_df)
                
                # 计算统计信息
                stats = self.calculate_statistics(cleaned_caregiver_df)
                logger.info(f"护工数据统计: {stats}")
                
                # 保存处理后的数据
                self.save_processed_data(features_caregiver_df, "caregiver_features")
            
            if crawled_df:
                # 清洗爬虫数据
                cleaned_crawled_df = self.clean_crawled_data(crawled_df)
                
                # 保存处理后的数据
                self.save_processed_data(cleaned_crawled_df, "crawled_data_clean")
            
            logger.info("✅ 数据处理流程完成")
            
        except Exception as e:
            logger.error(f"❌ 数据处理流程失败: {str(e)}")
    
    def close(self):
        """关闭Spark会话"""
        if self.spark:
            self.spark.stop()
            logger.info("✅ Spark会话已关闭")

def main():
    """主函数"""
    processor = SparkDataProcessor()
    try:
        processor.process_all_data()
    finally:
        processor.close()

if __name__ == "__main__":
    main()
