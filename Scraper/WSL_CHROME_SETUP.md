# 🐧 Chrome Setup for WSL - TikTok Downloads

This guide helps you set up Chrome browser cookies in WSL for better TikTok download performance with pyktok.

## 🎯 Why This Matters

- **Without Chrome cookies**: TikTok downloads work but may hit rate limits sooner
- **With Chrome cookies**: Better rate limits, more reliable downloads, access to more content

## 🔧 Option 1: Install Chrome in WSL (Recommended)

### Step 1: Install Chrome in WSL
```bash
# Update package list
sudo apt update

# Install required dependencies
sudo apt install -y wget gnupg

# Add Google Chrome repository
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list

# Update and install Chrome
sudo apt update
sudo apt install -y google-chrome-stable
```

### Step 2: Create TikTok cookies
```bash
# Launch Chrome (this will create the profile directory)
google-chrome --no-sandbox --disable-gpu --remote-debugging-port=9222 &

# Visit TikTok to create cookies
# Open: http://localhost:9222 in your Windows browser
# Navigate to tiktok.com and browse a bit
# Close Chrome
pkill chrome
```

### Step 3: Test the setup
```bash
# Quick Chrome test
python test_chrome.py

# Then test your main app
python app.py
```

You should now see: `✅ PyKTok: Using Chrome browser for TikTok downloads`

## 🔗 Option 2: Use Windows Chrome Profile (Advanced)

### Step 1: Find Windows Chrome profile
In Windows PowerShell:
```powershell
# Find Chrome user data directory
echo $env:LOCALAPPDATA\Google\Chrome\User Data
```

### Step 2: Mount Windows Chrome directory in WSL
```bash
# Create symlink to Windows Chrome profile
mkdir -p ~/.config/google-chrome
ln -sf /mnt/c/Users/[YOUR_USERNAME]/AppData/Local/Google/Chrome/User\ Data/Default ~/.config/google-chrome/Default

# Replace [YOUR_USERNAME] with your actual Windows username
```

### Step 3: Set Chrome path for pyktok
Add this to your `.env` file:
```env
CHROME_USER_DATA_DIR=/home/[your_wsl_username]/.config/google-chrome
```

**Note**: Make sure your `.env` file has Instagram credentials commented out if not using them:
```env
# INSTA_USER=your_real_username  
# INSTA_PASS=your_real_password
```

## 🚀 Option 3: Alternative Browser Setup

If Chrome doesn't work, try Firefox:

```bash
# Install Firefox
sudo apt install -y firefox

# Update scraper.py to use Firefox
```

Then modify `scraper.py`:
```python
# Replace the browser specification section
try:
    pyk.specify_browser('firefox')  # Try Firefox instead
    print("✅ PyKTok: Using Firefox browser for TikTok downloads")
except Exception as e:
    try:
        pyk.specify_browser('chrome')
        print("✅ PyKTok: Using Chrome browser for TikTok downloads")
    except Exception as e2:
        print(f"⚠️  PyKTok: No browser cookies available ({str(e2)})")
        print("   Continuing without browser cookies (may have rate limits)")
```

## 🧪 Verification Steps

### Test 1: Quick Chrome cookie test
```bash
# Run the dedicated Chrome test script
python test_chrome.py
```

This will check:
- Chrome installation
- Cookie accessibility 
- pyktok browser compatibility
- Alternative browser options

### Test 2: Test with your app
```bash
python app.py
# Look for: "✅ PyKTok: Using Chrome browser for TikTok downloads"

# In another terminal:
python test_app.py
```

### Test 3: Manual verification
```bash
# Check Chrome installation
google-chrome --version

# Check if cookies directory exists
ls -la ~/.config/google-chrome/Default/Cookies 2>/dev/null || echo "No cookies found"
```

## 🐛 Troubleshooting

### Chrome not found
```bash
# Check if Chrome is in PATH
which google-chrome

# If not found, try:
sudo ln -sf /usr/bin/google-chrome-stable /usr/bin/google-chrome
```

### Permission issues
```bash
# Fix Chrome permissions
sudo chown -R $USER:$USER ~/.config/google-chrome
chmod -R 755 ~/.config/google-chrome
```

### WSL2 specific issues
```bash
# Install additional dependencies
sudo apt install -y libnss3-dev libgconf-2-4 libxss1 libxtst6 libxrandr2 libasound2-dev libpangocairo-1.0-0 libgtk-3-0
```

### Check browser_cookie3 directly
```python
# Test browser cookie access
import browser_cookie3

try:
    cookies = browser_cookie3.chrome(domain_name='.tiktok.com')
    print("✅ Chrome cookies accessible")
    print(f"Found {len(list(cookies))} cookies")
except Exception as e:
    print(f"❌ Chrome cookies not accessible: {e}")
```

## 💡 Pro Tips

1. **Visit TikTok first**: After installing Chrome, visit tiktok.com to create cookies
2. **Keep Chrome updated**: Run `sudo apt upgrade google-chrome-stable` occasionally  
3. **Clear cookies if issues**: Delete `~/.config/google-chrome/Default/Cookies` and revisit TikTok
4. **WSL2 preferred**: WSL2 generally works better than WSL1 for browser integration

## 🔄 Alternative: Use Windows Chrome with WSL Integration

If the above doesn't work, you can also:

1. **Install Windows Subsystem for Linux GUI apps** (WSLg)
2. **Use Windows Chrome directly** through WSL integration
3. **Copy cookies manually** from Windows to WSL (complex)

## ✅ Success Indicators

When working correctly, you'll see:
```bash
(.venv) user@hostname:~/project$ python app.py
✅ PyKTok: Using Chrome browser for TikTok downloads
Instagram: Using unauthenticated loader (public content only)
 * Running on all addresses (0.0.0.0)
```

## 📚 Additional Resources

- [WSL GUI Apps](https://docs.microsoft.com/en-us/windows/wsl/tutorials/gui-apps)
- [Chrome on Ubuntu](https://www.google.com/chrome/)
- [pyktok Documentation](https://github.com/dfreelon/pyktok)

Choose the option that works best for your setup! Option 1 (installing Chrome in WSL) is usually the most reliable.

## 📋 Note

The `browser_cookie3` dependency (included in `requirements.txt`) is what enables pyktok to access browser cookies. If you're still having issues after following this guide, you may need to install additional system dependencies or try alternative browsers. 