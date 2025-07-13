# Video Scraping Service

A Python service that scrapes the top 15 Instagram videos (including reels) and the top 15 TikTok videos posted within the last two weeks for a given hashtag.

## Features

- **Instagram Scraping**: Retrieves videos and reels from hashtag pages
- **TikTok Scraping**: Retrieves videos from hashtag pages
- **Date Filtering**: Only includes videos posted within the last 2 weeks
- **Like-based Sorting**: Returns videos sorted by number of likes (descending)
- **Headless Browser**: Uses Playwright for JavaScript rendering
- **Rate Limiting**: Implements delays to respect platform resources
- **Error Handling**: Robust error handling and logging

## Installation

1. **Install Dependencies**:
   ```bash
   python setup.py
   ```
   
   This will install all required Python packages and set up Playwright browsers.

2. **Manual Installation** (if setup.py fails):
   ```bash
   pip install -r requirements.txt
   playwright install
   playwright install-deps
   ```

## Usage

### Basic Usage

```python
from video_scraper import get_top_videos

# Get top videos for a hashtag
result = get_top_videos('dance')

print(f"Instagram videos: {len(result['instagram'])}")
print(f"TikTok videos: {len(result['tiktok'])}")

# Access the URLs
for url in result['instagram']:
    print(f"Instagram: {url}")

for url in result['tiktok']:
    print(f"TikTok: {url}")
```

### Command Line Usage

```bash
python video_scraper.py
```

This will run a test with the hashtag 'dance' and display the results.

## Function Signature

```python
def get_top_videos(hashtag: str) -> dict:
    """
    Retrieves the top 15 Instagram videos and top 15 TikTok videos
    posted in the last two weeks for the given hashtag using web scraping.

    Args:
        hashtag (str): The hashtag name without the '#' symbol (e.g., 'dance').

    Returns:
        dict: A dictionary with keys 'instagram' and 'tiktok', each containing a list
              of up to 15 video URLs. If fewer than 15 videos are found, the list will
              contain all available videos.
              
    Note:
        - For Instagram, the service retrieves videos, which include reels, due to scraping limitations.
    """
```

## Output Format

The function returns a dictionary with the following structure:

```python
{
    "instagram": ["url1", "url2", ..., "urlN"],  # Up to 15 Instagram video URLs
    "tiktok": ["url1", "url2", ..., "urlM"]      # Up to 15 TikTok video URLs
}
```

## Configuration

The service is configured with the following default settings:

- **Delays**: 2-5 seconds between requests
- **Headless Mode**: Browser runs in headless mode
- **Date Filter**: Only videos from the last 2 weeks
- **Max Results**: Top 15 videos per platform
- **Scroll Attempts**: 10 for Instagram, 15 for TikTok

## Error Handling

The service handles various error scenarios:

- **Missing Elements**: Continues with available data if elements are not found
- **Page Load Failures**: Implements retry logic
- **Date Parsing Errors**: Skips videos with unparseable dates
- **Rate Limiting**: Uses delays to avoid detection

## Logging

The service uses Python's logging module to provide information about:

- Pages being scraped
- Videos found
- Errors encountered
- Processing progress

## Dependencies

- `playwright>=1.40.0` - Browser automation
- `beautifulsoup4>=4.12.0` - HTML parsing
- `python-dateutil>=2.8.0` - Date parsing
- `requests>=2.31.0` - HTTP requests
- `lxml>=4.9.0` - XML/HTML parsing

## Platform-Specific Notes

### Instagram
- Scrapes from `/explore/tags/{hashtag}/` pages
- Handles pagination through scrolling
- Visits individual posts to extract like counts
- Filters for video content (including reels)

### TikTok
- Scrapes from `/tag/{hashtag}` pages
- Handles infinite scrolling
- Parses relative dates (e.g., "2d ago")
- Handles like count suffixes (K, M)

## Limitations

- Subject to platform changes (HTML structure)
- Rate limiting may affect results
- Some videos may not be accessible due to privacy settings
- Like counts may not always be available
- Performance depends on network speed and platform response

## Testing

To test the service:

```bash
python video_scraper.py
```

Or create a custom test:

```python
from video_scraper import get_top_videos

# Test with different hashtags
hashtags = ['dance', 'music', 'funny', 'art']

for hashtag in hashtags:
    result = get_top_videos(hashtag)
    print(f"Hashtag: {hashtag}")
    print(f"  Instagram: {len(result['instagram'])} videos")
    print(f"  TikTok: {len(result['tiktok'])} videos")
```

## Troubleshooting

### Common Issues

1. **Browser Installation**: Make sure Playwright browsers are installed
   ```bash
   playwright install
   ```

2. **System Dependencies**: Install system dependencies for Playwright
   ```bash
   playwright install-deps
   ```

3. **Rate Limiting**: If you encounter rate limiting, the service will automatically add delays

4. **Empty Results**: Check if the hashtag exists and has recent videos

### Error Messages

- `Error scraping Instagram/TikTok`: Platform-specific scraping failed
- `Failed to parse date`: Date parsing error (video will be skipped)
- `Element not found`: HTML structure may have changed

## Contributing

When making changes:

1. Update the HTML selectors if platforms change their structure
2. Adjust delays if rate limiting becomes an issue
3. Add more robust error handling for edge cases
4. Update tests and documentation

## License

This project is for educational and research purposes. Please respect the terms of service of Instagram and TikTok when using this service. 