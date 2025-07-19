# 🎬 Gemini Video Analysis App

A Flask web application that downloads videos from TikTok and Instagram and analyzes them using Google's Gemini 1.5 Pro Vision API based on user prompts.

## 🌟 Features

- **Multi-Platform Support**: Download videos from TikTok and Instagram
- **AI-Powered Analysis**: Uses Google Gemini 1.5 Pro for intelligent video analysis
- **Robust Session Management**: Stable Instagram downloads with session persistence
- **Automatic Cleanup**: Temporary files are automatically removed after processing
- **RESTful API**: Simple JSON-based API for easy integration
- **Error Handling**: Comprehensive error handling with meaningful responses

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API Key
- Instagram account credentials (optional - for better rate limits)
- Chrome browser (optional - improves TikTok download rate limits)

### Installation

1. **Clone or download the project files**
   ```bash
   # Ensure you have these files:
   # app.py, scraper.py, gemini_analyzer.py, requirements.txt, test_app.py
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   # Google Gemini API Key (Required)
   GOOGLE_API_KEY="your_gemini_api_key_here"
   
   # Instagram Credentials (Optional - for better rate limits and reliability)
   # Leave these lines commented out or empty to use unauthenticated access
   # INSTA_USER=your_real_instagram_username
   # INSTA_PASS=your_real_instagram_password
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

The server will start on `http://localhost:5000`

### 🔧 Optional: Chrome Setup for WSL Users

If you're using WSL and want better TikTok download performance, see the detailed guide:
📖 **[WSL Chrome Setup Guide](WSL_CHROME_SETUP.md)**

This will help you get Chrome browser cookies working for improved rate limits and reliability.

### 🧪 Testing

Multiple test files are included to verify everything works correctly:

```bash
# Test Chrome browser cookies (optional - for better TikTok performance)
python test_chrome.py

# Test the main application (while the server is running)
python test_app.py
```

The test script will:
- Check server connectivity
- Test error handling with invalid requests
- Analyze a sample TikTok video (`@marcusonthelow/video/7526360050126818591`) with multiple prompts
- Show response times and detailed results

**Expected output:**
```
🚀 Starting Gemini Video Analysis App Tests

🩺 Checking server health...
✅ Server is responding

🔬 Testing error handling...
...

🧪 Testing Gemini Video Analysis App
📹 Video URL: https://www.tiktok.com/@marcusonthelow/video/7526360050126818591
📝 Analysis Result: [Gemini's analysis of the video content]
```

## 📡 API Documentation

### Analyze Video

**Endpoint:** `POST /analyze`

**Content-Type:** `application/json`

**Request Body:**
```json
{
    "url": "https://www.tiktok.com/@username/video/1234567890",
    "prompt": "What cooking techniques are demonstrated in this video?"
}
```

**Supported URL Formats:**
- TikTok: `https://www.tiktok.com/@username/video/1234567890`
- Instagram Reels: `https://www.instagram.com/reel/ABC123DEF456/`

**Success Response (200):**
```json
{
    "result": "The video demonstrates several cooking techniques including sautéing vegetables, proper knife techniques for dicing onions, and the importance of mise en place. The chef shows how to achieve proper caramelization by controlling heat and timing..."
}
```

**Error Responses:**

*Missing fields (400):*
```json
{
    "error": "Both 'url' and 'prompt' are required fields."
}
```

*Invalid content type (415):*
```json
{
    "error": "Request must be JSON"
}
```

*Processing error (500):*
```json
{
    "error": "An internal error occurred: Invalid URL. Must be a public TikTok or Instagram link."
}
```

## 💡 Usage Examples

### Example 1: Cooking Analysis
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.tiktok.com/@chef/video/1234567890",
    "prompt": "List all the ingredients and cooking steps shown in this recipe."
  }'
```

### Example 2: Fashion Analysis
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.instagram.com/reel/ABC123DEF456/",
    "prompt": "Describe the outfit and styling choices in this video."
  }'
```

