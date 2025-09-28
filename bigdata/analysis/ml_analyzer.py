"""
护工资源管理系统 - 机器学习分析
====================================

使用机器学习算法进行数据分析和预测
"""

import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark.ml.classification import RandomForestClassifier, LogisticRegression
from pyspark.ml.regression import RandomForestRegressor, LinearRegression
from pyspark.ml.clustering import KMeans
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import MulticlassClassificationEvaluator, RegressionEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.sql.functions import *
import numpy as np
import pandas as pd
import logging
from bigdata_config import SPARK_CONFIG, ML_CONFIG, DATA_PATHS

logger = logging.getLogger(__name__)

class MLAnalyzer:
    """机器学习分析类"""
    
    def __init__(self):
        self.spark = None
        self.initialize_spark()
    
    def initialize_spark(self):
        """初始化Spark会话"""
        try:
            self.spark = SparkSession.builder \
                .appName("CaregiverMLAnalysis") \
                .master(SPARK_CONFIG['SPARK_MASTER']) \
                .config("spark.driver.memory", "4g") \
                .config("spark.executor.memory", "2g") \
                .getOrCreate()
            
            logger.info("✅ Spark ML会话初始化成功")
            
        except Exception as e:
            logger.error(f"❌ Spark ML初始化失败: {str(e)}")
            raise
    
    def load_processed_data(self):
        """加载处理后的数据"""
        try:
            # 加载护工特征数据
            caregiver_df = self.spark.read.parquet(f"{DATA_PATHS['PROCESSED_DATA']}/caregiver_features")
            
            # 加载爬虫数据
            crawled_df = self.spark.read.parquet(f"{DATA_PATHS['PROCESSED_DATA']}/crawled_data_clean")
            
            logger.info("✅ 处理后数据加载成功")
            return caregiver_df, crawled_df
            
        except Exception as e:
            logger.error(f"❌ 处理后数据加载失败: {str(e)}")
            return None, None
    
    def predict_success_rate(self, df):
        """预测护工成功率"""
        try:
            # 准备训练数据
            # 假设我们有历史成功率数据
            training_df = df.withColumn(
                "success_rate",
                when(col("rating_clean") >= 4.0, 1.0)
                .when(col("rating_clean") >= 3.0, 0.7)
                .when(col("rating_clean") >= 2.0, 0.4)
                .otherwise(0.1)
            )
            
            # 分割训练和测试数据
            train_data, test_data = training_df.randomSplit([0.8, 0.2], seed=42)
            
            # 创建随机森林回归器
            rf = RandomForestRegressor(
                featuresCol="features",
                labelCol="success_rate",
                numTrees=100,
                maxDepth=10,
                seed=42
            )
            
            # 训练模型
            model = rf.fit(train_data)
            
            # 预测
            predictions = model.transform(test_data)
            
            # 评估模型
            evaluator = RegressionEvaluator(
                labelCol="success_rate",
                predictionCol="prediction",
                metricName="rmse"
            )
            
            rmse = evaluator.evaluate(predictions)
            logger.info(f"✅ 成功率预测模型RMSE: {rmse}")
            
            # 保存模型
            model.write().overwrite().save(f"{ML_CONFIG['MODEL_SAVE_PATH']}/success_rate_model")
            
            return model, predictions
            
        except Exception as e:
            logger.error(f"❌ 成功率预测失败: {str(e)}")
            return None, None
    
    def cluster_caregivers(self, df):
        """护工聚类分析"""
        try:
            # 使用K-means聚类
            kmeans = KMeans(
                featuresCol="features",
                k=5,  # 5个聚类
                seed=42
            )
            
            # 训练模型
            model = kmeans.fit(df)
            
            # 预测聚类
            predictions = model.transform(df)
            
            # 分析聚类结果
            cluster_stats = predictions.groupBy("prediction").agg(
                count("*").alias("count"),
                avg("hourly_rate_clean").alias("avg_hourly_rate"),
                avg("rating_clean").alias("avg_rating"),
                avg("age_clean").alias("avg_age")
            ).orderBy("prediction")
            
            logger.info("✅ 护工聚类分析完成")
            cluster_stats.show()
            
            # 保存模型
            model.write().overwrite().save(f"{ML_CONFIG['MODEL_SAVE_PATH']}/caregiver_cluster_model")
            
            return model, predictions
            
        except Exception as e:
            logger.error(f"❌ 护工聚类分析失败: {str(e)}")
            return None, None
    
    def recommend_caregivers(self, user_df, caregiver_df, appointment_df):
        """护工推荐系统"""
        try:
            # 准备推荐数据
            # 基于用户对护工的评价创建推荐数据
            recommendation_data = appointment_df.join(
                user_df, appointment_df.user_id == user_df.id
            ).join(
                caregiver_df, appointment_df.caregiver_id == caregiver_df.id
            ).select(
                col("user_id").cast("int"),
                col("caregiver_id").cast("int"),
                col("rating_clean").alias("rating")
            ).filter(col("rating").isNotNull())
            
            # 分割训练和测试数据
            train_data, test_data = recommendation_data.randomSplit([0.8, 0.2], seed=42)
            
            # 创建ALS推荐模型
            als = ALS(
                maxIter=10,
                regParam=0.01,
                userCol="user_id",
                itemCol="caregiver_id",
                ratingCol="rating",
                coldStartStrategy="drop"
            )
            
            # 训练模型
            model = als.fit(train_data)
            
            # 预测
            predictions = model.transform(test_data)
            
            # 评估模型
            evaluator = RegressionEvaluator(
                metricName="rmse",
                labelCol="rating",
                predictionCol="prediction"
            )
            
            rmse = evaluator.evaluate(predictions)
            logger.info(f"✅ 推荐系统RMSE: {rmse}")
            
            # 保存模型
            model.write().overwrite().save(f"{ML_CONFIG['MODEL_SAVE_PATH']}/recommendation_model")
            
            return model, predictions
            
        except Exception as e:
            logger.error(f"❌ 推荐系统训练失败: {str(e)}")
            return None, None
    
    def predict_demand(self, df):
        """预测护工需求"""
        try:
            # 基于历史数据预测需求
            # 这里简化处理，实际应该基于时间序列数据
            
            # 创建需求预测特征
            demand_df = df.groupBy("city", "service_type").agg(
                count("*").alias("demand_count"),
                avg("hourly_rate_clean").alias("avg_rate"),
                avg("rating_clean").alias("avg_rating")
            )
            
            # 使用线性回归预测需求
            from pyspark.ml.feature import VectorAssembler
            
            assembler = VectorAssembler(
                inputCols=["avg_rate", "avg_rating"],
                outputCol="features"
            )
            
            demand_features = assembler.transform(demand_df)
            
            # 创建线性回归模型
            lr = LinearRegression(
                featuresCol="features",
                labelCol="demand_count"
            )
            
            # 训练模型
            model = lr.fit(demand_features)
            
            # 预测
            predictions = model.transform(demand_features)
            
            # 评估模型
            evaluator = RegressionEvaluator(
                labelCol="demand_count",
                predictionCol="prediction",
                metricName="rmse"
            )
            
            rmse = evaluator.evaluate(predictions)
            logger.info(f"✅ 需求预测模型RMSE: {rmse}")
            
            # 保存模型
            model.write().overwrite().save(f"{ML_CONFIG['MODEL_SAVE_PATH']}/demand_prediction_model")
            
            return model, predictions
            
        except Exception as e:
            logger.error(f"❌ 需求预测失败: {str(e)}")
            return None, None
    
    def analyze_market_trends(self, crawled_df):
        """分析市场趋势"""
        try:
            # 分析薪资趋势
            salary_trend = crawled_df.groupBy("city", "service_type").agg(
                avg("salary_avg_clean").alias("avg_salary"),
                count("*").alias("job_count"),
                min("salary_avg_clean").alias("min_salary"),
                max("salary_avg_clean").alias("max_salary")
            ).orderBy("avg_salary", ascending=False)
            
            # 分析需求趋势
            demand_trend = crawled_df.groupBy("city").agg(
                count("*").alias("total_jobs"),
                countDistinct("service_type").alias("service_types"),
                avg("salary_avg_clean").alias("avg_salary")
            ).orderBy("total_jobs", ascending=False)
            
            logger.info("✅ 市场趋势分析完成")
            
            # 保存分析结果
            salary_trend.write.mode("overwrite").parquet(f"{DATA_PATHS['ANALYSIS_RESULTS']}/salary_trend")
            demand_trend.write.mode("overwrite").parquet(f"{DATA_PATHS['ANALYSIS_RESULTS']}/demand_trend")
            
            return salary_trend, demand_trend
            
        except Exception as e:
            logger.error(f"❌ 市场趋势分析失败: {str(e)}")
            return None, None
    
    def run_all_analysis(self):
        """运行所有分析"""
        try:
            logger.info("🚀 开始机器学习分析")
            
            # 加载数据
            caregiver_df, crawled_df = self.load_processed_data()
            
            if caregiver_df is None:
                logger.error("❌ 无法加载护工数据")
                return
            
            # 1. 预测护工成功率
            logger.info("📊 开始成功率预测分析")
            success_model, success_predictions = self.predict_success_rate(caregiver_df)
            
            # 2. 护工聚类分析
            logger.info("📊 开始护工聚类分析")
            cluster_model, cluster_predictions = self.cluster_caregivers(caregiver_df)
            
            # 3. 市场趋势分析
            if crawled_df is not None:
                logger.info("📊 开始市场趋势分析")
                salary_trend, demand_trend = self.analyze_market_trends(crawled_df)
            
            # 4. 需求预测
            logger.info("📊 开始需求预测分析")
            demand_model, demand_predictions = self.predict_demand(caregiver_df)
            
            logger.info("✅ 机器学习分析完成")
            
        except Exception as e:
            logger.error(f"❌ 机器学习分析失败: {str(e)}")
    
    def close(self):
        """关闭Spark会话"""
        if self.spark:
            self.spark.stop()
            logger.info("✅ Spark ML会话已关闭")

def main():
    """主函数"""
    analyzer = MLAnalyzer()
    try:
        analyzer.run_all_analysis()
    finally:
        analyzer.close()

if __name__ == "__main__":
    main()
