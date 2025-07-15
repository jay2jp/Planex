# Apify Instagram Video Getter

This Python service retrieves the top 15 Instagram videos (including reels) posted within the last two weeks for a given hashtag using the Apify Instagram Hashtag Scraper.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Copy .env.example to .env and fill in your Apify API token:
   ```
   cp .env.example .env
   # Edit .env and add your token
   ```

3. The APIFY_API_TOKEN will be loaded from .env.

## Usage

Import and use the function from `instagram_scraper.py`:

```python
from instagram_scraper import get_top_instagram_videos

hashtag = 'dance'
videos = get_top_instagram_videos(hashtag)
print(videos)
```

## Notes

- Ensure you have sufficient Apify usage credits.
- Refer to spec.md for detailed specifications. 