### Example 3: Educational Content
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.tiktok.com/@educator/video/9876543210",
    "prompt": "Summarize the key learning points from this educational video."
  }'
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | ✅ | Your Google Gemini API key |
| `INSTA_USER` | ❌ | Instagram username (optional - improves rate limits) |
| `INSTA_PASS` | ❌ | Instagram password (optional - improves rate limits) |
| `PORT` | ❌ | Server port (defaults to 5000) |

### Getting API Keys

1. **Google Gemini API Key**:
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Create a new project or select existing one
   - Navigate to API Keys section
   - Generate a new API key

2. **Instagram Credentials** (Optional):
   - **Without credentials**: The app can download public Instagram content using unauthenticated access
   - **With credentials**: Better rate limits, more reliable downloads, and access to more content
   - Use a valid Instagram account if providing credentials
   - Consider creating a dedicated account for API usage
   - Ensure the account can view public content

## 🛠️ Technical Details

### Architecture

- **`app.py`**: Flask server with REST API endpoint
- **`scraper.py`**: Video downloading logic for TikTok and Instagram
- **`gemini_analyzer.py`**: Google Gemini API integration for video analysis

### Dependencies

- **Flask**: Web framework for the REST API
- **google-generativeai**: Google Gemini API client
- **instaloader**: Instagram content downloading
- **pyktok**: TikTok video downloading (with automatic browser fallback)
- **pandas**: Data processing for video metadata
- **python-dotenv**: Environment variable management

### TikTok Download Behavior

- **With Chrome browser**: Uses browser cookies for better rate limits and reliability
- **Without Chrome**: Falls back to unauthenticated downloads (may hit rate limits sooner)
- **Automatic detection**: The app automatically detects browser availability and adjusts accordingly

### Session Management

The application automatically manages Instagram access:
- **With credentials**: Sessions are saved to `sessions/` directory with automatic login and session persistence
- **Without credentials**: Uses unauthenticated access for public content (may hit rate limits sooner)
- Robust error handling for session and access issues

### File Cleanup

- All downloaded videos are stored in temporary directories
- Automatic cleanup occurs after processing (success or failure)
- Uploaded files are removed from Gemini servers after analysis

## 🚨 Troubleshooting

### Common Issues

1. **"TikTok video file not found" or browser cookie errors**
   - **Chrome not found**: The app will work without Chrome but may have rate limits
   - **WSL/Linux**: Chrome browser cookies may not be accessible in WSL environments
   - **Alternative**: Try installing Chrome or use without browser cookies (automatic fallback)
   - Check if the TikTok URL is public and accessible

2. **Instagram download errors**
   - **If using unauthenticated access**: Rate limits may be hit more quickly
   - **If using credentials**: Verify credentials in `.env` file
   - Check if Instagram account is not locked/restricted
   - Try logging in manually to verify credentials
   - Some private or restricted content may not be accessible without authentication

3. **Gemini API errors**
   - Verify your API key is correct and active
   - Check if you have sufficient API quota
   - Ensure the video file is not corrupted

4. **Import errors**
   - Run `pip install -r requirements.txt` to install all dependencies
   - Ensure you're using Python 3.8+

5. **Browser cookie errors (BrowserCookieError)**
   - Common in WSL/Linux environments where Chrome cookies aren't accessible
   - The app automatically falls back to work without browser cookies
   - You should see: "⚠️ PyKTok: Could not access Chrome browser" followed by normal operation
   - This is not a fatal error - TikTok downloads will still work
   - **For better performance**: See `WSL_CHROME_SETUP.md` for Chrome setup in WSL

### Debug Mode

Run with debug enabled for detailed error information:
```bash
python app.py
# Debug mode is enabled by default in the application
```

## 📄 License

This project is provided as-is for educational and development purposes.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

## ⚠️ Disclaimer

- Respect platform terms of service when downloading content
- Only download public content that you have permission to access
- Be mindful of API rate limits and quotas
- Use responsibly and ethically 