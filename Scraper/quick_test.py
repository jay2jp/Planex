#!/usr/bin/env python3
"""
Quick test script to demonstrate working TikTok video analysis
Uses verified working URLs from pyktok documentation
"""

import requests
import json

# Use working TikTok URL
API_URL = "http://localhost:5000/analyze"
WORKING_TIKTOK_URL = "https://www.tiktok.com/@tiktok/video/7106594312292453675?is_copy_url=1&is_from_webapp=v1"

def quick_test():
    """Quick test with working TikTok URL"""
    print("🚀 Quick TikTok Analysis Test")
    print("=" * 40)
    print(f"📹 Using verified working URL: {WORKING_TIKTOK_URL}")
    print(f"🔗 API Endpoint: {API_URL}")
    print()
    
    # Simple test prompt
    test_prompt = "What is the main topic of this TikTok video?"
    
    payload = {
        "url": WORKING_TIKTOK_URL,
        "prompt": test_prompt
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("⏳ Sending analysis request...")
        response = requests.post(API_URL, json=payload, headers=headers, timeout=300)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! TikTok analysis working!")
            print()
            print("📝 Analysis Result:")
            print("-" * 50)
            print(result.get('result', 'No result found'))
            print("-" * 50)
            print()
            print("🎉 Your TikTok video analysis app is fully functional!")
            
        else:
            print("❌ Error!")
            try:
                error_data = response.json()
                print(f"🚨 Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"🚨 Raw response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("🚫 Connection error - is the server running?")
        print("💡 Start server with: python app.py")
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (this can take a few minutes for video processing)")
    except Exception as e:
        print(f"💥 Unexpected error: {str(e)}")

def test_server_health():
    """Quick server health check"""
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        return True
    except:
        return False

if __name__ == "__main__":
    print("🧪 Quick Test - TikTok Video Analysis")
    print()
    
    # Check if server is running
    if not test_server_health():
        print("❌ Server not reachable")
        print("💡 Start the server first: python app.py")
        print("💡 Then run this test: python quick_test.py")
        exit(1)
    
    print("✅ Server is responding")
    print()
    
    # Run the test
    quick_test()
    
    print()
    print("📚 Next Steps:")
    print("  - Try different TikTok URLs from popular accounts")
    print("  - Test with Instagram URLs for even more reliability") 
    print("  - Check out the full test suite: python test_app.py") 