import os
from datetime import datetime, timedelta
from dateutil import parser
from apify_client import ApifyClient
from dotenv import load_dotenv

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
        - The service retrieves videos, which include reels, as the scraper does not distinguish between video types.
    """
    try:
        client = ApifyClient(os.getenv('APIFY_API_TOKEN'))
        run_input = {
            "hashtags": [hashtag],
            "resultsLimit": 50
        }
        actor_call = client.actor('apify/instagram-hashtag-scraper').call(run_input=run_input)
        dataset_items = client.dataset(actor_call['defaultDatasetId']).list_items().items
        
        two_weeks_ago = datetime.now() - timedelta(weeks=2)
        videos = []
        for item in dataset_items:
            if item.get('type') == 'Video':
                try:
                    timestamp = parser.parse(item['timestamp'])
                    if timestamp >= two_weeks_ago:
                        videos.append({
                            'url': item['url'],
                            'likes': item.get('likesCount', 0)
                        })
                except (KeyError, ValueError):
                    continue  # Skip invalid entries
        
        videos.sort(key=lambda x: x['likes'], reverse=True)
        top_videos = [v['url'] for v in videos[:15]]
        return top_videos
    except Exception:
        return []

if __name__ == '__main__':
    # Sample test
    hashtag = 'dance'
    videos = get_top_instagram_videos(hashtag)
    print(f'Top videos for #{hashtag}:')
    for url in videos:
        print(url) 