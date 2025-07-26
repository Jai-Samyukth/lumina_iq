#!/usr/bin/env python3
"""
Demonstration script showing API key rotation in action.
This simulates how the chat service will use different API keys for each request.
"""

import sys
import os
import logging

# Add current directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from api_rotation.api_key_rotator import api_key_rotator

def simulate_chat_requests():
    """Simulate multiple chat requests to demonstrate API key rotation."""
    
    print("🚀 API Key Rotation Demo")
    print("=" * 50)
    
    # Show initial status
    stats = api_key_rotator.get_current_stats()
    print(f"📊 Initial Status:")
    print(f"   Total API keys available: {stats['total_keys']}")
    print(f"   Current rotation index: {stats['current_index']}")
    print(f"   Rotation enabled: {stats['has_keys']}")
    
    if not stats['has_keys']:
        print("❌ No API keys available for rotation!")
        return
    
    print(f"\n🔄 Simulating {stats['total_keys'] + 3} chat requests...")
    print("   Each request will use a different API key:")
    print()
    
    # Simulate multiple requests
    for i in range(stats['total_keys'] + 3):
        # Get the next API key (this is what happens in each chat request)
        api_key = api_key_rotator.get_next_key()
        
        if api_key:
            # Show which key is being used (masked for security)
            key_preview = api_key_rotator.get_key_preview(api_key, 12)
            print(f"   Request {i+1:2d}: Using API key {key_preview}")
            
            # Show when we wrap around to the first key again
            current_stats = api_key_rotator.get_current_stats()
            if i >= stats['total_keys'] and (i - stats['total_keys']) < 3:
                print(f"              ↳ 🔄 Wrapped around! Back to key {(i % stats['total_keys']) + 1}")
        else:
            print(f"   Request {i+1:2d}: ❌ No API key available")
    
    # Show final status
    final_stats = api_key_rotator.get_current_stats()
    print(f"\n📊 Final Status:")
    print(f"   Current rotation index: {final_stats['current_index']}")
    print(f"   Next request will use key #{final_stats['current_index'] + 1}")
    
    print(f"\n✅ Demo completed!")
    print(f"   The rotation system ensures each request uses a different API key")
    print(f"   After using all {stats['total_keys']} keys, it cycles back to the first one")
    print(f"   The current position is saved to disk for persistence across restarts")

def show_rotation_benefits():
    """Show the benefits of API key rotation."""
    
    print("\n" + "=" * 50)
    print("🎯 Benefits of API Key Rotation")
    print("=" * 50)
    
    benefits = [
        "🚀 Load Distribution: Spreads requests across multiple API keys",
        "⚡ Rate Limit Avoidance: Reduces chance of hitting per-key rate limits", 
        "🔒 Security: No single point of failure if one key is compromised",
        "📈 Scalability: Can handle more concurrent requests",
        "🔄 Automatic: Rotation happens transparently for each request",
        "💾 Persistent: Rotation state survives application restarts",
        "🧵 Thread-Safe: Works correctly with concurrent requests"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")
    
    print(f"\n📝 How it works:")
    print(f"   1. Each chat request calls get_rotated_model()")
    print(f"   2. get_rotated_model() gets the next API key from the rotator")
    print(f"   3. A new Gemini model is created with that specific API key")
    print(f"   4. The request uses that model, ensuring key rotation")
    print(f"   5. The rotation index advances for the next request")

if __name__ == "__main__":
    try:
        # Set up basic logging
        logging.basicConfig(level=logging.WARNING)  # Reduce log noise for demo
        
        simulate_chat_requests()
        show_rotation_benefits()
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
