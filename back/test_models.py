#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试模型初始化脚本
用于验证修复后的模型是否正常工作
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_model_initialization():
    """测试模型初始化"""
    try:
        print("🧪 开始测试模型初始化...")
        
        # 导入必要的模块
        from extensions import db
        from models.user import User
        from models.caregiver import Caregiver
        from models.service import ServiceType
        from models.business import JobData, AnalysisResult, Appointment, Employment, Message
        
        print("✅ 模块导入成功")
        
        # 测试模型获取
        print("\n📋 测试模型获取...")
        
        # 测试User模型
        user_model = User.get_model(db)
        print(f"✅ User模型: {user_model.__name__}")
        
        # 测试Caregiver模型
        caregiver_model = Caregiver.get_model(db)
        print(f"✅ Caregiver模型: {caregiver_model.__name__}")
        
        # 测试ServiceType模型
        service_type_model = ServiceType.get_model(db)
        print(f"✅ ServiceType模型: {service_type_model.__name__}")
        
        # 测试JobData模型
        job_data_model = JobData.get_model(db)
        print(f"✅ JobData模型: {job_data_model.__name__}")
        
        # 测试AnalysisResult模型
        analysis_result_model = AnalysisResult.get_model(db)
        print(f"✅ AnalysisResult模型: {analysis_result_model.__name__}")
        
        # 测试Appointment模型
        appointment_model = Appointment.get_model(db)
        print(f"✅ Appointment模型: {appointment_model.__name__}")
        
        # 测试Employment模型
        employment_model = Employment.get_model(db)
        print(f"✅ Employment模型: {employment_model.__name__}")
        
        # 测试Message模型
        message_model = Message.get_model(db)
        print(f"✅ Message模型: {message_model.__name__}")
        
        print("\n🎉 所有模型初始化测试通过！")
        
        # 测试重复获取是否正常
        print("\n🔄 测试重复获取模型...")
        user_model2 = User.get_model(db)
        if user_model is user_model2:
            print("✅ 模型缓存机制正常，返回相同实例")
        else:
            print("❌ 模型缓存机制异常，返回不同实例")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型初始化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 护工资源管理系统 - 模型初始化测试")
    print("=" * 50)
    
    success = test_model_initialization()
    
    if success:
        print("\n🎯 测试完成，模型初始化正常！")
        sys.exit(0)
    else:
        print("\n💥 测试失败，请检查错误信息！")
        sys.exit(1)
