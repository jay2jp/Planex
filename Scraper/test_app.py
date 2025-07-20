#!/usr/bin/env python3
"""
Test script for the Gemini Video Analysis App
Tests the application with a specific TikTok video URL
"""

import requests
import json
import time

# Configuration
API_URL = "http://localhost:5000/analyze"
# Using working URLs from pyktok documentation
TEST_VIDEO_URL = "https://www.tiktok.com/@tiktok/video/7106594312292453675?is_copy_url=1&is_from_webapp=v1"

# Backup URLs that are confirmed to work
BACKUP_URLS = [
    "https://www.tiktok.com/@tiktok/video/7011536772089924869?is_copy_url=1&is_from_webapp=v1",  # TikTok official
    "https://www.tiktok.com/@marcusonthelow/video/7526360050126818591",  # Original URL (problematic)
]

def test_video_analysis():
    """Test the video analysis endpoint with the TikTok video"""
    
    print("🧪 Testing Gemini Video Analysis App")
    print("=" * 50)
    print(f"📹 Video URL: {TEST_VIDEO_URL}")
    print(f"🔗 API Endpoint: {API_URL}")
    print()
    
    # Test prompts to try
    test_prompts = [
        "What is the main topic or subject of this video?",
        "Describe what you see happening in this video.",
        "What is the person doing in this video?",
        "Summarize the content of this video in 2-3 sentences."
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"🔍 Test {i}: {prompt}")
        print("-" * 30)
        
        # Prepare the request
        payload = {
            "url": TEST_VIDEO_URL,
            "prompt": prompt
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            print("⏳ Sending request...")
            start_time = time.time()
            
            # Make the API request
            response = requests.post(API_URL, json=payload, headers=headers, timeout=300)
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏱️  Response time: {duration:.2f} seconds")
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Success!")
                print(f"📝 Analysis Result:")
                print(f"   {result.get('result', 'No result found')}")
            else:
                print("❌ Error!")
                try:
                    error_data = response.json()
                    print(f"🚨 Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"🚨 Raw response: {response.text}")
            
        except requests.exceptions.Timeout:
            print("⏰ Request timed out (5 minutes)")
        except requests.exceptions.ConnectionError:
            print("🚫 Connection error - is the server running on localhost:5000?")
        except Exception as e:
            print(f"💥 Unexpected error: {str(e)}")
        
        print()
        if i < len(test_prompts):
            print("⏸️  Waiting 3 seconds before next test...")
            time.sleep(3)
            print()

def test_with_backup_urls():
    """Test with backup URLs if the main one fails"""
    print("\n🔄 Testing Backup TikTok URLs")
    print("=" * 50)
    
    # Simple test prompt
    test_prompt = "What is happening in this video?"
    
    all_urls = [TEST_VIDEO_URL] + BACKUP_URLS
    
    for i, url in enumerate(all_urls):
        url_type = "Primary" if i == 0 else f"Backup {i}"
        print(f"🎬 {url_type} URL: {url}")
        
        payload = {
            "url": url,
            "prompt": test_prompt
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            print("⏳ Testing...")
            response = requests.post(API_URL, json=payload, headers=headers, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SUCCESS! This URL works!")
                print(f"📝 Sample result: {result.get('result', '')[:150]}...")
                return url  # Return the working URL
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"error": response.text}
                print(f"❌ Failed: {error_data.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"💥 Error: {str(e)}")
        
        print()
        
        if i < len(all_urls) - 1:
            print("⏳ Waiting 2 seconds before trying next URL...")
            time.sleep(2)
    
    print("❌ All URLs failed to work")
    return None

def test_server_health():
    """Test if the server is running"""
    print("🩺 Checking server health...")
    
    try:
        # Try a simple request to see if server responds
        response = requests.get("http://localhost:5000/", timeout=5)
        print("✅ Server is responding")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Server not reachable - make sure to run 'python app.py' first")
        return False
    except Exception as e:
        print(f"⚠️  Server health check failed: {str(e)}")
        return False

def test_invalid_requests():
    """Test error handling with invalid requests"""
    print("🔬 Testing error handling...")
    print("-" * 30)
    
    # Test 1: Missing prompt
    print("Test: Missing prompt")
    response = requests.post(API_URL, json={"url": TEST_VIDEO_URL}, timeout=30)
    print(f"Status: {response.status_code} (expected 400)")
    
    # Test 2: Missing URL
    print("Test: Missing URL")
    response = requests.post(API_URL, json={"prompt": "test"}, timeout=30)
    print(f"Status: {response.status_code} (expected 400)")
    
    # Test 3: Invalid URL
    print("Test: Invalid URL")
    response = requests.post(API_URL, json={"url": "https://invalid.com", "prompt": "test"}, timeout=30)
    print(f"Status: {response.status_code} (expected 500)")
    
    print("✅ Error handling tests completed")
    print()

if __name__ == "__main__":
    print("🚀 Starting Gemini Video Analysis App Tests")
    print()
    
    # Check if server is running
    if not test_server_health():
        print("\n💡 To start the server, run: python app.py")
        exit(1)
    
    print()
    
    # Test error handling
    test_invalid_requests()
    
    # Test main functionality
    test_video_analysis()
    
    # If main test had issues, try backup URLs
    print("\n" + "="*50)
    print("🔍 Quick check with backup URLs...")
    working_url = test_with_backup_urls()
    
    if working_url:
        print(f"\n✅ Found working URL: {working_url}")
        print("💡 Consider updating TEST_VIDEO_URL in this script to use the working URL")
    else:
        print("\n⚠️  All TikTok URLs failed. This could be due to:")
        print("   - TikTok rate limiting or API changes")
        print("   - Network/geographic restrictions")
        print("   - Videos being private or deleted")
        print("\n🔧 For detailed debugging, run: python debug_tiktok.py")
    
    print("\n🎉 Testing completed!")
    print()
    print("💡 Tips:")
    print("   - If you get connection errors, make sure the server is running: python app.py")
    print("   - If analysis fails, check your .env file has GOOGLE_API_KEY set")
    print("   - For TikTok issues: run 'python debug_tiktok.py' for detailed diagnostics")
    print("   - Chrome browser helps but isn't required for basic functionality") 