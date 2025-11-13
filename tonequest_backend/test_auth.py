#!/usr/bin/env python3
"""
Simple test script for authentication endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1/auth"

def test_signup():
    """Test user signup"""
    signup_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "displayName": "Test User"
    }
    
    response = requests.post(f"{BASE_URL}/signup", json=signup_data)
    print(f"Signup Status: {response.status_code}")
    print(f"Signup Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        return response.json()["token"]
    return None

def test_login():
    """Test user login"""
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Login Status: {response.status_code}")
    print(f"Login Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        return response.json()["token"]
    return None

def test_protected_endpoint(token):
    """Test accessing protected endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/me", headers=headers)
    print(f"Protected Endpoint Status: {response.status_code}")
    print(f"Protected Endpoint Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("Testing Authentication Endpoints...")
    print("=" * 50)
    
    # Test signup
    print("\n1. Testing Signup:")
    token = test_signup()
    
    if token:
        print("\n2. Testing Protected Endpoint with Signup Token:")
        test_protected_endpoint(token)
    
    # Test login
    print("\n3. Testing Login:")
    login_token = test_login()
    
    if login_token:
        print("\n4. Testing Protected Endpoint with Login Token:")
        test_protected_endpoint(login_token)