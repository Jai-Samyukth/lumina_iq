#!/usr/bin/env python3
"""
Concurrent Performance Test Script for Learning App API
Tests multiple users sending chat requests simultaneously
"""

import asyncio
import aiohttp
import time
import json
from typing import List, Dict
import statistics

# Test configuration
BASE_URL = "http://localhost:8000"
CONCURRENT_USERS = 5
REQUESTS_PER_USER = 3
TEST_MESSAGE = "What is the main topic of this document?"

async def send_chat_request(session: aiohttp.ClientSession, user_id: int, request_id: int) -> Dict:
    """Send a single chat request and measure response time"""
    start_time = time.time()
    
    # Simulate different user agents for different sessions
    headers = {
        "User-Agent": f"TestClient-User{user_id}/1.0",
        "Content-Type": "application/json"
    }
    
    payload = {
        "message": f"{TEST_MESSAGE} (User {user_id}, Request {request_id})"
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
                    "response_length": len(data.get("response", ""))
                }
            else:
                error_text = await response.text()
                return {
                    "user_id": user_id,
                    "request_id": request_id,
                    "response_time": response_time,
                    "status": "error",
                    "error": f"HTTP {response.status}: {error_text}"
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
    """Simulate a single user sending multiple requests"""
    print(f"👤 User {user_id} starting {REQUESTS_PER_USER} requests...")
    
    tasks = []
    for request_id in range(1, REQUESTS_PER_USER + 1):
        task = send_chat_request(session, user_id, request_id)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    print(f"✅ User {user_id} completed all requests")
    return results

async def run_concurrent_test():
    """Run the concurrent performance test"""
    print(f"🚀 Starting concurrent performance test...")
    print(f"📊 Configuration: {CONCURRENT_USERS} users, {REQUESTS_PER_USER} requests each")
    print(f"🎯 Target: {BASE_URL}")
    print("-" * 60)
    
    start_time = time.time()
    
    # Create HTTP session with connection pooling
    connector = aiohttp.TCPConnector(
        limit=100,  # Total connection pool size
        limit_per_host=20,  # Connections per host
        ttl_dns_cache=300,  # DNS cache TTL
        use_dns_cache=True,
    )
    
    async with aiohttp.ClientSession(connector=connector) as session:
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
    
    # Analyze results
    analyze_results(flat_results, total_time)

def analyze_results(results: List[Dict], total_time: float):
    """Analyze and display test results"""
    print("\n" + "=" * 60)
    print("📈 PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    successful_requests = [r for r in results if r["status"] == "success"]
    failed_requests = [r for r in results if r["status"] == "error"]
    
    total_requests = len(results)
    success_rate = (len(successful_requests) / total_requests) * 100
    
    print(f"📊 Total Requests: {total_requests}")
    print(f"✅ Successful: {len(successful_requests)} ({success_rate:.1f}%)")
    print(f"❌ Failed: {len(failed_requests)} ({100-success_rate:.1f}%)")
    print(f"⏱️  Total Test Time: {total_time:.2f}s")
    
    if successful_requests:
        response_times = [r["response_time"] for r in successful_requests]
        
        print(f"\n⚡ RESPONSE TIME STATISTICS:")
        print(f"   Average: {statistics.mean(response_times):.2f}s")
        print(f"   Median:  {statistics.median(response_times):.2f}s")
        print(f"   Min:     {min(response_times):.2f}s")
        print(f"   Max:     {max(response_times):.2f}s")
        
        if len(response_times) > 1:
            print(f"   Std Dev: {statistics.stdev(response_times):.2f}s")
        
        # Throughput calculation
        requests_per_second = len(successful_requests) / total_time
        print(f"\n🚀 THROUGHPUT:")
        print(f"   Requests/second: {requests_per_second:.2f}")
        print(f"   Concurrent efficiency: {(requests_per_second / CONCURRENT_USERS):.2f} req/s per user")
    
    # Show errors if any
    if failed_requests:
        print(f"\n❌ ERROR DETAILS:")
        error_counts = {}
        for req in failed_requests:
            error = req.get("error", "Unknown error")
            error_counts[error] = error_counts.get(error, 0) + 1
        
        for error, count in error_counts.items():
            print(f"   {error}: {count} times")
    
    print("\n" + "=" * 60)
    
    # Performance recommendations
    if successful_requests:
        avg_response_time = statistics.mean([r["response_time"] for r in successful_requests])
        if avg_response_time > 5.0:
            print("⚠️  WARNING: Average response time > 5s. Consider further optimization.")
        elif avg_response_time < 2.0:
            print("🎉 EXCELLENT: Fast response times achieved!")
        else:
            print("✅ GOOD: Response times are acceptable.")
        
        if success_rate < 95:
            print("⚠️  WARNING: Success rate < 95%. Check for errors.")
        else:
            print("✅ GOOD: High success rate achieved.")

if __name__ == "__main__":
    print("🧪 Learning App Concurrent Performance Test")
    print("=" * 60)
    
    try:
        asyncio.run(run_concurrent_test())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
