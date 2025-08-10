#!/usr/bin/env python3
"""
TikTok Video Scraper Service

This module provides a service to retrieve the top 15 TikTok videos posted within 
the last two weeks for a given search query, using the Apify TikTok Scraper.
"""

import os
import logging
import time
from datetime import datetime, timedelta
from typing import List, Union
from apify_client import ApifyClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_top_tiktok_videos(search_queries: Union[str, List[str]], days_back: int = 14) -> List[str]:
    """
    Retrieves the top 15 TikTok videos posted in the last specified days for the given search query or queries
    using the Apify TikTok Scraper.

    Args:
        search_queries (Union[str, List[str]]): The search query or a list of search queries.
        days_back (int): Number of days to look back (default: 14 for two weeks).

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

        if isinstance(search_queries, str):
            search_queries = [search_queries]
        
        # Configure scraper input
        scraper_input = {
            "searchQueries": search_queries,
            "resultsLimit": 20,
             "resultsPerPage": 20
        }
        
        # Run the clockworks/tiktok-scraper actor
        print(f"Running TikTok scraper for search queries: {search_queries}")
        run = client.actor("clockworks/tiktok-scraper").call(run_input=scraper_input)
        
        # Debug: Print run information
        print(f"Run completed with status: {run.get('status')}")
        print(f"Dataset ID: {run.get('defaultDatasetId')}")
        
        # Wait a moment for the dataset to be fully populated
        print("Waiting for dataset to be ready...")
        time.sleep(5)  # Increased wait time
        
        # Get the dataset from the run
        dataset = client.dataset(run["defaultDatasetId"])

        dataset_dict = dataset.list_items()
        dataset_dict = dataset_dict.items
        # Try multiple methods to get dataset items with retry logic
        dataset_items = []
        max_retries = 3
        # INSERT_YOUR_CODE
        # Write dataset items to a .json file for debugging/inspection
        import json
        #output_filename = f"tiktok_{search_queries[0]}_dataset.json"
        #try:
        #    with open(output_filename, "w", encoding="utf-8") as f:
        #        json.dump(dataset_dict, f, ensure_ascii=False, indent=2)
        #    print(f"Dataset written to {output_filename}")
        #except Exception as e:
        #    print(f"Failed to write dataset to file: {e}")
        
        for attempt in range(max_retries):
            try:
                # Method 1: iterate_items() converted to list
                dataset_items = list(dataset.iterate_items())
                print(f"Attempt {attempt + 1} - iterate_items(): Fetched {len(dataset_items)} items from dataset")
                
                # If we got a reasonable number of items, break
                if len(dataset_items) > 5:  # Expect more than just a few items
                    break
                    
                # If we got some items but not many, wait and try again
                if len(dataset_items) > 0:
                    print(f"Got {len(dataset_items)} items, but expected more. Waiting and retrying...")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    
        # If still no items, try alternative methods
        if len(dataset_items) == 0:
            try:
                # Try direct API call with pagination
                print("Trying direct API call...")
                all_items = []
                offset = 0
                limit = 100
                
                while True:
                    response = dataset.get_items(offset=offset, limit=limit)
                    if not response:
                        break
                    all_items.extend(response)
                    if len(response) < limit:
                        break
                    offset += limit
                    
                dataset_items = all_items
                print(f"Direct API call: Fetched {len(dataset_items)} items")
                
            except Exception as e:
                print(f"Direct API call failed: {e}")
                dataset_items = []
        
        # If we got items, check their structure
        if dataset_items:
            print(f"Total items retrieved: {len(dataset_items)}")
            print("Sample item structure:", type(dataset_items[0]), list(dataset_items[0].keys()) if dataset_items[0] else "No keys")
            print("FIRST FEW DATASET ITEMS: ", dataset_items[:1])
        else:
            print("No items retrieved from any method")


        if not dataset_items:
            print(f"No videos found for search queries: {search_queries}")
            return []
        
        # Calculate the cutoff date
        cutoff_date = datetime.now() - timedelta(days=days_back)
        print(f"Filtering for videos newer than: {cutoff_date} ({days_back} days back)")
        
        # Filter videos from the specified time period
        recent_videos = []
        for item in dataset_items:
            try:
                # Parse the createTimeISO (e.g., '2025-07-13T00:41:15.000Z')
                create_time_iso = item.get('createTimeISO')
                if create_time_iso:
                    # Remove 'Z' and parse as UTC time
                    if create_time_iso.endswith('Z'):
                        create_time_iso = create_time_iso[:-1]
                    
                    # Parse the ISO format datetime
                    video_date = datetime.fromisoformat(create_time_iso)
                    
                    print(f"Video date: {video_date}, Cutoff: {cutoff_date}, Within range: {video_date >= cutoff_date}")
                    
                    # Check if the video was posted within the specified time period
                    if video_date >= cutoff_date:
                        recent_videos.append(item)
                        print(f"Added video with {item.get('diggCount', 0)} likes from {video_date}")
                        
            except (ValueError, TypeError) as e:
                logging.warning(f"Error parsing createTimeISO for video: {e}")
                continue
        
        if not recent_videos:
            print(f"No videos found within the last {days_back} days for search queries: {search_queries}")
            return []
        
        # Sort by stats.hearts (likes) in descending order
        def get_hearts(video):
            # TikTok API returns likes as 'diggCount', not 'stats.hearts'
            return video.get('diggCount', 0)
        
        sorted_videos = sorted(recent_videos, key=get_hearts, reverse=True)
        
        # Select the top 15 videos and extract their URLs
        top_videos = sorted_videos[:15]
        video_urls = []
        
        for video in top_videos:
            # TikTok API returns URL as 'webVideoUrl', not 'url'
            url = video.get('webVideoUrl')
            if url:
                video_urls.append(url)
        
        print(f"Found {len(video_urls)} videos for search queries: {search_queries}")
        return video_urls
        
    except Exception as e:
        logging.error(f"Error in get_top_tiktok_videos: {e}")
        return []

"""
if __name__ == "__main__":
    # Test the function with a sample search query
    test_query = "dance"
    test_days = 7  # Change this to 7 for last week, 14 for last two weeks
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    print(f"Testing TikTok scraper with search query: {test_query}")
    print(f"Looking for videos from the last {test_days} days")
    results = get_top_tiktok_videos(test_query, days_back=test_days)
    
    if results:
        print(f"Found {len(results)} videos:")
        for i, url in enumerate(results, 1):
            print(f"{i}. {url}")
    else:
        print("No videos found or an error occurred.") 

    print("RESULT: ", results)

"""
