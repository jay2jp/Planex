from playwright.sync_api import sync_playwright
import time
import os

def manual_login():
    """
    Opens a browser for manual login to TikTok.
    User can manually enter their credentials and the browser will stay open.
    """
    with sync_playwright() as p:
        # Create a user data directory to make browser appear more legitimate
        user_data_dir = os.path.join(os.getcwd(), "browser_data")
        
        # Launch persistent context with settings to make it less detectable as automated
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-extensions-except=',
                '--disable-extensions',
                '--no-first-run',
                '--no-default-browser-check',
                '--no-sandbox',
                '--disable-infobars',
                '--disable-dev-shm-usage',
                '--disable-browser-side-navigation',
                '--disable-gpu',
                '--remote-debugging-port=9222'
            ],
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York'
        )
        
        page = context.new_page()
        
        # Add script to remove webdriver property
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        # Navigate to TikTok
        print("Opening TikTok...")
        page.goto("https://tiktok.com")
        
        print("\n" + "="*50)
        print("MANUAL LOGIN INSTRUCTIONS:")
        print("="*50)
        print("1. The browser window is now open")
        print("2. Please log in to TikTok manually")
        print("3. You should now be able to use Google login")
        print("4. Once logged in, press Enter here to continue...")
        print("5. The script will then save your login state")
        print("="*50)
        
        # Wait for user to manually log in
        input("Press Enter after you've logged in...")
        
        # Check if user is logged in by looking for common logged-in elements
        try:
            # Look for profile or upload button (common indicators of being logged in)
            if page.locator('[data-e2e="profile-icon"]').is_visible() or page.locator('[data-e2e="upload-icon"]').is_visible():
                print("✓ Login detected!")
            else:
                print("⚠ Could not detect login status, but proceeding anyway...")
        except:
            print("⚠ Could not verify login status, but proceeding anyway...")
        
        # Save the browser state (cookies, localStorage, etc.)
        # This will save the login session for future use
        print("Saving login state...")
        context.storage_state(path="tiktok_login_state.json")
        
        print("✓ Login state saved to 'tiktok_login_state.json'")
        print("✓ You can now use this saved state in your scraping scripts")
        print("\nClosing browser in 3 seconds...")
        time.sleep(3)
        
        context.close()

if __name__ == "__main__":
    manual_login()
