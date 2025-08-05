#!/usr/bin/env python3
"""
Simple concurrent test without authentication
Tests the chat endpoint directly with concurrent requests
"""

import asyncio
import aiohttp
import time
import json
from typing import List, Dict

# Test configuration
BASE_URL = "http://localhost:8000"
CONCURRENT_USERS = 5
REQUESTS_PER_USER = 2

async def test_chat_endpoint(session: aiohttp.ClientSession, user_id: int, request_id: int) -> Dict:
    """Test chat endpoint with a simple message"""
    start_time = time.time()
    
    # Different user agents to simulate different users
    headers = {
        "User-Agent": f"TestClient-User{user_id}/1.0",
        "Content-Type": "application/json"
    }
    
    payload = {
        "message": f"Hello! This is a test message from User {user_id}, Request {request_id}. Can you respond?"
    }
    
    try:
        async with session.post(
            f"{BASE_URL}/api/chat/", 
            json=payload,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status == 200:
                data = await response.json()
                return {
                    "user_id": user_id,
                    "request_id": request_id,
                    "response_time": response_time,
                    "status": "success",
                    "response_preview": data.get("response", "")[:100] + "..."
                }
            else:
                error_text = await response.text()
                return {
                    "user_id": user_id,
                    "request_id": request_id,
                    "response_time": response_time,
                    "status": "error",
                    "error": f"HTTP {response.status}: {error_text[:200]}"
                }
                
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        return {
            "user_id": user_id,
            "request_id": request_id,
            "response_time": response_time,
            "status": "error",
            "error": str(e)
        }

async def simulate_user(session: aiohttp.ClientSession, user_id: int) -> List[Dict]:
    """Simulate a user sending requests"""
    print(f"👤 User {user_id} starting {REQUESTS_PER_USER} requests...")
    
    tasks = []
    for request_id in range(1, REQUESTS_PER_USER + 1):
        task = test_chat_endpoint(session, user_id, request_id)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    print(f"✅ User {user_id} completed")
    return results

async def run_test():
    """Run the concurrent test"""
    print("🧪 Testing Concurrent Chat Performance")
    print("=" * 50)
    print(f"👥 Users: {CONCURRENT_USERS}")
    print(f"📨 Requests per user: {REQUESTS_PER_USER}")
    print(f"🎯 Total requests: {CONCURRENT_USERS * REQUESTS_PER_USER}")
    print("-" * 50)
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        # Create tasks for all users
        user_tasks = []
        for user_id in range(1, CONCURRENT_USERS + 1):
            task = simulate_user(session, user_id)
            user_tasks.append(task)
        
        # Run all users concurrently
        all_results = await asyncio.gather(*user_tasks)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Flatten results
    flat_results = []
    for user_results in all_results:
        flat_results.extend(user_results)
    
    # Show results
    print("\n" + "=" * 50)
    print("📊 RESULTS")
    print("=" * 50)
    
    successful = [r for r in flat_results if r["status"] == "success"]
    failed = [r for r in flat_results if r["status"] == "error"]
    
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"⏱️  Total time: {total_time:.2f}s")
    
    if successful:
        avg_time = sum(r["response_time"] for r in successful) / len(successful)
        print(f"⚡ Average response time: {avg_time:.2f}s")
        print(f"🚀 Requests per second: {len(successful) / total_time:.2f}")
        
        print(f"\n📝 Sample responses:")
        for i, result in enumerate(successful[:3]):
            print(f"   User {result['user_id']}: {result['response_preview']}")
    
    if failed:
        print(f"\n❌ Errors:")
        for result in failed[:3]:
            print(f"   User {result['user_id']}: {result['error'][:100]}")

if __name__ == "__main__":
    print("🚀 Make sure your server is running on http://localhost:8000")
    print("   Run: python start_optimized.py")
    print()
    
    try:
        asyncio.run(run_test())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted")
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
