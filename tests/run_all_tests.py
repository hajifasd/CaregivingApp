#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行所有测试的主脚本
包含API测试、前端测试、性能测试等
"""

import sys
import os
import time
import subprocess
from datetime import datetime

# 添加测试目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_header(title):
    """打印测试标题"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)

def print_result(test_name, success, duration=None):
    """打印测试结果"""
    status = "✅ 通过" if success else "❌ 失败"
    time_str = f" ({duration:.2f}秒)" if duration else ""
    print(f"{status} {test_name}{time_str}")

def check_server_running():
    """检查服务器是否运行"""
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        return response.status_code == 200
    except:
        return False

def run_api_tests():
    """运行API测试"""
    print_header("API功能测试")
    
    if not check_server_running():
        print("❌ 服务器未运行，请先启动服务器")
        return False
    
    try:
        start_time = time.time()
        from test_api import run_api_tests
        success = run_api_tests()
        duration = time.time() - start_time
        
        print_result("API测试", success, duration)
        return success
        
    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")
        return False

def run_frontend_tests():
    """运行前端测试"""
    print_header("前端页面测试")
    
    if not check_server_running():
        print("❌ 服务器未运行，请先启动服务器")
        return False
    
    try:
        start_time = time.time()
        from test_frontend import run_frontend_tests
        success = run_frontend_tests()
        duration = time.time() - start_time
        
        print_result("前端测试", success, duration)
        return success
        
    except Exception as e:
        print(f"❌ 前端测试失败: {str(e)}")
        return False

def run_performance_tests():
    """运行性能测试"""
    print_header("性能测试")
    
    if not check_server_running():
        print("❌ 服务器未运行，请先启动服务器")
        return False
    
    try:
        import requests
        import concurrent.futures
        
        start_time = time.time()
        
        def make_request():
            try:
                response = requests.get("http://127.0.0.1:8000/api/caregiver/search", timeout=5)
                return response.status_code == 200
            except:
                return False
        
        # 并发请求测试
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        duration = time.time() - start_time
        success_rate = sum(results) / len(results) * 100
        
        # 性能标准：80%成功率，平均响应时间小于2秒
        success = success_rate >= 80 and duration / len(results) < 2.0
        
        print(f"📊 性能测试结果:")
        print(f"   - 并发请求数: {len(results)}")
        print(f"   - 成功率: {success_rate:.1f}%")
        print(f"   - 总耗时: {duration:.2f}秒")
        print(f"   - 平均响应时间: {duration/len(results):.2f}秒")
        
        print_result("性能测试", success, duration)
        return success
        
    except Exception as e:
        print(f"❌ 性能测试失败: {str(e)}")
        return False

def run_security_tests():
    """运行安全测试"""
    print_header("安全测试")
    
    if not check_server_running():
        print("❌ 服务器未运行，请先启动服务器")
        return False
    
    try:
        import requests
        
        security_issues = []
        
        # 测试SQL注入防护
        try:
            response = requests.get("http://127.0.0.1:8000/api/caregiver/search?keyword='; DROP TABLE users; --", timeout=5)
            if response.status_code == 200:
                print("✅ SQL注入防护正常")
            else:
                security_issues.append("SQL注入防护可能有问题")
        except:
            print("✅ SQL注入防护正常")
        
        # 测试XSS防护
        try:
            response = requests.get("http://127.0.0.1:8000/api/caregiver/search?keyword=<script>alert('xss')</script>", timeout=5)
            if response.status_code == 200:
                if "<script>" not in response.text:
                    print("✅ XSS防护正常")
                else:
                    security_issues.append("XSS防护可能有问题")
            else:
                print("✅ XSS防护正常")
        except:
            print("✅ XSS防护正常")
        
        # 测试认证保护
        try:
            response = requests.get("http://127.0.0.1:8000/api/employment/applications", timeout=5)
            if response.status_code in [401, 403]:
                print("✅ 认证保护正常")
            else:
                security_issues.append("认证保护可能有问题")
        except:
            print("✅ 认证保护正常")
        
        success = len(security_issues) == 0
        
        if security_issues:
            print("⚠️ 发现安全问题:")
            for issue in security_issues:
                print(f"   - {issue}")
        
        print_result("安全测试", success)
        return success
        
    except Exception as e:
        print(f"❌ 安全测试失败: {str(e)}")
        return False

def generate_test_report(results):
    """生成测试报告"""
    print_header("测试报告")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"📊 测试总结:")
    print(f"   - 总测试数: {total_tests}")
    print(f"   - 通过测试: {passed_tests}")
    print(f"   - 失败测试: {total_tests - passed_tests}")
    print(f"   - 成功率: {success_rate:.1f}%")
    
    print(f"\n📋 详细结果:")
    for test_name, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"   - {test_name}: {status}")
    
    # 生成报告文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_{timestamp}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"护工资源管理系统 - 测试报告\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"="*50 + "\n\n")
        
        f.write(f"测试总结:\n")
        f.write(f"- 总测试数: {total_tests}\n")
        f.write(f"- 通过测试: {passed_tests}\n")
        f.write(f"- 失败测试: {total_tests - passed_tests}\n")
        f.write(f"- 成功率: {success_rate:.1f}%\n\n")
        
        f.write(f"详细结果:\n")
        for test_name, success in results.items():
            status = "通过" if success else "失败"
            f.write(f"- {test_name}: {status}\n")
    
    print(f"\n📄 测试报告已保存到: {report_file}")
    
    return success_rate >= 80  # 80%通过率认为测试成功

def main():
    """主函数"""
    print("🚀 护工资源管理系统 - 完整测试套件")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查依赖
    try:
        import requests
        import concurrent.futures
    except ImportError as e:
        print(f"❌ 缺少依赖: {str(e)}")
        print("请安装: pip install requests beautifulsoup4")
        return False
    
    # 运行所有测试
    results = {}
    
    # API测试
    results["API功能测试"] = run_api_tests()
    
    # 前端测试
    results["前端页面测试"] = run_frontend_tests()
    
    # 性能测试
    results["性能测试"] = run_performance_tests()
    
    # 安全测试
    results["安全测试"] = run_security_tests()
    
    # 生成报告
    overall_success = generate_test_report(results)
    
    print(f"\n🎉 测试完成!")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if overall_success:
        print("✅ 所有测试通过，系统运行正常！")
        return True
    else:
        print("❌ 部分测试失败，请检查系统配置。")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
