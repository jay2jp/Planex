Specification for Python Service to Scrape Instagram Videos Using Apify Instagram Hashtag Scraper
Overview
This document specifies a Python service that retrieves the top 15 Instagram videos (including reels) posted within the last two weeks for a given hashtag, using the Apify Instagram Hashtag Scraper (https://apify.com/apify/instagram-hashtag-scraper). The "top" videos are determined by the number of likes. The service is designed for an MVP to bypass Instagram’s anti-scraping measures by leveraging Apify’s infrastructure.
Requirements

Language: The service must be implemented in Python 3.x.
Dependencies:
apify-client for interacting with the Apify Instagram Hashtag Scraper.
python-dateutil for date handling.


Configuration:
An Apify account with an API token stored in the environment variable APIFY_API_TOKEN.
The Apify Instagram Hashtag Scraper actor (apify/instagram-hashtag-scraper) must be accessible via the Apify platform.
The service assumes the free plan or a paid plan with sufficient usage credits (e.g., the free plan provides $5 monthly credits, sufficient for ~1,000 results at approximately $0.005 per item).



Function Signature
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

Implementation Details
Apify Instagram Hashtag Scraper Integration

Initialize Apify Client:

Use the apify-client library to authenticate with the Apify platform using the APIFY_API_TOKEN environment variable.
Configure the client to interact with the apify/instagram-hashtag-scraper actor.


Set Up Input Parameters:

Configure the scraper input to fetch posts for the specified hashtag:{
    "hashtags": ["{hashtag}"],
    "resultsLimit": 50
}


Set resultsLimit to 50 to ensure enough posts are retrieved to filter for the top 15 videos. Adjust as needed based on hashtag popularity.


Run the Scraper:

Use the Apify client to call the apify/instagram-hashtag-scraper actor with the input parameters.
Wait for the actor to complete and retrieve the dataset from the run.


Process the Dataset:

The scraper returns a dataset with post details, including:
type: The post type (e.g., "Video" for videos, including reels).
url: The post URL (e.g., https://www.instagram.com/p/{shortcode}/).
likesCount: The number of likes.
timestamp: The post timestamp in ISO 8601 format (e.g., 2023-10-01T12:00:00.000Z).


Filter posts to include only those where type is "Video".
Parse the timestamp using python-dateutil to check if the video was posted within the last two weeks (from the current date).
Sort the filtered videos by likesCount in descending order.
Select the top 15 videos (or fewer if not enough) and extract their url fields.



Output Format

The function returns a list of up to 15 Instagram video URLs:["url1", "url2", ..., "urlN"]


If no videos are found for the hashtag or none meet the date criteria, return an empty list.

Error Handling

Invalid Hashtag: If the hashtag does not exist or returns no results, return an empty list.
API Errors: Handle Apify API errors (e.g., invalid token, rate limits) by logging the error (optional) and returning an empty list.
Rate Limits: The Apify platform manages rate limits internally. If usage credits are exceeded, log a message suggesting the user check their Apify plan.
Date Parsing Errors: Skip videos with invalid timestamp values.

Notes

Instagram Limitations: The Apify scraper retrieves all video posts under type="Video", which includes reels. It cannot distinguish between reels and regular videos.
Hashtag Input: The hashtag should be provided without the '#' symbol. The Apify scraper handles case-insensitivity.
Performance: The Apify scraper handles Instagram’s anti-scraping measures (e.g., CAPTCHAs, IP bans) internally, making it suitable for an MVP.
Cost: The Apify Instagram Hashtag Scraper uses a pay-per-result pricing model (approximately $0.005 per item). The free plan’s $5 monthly credit allows ~1,000 results, sufficient for this MVP.
Maintenance: The Apify scraper is actively maintained, but check the Apify documentation for updates to the apify/instagram-hashtag-scraper actor.

References

Apify Instagram Hashtag Scraper: https://apify.com/apify/instagram-hashtag-scraper
Apify Python Client: https://docs.apify.com/sdk/python/
Apify Pricing: https://apify.com/pricing
