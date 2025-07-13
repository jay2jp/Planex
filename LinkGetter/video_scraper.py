import asyncio
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import random

from playwright.async_api import async_playwright, Page, Browser
from bs4 import BeautifulSoup
from dateutil.parser import parse as date_parse
from dateutil.relativedelta import relativedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VideoData:
    """Data structure for video information"""
    url: str
    likes: int
    date: datetime

class VideoScraper:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        
        # Launch browser in headed mode with stealth settings
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Using headed browser as requested
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--start-maximized',
            ]
        )
        
        # Create new context with user agent
        context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        
        # Create new page
        self.page = await context.new_page()
        
        # Set additional headers
        await self.page.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Remove automation indicators
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Override the chrome object
            delete window.chrome;
            
            // Override the plugins property
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Override the languages property
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
        """)
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def _delay(self, min_seconds: float = 2.0, max_seconds: float = 5.0):
        """Add random delay between actions"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)

    def _parse_relative_date(self, date_str: str) -> Optional[datetime]:
        """Parse relative date strings like '2 days ago', '1 week ago', etc."""
        try:
            now = datetime.now()
            date_str = date_str.lower().strip()
            
            # Handle various formats
            if 'just now' in date_str or 'now' in date_str:
                return now
            elif 'minute' in date_str:
                minutes = int(re.search(r'(\d+)', date_str).group(1))
                return now - timedelta(minutes=minutes)
            elif 'hour' in date_str:
                hours = int(re.search(r'(\d+)', date_str).group(1))
                return now - timedelta(hours=hours)
            elif 'day' in date_str:
                days = int(re.search(r'(\d+)', date_str).group(1))
                return now - timedelta(days=days)
            elif 'week' in date_str:
                weeks = int(re.search(r'(\d+)', date_str).group(1))
                return now - timedelta(weeks=weeks)
            elif 'month' in date_str:
                months = int(re.search(r'(\d+)', date_str).group(1))
                return now - relativedelta(months=months)
            elif 'year' in date_str:
                years = int(re.search(r'(\d+)', date_str).group(1))
                return now - relativedelta(years=years)
            
            return None
        except:
            return None
    
    def _is_within_two_weeks(self, date: datetime) -> bool:
        """Check if date is within the last two weeks"""
        two_weeks_ago = datetime.now() - timedelta(weeks=2)
        return date >= two_weeks_ago

    async def _scrape_instagram_videos(self, hashtag: str) -> List[VideoData]:
        """Scrape Instagram videos for a given hashtag following the spec requirements"""
        videos = []
        
        try:
            url = f"https://www.instagram.com/explore/tags/{hashtag}/"
            logger.info(f"Navigating to Instagram hashtag page: {url}")
            
            # Navigate with retry logic (up to 3 attempts as per spec)
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    await self.page.goto(url, wait_until='networkidle', timeout=30000)
                    await self._delay(2, 5)  # 2-5 second delay as per spec
                    break
                except Exception as e:
                    logger.warning(f"Instagram navigation attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        raise
                    await self._delay(5, 8)  # Longer wait before retry
            
            # Wait for content to load
            content_loaded = False
            selectors_to_try = [
                'article',
                '[role="main"]',
                'main',
                'section'
            ]
            
            for selector in selectors_to_try:
                try:
                    await self.page.wait_for_selector(selector, timeout=10000)
                    content_loaded = True
                    logger.info(f"Instagram content loaded with selector: {selector}")
                    break
                except:
                    continue
            
            if not content_loaded:
                logger.warning("No content found on Instagram page")
                return videos
            
            # Collect video posts through scrolling (as per spec)
            collected_urls = set()  # Avoid duplicates
            scroll_attempts = 0
            max_scrolls = 8  # Reasonable limit
            no_new_content_count = 0
            
            while scroll_attempts < max_scrolls and no_new_content_count < 3:
                # Get current page content
                content = await self.page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Find video/reel links
                video_links = []
                
                # Look for reel links first (these are definitely videos)
                reel_links = soup.find_all('a', href=re.compile(r'/reel/'))
                for link in reel_links:
                    href = link.get('href')
                    if href and href not in collected_urls:
                        video_links.append(href)
                        collected_urls.add(href)
                
                # Also look for regular post links that might be videos
                post_links = soup.find_all('a', href=re.compile(r'/p/'))
                for link in post_links:
                    href = link.get('href')
                    if href and href not in collected_urls:
                        video_links.append(href)
                        collected_urls.add(href)
                
                # Process found links
                initial_video_count = len(videos)
                
                for href in video_links:
                    if len(videos) >= 50:  # Collect more than needed for better filtering
                        break
                    
                    try:
                        if not href.startswith('http'):
                            post_url = "https://www.instagram.com" + href
                        else:
                            post_url = href
                        
                        # Get detailed information (like count and date)
                        video_data = await self._get_instagram_video_details(post_url)
                        if video_data and self._is_within_two_weeks(video_data.date):
                            videos.append(video_data)
                            logger.info(f"Found Instagram video: {post_url} (likes: {video_data.likes})")
                        
                        # Small delay between processing videos
                        await self._delay(1, 2)
                        
                    except Exception as e:
                        logger.warning(f"Error processing Instagram link {href}: {e}")
                        continue
                
                # Check if we found new content
                if len(videos) == initial_video_count:
                    no_new_content_count += 1
                else:
                    no_new_content_count = 0
                
                # Scroll to load more content
                await self.page.evaluate("window.scrollBy(0, 1000)")
                await self._delay(2, 4)  # Wait for content to load
                scroll_attempts += 1
                
                logger.info(f"Instagram scroll {scroll_attempts}/{max_scrolls}, found {len(videos)} videos")
        
        except Exception as e:
            logger.error(f"Error scraping Instagram: {e}")
        
        return videos

    async def _get_instagram_video_details(self, post_url: str) -> Optional[VideoData]:
        """Get detailed information for an Instagram video post"""
        try:
            # Open post in new tab to avoid losing main page
            new_page = await self.page.context.new_page()
            
            try:
                await new_page.goto(post_url, wait_until='networkidle', timeout=20000)
                await asyncio.sleep(2)  # Give page time to load
                
                # Get page content
                content = await new_page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract like count
                likes = 0
                like_patterns = [
                    r'(\d+(?:,\d+)*)\s*likes?',
                    r'(\d+(?:,\d+)*)\s*others?',
                    r'Liked by.*?(\d+(?:,\d+)*)',
                    r'"like_count":(\d+)',
                    r'"likes":{"count":(\d+)'
                ]
                
                for pattern in like_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        try:
                            likes = int(matches[0].replace(',', ''))
                            break
                        except:
                            continue
                
                # Extract date
                date = datetime.now()
                
                # Try to find time elements
                time_elements = soup.find_all('time')
                for elem in time_elements:
                    datetime_attr = elem.get('datetime')
                    if datetime_attr:
                        try:
                            date = date_parse(datetime_attr)
                            break
                        except:
                            continue
                
                # Also try to find date in JSON-LD or other structured data
                if date == datetime.now():
                    script_tags = soup.find_all('script', type='application/ld+json')
                    for script in script_tags:
                        try:
                            data = script.get_text()
                            if 'datePublished' in data:
                                date_match = re.search(r'"datePublished":"([^"]+)"', data)
                                if date_match:
                                    date = date_parse(date_match.group(1))
                                    break
                        except:
                            continue
                
                return VideoData(url=post_url, likes=likes, date=date)
                
            finally:
                await new_page.close()
                
        except Exception as e:
            logger.warning(f"Error getting Instagram video details for {post_url}: {e}")
            return VideoData(url=post_url, likes=0, date=datetime.now())

    async def _scrape_tiktok_videos(self, hashtag: str) -> List[VideoData]:
        """Scrape TikTok videos for a given hashtag following the spec requirements"""
        videos = []
        
        try:
            # Generate timestamp for the search URL
            import time
            timestamp = int(time.time() * 1000)
            
            # Try different URL formats that work with TikTok's current system
            urls_to_try = [
                f"https://www.tiktok.com/search/video?lang=en&q={hashtag}&t={timestamp}",
                f"https://www.tiktok.com/search/video?lang=en&q=%23{hashtag}&t={timestamp}",
                f"https://www.tiktok.com/search?q=%23{hashtag}&t=video",
                f"https://www.tiktok.com/tag/{hashtag}",
                f"https://www.tiktok.com/discover/{hashtag}"
            ]
            
            successful_url = None
            
            for url in urls_to_try:
                logger.info(f"Trying TikTok URL: {url}")
                
                # Navigate with retry logic (up to 3 attempts as per spec)
                max_retries = 3
                navigation_successful = False
                
                for attempt in range(max_retries):
                    try:
                        await self.page.goto(url, wait_until='networkidle', timeout=30000)
                        await self._delay(3, 6)  # Longer delay for TikTok
                        
                        # Check if we're on the right page (not redirected to For You)
                        current_url = self.page.url
                        page_title = await self.page.title()
                        
                        logger.info(f"Current URL: {current_url}")
                        logger.info(f"Page title: {page_title}")
                        
                        # Check if we're NOT on the For You page
                        if 'foryou' not in current_url.lower():
                            # Check if we're on a search/hashtag page
                            if (hashtag.lower() in current_url.lower() or 
                                hashtag.lower() in page_title.lower() or
                                'search' in current_url.lower() or
                                'tag' in current_url.lower() or
                                'discover' in current_url.lower()):
                                
                                # Check if page content contains hashtag-related elements
                                page_content = await self.page.content()
                                if (f'{hashtag}' in page_content or 
                                    f'#{hashtag}' in page_content or
                                    f'tag/{hashtag}' in page_content or
                                    f'discover/{hashtag}' in page_content or
                                    'search' in page_content):
                                    
                                    logger.info(f"Successfully navigated to hashtag page: {current_url}")
                                    navigation_successful = True
                                    successful_url = url
                                    break
                        
                        logger.warning(f"Redirected to For You page or wrong page: {current_url}")
                        
                    except Exception as e:
                        logger.warning(f"TikTok navigation attempt {attempt + 1} failed: {e}")
                        if attempt == max_retries - 1:
                            break  # Try next URL
                        await self._delay(5, 8)  # Longer wait before retry
                
                if navigation_successful:
                    break
                    
                await self._delay(3, 5)  # Wait before trying next URL
            
            if not successful_url:
                logger.error("Failed to navigate to any TikTok hashtag page - all URLs redirected to For You")
                return videos
            
            # Try multiple selectors for content (updated for search page)
            content_selectors = [
                '[data-e2e="search-video-item"]',
                '[data-e2e="challenge-item"]',
                '[data-e2e="video-item"]',
                'div[data-e2e*="video"]',
                'div[data-e2e*="item"]',
                'a[href*="/video/"]',
                'div[class*="video"]',
                'div[class*="DivItemContainer"]',
                'div[class*="DivVideoWrapper"]',
                'div[class*="VideoItemContainer"]'
            ]
            
            content_found = False
            working_selector = None
            
            for selector in content_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=10000)
                    content_found = True
                    working_selector = selector
                    logger.info(f"TikTok content found with selector: {selector}")
                    break
                except:
                    continue
            
            if not content_found:
                logger.warning("No content selectors found on TikTok page, trying fallback approach")
                # Fallback: look for video links in page source
                content = await self.page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Multiple fallback approaches
                video_links = []
                
                # Look for video URLs in href attributes
                for pattern in [r'/video/\d+', r'/@[\w.]+/video/\d+']:
                    links = soup.find_all('a', href=re.compile(pattern))
                    video_links.extend(links)
                
                # Look for video URLs in the page source
                video_url_pattern = r'https://www\.tiktok\.com/@[\w.]+/video/\d+'
                video_urls = re.findall(video_url_pattern, content)
                
                for video_url in video_urls[:15]:  # Limit to prevent too many requests
                    video_data = VideoData(url=video_url, likes=0, date=datetime.now())
                    videos.append(video_data)
                    logger.info(f"Found TikTok video (URL pattern): {video_url}")
                
                for link in video_links[:15]:  # Limit to prevent too many requests
                    href = link.get('href')
                    if href:
                        if not href.startswith('http'):
                            video_url = "https://www.tiktok.com" + href
                        else:
                            video_url = href
                        
                        video_data = VideoData(url=video_url, likes=0, date=datetime.now())
                        videos.append(video_data)
                        logger.info(f"Found TikTok video (fallback): {video_url}")
                
                return videos
            
            # Handle infinite scroll (as per spec)
            collected_urls = set()
            scroll_attempts = 0
            max_scrolls = 10
            no_new_content_count = 0
            
            while scroll_attempts < max_scrolls and no_new_content_count < 3:
                # Get current page content
                content = await self.page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Find video elements
                if working_selector:
                    video_items = soup.select(working_selector)
                else:
                    video_items = soup.find_all('a', href=re.compile(r'/video/'))
                
                initial_video_count = len(videos)
                
                for item in video_items:
                    if len(videos) >= 50:  # Collect more than needed for better filtering
                        break
                    
                    try:
                        # Extract video URL
                        if item.name == 'a':
                            link_elem = item
                        else:
                            link_elem = item.find('a')
                        
                        if not link_elem or not link_elem.get('href'):
                            continue
                        
                        href = link_elem.get('href')
                        if href in collected_urls:
                            continue
                        
                        collected_urls.add(href)
                        
                        if not href.startswith('http'):
                            video_url = "https://www.tiktok.com" + href
                        else:
                            video_url = href
                        
                        # Extract like count
                        likes = 0
                        item_text = item.get_text()
                        
                        # Look for like count patterns
                        like_patterns = [
                            r'(\d+(?:\.\d+)?)\s*([KMB])\s*likes?',
                            r'(\d+(?:,\d+)*)\s*likes?',
                            r'(\d+(?:\.\d+)?)\s*([KMB])',
                            r'(\d+(?:,\d+)*)'
                        ]
                        
                        for pattern in like_patterns:
                            matches = re.findall(pattern, item_text, re.IGNORECASE)
                            if matches:
                                try:
                                    if len(matches[0]) == 2:  # Has suffix
                                        base_likes = float(matches[0][0])
                                        suffix = matches[0][1].upper()
                                        if suffix == 'K':
                                            likes = int(base_likes * 1000)
                                        elif suffix == 'M':
                                            likes = int(base_likes * 1000000)
                                        elif suffix == 'B':
                                            likes = int(base_likes * 1000000000)
                                        else:
                                            likes = int(base_likes)
                                    else:
                                        likes = int(matches[0].replace(',', ''))
                                    break
                                except:
                                    continue
                        
                        # Extract date (handle relative dates)
                        date = datetime.now()
                        date_patterns = [
                            r'(\d+)\s*days?\s*ago',
                            r'(\d+)\s*weeks?\s*ago',
                            r'(\d+)\s*months?\s*ago',
                            r'(\d+)\s*hours?\s*ago',
                            r'(\d+)\s*minutes?\s*ago'
                        ]
                        
                        for pattern in date_patterns:
                            match = re.search(pattern, item_text, re.IGNORECASE)
                            if match:
                                parsed_date = self._parse_relative_date(match.group(0))
                                if parsed_date:
                                    date = parsed_date
                                    break
                        
                        # Only include videos from last 2 weeks
                        if self._is_within_two_weeks(date):
                            video_data = VideoData(url=video_url, likes=likes, date=date)
                            videos.append(video_data)
                            logger.info(f"Found TikTok video: {video_url} (likes: {likes})")
                    
                    except Exception as e:
                        logger.warning(f"Error processing TikTok video item: {e}")
                        continue
                
                # Check if we found new content
                if len(videos) == initial_video_count:
                    no_new_content_count += 1
                else:
                    no_new_content_count = 0
                
                # Scroll to load more content (infinite scroll)
                await self.page.evaluate("window.scrollBy(0, 1000)")
                await self._delay(3, 5)  # Wait for new content to load
                scroll_attempts += 1
                
                logger.info(f"TikTok scroll {scroll_attempts}/{max_scrolls}, found {len(videos)} videos")
        
        except Exception as e:
            logger.error(f"Error scraping TikTok: {e}")
        
        return videos

