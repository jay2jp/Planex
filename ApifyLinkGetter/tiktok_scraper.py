#!/usr/bin/env python3
"""
TikTok Video Scraper Service

This module provides a service to retrieve the top 15 TikTok videos posted within 
the last two weeks for a given hashtag, using the Apify TikTok Scraper.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List
from dateutil.parser import parse
from apify_client import ApifyClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_top_tiktok_videos(hashtag: str) -> List[str]:
    """
    Retrieves the top 15 TikTok videos posted in the last two weeks for the given hashtag
    using the Apify TikTok Scraper.

    Args:
        hashtag (str): The hashtag name without the '#' symbol (e.g., 'dance').

    Returns:
        list: A list of up to 15 TikTok video URLs, sorted by the number of likes (hearts)
              in descending order. If fewer than 15 videos are found, the list will contain
              all available videos.
    """
    
    try:
        # Initialize Apify client
        api_token = os.environ.get('APIFY_API_TOKEN')
        if not api_token:
            logging.error("APIFY_API_TOKEN environment variable is not set")
            return []
        
        client = ApifyClient(api_token)
        
        # Configure scraper input
        scraper_input = {
            "hashtags": [hashtag],
            "resultsLimit": 50
        }
        
        # Run the clockworks/tiktok-scraper actor
        print(f"Running TikTok scraper for hashtag: {hashtag}")
        run = client.actor("clockworks/tiktok-scraper").call(run_input=scraper_input)
        
        # Get the dataset from the run
        dataset = client.dataset(run["defaultDatasetId"])
        dataset_items = list(dataset.iterate_items())
        
        if not dataset_items:
            print(f"No videos found for hashtag: {hashtag}")
            return []
        
        # Calculate the date two weeks ago
        two_weeks_ago = datetime.now() - timedelta(weeks=2)
        
        # Filter videos from the last two weeks
        recent_videos = []
        for item in dataset_items:
            try:
                # Parse the createTime
                create_time = item.get('createTime')
                if create_time:
                    # Handle both Unix timestamp and ISO format
                    if isinstance(create_time, (int, float)):
                        video_date = datetime.fromtimestamp(create_time)
                    else:
                        video_date = parse(str(create_time))
                    
                    # Check if the video was posted within the last two weeks
                    if video_date >= two_weeks_ago:
                        recent_videos.append(item)
                        
            except (ValueError, TypeError) as e:
                logging.warning(f"Error parsing createTime for video: {e}")
                continue
        
        if not recent_videos:
            print(f"No videos found within the last two weeks for hashtag: {hashtag}")
            return []
        
        # Sort by stats.hearts (likes) in descending order
        def get_hearts(video):
            stats = video.get('stats', {})
            return stats.get('hearts', 0) if stats else 0
        
        sorted_videos = sorted(recent_videos, key=get_hearts, reverse=True)
        
        # Select the top 15 videos and extract their URLs
        top_videos = sorted_videos[:15]
        video_urls = []
        
        for video in top_videos:
            url = video.get('url')
            if url:
                video_urls.append(url)
        
        print(f"Found {len(video_urls)} videos for hashtag: {hashtag}")
        return video_urls
        
    except Exception as e:
        logging.error(f"Error in get_top_tiktok_videos: {e}")
        return []


if __name__ == "__main__":
    # Test the function with a sample hashtag
    test_hashtag = "dance"
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    print(f"Testing TikTok scraper with hashtag: {test_hashtag}")
    results = get_top_tiktok_videos(test_hashtag)
    
    if results:
        print(f"\nFound {len(results)} videos:")
        for i, url in enumerate(results, 1):
            print(f"{i}. {url}")
    else:
        print("No videos found or an error occurred.") 