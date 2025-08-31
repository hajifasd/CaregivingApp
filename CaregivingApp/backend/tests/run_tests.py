#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test runner for the caregiving system
"""

import os
import sys
import subprocess

def run_test(test_name, script_path):
    """Run a specific test"""
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, cwd=os.path.dirname(script_path))
        
        if result.returncode == 0:
            print("✓ Test completed successfully")
            if result.stdout:
                print("Output:")
                print(result.stdout)
        else:
            print("✗ Test failed")
            if result.stderr:
                print("Error:")
                print(result.stderr)
                
    except Exception as e:
        print(f"✗ Error running test: {e}")

def main():
    """Run all tests"""
    print("Caregiving System Test Suite")
    print("=" * 60)
    
    # 定义测试列表
    tests = [
        ("Create All Test Accounts", "create_all_test_accounts.py"),
        ("Database Quick View", "quick_view.py"),
        ("User Login Test", "test_user_login.py"),
    ]
    
    # 运行测试
    for test_name, script_name in tests:
        script_path = os.path.join(os.path.dirname(__file__), script_name)
        if os.path.exists(script_path):
            run_test(test_name, script_path)
        else:
            print(f"\n✗ Test script not found: {script_name}")
    
    print(f"\n{'='*60}")
    print("Test Suite Completed")
    print(f"{'='*60}")
    
    print("\nTest Account Information:")
    print("-" * 30)
    print("User Account:")
    print("  Phone: 13800138000")
    print("  Password: 123456")
    print()
    print("Caregiver Account:")
    print("  Phone: 13800138001")
    print("  Password: 123456")
    print()
    print("Admin Account:")
    print("  Username: admin")
    print("  Password: admin123")
    print()
    print("You can now test the system at: http://127.0.0.1:8000/")

if __name__ == "__main__":
    main() 