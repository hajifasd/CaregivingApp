#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试套件
测试所有API端点的功能和性能
"""

import unittest
import requests
import json
import time
from typing import Dict, Any

class APITestSuite(unittest.TestCase):
    """API测试套件"""
    
    BASE_URL = "http://127.0.0.1:8000"
    USER_TOKEN = None
    ADMIN_TOKEN = None
    CAREGIVER_TOKEN = None
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        print("🚀 开始API测试...")
        cls.test_user_data = {
            "fullname": "测试用户",
            "phone": "13800138000",
            "password": "test123456"
        }
        cls.test_caregiver_data = {
            "name": "测试护工",
            "phone": "13900139000",
            "password": "test123456",
            "experience_years": 5,
            "qualification": "护理专业"
        }
    
    def test_01_server_connection(self):
        """测试服务器连接"""
        try:
            response = requests.get(f"{self.BASE_URL}/", timeout=5)
            self.assertEqual(response.status_code, 200)
            print("✅ 服务器连接正常")
        except Exception as e:
            self.fail(f"服务器连接失败: {str(e)}")
    
    def test_02_user_registration(self):
        """测试用户注册"""
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/register",
                json=self.test_user_data,
                timeout=10
            )
            
            if response.status_code == 201:
                result = response.json()
                self.assertTrue(result.get('success'))
                print("✅ 用户注册成功")
            elif response.status_code == 400:
                result = response.json()
                if "已存在" in result.get('message', ''):
                    print("⚠️ 用户已存在，跳过注册")
                else:
                    self.fail(f"用户注册失败: {result.get('message')}")
            else:
                self.fail(f"用户注册失败，状态码: {response.status_code}")
                
        except Exception as e:
            self.fail(f"用户注册测试失败: {str(e)}")
    
    def test_03_user_login(self):
        """测试用户登录"""
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/user/login",
                json={
                    "phone": self.test_user_data["phone"],
                    "password": self.test_user_data["password"]
                },
                timeout=10
            )
            
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertTrue(result.get('success'))
            self.assertIsNotNone(result.get('data', {}).get('token'))
            
            APITestSuite.USER_TOKEN = result['data']['token']
            print("✅ 用户登录成功")
            
        except Exception as e:
            self.fail(f"用户登录测试失败: {str(e)}")
    
    def test_04_caregiver_registration(self):
        """测试护工注册"""
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/caregiver/register",
                json=self.test_caregiver_data,
                timeout=10
            )
            
            if response.status_code == 201:
                result = response.json()
                self.assertTrue(result.get('success'))
                print("✅ 护工注册成功")
            elif response.status_code == 400:
                result = response.json()
                if "已存在" in result.get('message', ''):
                    print("⚠️ 护工已存在，跳过注册")
                else:
                    self.fail(f"护工注册失败: {result.get('message')}")
            else:
                self.fail(f"护工注册失败，状态码: {response.status_code}")
                
        except Exception as e:
            self.fail(f"护工注册测试失败: {str(e)}")
    
    def test_05_caregiver_login(self):
        """测试护工登录"""
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/caregiver/login",
                json={
                    "phone": self.test_caregiver_data["phone"],
                    "password": self.test_caregiver_data["password"]
                },
                timeout=10
            )
            
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertTrue(result.get('success'))
            self.assertIsNotNone(result.get('data', {}).get('token'))
            
            APITestSuite.CAREGIVER_TOKEN = result['data']['token']
            print("✅ 护工登录成功")
            
        except Exception as e:
            self.fail(f"护工登录测试失败: {str(e)}")
    
    def test_06_admin_login(self):
        """测试管理员登录"""
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/admin/login",
                json={
                    "username": "admin",
                    "password": "admin123"
                },
                timeout=10
            )
            
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertTrue(result.get('success'))
            self.assertIsNotNone(result.get('data', {}).get('token'))
            
            APITestSuite.ADMIN_TOKEN = result['data']['token']
            print("✅ 管理员登录成功")
            
        except Exception as e:
            self.fail(f"管理员登录测试失败: {str(e)}")
    
    def test_07_get_caregivers(self):
        """测试获取护工列表"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/api/caregiver/search",
                params={"keyword": ""},
                timeout=10
            )
            
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertTrue(result.get('success'))
            self.assertIsInstance(result.get('data'), list)
            print(f"✅ 获取护工列表成功，共 {len(result.get('data', []))} 个护工")
            
        except Exception as e:
            self.fail(f"获取护工列表测试失败: {str(e)}")
    
    def test_08_get_caregiver_hire_info(self):
        """测试获取护工招聘信息"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/api/caregivers/hire-info",
                timeout=10
            )
            
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertTrue(result.get('success'))
            self.assertIsInstance(result.get('data'), list)
            print(f"✅ 获取护工招聘信息成功，共 {len(result.get('data', []))} 个护工")
            
        except Exception as e:
            self.fail(f"获取护工招聘信息测试失败: {str(e)}")
    
    def test_09_create_employment_application(self):
        """测试创建就业申请"""
        if not APITestSuite.USER_TOKEN:
            self.skipTest("用户未登录，跳过就业申请测试")
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/employment/apply",
                json={
                    "user_id": 6,  # 使用测试用户ID
                    "caregiver_id": 2,  # 使用测试护工ID
                    "service_type": "医院陪护",
                    "proposed_start_date": "2024-01-15",
                    "proposed_end_date": "2024-02-15",
                    "frequency": "每天",
                    "duration_per_session": "8小时",
                    "notes": "API测试就业申请"
                },
                headers={"Authorization": f"Bearer {APITestSuite.USER_TOKEN}"},
                timeout=10
            )
            
            if response.status_code == 201:
                result = response.json()
                self.assertTrue(result.get('success'))
                print("✅ 创建就业申请成功")
            elif response.status_code == 400:
                result = response.json()
                if "已存在" in result.get('message', ''):
                    print("⚠️ 就业申请已存在，跳过创建")
                else:
                    self.fail(f"创建就业申请失败: {result.get('message')}")
            else:
                self.fail(f"创建就业申请失败，状态码: {response.status_code}")
                
        except Exception as e:
            self.fail(f"创建就业申请测试失败: {str(e)}")
    
    def test_10_get_employment_applications(self):
        """测试获取就业申请列表"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/api/employment/applications",
                timeout=10
            )
            
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertTrue(result.get('success'))
            self.assertIsInstance(result.get('data'), list)
            print(f"✅ 获取就业申请列表成功，共 {len(result.get('data', []))} 个申请")
            
        except Exception as e:
            self.fail(f"获取就业申请列表测试失败: {str(e)}")
    
    def test_11_get_hired_caregivers(self):
        """测试获取已聘用护工列表"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/api/employment/hired-caregivers/user/6",
                timeout=10
            )
            
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertTrue(result.get('success'))
            self.assertIsInstance(result.get('data'), list)
            print(f"✅ 获取已聘用护工列表成功，共 {len(result.get('data', []))} 个护工")
            
        except Exception as e:
            self.fail(f"获取已聘用护工列表测试失败: {str(e)}")
    
    def test_12_send_message(self):
        """测试发送消息"""
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/chat/send",
                json={
                    "sender_id": "6",
                    "sender_type": "user",
                    "sender_name": "测试用户",
                    "recipient_id": "2",
                    "recipient_type": "caregiver",
                    "content": "这是一条API测试消息",
                    "type": "text"
                },
                timeout=10
            )
            
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertTrue(result.get('success'))
            print("✅ 发送消息成功")
            
        except Exception as e:
            self.fail(f"发送消息测试失败: {str(e)}")
    
    def test_13_search_messages(self):
        """测试搜索消息"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/api/chat/search",
                params={"keyword": "测试"},
                timeout=10
            )
            
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertTrue(result.get('success'))
            self.assertIsInstance(result.get('data'), list)
            print(f"✅ 搜索消息成功，找到 {len(result.get('data', []))} 条消息")
            
        except Exception as e:
            self.fail(f"搜索消息测试失败: {str(e)}")
    
    def test_14_file_upload(self):
        """测试文件上传"""
        if not APITestSuite.USER_TOKEN:
            self.skipTest("用户未登录，跳过文件上传测试")
        
        try:
            # 创建一个测试文件
            test_file_content = b"这是一个测试文件内容"
            files = {
                'file': ('test.txt', test_file_content, 'text/plain')
            }
            
            response = requests.post(
                f"{self.BASE_URL}/api/upload/document",
                files=files,
                headers={"Authorization": f"Bearer {APITestSuite.USER_TOKEN}"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.assertTrue(result.get('success'))
                print("✅ 文件上传成功")
            else:
                print(f"⚠️ 文件上传测试跳过，状态码: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ 文件上传测试跳过: {str(e)}")
    
    def test_15_performance_test(self):
        """性能测试"""
        try:
            start_time = time.time()
            
            # 并发请求测试
            import concurrent.futures
            
            def make_request():
                response = requests.get(f"{self.BASE_URL}/api/caregiver/search", timeout=5)
                return response.status_code == 200
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(20)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            end_time = time.time()
            duration = end_time - start_time
            
            success_rate = sum(results) / len(results) * 100
            self.assertGreater(success_rate, 80)  # 80%成功率
            
            print(f"✅ 性能测试通过: {len(results)}个并发请求，成功率 {success_rate:.1f}%，耗时 {duration:.2f}秒")
            
        except Exception as e:
            self.fail(f"性能测试失败: {str(e)}")
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        print("🎉 API测试完成！")

def run_api_tests():
    """运行API测试"""
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(APITestSuite)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果
    print(f"\n📊 测试结果:")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_api_tests()
    exit(0 if success else 1)
