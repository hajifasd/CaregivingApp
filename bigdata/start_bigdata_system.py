"""
护工资源管理系统 - 大数据系统启动脚本
====================================

启动大数据技术栈的各个组件
"""

import os
import sys
import subprocess
import time
import logging
from bigdata_config import create_directories

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BigDataSystemStarter:
    """大数据系统启动器"""
    
    def __init__(self):
        self.processes = {}
    
    def start_hadoop(self):
        """启动Hadoop服务"""
        try:
            logger.info("🚀 启动Hadoop服务...")
            
            # 启动HDFS
            hdfs_process = subprocess.Popen(
                ['start-dfs.sh'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes['hdfs'] = hdfs_process
            
            # 启动YARN
            yarn_process = subprocess.Popen(
                ['start-yarn.sh'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes['yarn'] = yarn_process
            
            logger.info("✅ Hadoop服务启动成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ Hadoop服务启动失败: {str(e)}")
            return False
    
    def start_spark(self):
        """启动Spark服务"""
        try:
            logger.info("🚀 启动Spark服务...")
            
            # 启动Spark Master
            spark_master = subprocess.Popen(
                ['$SPARK_HOME/sbin/start-master.sh'],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes['spark_master'] = spark_master
            
            # 启动Spark Worker
            spark_worker = subprocess.Popen(
                ['$SPARK_HOME/sbin/start-worker.sh spark://localhost:7077'],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes['spark_worker'] = spark_worker
            
            logger.info("✅ Spark服务启动成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ Spark服务启动失败: {str(e)}")
            return False
    
    def start_mongodb(self):
        """启动MongoDB服务"""
        try:
            logger.info("🚀 启动MongoDB服务...")
            
            mongodb_process = subprocess.Popen(
                ['mongod', '--dbpath', './data/mongodb'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes['mongodb'] = mongodb_process
            
            logger.info("✅ MongoDB服务启动成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ MongoDB服务启动失败: {str(e)}")
            return False
    
    def start_redis(self):
        """启动Redis服务"""
        try:
            logger.info("🚀 启动Redis服务...")
            
            redis_process = subprocess.Popen(
                ['redis-server'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes['redis'] = redis_process
            
            logger.info("✅ Redis服务启动成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ Redis服务启动失败: {str(e)}")
            return False
    
    def start_crawler(self):
        """启动爬虫服务"""
        try:
            logger.info("🚀 启动爬虫服务...")
            
            crawler_process = subprocess.Popen(
                [sys.executable, 'bigdata/crawler/caregiver_spider.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes['crawler'] = crawler_process
            
            logger.info("✅ 爬虫服务启动成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 爬虫服务启动失败: {str(e)}")
            return False
    
    def start_data_processing(self):
        """启动数据处理服务"""
        try:
            logger.info("🚀 启动数据处理服务...")
            
            processing_process = subprocess.Popen(
                [sys.executable, 'bigdata/processing/spark_processor.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes['data_processing'] = processing_process
            
            logger.info("✅ 数据处理服务启动成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 数据处理服务启动失败: {str(e)}")
            return False
    
    def start_ml_analysis(self):
        """启动机器学习分析服务"""
        try:
            logger.info("🚀 启动机器学习分析服务...")
            
            ml_process = subprocess.Popen(
                [sys.executable, 'bigdata/analysis/ml_analyzer.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes['ml_analysis'] = ml_process
            
            logger.info("✅ 机器学习分析服务启动成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 机器学习分析服务启动失败: {str(e)}")
            return False
    
    def check_services_status(self):
        """检查服务状态"""
        try:
            logger.info("🔍 检查服务状态...")
            
            status = {}
            
            # 检查Hadoop
            try:
                result = subprocess.run(['hdfs', 'dfsadmin', '-report'], 
                                      capture_output=True, text=True, timeout=10)
                status['hadoop'] = 'running' if result.returncode == 0 else 'stopped'
            except:
                status['hadoop'] = 'stopped'
            
            # 检查Spark
            try:
                result = subprocess.run(['curl', '-s', 'http://localhost:8080'], 
                                      capture_output=True, text=True, timeout=5)
                status['spark'] = 'running' if result.returncode == 0 else 'stopped'
            except:
                status['spark'] = 'stopped'
            
            # 检查MongoDB
            try:
                result = subprocess.run(['mongosh', '--eval', 'db.runCommand("ping")'], 
                                      capture_output=True, text=True, timeout=5)
                status['mongodb'] = 'running' if result.returncode == 0 else 'stopped'
            except:
                status['mongodb'] = 'stopped'
            
            # 检查Redis
            try:
                result = subprocess.run(['redis-cli', 'ping'], 
                                      capture_output=True, text=True, timeout=5)
                status['redis'] = 'running' if 'PONG' in result.stdout else 'stopped'
            except:
                status['redis'] = 'stopped'
            
            logger.info(f"📊 服务状态: {status}")
            return status
            
        except Exception as e:
            logger.error(f"❌ 检查服务状态失败: {str(e)}")
            return {}
    
    def start_all_services(self):
        """启动所有服务"""
        try:
            logger.info("🚀 启动大数据系统...")
            
            # 创建必要目录
            create_directories()
            
            # 启动各个服务
            services = [
                ('Hadoop', self.start_hadoop),
                ('Spark', self.start_spark),
                ('MongoDB', self.start_mongodb),
                ('Redis', self.start_redis),
                ('爬虫', self.start_crawler),
                ('数据处理', self.start_data_processing),
                ('机器学习分析', self.start_ml_analysis)
            ]
            
            for service_name, start_func in services:
                logger.info(f"启动 {service_name} 服务...")
                if start_func():
                    logger.info(f"✅ {service_name} 服务启动成功")
                else:
                    logger.warning(f"⚠️ {service_name} 服务启动失败")
            
            # 等待服务启动
            logger.info("⏳ 等待服务启动完成...")
            time.sleep(10)
            
            # 检查服务状态
            status = self.check_services_status()
            
            logger.info("🎉 大数据系统启动完成!")
            return status
            
        except Exception as e:
            logger.error(f"❌ 大数据系统启动失败: {str(e)}")
            return {}
    
    def stop_all_services(self):
        """停止所有服务"""
        try:
            logger.info("🛑 停止大数据系统...")
            
            for service_name, process in self.processes.items():
                try:
                    process.terminate()
                    process.wait(timeout=10)
                    logger.info(f"✅ {service_name} 服务已停止")
                except subprocess.TimeoutExpired:
                    process.kill()
                    logger.warning(f"⚠️ {service_name} 服务强制停止")
                except Exception as e:
                    logger.error(f"❌ 停止 {service_name} 服务失败: {str(e)}")
            
            logger.info("🎉 大数据系统已停止")
            
        except Exception as e:
            logger.error(f"❌ 停止大数据系统失败: {str(e)}")

def main():
    """主函数"""
    starter = BigDataSystemStarter()
    
    try:
        # 启动所有服务
        status = starter.start_all_services()
        
        # 显示服务状态
        print("\n" + "="*50)
        print("大数据系统状态:")
        print("="*50)
        for service, state in status.items():
            status_icon = "✅" if state == "running" else "❌"
            print(f"{status_icon} {service}: {state}")
        print("="*50)
        
        # 保持运行
        print("\n按 Ctrl+C 停止系统...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 收到停止信号...")
        starter.stop_all_services()
    except Exception as e:
        logger.error(f"❌ 系统运行错误: {str(e)}")
        starter.stop_all_services()

if __name__ == "__main__":
    main()
