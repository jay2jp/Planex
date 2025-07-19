#!/usr/bin/env python3
"""
Quick test script to check if Chrome browser cookies are accessible for pyktok
"""

import pyktok as pyk
import browser_cookie3

def test_chrome_cookies():
    """Test if Chrome cookies are accessible"""
    print("🔍 Testing Chrome Browser Cookie Access")
    print("=" * 40)
    
    # Test 1: Direct browser_cookie3 access
    print("\n1. Testing browser_cookie3 directly...")
    try:
        cookies = browser_cookie3.chrome(domain_name='.tiktok.com')
        cookie_list = list(cookies)
        print(f"✅ Chrome cookies accessible - Found {len(cookie_list)} cookies for TikTok")
        
        # Show some cookie info (without sensitive data)
        if cookie_list:
            print("📋 Sample cookies found:")
            for i, cookie in enumerate(cookie_list[:3]):  # Show first 3 cookies
                print(f"   - {cookie.name} (domain: {cookie.domain})")
        else:
            print("⚠️  No TikTok cookies found - visit tiktok.com in Chrome first")
            
    except Exception as e:
        print(f"❌ Chrome cookies not accessible: {e}")
        print("💡 Tip: See WSL_CHROME_SETUP.md for setup instructions")
    
    # Test 2: pyktok browser specification
    print("\n2. Testing pyktok browser specification...")
    try:
        pyk.specify_browser('chrome')
        print("✅ pyktok can use Chrome browser successfully")
    except Exception as e:
        print(f"❌ pyktok cannot use Chrome: {e}")
    
    # Test 3: Alternative browsers
    print("\n3. Testing alternative browsers...")
    browsers = ['firefox', 'edge', 'safari']
    
    for browser in browsers:
        try:
            # Test if browser_cookie3 can access this browser
            browser_func = getattr(browser_cookie3, browser, None)
            if browser_func:
                cookies = browser_func(domain_name='.tiktok.com')
                cookie_count = len(list(cookies))
                print(f"✅ {browser.title()}: {cookie_count} cookies found")
            else:
                print(f"❓ {browser.title()}: Not supported by browser_cookie3")
        except Exception as e:
            print(f"❌ {browser.title()}: {str(e)}")
    
    print("\n" + "=" * 40)
    print("🚀 Test Summary:")
    print("   - If Chrome works: Your app will have better TikTok rate limits")
    print("   - If Chrome fails: Your app will still work, just with more limitations")
    print("   - See WSL_CHROME_SETUP.md for detailed setup instructions")

def check_chrome_installation():
    """Check if Chrome is installed"""
    print("\n🔧 Chrome Installation Check")
    print("-" * 30)
    
    import subprocess
    import os
    
    # Check common Chrome locations
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium-browser',
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS
    ]
    
    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ Chrome found at: {path}")
            chrome_found = True
            break
    
    if not chrome_found:
        print("❌ Chrome not found in standard locations")
        print("💡 Install Chrome: See WSL_CHROME_SETUP.md")
    
    # Check via which command
    try:
        result = subprocess.run(['which', 'google-chrome'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Chrome in PATH: {result.stdout.strip()}")
        else:
            print("❌ Chrome not in PATH")
    except:
        print("❓ Could not check PATH")
    
    # Check Chrome version if available
    try:
        result = subprocess.run(['google-chrome', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"🔖 Version: {result.stdout.strip()}")
    except:
        try:
            result = subprocess.run(['google-chrome-stable', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"🔖 Version: {result.stdout.strip()}")
        except:
            print("❓ Could not check Chrome version")

if __name__ == "__main__":
    print("🧪 Chrome Cookie Test for TikTok Downloads")
    print()
    
    check_chrome_installation()
    test_chrome_cookies()
    
    print("\n📖 Next Steps:")
    print("   1. If Chrome works: You're all set!")
    print("   2. If Chrome fails: Check WSL_CHROME_SETUP.md")
    print("   3. Run your main app: python app.py")
    print("   4. Test TikTok downloads: python test_app.py") 