async def get_top_videos_async(hashtag: str) -> dict:
    """
    Async version of get_top_videos function - Currently TikTok only due to Instagram's anti-scraping protections
    """
    logger.info(f"Starting video scraping for hashtag: {hashtag}")
    
    async with VideoScraper() as scraper:
        # Instagram scraping commented out due to heavy anti-scraping protections
        instagram_videos = []
        # try:
        #     logger.info("Scraping Instagram videos...")
        #     instagram_videos = await scraper._scrape_instagram_videos(hashtag)
        #     logger.info(f"Instagram scraping completed: {len(instagram_videos)} videos found")
        # except Exception as e:
        #     logger.error(f"Instagram scraping failed: {e}")
        #     instagram_videos = []
        
        # Focus on TikTok scraping only
        tiktok_videos = []
        try:
            logger.info("Scraping TikTok videos...")
            tiktok_videos = await scraper._scrape_tiktok_videos(hashtag)
            logger.info(f"TikTok scraping completed: {len(tiktok_videos)} videos found")
        except Exception as e:
            logger.error(f"TikTok scraping failed: {e}")
            tiktok_videos = []
        
        # Sort by likes and get top 15
        instagram_videos.sort(key=lambda x: x.likes, reverse=True)
        tiktok_videos.sort(key=lambda x: x.likes, reverse=True)
        
        # Extract URLs and limit to 15
        instagram_urls = [video.url for video in instagram_videos[:15]]  # Will be empty
        tiktok_urls = [video.url for video in tiktok_videos[:15]]
        
        logger.info(f"Final results: {len(instagram_urls)} Instagram URLs, {len(tiktok_urls)} TikTok URLs")
        
        return {
            "instagram": instagram_urls,
            "tiktok": tiktok_urls
        }

