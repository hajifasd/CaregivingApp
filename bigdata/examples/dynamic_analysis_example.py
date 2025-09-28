"""
护工资源管理系统 - 动态分析示例
====================================

演示如何使用动态分析功能
"""

import os
import sys
import pandas as pd
import json
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from bigdata.processing.data_import_trigger import DataImportTrigger
from bigdata.analysis.dynamic_analyzer import DynamicAnalyzer

def create_sample_data():
    """创建示例数据"""
    print("📊 创建示例数据...")
    
    # 创建护工数据
    caregiver_data = {
        'name': ['张护工', '李护工', '王护工', '赵护工', '陈护工'],
        'age': [35, 42, 28, 45, 38],
        'gender': ['女', '男', '女', '男', '女'],
        'city': ['北京', '上海', '广州', '深圳', '北京'],
        'hourly_rate': [50, 60, 45, 55, 48],
        'rating': [4.5, 4.8, 4.2, 4.6, 4.3],
        'service_type': ['养老护理', '康复护理', '医疗护理', '养老护理', '康复护理']
    }
    
    caregiver_df = pd.DataFrame(caregiver_data)
    caregiver_file = 'sample_caregiver_data.csv'
    caregiver_df.to_csv(caregiver_file, index=False, encoding='utf-8')
    print(f"✅ 护工数据创建完成: {caregiver_file}")
    
    # 创建招聘数据
    job_data = {
        'title': ['护工招聘', '护理员招聘', '康复护理招聘', '医疗护理招聘', '养老护理招聘'],
        'company': ['北京养老院', '上海康复中心', '广州医院', '深圳护理中心', '北京医疗集团'],
        'location': ['北京朝阳区', '上海浦东区', '广州天河区', '深圳南山区', '北京海淀区'],
        'salary': ['5000-8000元/月', '6000-9000元/月', '4500-7000元/月', '5500-8500元/月', '4800-7500元/月'],
        'requirements': ['有经验优先', '护理专业', '康复专业', '医疗专业', '养老护理经验']
    }
    
    job_df = pd.DataFrame(job_data)
    job_file = 'sample_job_data.csv'
    job_df.to_csv(job_file, index=False, encoding='utf-8')
    print(f"✅ 招聘数据创建完成: {job_file}")
    
    return caregiver_file, job_file

def demonstrate_dynamic_analysis():
    """演示动态分析功能"""
    print("\n🚀 开始动态分析演示")
    
    # 创建示例数据
    caregiver_file, job_file = create_sample_data()
    
    # 初始化数据导入触发器
    trigger = DataImportTrigger()
    
    # 导入护工数据并触发分析
    print("\n📊 导入护工数据...")
    success1 = trigger.import_csv_data(caregiver_file, "sample_caregivers")
    if success1:
        print("✅ 护工数据导入成功，分析已触发")
    else:
        print("❌ 护工数据导入失败")
    
    # 导入招聘数据并触发分析
    print("\n📊 导入招聘数据...")
    success2 = trigger.import_csv_data(job_file, "sample_jobs")
    if success2:
        print("✅ 招聘数据导入成功，分析已触发")
    else:
        print("❌ 招聘数据导入失败")
    
    # 直接运行动态分析
    print("\n🤖 直接运行动态分析...")
    analyzer = DynamicAnalyzer()
    results = analyzer.run_dynamic_analysis(trigger_source="demo")
    
    if results:
        print("✅ 动态分析完成")
        print(f"分析时间: {results.get('analysis_timestamp')}")
        print(f"数据版本: {results.get('data_version')}")
        print(f"数据源: {results.get('data_sources')}")
        print(f"数据量: {results.get('data_counts')}")
        
        # 显示分析结果
        if 'caregiver_distribution' in results:
            dist = results['caregiver_distribution']
            print(f"\n📈 护工分布分析:")
            print(f"  总护工数: {dist.get('total_caregivers', 0)}")
            print(f"  地域分布: {dist.get('location_distribution', {})}")
            print(f"  薪资分布: {dist.get('salary_distribution', {})}")
        
        if 'success_prediction' in results:
            pred = results['success_prediction']
            print(f"\n🎯 成功率预测:")
            print(f"  模型准确率: {pred.get('model_accuracy', 0):.3f}")
            print(f"  特征重要性: {pred.get('feature_importance', {})}")
        
        if 'cluster_analysis' in results:
            cluster = results['cluster_analysis']
            print(f"\n🔍 聚类分析:")
            print(f"  聚类数量: {cluster.get('total_clusters', 0)}")
            for cluster_info in cluster.get('clusters', []):
                print(f"  聚类 {cluster_info['cluster_id']}: {cluster_info['count']} 个护工")
    else:
        print("❌ 动态分析失败")
    
    # 显示导入历史
    print("\n📋 导入历史:")
    history = trigger.get_import_history()
    for log in history:
        print(f"  {log['timestamp']}: {log['source']} ({log['count']} 条记录)")
    
    # 清理示例文件
    print("\n🧹 清理示例文件...")
    try:
        os.remove(caregiver_file)
        os.remove(job_file)
        print("✅ 示例文件清理完成")
    except:
        print("⚠️ 示例文件清理失败")

def demonstrate_api_usage():
    """演示API使用"""
    print("\n🌐 API使用演示")
    
    import requests
    
    try:
        # 触发动态分析
        print("📡 通过API触发动态分析...")
        response = requests.post('http://localhost:8000/api/bigdata/dynamic/trigger', 
                               json={'source': 'api_demo'}, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ API触发成功")
                print(f"分析时间: {result['data']['analysis_timestamp']}")
            else:
                print(f"❌ API触发失败: {result.get('message')}")
        else:
            print(f"❌ API调用失败: {response.status_code}")
        
        # 获取最新分析结果
        print("\n📡 通过API获取最新分析结果...")
        response = requests.get('http://localhost:8000/api/bigdata/dynamic/latest', timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 获取最新分析成功")
                data = result['data']
                print(f"数据版本: {data.get('data_version')}")
                print(f"数据源: {data.get('data_sources')}")
            else:
                print(f"⚠️ 没有可用分析结果: {result.get('message')}")
        else:
            print(f"❌ API调用失败: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器，请确保Flask应用正在运行")
    except Exception as e:
        print(f"❌ API调用异常: {str(e)}")

def main():
    """主函数"""
    print("🎯 护工资源管理系统 - 动态分析演示")
    print("=" * 50)
    
    # 演示动态分析功能
    demonstrate_dynamic_analysis()
    
    # 演示API使用
    demonstrate_api_usage()
    
    print("\n🎉 演示完成！")
    print("\n💡 使用说明:")
    print("1. 每次导入新数据时，系统会自动触发动态分析")
    print("2. 可以通过API手动触发分析")
    print("3. 分析结果会实时更新到仪表盘")
    print("4. 支持多种数据格式：CSV、JSON、Parquet")
    print("5. 分析结果会保存到文件，支持历史查询")

if __name__ == "__main__":
    main()

