#!/usr/bin/env python3
"""
Debug chat functionality to identify response generation issues
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_chat_with_debug():
    """Test chat endpoint and show detailed debug info"""
    print("🔍 Testing Chat Response Generation")
    print("=" * 50)
    
    # Test message
    chat_data = {
        "message": "Hello! Can you help me understand this document?"
    }
    
    print(f"📤 Sending chat request:")
    print(f"   Message: '{chat_data['message']}'")
    print(f"   URL: {BASE_URL}/api/chat/")
    print(f"   User-Agent: TestClient-Debug/1.0")
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "TestClient-Debug/1.0"
    }
    
    try:
        print(f"\n⏱️  Sending request at {time.strftime('%H:%M:%S')}...")
        
        response = requests.post(
            f"{BASE_URL}/api/chat/",
            json=chat_data,
            headers=headers,
            timeout=30  # Give it time to generate
        )
        
        print(f"📥 Response received at {time.strftime('%H:%M:%S')}")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS!")
            print(f"   Response: {data.get('response', 'No response field')[:200]}...")
            print(f"   Timestamp: {data.get('timestamp', 'No timestamp')}")
        elif response.status_code == 400:
            print(f"   ⚠️  BAD REQUEST: {response.text}")
            print(f"   This is expected if no PDF is uploaded")
        elif response.status_code == 500:
            print(f"   ❌ SERVER ERROR: {response.text}")
            print(f"   Check server logs for detailed error info")
        else:
            print(f"   ❓ UNEXPECTED STATUS: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - response generation taking too long")
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure server is running")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_server_status():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"⚠️  Server responded with status {response.status_code}")
            return False
    except:
        print("❌ Server is not responding")
        return False

if __name__ == "__main__":
    print("🧪 Chat Response Debug Test")
    print("Make sure your server is running: python start_optimized.py")
    print()
    
    if check_server_status():
        test_chat_with_debug()
        print("\n💡 Check the server console for detailed debug logs!")
        print("💡 Look for emojis like 🎯, 📚, 🤖, ⚡, ✅, ❌ in the logs")
    else:
        print("Please start the server first!")
