#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test user login functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, DataStore, User
from werkzeug.security import generate_password_hash

def create_test_user():
    """Create a test user"""
    with app.app_context():
        # Check if test user already exists
        existing_user = DataStore.get_user_by_phone("13800138000")
        if existing_user:
            print("Test user already exists")
            return existing_user
        
        # Create test user
        user = User(
            email="test_user_13800138000@temp.com",
            password_hash=generate_password_hash("123456"),
            name="Test User",
            phone="13800138000",
            is_approved=True  # Set as approved
        )
        
        db.session.add(user)
        db.session.commit()
        
        print(f"Created test user successfully: {user.name} ({user.phone})")
        return user

def test_user_login():
    """Test user login"""
    with app.app_context():
        # Create test user
        user = create_test_user()
        
        # Test finding user by phone
        user_by_phone = DataStore.get_user_by_phone("13800138000")
        print(f"Find user by phone: {user_by_phone.name if user_by_phone else 'Not found'}")
        
        # Test finding user by email
        user_by_email = DataStore.get_user_by_email("test_user_13800138000@temp.com")
        print(f"Find user by email: {user_by_email.name if user_by_email else 'Not found'}")
        
        # Show all users
        all_users = DataStore.get_all_users()
        print(f"\nTotal users: {len(all_users)}")
        for u in all_users:
            print(f"- {u.name} ({u.phone}) - Approved: {u.is_approved}")

if __name__ == "__main__":
    test_user_login() 