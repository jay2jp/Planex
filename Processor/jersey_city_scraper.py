#!/usr/bin/env python3
"""
Jersey City TikTok Scraper and Analyzer

This script scrapes TikTok for videos related to Jersey City, NJ,
analyzes them using Gemini, and saves the results to a JSONL file.
"""

import os
import json
import sys
import requests
from dotenv import load_dotenv

# Add the path to the ApifyLinkGetter module to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'ApifyLinkGetter')))

from tiktok_scraper import get_top_tiktok_videos


def analyze_video_via_api(url, prompt):
    """
    Calls the local Flask app's /analyze endpoint to process a video.
    """
    api_url = "http://localhost:8000/analyze"
    payload = {"url": url, "prompt": prompt}
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed for {url}: {e}")
        return None


def main():
    """
    Main function to run the scraper and analyzer.
    """
    load_dotenv()

    # Hashtags to scrape
    hashtags = ["jerseycity", "jc", "downtownjc", "jerseycitynj"]

    # Output file
    output_filename = "jersey_city_recommendations.jsonl"

    print("Starting Jersey City TikTok scraper...")

    with open(output_filename, 'w') as outfile:
        for hashtag in hashtags:
            print(f"Scraping for hashtag: #{hashtag}")
            video_urls = get_top_tiktok_videos(hashtag, days_back=90)

            for url in video_urls:
                print(f"Processing video: {url}")

                # Create a prompt for Gemini
                prompt = """\
                Analyze the following video and its metadata to extract information about a recommendation in Jersey City.
                Please provide the following details in a JSON format:
                - "name": The name of the recommended place or activity.
                - "location": The specific address or cross-streets.
                - "neighborhood": The neighborhood in Jersey City (e.g., Downtown, The Heights, Journal Square).
                - "summary": A brief summary of what the video recommends.
                - "tags": A list of relevant tags (e.g., "food", "park", "nightlife").
                - "quote": A direct quote from the video that best describes the recommendation.

                If any information is not available, please use "N/A".
                """

                # Analyze the video via the API
                analysis_result = analyze_video_via_api(url, prompt)

                if analysis_result and 'result' in analysis_result:
                    # The result from Gemini might be in a markdown code block
                    cleaned_result = analysis_result['result'].strip().replace('```json', '').replace('```', '').strip()

                    # Parse the JSON and add the URL to it
                    try:
                        data = json.loads(cleaned_result)
                        data['source_url'] = url
                        json.dump(data, outfile)
                        outfile.write('\\n')
                    except json.JSONDecodeError:
                        print(f"Could not parse JSON from Gemini for video {url}")
                else:
                    print(f"Analysis failed for video {url}")

    print(f"Scraping complete. Results saved to {output_filename}")


if __name__ == "__main__":
    main()
