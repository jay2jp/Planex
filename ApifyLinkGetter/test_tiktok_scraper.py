#!/usr/bin/env python3
"""
Test script for TikTok Video Scraper Service

This script demonstrates how to use the get_top_tiktok_videos function
with various hashtags and scenarios.
"""

import os
import logging
from dotenv import load_dotenv
from tiktok_scraper import get_top_tiktok_videos

# Load environment variables from .env file
load_dotenv()


def test_scraper():
    """
    Test the TikTok scraper with different hashtags and scenarios.
    """
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Check if API token is set
    if not os.environ.get('APIFY_API_TOKEN'):
        print("❌ APIFY_API_TOKEN environment variable is not set!")
        print("Please set your Apify API token:")
        print("export APIFY_API_TOKEN='your_token_here'")
        return
    
    print("🚀 Testing TikTok Video Scraper\n")
    
    # Test hashtags
    test_hashtags = [
        "dance",
        "cooking",
        "fitness",
        "travel",
        "music"
    ]
    
    for hashtag in test_hashtags:
        print(f"📱 Testing hashtag: #{hashtag}")
        print("-" * 50)
        
        try:
            results = get_top_tiktok_videos(hashtag)
            
            if results:
                print(f"✅ Found {len(results)} videos for #{hashtag}")
                
                # Display first 3 URLs as examples
                for i, url in enumerate(results[:3], 1):
                    print(f"  {i}. {url}")
                
                if len(results) > 3:
                    print(f"  ... and {len(results) - 3} more videos")
                    
            else:
                print(f"❌ No videos found for #{hashtag}")
                
        except Exception as e:
            print(f"❌ Error testing #{hashtag}: {e}")
        
        print()  # Empty line for readability
    
    # Test edge cases
    print("🧪 Testing edge cases")
    print("-" * 50)
    
    # Test with empty hashtag
    print("Testing empty hashtag...")
    results = get_top_tiktok_videos("")
    print(f"Empty hashtag result: {len(results)} videos\n")
    
    # Test with non-existent hashtag
    print("Testing non-existent hashtag...")
    results = get_top_tiktok_videos("thishshtagdoesnotexist12345")
    print(f"Non-existent hashtag result: {len(results)} videos\n")


if __name__ == "__main__":
    test_scraper() 