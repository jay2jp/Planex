import os
from datetime import datetime, timedelta
from dateutil import parser
from apify_client import ApifyClient
from dotenv import load_dotenv
import json

load_dotenv()

def get_top_instagram_videos(hashtag: str) -> list:
    """
    Retrieves the top 15 Instagram videos posted in the last two weeks for the given hashtag
    using the Apify Instagram Hashtag Scraper.

    Args:
        hashtag (str): The hashtag name without the '#' symbol (e.g., 'dance').

    Returns:
        list: A list of up to 15 Instagram video URLs, sorted by the number of likes
              in descending order. If fewer than 15 videos are found, the list will
              contain all available videos.
              
    Note:
        - The service retrieves videos/reels using the 'stories' resultsType parameter.
    """
    try:
        client = ApifyClient(os.getenv('APIFY_API_TOKEN'))
        run_input = {
            "hashtags": [hashtag],
            "resultsLimit": 50,
            "resultsPerPage": 50,
            "resultsType": "stories"
        }
        
        print(f"Starting scrape for hashtag: {hashtag} with resultsType: stories")
        actor_call = client.actor('apify/instagram-hashtag-scraper').call(run_input=run_input)
        
        if not actor_call or 'defaultDatasetId' not in actor_call:
            print("Error: Failed to get valid response from Apify actor")
            return []
            
        dataset_items = client.dataset(actor_call['defaultDatasetId']).list_items().items

        # Save dataset for debugging
        output_filename = f"instagram_{hashtag}_dataset.json"
        try:
            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump(dataset_items, f, ensure_ascii=False, indent=2)
            print(f"Dataset written to {output_filename}")
        except Exception as e:
            print(f"Failed to write dataset to file: {e}")

        print(f"Found {len(dataset_items)} total items")
        
        # Filter for recent videos (last 2 weeks)
        from datetime import timezone
        two_weeks_ago = datetime.now(timezone.utc) - timedelta(weeks=2)
        videos = []
        
        for item in dataset_items:
            # Check if item is a video type - look for both Video type and productType clips
            is_video = (
                item.get('type') == 'Video' or 
                item.get('productType') == 'clips' or
                'videoUrl' in item
            )
            
            if is_video:
                try:
                    # Parse timestamp 
                    timestamp_str = item.get('timestamp')
                    if not timestamp_str:
                        print(f"Skipping item with no timestamp: {item.get('id', 'unknown')}")
                        continue
                        
                    timestamp = parser.parse(timestamp_str)
                    if timestamp >= two_weeks_ago:
                        # Get likes count - try multiple possible fields
                        likes = (
                            item.get('likesCount') or 
                            item.get('likeCount') or 
                            item.get('likes') or 
                            0
                        )
                        
                        video_info = {
                            'url': item.get('url'),
                            'videoUrl': item.get('videoUrl'),  # Direct video URL
                            'likes': likes,
                            'timestamp': timestamp,
                            'type': item.get('type'),
                            'productType': item.get('productType'),
                            'owner': item.get('ownerUsername', 'unknown')
                        }
                        
                        # Only add if we have a URL
                        if video_info['url']:
                            videos.append(video_info)
                        else:
                            print(f"Skipping item with no URL: {item.get('id', 'unknown')}")
                            
                except (KeyError, ValueError, TypeError) as e:
                    print(f"Skipping invalid video entry: {e} - Item: {item.get('id', 'unknown')}")
                    continue
        
        print(f"Found {len(videos)} videos from the last 2 weeks")
        
        # Sort by likes (descending) and take top 15
        videos.sort(key=lambda x: x['likes'], reverse=True)
        top_videos = [v['url'] for v in videos[:15]]
        
        print(f"Returning {len(top_videos)} top videos")
        
        # Print some debug info about the top videos
        for i, video in enumerate(videos[:5], 1):
            print(f"Top {i}: {video['likes']} likes - {video['owner']} - {video['type']}/{video['productType']}")
        
        return top_videos
        
    except Exception as e:
        print(f"Error in get_top_instagram_videos: {e}")
        return []

if __name__ == '__main__':
    # Sample test
    hashtag = 'dance'
    videos = get_top_instagram_videos(hashtag)
    print(f'\nTop videos for #{hashtag}:')
    for i, url in enumerate(videos, 1):
        print(f"{i}. {url}") 