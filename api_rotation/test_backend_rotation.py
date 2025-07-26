#!/usr/bin/env python3
"""
Test script to demonstrate API key rotation in the backend by making actual requests.
This will show the rotation logging in action.
"""

import requests
import json
import time

def test_backend_rotation():
    """Test API key rotation by making requests to the backend."""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Backend API Key Rotation")
    print("=" * 50)
    
    # Test the rotation status endpoint first
    try:
        print("📊 Checking rotation status...")
        response = requests.get(f"{base_url}/api/chat/api-rotation-status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Rotation Status: {json.dumps(status, indent=2)}")
        else:
            print(f"❌ Failed to get rotation status: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error checking rotation status: {e}")
        return
    
    # First, select a PDF
    print(f"\n📚 Selecting a PDF for testing...")
    try:
        # List available PDFs
        pdf_response = requests.get(f"{base_url}/api/pdf/list")
        if pdf_response.status_code == 200:
            pdfs = pdf_response.json().get('pdfs', [])
            if pdfs:
                # Select the first PDF
                first_pdf = pdfs[0]['filename']
                print(f"   Found PDF: {first_pdf}")

                # Select the PDF
                select_response = requests.post(
                    f"{base_url}/api/pdf/select",
                    json={"filename": first_pdf}
                )
                if select_response.status_code == 200:
                    print(f"✅ PDF selected successfully: {first_pdf}")
                else:
                    print(f"❌ Failed to select PDF: {select_response.status_code}")
                    return
            else:
                print(f"❌ No PDFs found in the books directory")
                return
        else:
            print(f"❌ Failed to list PDFs: {pdf_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error selecting PDF: {e}")
        return

    # Test multiple chat requests to trigger rotation
    print(f"\n🔄 Making multiple requests to trigger API key rotation...")
    print("   (Check the backend logs to see rotation in action)")

    test_messages = [
        "What is the main topic of this document?",
        "Can you summarize the key points?",
        "What are the most important concepts discussed?",
        "Explain the main ideas in simple terms.",
        "What should I focus on when studying this?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        try:
            print(f"\n📤 Request {i}: Sending message...")
            print(f"   Message: {message[:50]}...")
            
            # Make the request
            response = requests.post(
                f"{base_url}/api/chat",
                json={"message": message},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')[:100]
                print(f"✅ Response received: {response_text}...")
                print(f"   👀 Check backend logs for rotation info!")
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"   Error: {response.text}")
            
            # Small delay between requests
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error making request {i}: {e}")
    
    print(f"\n📊 Final rotation status check...")
    try:
        response = requests.get(f"{base_url}/api/chat/api-rotation-status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Final Status: {json.dumps(status, indent=2)}")
        else:
            print(f"❌ Failed to get final status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking final status: {e}")
    
    print(f"\n🎉 Test completed!")
    print(f"   Each request should have used a different API key.")
    print(f"   Check the backend terminal logs for rotation messages like:")
    print(f"   'INFO:root:🔄 API ROTATION: Using key #X/14 - AIzaSy...'")

if __name__ == "__main__":
    try:
        test_backend_rotation()
    except KeyboardInterrupt:
        print(f"\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
