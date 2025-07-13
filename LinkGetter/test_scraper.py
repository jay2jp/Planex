#!/usr/bin/env python3
"""
Test script for the video scraping service.
Tests the service with multiple hashtags and displays results.
"""

import time
import sys
from video_scraper import get_top_videos

def test_hashtag(hashtag: str) -> bool:
    """Test scraping for a specific hashtag"""
    print(f"\n{'='*60}")
    print(f"Testing hashtag: #{hashtag}")
    print(f"{'='*60}")
    
    try:
        start_time = time.time()
        result = get_top_videos(hashtag)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        instagram_count = len(result['instagram'])
        tiktok_count = len(result['tiktok'])
        
        print(f"\nResults for #{hashtag}:")
        print(f"  Execution time: {execution_time:.2f} seconds")
        print(f"  Instagram videos found: {instagram_count}")
        print(f"  TikTok videos found: {tiktok_count}")
        
        # Display sample URLs
        if instagram_count > 0:
            print(f"\nSample Instagram URLs:")
            for i, url in enumerate(result['instagram'][:3]):
                print(f"  {i+1}. {url}")
            if instagram_count > 3:
                print(f"  ... and {instagram_count - 3} more")
        
        if tiktok_count > 0:
            print(f"\nSample TikTok URLs:")
            for i, url in enumerate(result['tiktok'][:3]):
                print(f"  {i+1}. {url}")
            if tiktok_count > 3:
                print(f"  ... and {tiktok_count - 3} more")
        
        # Check if results are reasonable
        if instagram_count == 0 and tiktok_count == 0:
            print("  ⚠️  No videos found for this hashtag")
            return False
        
        print(f"  ✓ Test passed")
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Video Scraper Test Suite")
    print("=" * 60)
    
    # Test hashtags
    test_hashtags = [
        'dance',
        'music',
        'funny',
        'art',
        'food'
    ]
    
    results = []
    
    for hashtag in test_hashtags:
        success = test_hashtag(hashtag)
        results.append((hashtag, success))
        
        # Add delay between tests to be respectful
        if hashtag != test_hashtags[-1]:
            print(f"\nWaiting 30 seconds before next test...")
            time.sleep(30)
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    print(f"\nDetailed results:")
    for hashtag, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  #{hashtag}: {status}")
    
    if passed == total:
        print(f"\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  Some tests failed. This might be due to:")
        print(f"  - Rate limiting")
        print(f"  - Platform changes")
        print(f"  - Network issues")
        print(f"  - Hashtag with no recent videos")
        sys.exit(1)

if __name__ == "__main__":
    main() 