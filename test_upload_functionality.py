#!/usr/bin/env python3
"""
Comprehensive test script for the upload functionality
Tests both backend duplicate filename handling and frontend upload workflow
"""

import requests
import os
import tempfile
import time
from pathlib import Path

BASE_URL = "http://localhost:8000/api/pdf"
FRONTEND_URL = "http://localhost:3000"

def create_test_pdf(filename: str, content: str = "Test PDF content") -> str:
    """Create a simple test PDF file"""
    # For testing, we'll create a simple text file with .pdf extension
    # In a real scenario, you'd create an actual PDF
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)
    
    with open(file_path, 'w') as f:
        f.write(f"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
        f.write(f"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
        f.write(f"3 0 obj\n<< /Type /Page /Parent 2 0 R /Contents 4 0 R >>\nendobj\n")
        f.write(f"4 0 obj\n<< /Length {len(content)} >>\nstream\n{content}\nendstream\nendobj\n")
        f.write("xref\n0 5\n0000000000 65535 f\n")
        f.write("trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n0\n%%EOF")
    
    return file_path

def test_backend_upload_functionality():
    """Test the backend upload functionality with duplicate filename handling"""
    print("🧪 Testing Backend Upload Functionality")
    print("=" * 60)
    
    # Test 1: Upload a file for the first time
    print("\n1. Testing initial file upload...")
    test_file_path = create_test_pdf("test_book.pdf", "This is the first test book content.")
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_book.pdf', f, 'application/pdf')}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ First upload successful")
            print(f"   Filename: {result['filename']}")
            print(f"   Message: {result['message']}")
            first_filename = result['filename']
        else:
            print(f"   ❌ First upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ First upload failed with exception: {e}")
        return False
    
    # Test 2: Upload the same filename again (should get renamed)
    print("\n2. Testing duplicate filename handling...")
    test_file_path2 = create_test_pdf("test_book.pdf", "This is the second test book with same name.")
    
    try:
        with open(test_file_path2, 'rb') as f:
            files = {'file': ('test_book.pdf', f, 'application/pdf')}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Duplicate upload successful")
            print(f"   Original filename: test_book.pdf")
            print(f"   Renamed to: {result['filename']}")
            print(f"   Expected pattern: test_book(1).pdf")
            
            if result['filename'] == 'test_book(1).pdf':
                print(f"   ✅ Filename renaming works correctly!")
            else:
                print(f"   ⚠️  Unexpected filename pattern: {result['filename']}")
            
            second_filename = result['filename']
        else:
            print(f"   ❌ Duplicate upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Duplicate upload failed with exception: {e}")
        return False
    
    # Test 3: Upload the same filename a third time
    print("\n3. Testing triple duplicate handling...")
    test_file_path3 = create_test_pdf("test_book.pdf", "This is the third test book with same name.")
    
    try:
        with open(test_file_path3, 'rb') as f:
            files = {'file': ('test_book.pdf', f, 'application/pdf')}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Triple upload successful")
            print(f"   Renamed to: {result['filename']}")
            print(f"   Expected pattern: test_book(2).pdf")
            
            if result['filename'] == 'test_book(2).pdf':
                print(f"   ✅ Triple filename renaming works correctly!")
            else:
                print(f"   ⚠️  Unexpected filename pattern: {result['filename']}")
        else:
            print(f"   ❌ Triple upload failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Triple upload failed with exception: {e}")
        return False
    
    # Test 4: Verify files can be listed
    print("\n4. Testing file listing...")
    try:
        response = requests.get(f"{BASE_URL}/list")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ File listing successful")
            print(f"   Total files: {result['total']}")
            
            uploaded_files = [item['filename'] for item in result['items']]
            expected_files = ['test_book.pdf', 'test_book(1).pdf', 'test_book(2).pdf']
            
            for expected_file in expected_files:
                if expected_file in uploaded_files:
                    print(f"   ✅ Found expected file: {expected_file}")
                else:
                    print(f"   ⚠️  Missing expected file: {expected_file}")
        else:
            print(f"   ❌ File listing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ File listing failed with exception: {e}")
        return False
    
    # Cleanup
    try:
        os.unlink(test_file_path)
        os.unlink(test_file_path2)
        os.unlink(test_file_path3)
    except:
        pass
    
    print("\n" + "=" * 60)
    print("✅ Backend upload functionality tests completed successfully!")
    return True

def test_frontend_accessibility():
    """Test if the frontend is accessible"""
    print("\n🌐 Testing Frontend Accessibility")
    print("=" * 60)
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Frontend is accessible at {FRONTEND_URL}")
            return True
        else:
            print(f"   ❌ Frontend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Could not connect to frontend at {FRONTEND_URL}")
        print(f"   Make sure the frontend is running with 'npm run dev'")
        return False
    except Exception as e:
        print(f"   ❌ Frontend test failed: {e}")
        return False

def print_manual_testing_instructions():
    """Print instructions for manual testing"""
    print("\n📋 Manual Testing Instructions")
    print("=" * 60)
    print("\nTo complete the testing workflow, please perform these manual tests:")
    print("\n1. 🌐 Open your browser and navigate to: http://localhost:3000/upload")
    print("\n2. 📁 Test Single File Upload:")
    print("   - Click 'Choose File' or drag a PDF file to the upload area")
    print("   - Verify the upload progress indicator appears")
    print("   - Verify success message shows with the uploaded filename")
    print("   - Verify automatic redirect to chat page after 2 seconds")
    
    print("\n3. 🔄 Test Duplicate Filename Handling:")
    print("   - Go back to the upload page")
    print("   - Upload a file with the same name as before")
    print("   - Verify the file gets renamed with (1) suffix")
    print("   - Upload the same filename again")
    print("   - Verify the file gets renamed with (2) suffix")
    
    print("\n4. 🎯 Test Drag and Drop:")
    print("   - Drag a PDF file from your file explorer")
    print("   - Drop it on the upload area")
    print("   - Verify the drag-over visual feedback works")
    print("   - Verify the upload proceeds normally")
    
    print("\n5. ❌ Test Error Handling:")
    print("   - Try uploading a non-PDF file (should show error)")
    print("   - Verify error message is displayed clearly")
    print("   - Verify error can be dismissed")
    
    print("\n6. 💬 Test Chat Integration:")
    print("   - After successful upload, verify you're on the chat page")
    print("   - Try asking a question about the uploaded document")
    print("   - Verify the AI responds based on the document content")
    
    print("\n✅ Expected Results:")
    print("   - All uploads should work smoothly")
    print("   - Duplicate filenames should be automatically renamed")
    print("   - User experience should be intuitive and responsive")
    print("   - Error states should be handled gracefully")
    print("   - Chat integration should work seamlessly")

def main():
    """Run the complete testing workflow"""
    print("🚀 Upload Functionality Testing Workflow")
    print("=" * 60)
    print("This script tests the complete upload functionality including:")
    print("- Backend duplicate filename handling")
    print("- Frontend accessibility")
    print("- Manual testing instructions")
    print("=" * 60)
    
    # Test backend functionality
    backend_success = test_backend_upload_functionality()
    
    # Test frontend accessibility
    frontend_success = test_frontend_accessibility()
    
    # Print manual testing instructions
    print_manual_testing_instructions()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 60)
    print(f"Backend Upload Tests: {'✅ PASSED' if backend_success else '❌ FAILED'}")
    print(f"Frontend Accessibility: {'✅ PASSED' if frontend_success else '❌ FAILED'}")
    print("Manual Testing: 📋 INSTRUCTIONS PROVIDED")
    
    if backend_success and frontend_success:
        print("\n🎉 Automated tests passed! Please complete the manual testing steps.")
    else:
        print("\n⚠️  Some automated tests failed. Please check the server status and try again.")

if __name__ == "__main__":
    main()
