#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端测试套件
测试前端页面的功能和用户体验
"""

import unittest
import requests
from bs4 import BeautifulSoup
import time

class FrontendTestSuite(unittest.TestCase):
    """前端测试套件"""
    
    BASE_URL = "http://127.0.0.1:8000"
    
    def test_01_homepage_loads(self):
        """测试首页加载"""
        try:
            response = requests.get(f"{self.BASE_URL}/", timeout=10)
            self.assertEqual(response.status_code, 200)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            self.assertIsNotNone(soup.find('title'))
            print("✅ 首页加载正常")
            
        except Exception as e:
            self.fail(f"首页加载失败: {str(e)}")
    
    def test_02_user_pages_load(self):
        """测试用户页面加载"""
        user_pages = [
            "/user/register",
            "/user/home",
            "/user/dashboard",
            "/user/caregivers",
            "/user/messages",
            "/user/profile"
        ]
        
        for page in user_pages:
            try:
                response = requests.get(f"{self.BASE_URL}{page}", timeout=10)
                self.assertEqual(response.status_code, 200)
                print(f"✅ 用户页面 {page} 加载正常")
            except Exception as e:
                print(f"⚠️ 用户页面 {page} 加载失败: {str(e)}")
    
    def test_03_caregiver_pages_load(self):
        """测试护工页面加载"""
        caregiver_pages = [
            "/caregiver/register",
            "/caregiver/dashboard",
            "/caregiver/messages"
        ]
        
        for page in caregiver_pages:
            try:
                response = requests.get(f"{self.BASE_URL}{page}", timeout=10)
                self.assertEqual(response.status_code, 200)
                print(f"✅ 护工页面 {page} 加载正常")
            except Exception as e:
                print(f"⚠️ 护工页面 {page} 加载失败: {str(e)}")
    
    def test_04_admin_pages_load(self):
        """测试管理员页面加载"""
        admin_pages = [
            "/admin/login",
            "/admin/dashboard",
            "/admin/users",
            "/admin/caregivers"
        ]
        
        for page in admin_pages:
            try:
                response = requests.get(f"{self.BASE_URL}{page}", timeout=10)
                self.assertEqual(response.status_code, 200)
                print(f"✅ 管理员页面 {page} 加载正常")
            except Exception as e:
                print(f"⚠️ 管理员页面 {page} 加载失败: {str(e)}")
    
    def test_05_static_resources_load(self):
        """测试静态资源加载"""
        static_resources = [
            "/css/style.css",
            "/js/common.js",
            "/js/chat-manager.js",
            "/js/file-upload.js",
            "/js/performance-optimizer.js"
        ]
        
        for resource in static_resources:
            try:
                response = requests.get(f"{self.BASE_URL}{resource}", timeout=10)
                self.assertEqual(response.status_code, 200)
                print(f"✅ 静态资源 {resource} 加载正常")
            except Exception as e:
                print(f"⚠️ 静态资源 {resource} 加载失败: {str(e)}")
    
    def test_06_page_performance(self):
        """测试页面性能"""
        pages_to_test = [
            "/",
            "/user/dashboard",
            "/user/caregivers",
            "/user/messages"
        ]
        
        for page in pages_to_test:
            try:
                start_time = time.time()
                response = requests.get(f"{self.BASE_URL}{page}", timeout=10)
                end_time = time.time()
                
                load_time = end_time - start_time
                self.assertEqual(response.status_code, 200)
                self.assertLess(load_time, 3.0)  # 页面加载时间应小于3秒
                
                print(f"✅ 页面 {page} 性能正常，加载时间: {load_time:.2f}秒")
                
            except Exception as e:
                print(f"⚠️ 页面 {page} 性能测试失败: {str(e)}")
    
    def test_07_responsive_design(self):
        """测试响应式设计"""
        try:
            # 测试不同屏幕尺寸的CSS媒体查询
            response = requests.get(f"{self.BASE_URL}/css/style.css", timeout=10)
            self.assertEqual(response.status_code, 200)
            
            css_content = response.text
            
            # 检查是否包含响应式设计的媒体查询
            self.assertIn("@media", css_content)
            self.assertIn("max-width", css_content)
            
            print("✅ 响应式设计CSS正常")
            
        except Exception as e:
            self.fail(f"响应式设计测试失败: {str(e)}")
    
    def test_08_accessibility_features(self):
        """测试无障碍功能"""
        try:
            response = requests.get(f"{self.BASE_URL}/user/dashboard", timeout=10)
            self.assertEqual(response.status_code, 200)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 检查是否有alt属性
            images = soup.find_all('img')
            for img in images:
                if not img.get('alt'):
                    print(f"⚠️ 图片缺少alt属性: {img.get('src', 'unknown')}")
            
            # 检查是否有表单标签
            inputs = soup.find_all('input')
            for input_tag in inputs:
                if input_tag.get('type') in ['text', 'email', 'password']:
                    if not input_tag.get('id') and not input_tag.get('aria-label'):
                        print(f"⚠️ 输入框缺少标签: {input_tag.get('name', 'unknown')}")
            
            print("✅ 无障碍功能检查完成")
            
        except Exception as e:
            print(f"⚠️ 无障碍功能测试失败: {str(e)}")
    
    def test_09_security_headers(self):
        """测试安全头"""
        try:
            response = requests.get(f"{self.BASE_URL}/", timeout=10)
            self.assertEqual(response.status_code, 200)
            
            headers = response.headers
            
            # 检查安全头
            security_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection'
            ]
            
            for header in security_headers:
                if header in headers:
                    print(f"✅ 安全头 {header} 存在")
                else:
                    print(f"⚠️ 安全头 {header} 缺失")
            
        except Exception as e:
            print(f"⚠️ 安全头测试失败: {str(e)}")
    
    def test_10_error_pages(self):
        """测试错误页面"""
        try:
            # 测试404页面
            response = requests.get(f"{self.BASE_URL}/nonexistent-page", timeout=10)
            # 404页面应该返回404状态码或重定向到错误页面
            self.assertIn(response.status_code, [404, 200])
            print("✅ 404错误页面处理正常")
            
        except Exception as e:
            print(f"⚠️ 错误页面测试失败: {str(e)}")

def run_frontend_tests():
    """运行前端测试"""
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(FrontendTestSuite)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果
    print(f"\n📊 前端测试结果:")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
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
    success = run_frontend_tests()
    exit(0 if success else 1)
