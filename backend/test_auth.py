#!/usr/bin/env python3
"""
Test authentication endpoint to debug login issues
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """Test login with correct credentials"""
    print("🔐 Testing Authentication")
    print("=" * 40)
    
    # Test data - using the exact credentials from settings
    login_data = {
        "username": "vsbec",
        "password": "vsbec"
    }
    
    print(f"📤 Sending login request:")
    print(f"   Username: '{login_data['username']}'")
    print(f"   Password: '{login_data['password']}'")
    print(f"   URL: {BASE_URL}/api/auth/login")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n📥 Response:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS: {data}")
        else:
            print(f"   ❌ ERROR: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_wrong_credentials():
    """Test with wrong credentials to verify error handling"""
    print("\n🚫 Testing Wrong Credentials")
    print("=" * 40)
    
    login_data = {
        "username": "wrong",
        "password": "wrong"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 401:
            print("✅ Correctly rejected wrong credentials")
        else:
            print(f"❌ Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Authentication Test")
    print("Make sure your server is running: python start_optimized.py")
    print()
    
    test_login()
    test_wrong_credentials()
    
    print("\n💡 Check the server logs for detailed debug information!")
