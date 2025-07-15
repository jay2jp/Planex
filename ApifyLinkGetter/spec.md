Specification for Python Service to Scrape TikTok Videos Using Apify TikTok Scraper
Overview
This document specifies a Python service that retrieves the top 15 TikTok videos posted within the last two weeks for a given hashtag, using the Apify TikTok Scraper (https://apify.com/clockworks/tiktok-scraper). The "top" videos are determined by the number of likes (referred to as hearts in the TikTok data). The service is designed for an MVP to simplify implementation and bypass TikTok’s anti-scraping measures by leveraging Apify’s infrastructure.
Requirements

Language: The service must be implemented in Python 3.x.
Dependencies:
apify-client for interacting with the Apify TikTok Scraper.
python-dateutil for date handling.


Configuration:
An Apify account with an API token stored in the environment variable APIFY_API_TOKEN.
The Apify TikTok Scraper actor (clockworks/tiktok-scraper) must be accessible via the Apify platform.
The service assumes the free plan or a paid plan with sufficient usage credits (e.g., the free plan provides $5 monthly credits, enough for ~1,000 results at $0.005 per item).



Function Signature
def get_top_tiktok_videos(hashtag: str) -> list:
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

Implementation Details
Apify TikTok Scraper Integration

Initialize Apify Client:

Use the apify-client library to authenticate with the Apify platform using the APIFY_API_TOKEN environment variable.
Configure the client to interact with the clockworks/tiktok-scraper actor.


Set Up Input Parameters:

Configure the scraper input to fetch videos for the specified hashtag:{
    "hashtags": ["{hashtag}"],
    "resultsLimit": 50
}


Set resultsLimit to 50 to ensure enough videos are retrieved to filter for the top 15 within the two-week period. Adjust as needed based on hashtag popularity.


Run the Scraper:

Use the Apify client to call the clockworks/tiktok-scraper actor with the input parameters.
Wait for the actor to complete and retrieve the dataset from the run.


Process the Dataset:

The scraper returns a dataset with video details, including:
url: The video URL (e.g., https://www.tiktok.com/@username/video/{video_id}).
stats.hearts: The number of likes.
createTime: The Unix timestamp of when the video was posted.


Parse the createTime using python-dateutil to check if the video was posted within the last two weeks (from the current date).
Filter videos to include only those posted within the last two weeks.
Sort the filtered videos by stats.hearts in descending order.
Select the top 15 videos (or fewer if not enough) and extract their url fields.



Output Format

The function returns a list of up to 15 TikTok video URLs:["url1", "url2", ..., "urlN"]


If no videos are found for the hashtag or none meet the date criteria, return an empty list.

Error Handling

Invalid Hashtag: If the hashtag does not exist or returns no results, return an empty list.
API Errors: Handle Apify API errors (e.g., invalid token, rate limits) by logging the error (optional) and returning an empty list.
Rate Limits: The Apify platform manages rate limits internally. If the usage credits are exceeded, log a message suggesting the user check their Apify plan.
Date Parsing Errors: Skip videos with invalid createTime values.

Notes

Hashtag Input: The hashtag should be provided without the '#' symbol. The Apify scraper handles case-insensitivity.
Performance: The Apify scraper handles TikTok’s anti-scraping measures (e.g., CAPTCHAs, IP bans) internally, making it suitable for an MVP.
Limitations: The scraper retrieves publicly available data only, as per Apify’s ethical scraping policy. It cannot access private user data.
Cost: The Apify TikTok Scraper uses a pay-per-result pricing model ($0.005 per item). The free plan’s $5 monthly credit allows ~1,000 results, sufficient for this MVP.
Maintenance: The Apify scraper is actively maintained, but check the Apify documentation for updates to the clockworks/tiktok-scraper actor.

References

Apify TikTok Scraper: https://apify.com/clockworks/tiktok-scraper
Apify Python Client: https://docs.apify.com/sdk/python/
Apify Pricing: https://apify.com/pricing
