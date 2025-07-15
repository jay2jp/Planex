#!/usr/bin/env python3
"""
Example usage of the TikTok Video Scraper Service

This script demonstrates various ways to use the get_top_tiktok_videos function
in your applications.
"""

import os
from dotenv import load_dotenv
from tiktok_scraper import get_top_tiktok_videos

# Load environment variables from .env file
load_dotenv()


def example_basic_usage():
    """
    Basic example of getting top TikTok videos for a hashtag
    """
    print("📱 Basic Usage Example")
    print("=" * 40)
    
    hashtag = "dance"
    videos = get_top_tiktok_videos(hashtag)
    
    if videos:
        print(f"Found {len(videos)} top videos for #{hashtag}:")
        for i, url in enumerate(videos, 1):
            print(f"{i:2d}. {url}")
    else:
        print(f"No videos found for #{hashtag}")
    
    print()


def example_multiple_hashtags():
    """
    Example of processing multiple hashtags
    """
    print("🔄 Multiple Hashtags Example")
    print("=" * 40)
    
    hashtags = ["fitness", "cooking", "travel", "music"]
    results = {}
    
    for hashtag in hashtags:
        print(f"Processing #{hashtag}...")
        videos = get_top_tiktok_videos(hashtag)
        results[hashtag] = videos
        print(f"  Found {len(videos)} videos")
    
    print("\n📊 Summary:")
    for hashtag, videos in results.items():
        print(f"  #{hashtag}: {len(videos)} videos")
    
    print()


def example_with_analysis():
    """
    Example with basic analysis of results
    """
    print("📈 Analysis Example")
    print("=" * 40)
    
    hashtag = "fitness"
    videos = get_top_tiktok_videos(hashtag)
    
    if videos:
        print(f"Analysis for #{hashtag}:")
        print(f"  Total videos found: {len(videos)}")
        print(f"  Top 3 most liked videos:")
        
        for i, url in enumerate(videos[:3], 1):
            print(f"    {i}. {url}")
        
        # Simple URL analysis
        tiktok_users = []
        for url in videos:
            if "/@" in url:
                user_part = url.split("/@")[1]
                username = user_part.split("/")[0]
                tiktok_users.append(username)
        
        unique_users = len(set(tiktok_users))
        print(f"  Unique creators: {unique_users}")
        
        if unique_users > 0:
            print(f"  Average videos per creator: {len(videos) / unique_users:.1f}")
    
    print()


def example_error_handling():
    """
    Example demonstrating error handling
    """
    print("🛡️ Error Handling Example")
    print("=" * 40)
    
    # Test with various edge cases
    test_cases = [
        ("", "Empty hashtag"),
        ("nonexistenthashtag12345", "Non-existent hashtag"),
        ("a" * 100, "Very long hashtag"),
        ("test123", "Normal hashtag")
    ]
    
    for hashtag, description in test_cases:
        print(f"Testing {description}: '{hashtag}'")
        try:
            videos = get_top_tiktok_videos(hashtag)
            print(f"  Result: {len(videos)} videos found")
        except Exception as e:
            print(f"  Error: {e}")
        print()


def main():
    """
    Main function to run all examples
    """
    print("🚀 TikTok Video Scraper - Example Usage")
    print("=" * 50)
    
    # Check if API token is set
    if not os.environ.get('APIFY_API_TOKEN'):
        print("❌ APIFY_API_TOKEN environment variable is not set!")
        print("Please set your Apify API token before running examples:")
        print("export APIFY_API_TOKEN='your_token_here'")
        return
    
    print("✅ API token is configured\n")
    
    # Run examples
    example_basic_usage()
    example_multiple_hashtags()
    example_with_analysis()
    example_error_handling()
    
    print("🎉 All examples completed!")


if __name__ == "__main__":
    main() 