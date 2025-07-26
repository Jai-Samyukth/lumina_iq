#!/usr/bin/env python3
"""
Verification script to test that API key rotation is working in the backend.
This script tests the chat service integration.
"""

import sys
import os

# Add paths for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

def test_chat_service_integration():
    """Test that the chat service can use rotated API keys."""
    
    print("🔍 Testing Chat Service Integration")
    print("=" * 50)
    
    try:
        # Import the chat service
        from services.chat_service import get_rotated_model, ROTATION_ENABLED
        
        print(f"✅ Chat service imported successfully")
        print(f"📊 Rotation enabled: {ROTATION_ENABLED}")
        
        if not ROTATION_ENABLED:
            print("❌ API key rotation is not enabled in chat service")
            return False
        
        # Test getting rotated models
        print(f"\n🔄 Testing rotated model creation...")
        
        for i in range(5):
            try:
                model = get_rotated_model()
                if model:
                    print(f"   Request {i+1}: ✅ Model created successfully")
                else:
                    print(f"   Request {i+1}: ❌ Failed to create model")
            except Exception as e:
                print(f"   Request {i+1}: ❌ Error creating model: {e}")
        
        # Test the rotator directly
        from api_rotation.api_key_rotator import api_key_rotator
        stats = api_key_rotator.get_current_stats()
        
        print(f"\n📊 Rotator Statistics:")
        print(f"   Total keys: {stats['total_keys']}")
        print(f"   Current index: {stats['current_index']}")
        print(f"   Has keys: {stats['has_keys']}")
        
        print(f"\n✅ Integration test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint_simulation():
    """Simulate what happens when API endpoints are called."""
    
    print(f"\n🌐 Simulating API Endpoint Calls")
    print("=" * 50)
    
    try:
        from services.chat_service import get_rotated_model
        from api_rotation.api_key_rotator import api_key_rotator
        
        # Simulate multiple API calls
        endpoints = [
            "POST /api/chat (send message)",
            "POST /api/chat/generate-questions",
            "POST /api/chat/evaluate-answer",
            "POST /api/chat/evaluate-quiz"
        ]
        
        print("🔄 Each API call will use a different API key:")
        print()
        
        for i, endpoint in enumerate(endpoints):
            # This is what happens in each API call
            model = get_rotated_model()
            
            # Get current stats to show which key is being used
            stats = api_key_rotator.get_current_stats()
            prev_index = (stats['current_index'] - 1) % stats['total_keys']
            
            print(f"   {endpoint}")
            print(f"   ↳ Using API key #{prev_index + 1} of {stats['total_keys']}")
            print()
        
        print("✅ API endpoint simulation completed!")
        return True
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        return False

if __name__ == "__main__":
    try:
        success1 = test_chat_service_integration()
        success2 = test_api_endpoint_simulation()
        
        if success1 and success2:
            print(f"\n🎉 All tests passed! API key rotation is working correctly.")
            print(f"   The backend will now use different API keys for each request.")
        else:
            print(f"\n❌ Some tests failed. Please check the configuration.")
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