def get_top_videos(hashtag: str) -> dict:
    """
    Retrieves the top 15 TikTok videos posted in the last two weeks for the given hashtag.
    
    Note: Instagram scraping is currently disabled due to heavy anti-scraping protections.
    The function still returns the expected format with an empty Instagram list.

    Args:
        hashtag (str): The hashtag name without the '#' symbol (e.g., 'dance').

    Returns:
        dict: A dictionary with keys 'instagram' and 'tiktok', where:
              - 'instagram' contains an empty list (disabled)
              - 'tiktok' contains a list of up to 15 video URLs
              If fewer than 15 videos are found, the list will contain all available videos.
              
    Note:
        - Currently focuses on TikTok only due to Instagram's robust anti-scraping measures
        - This function uses web scraping with stealth techniques to avoid detection
        - Instagram functionality can be re-enabled by uncommenting the relevant code
    """
    try:
        # Run the async function
        return asyncio.run(get_top_videos_async(hashtag))
    except Exception as e:
        logger.error(f"Error in get_top_videos: {e}")
        return {"instagram": [], "tiktok": []}

# Example usage and testing
if __name__ == "__main__":
    import argparse
    import sys
    
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description="Scrape top TikTok videos for a given hashtag (Instagram disabled due to anti-scraping protections)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python video_scraper.py dance
  python video_scraper.py music
  python video_scraper.py travel
  python video_scraper.py "funny cats"
        """
    )
    
    parser.add_argument(
        'hashtag',
        help='Hashtag to search for (without the # symbol, e.g., "dance")',
        nargs='?',  # Make it optional
        default=None
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed progress information'
    )
    
    args = parser.parse_args()
    
    # Check if hashtag was provided
    if not args.hashtag:
        print("Error: Please provide a hashtag to search for")
        print("\nUsage: python video_scraper.py <hashtag>")
        print("Example: python video_scraper.py dance")
        sys.exit(1)
    
    # Use the provided hashtag
    test_hashtag = args.hashtag
    print(f"Testing video scraper with hashtag: {test_hashtag}")
    print("Note: Instagram scraping is currently disabled due to anti-scraping protections")
    
    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    result = get_top_videos(test_hashtag)
    
    print(f"\nResults:")
    print(f"Instagram videos found: {len(result['instagram'])} (disabled)")
    print(f"TikTok videos found: {len(result['tiktok'])}")
    
    if result['instagram']:
        print(f"\nSample Instagram URLs:")
        for i, url in enumerate(result['instagram'][:3]):
            print(f"{i+1}. {url}")
        if len(result['instagram']) > 3:
            print(f"... and {len(result['instagram']) - 3} more")
    else:
        print("\nInstagram scraping is currently disabled")
    
    if result['tiktok']:
        print(f"\nSample TikTok URLs:")
        for i, url in enumerate(result['tiktok'][:3]):
            print(f"{i+1}. {url}")
        if len(result['tiktok']) > 3:
            print(f"... and {len(result['tiktok']) - 3} more")
    else:
        print("\nNo TikTok videos found") 