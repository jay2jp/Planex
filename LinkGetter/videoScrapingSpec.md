Specification for Python Service to Scrape Top Videos by Hashtag
Overview
This document specifies a Python service that retrieves the top 15 Instagram videos (including reels) and the top 15 TikTok videos posted within the last two weeks for a given hashtag, using web scraping techniques. The "top" videos are determined by the number of likes.
Requirements

Language: The service must be implemented in Python 3.x.
Dependencies:
selenium or playwright for browser automation and JavaScript rendering.
beautifulsoup4 for HTML parsing.
python-dateutil for date handling.
webdriver-manager (if using Selenium) for managing browser drivers.


Configuration:
The service should use a headless browser to avoid detection and for efficiency.
Implement delays between requests (2-5 seconds) to mimic human behavior and avoid rate limiting.



Function Signature
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

Implementation Details
General Scraping Approach

Use a headless browser (e.g., Chrome or Firefox in headless mode) to load pages and execute JavaScript.
Implement a delay of 2-5 seconds between page loads to avoid detection.
Handle potential CAPTCHAs or bot detection by implementing retry logic or using proxies (optional).

Instagram Scraping

Navigate to Hashtag Page:

URL: https://www.instagram.com/explore/tags/{hashtag}/
Wait for the page to load completely.


Extract Video Posts:

Use CSS selectors or XPath to find video post elements.
Extract the following for each video:
Video URL (e.g., https://www.instagram.com/p/{shortcode}/)
Like count (if visible, otherwise may need to visit each post page)
Post date (usually in a <time> tag)




Handle Pagination:

Instagram loads more posts as you scroll. Simulate scrolling to load additional posts.
Continue scrolling until no new posts are loaded or a sufficient number of posts are collected.


Filter and Sort Videos:

Parse the post dates using python-dateutil and filter videos posted within the last two weeks.
If like counts are not directly available, visit each video's page to extract the like count.
Collect videos into a list with their URL, like count, and date.
Sort the list by like count in descending order.
Select the top 15 videos (or fewer if not enough) and extract their URLs.



TikTok Scraping

Navigate to Hashtag Page:

URL: https://www.tiktok.com/tag/{hashtag}
Wait for the page to load completely.


Extract Video Posts:

Use CSS selectors or XPath to find video post elements.
Extract the following for each video:
Video URL (e.g., https://www.tiktok.com/@username/video/{video_id})
Like count
Post date (may require parsing relative dates like "2d ago")




Handle Infinite Scroll:

TikTok uses infinite scrolling. Simulate scrolling to load more videos.
Continue scrolling until no new videos are loaded or a sufficient number of videos are collected.


Filter and Sort Videos:

Parse the post dates (handling relative dates) and filter videos posted within the last two weeks.
Collect videos into a list with their URL, like count, and date.
Sort the list by like count in descending order.
Select the top 15 videos (or fewer if not enough) and extract their URLs.



Output Format

The function returns a dictionary:{
    "instagram": ["url1", "url2", ..., "urlN"],  # Up to 15 Instagram video URLs
    "tiktok": ["url1", "url2", ..., "urlM"]      # Up to 15 TikTok video URLs
}


If no videos are found for a platform, the corresponding list will be empty.

Error Handling

Element Not Found: If expected elements are not found on the page, log the error (optional) and continue with available data.
Page Load Failures: Implement retry logic (e.g., up to 3 attempts) for failed page loads.
Date Parsing Errors: Skip videos with unparseable dates.
Rate Limiting or Blocking: If detected, implement longer delays or use proxies (optional).

