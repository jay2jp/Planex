# TikTok Video Scraper Service

A Python service that retrieves the top 15 TikTok videos posted within the last two weeks for a given hashtag, using the Apify TikTok Scraper.

## Overview

This service leverages the Apify TikTok Scraper (`clockworks/tiktok-scraper`) to bypass TikTok's anti-scraping measures and retrieve video data efficiently. The service filters videos by date (last two weeks) and sorts them by the number of likes (hearts) to return the most popular content.

## Features

- 🎯 Retrieves top 15 TikTok videos for any hashtag
- 📅 Filters videos from the last two weeks only
- ❤️ Sorts videos by number of likes (hearts) in descending order
- 🚀 Uses Apify's infrastructure to handle anti-scraping measures
- 🛡️ Comprehensive error handling for API issues and edge cases
- 💰 Cost-effective: ~$0.25 per request (50 videos × $0.005 per item)

## Prerequisites

1. **Python 3.x** installed on your system
2. **Apify account** with an API token
3. **Sufficient Apify credits** (free plan provides $5 monthly, enough for ~1,000 results)

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your environment variables:

```bash
cp env.example .env
# Edit .env and add your Apify API token
```

## Configuration

### Option 1: Using .env file (Recommended)

1. Copy the environment template file:
```bash
cp env.example .env
```

2. Edit the `.env` file and add your Apify API token:
```bash
APIFY_API_TOKEN=your_apify_token_here
```

### Option 2: Using Environment Variables

Set your Apify API token as an environment variable:

```bash
export APIFY_API_TOKEN='your_apify_token_here'
```

### Getting Your Apify API Token

1. Create an account at [Apify.com](https://apify.com/)
2. Go to your [Account Settings](https://console.apify.com/settings)
3. Copy your API token from the "Integrations" section
4. Add it to your `.env` file or set as an environment variable

## Usage

### Basic Usage

```python
from tiktok_scraper import get_top_tiktok_videos

# Get top 15 videos for a hashtag
videos = get_top_tiktok_videos("dance")

# Print the results
for i, url in enumerate(videos, 1):
    print(f"{i}. {url}")
```

### Running the Test Script

```bash
python test_tiktok_scraper.py
```

### Running the Main Script

```bash
python tiktok_scraper.py
```

### Running Examples

```bash
python example_usage.py
```

**Note:** All scripts automatically load environment variables from the `.env` file if it exists.

## Function Reference

### `get_top_tiktok_videos(hashtag: str) -> list`

**Parameters:**
- `hashtag` (str): The hashtag name without the '#' symbol (e.g., 'dance', 'cooking')

**Returns:**
- `list`: A list of up to 15 TikTok video URLs, sorted by likes in descending order

**Example:**
```python
videos = get_top_tiktok_videos("fitness")
# Returns: ['https://www.tiktok.com/@user1/video/123', 'https://www.tiktok.com/@user2/video/456', ...]
```

## Error Handling

The service handles various error scenarios gracefully:

- **Invalid/Missing API Token**: Returns empty list and logs error
- **Non-existent Hashtag**: Returns empty list
- **API Rate Limits**: Handled by Apify platform
- **Date Parsing Errors**: Skips problematic videos, continues processing
- **Network Issues**: Returns empty list and logs error

## Cost Considerations

- **Pricing**: $0.005 per video result
- **Request Cost**: ~$0.25 per hashtag (50 videos × $0.005)
- **Free Plan**: $5 monthly credit = ~1,000 results = ~20 hashtag requests
- **Optimization**: Service requests 50 videos to ensure enough recent content for filtering

## Limitations

- Only retrieves publicly available TikTok videos
- Limited to videos posted within the last two weeks
- Results depend on hashtag popularity and recent activity
- Subject to Apify's rate limits and usage policies

## File Structure

```
├── tiktok_scraper.py      # Main service implementation
├── test_tiktok_scraper.py # Test script with examples
├── example_usage.py       # Usage examples and demonstrations
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── .env                  # Your environment variables (create from env.example)
├── README.md             # This file
└── spec.md               # Original specification document
```

## Dependencies

- `apify-client>=1.0.0`: For interacting with Apify platform
- `python-dateutil>=2.8.0`: For parsing video creation dates
- `python-dotenv>=0.19.0`: For loading environment variables from .env file

## Troubleshooting

### Common Issues

1. **"APIFY_API_TOKEN environment variable is not set"**
   - Solution: Create a `.env` file from `env.example` and add your API token, or set it as an environment variable as shown in the Configuration section

2. **"No videos found for hashtag"**
   - Check if the hashtag exists and has recent videos
   - Try a more popular hashtag like "dance" or "music"

3. **Empty results**
   - Hashtag might not have videos from the last two weeks
   - Check your Apify account credits and usage limits

### Debug Mode

Enable debug logging to see detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and development purposes. Please ensure compliance with TikTok's Terms of Service and Apify's usage policies.

## Support

For issues related to:
- **This service**: Create an issue in this repository
- **Apify platform**: Check [Apify Documentation](https://docs.apify.com/)
- **TikTok Scraper**: Visit [clockworks/tiktok-scraper](https://apify.com/clockworks/tiktok-scraper)

## References

- [Apify TikTok Scraper](https://apify.com/clockworks/tiktok-scraper)
- [Apify Python Client Documentation](https://docs.apify.com/sdk/python/)
- [Apify Pricing](https://apify.com/pricing) 