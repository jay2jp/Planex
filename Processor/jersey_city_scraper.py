#!/usr/bin/env python3
"""
Jersey City TikTok Scraper and Analyzer

This script scrapes TikTok for videos related to Jersey City, NJ,
analyzes them using Gemini, and saves the results to a PostgreSQL database.
"""

import os
import json
import sys
import requests
import psycopg2
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import types

# Add the root directory to the Python path to access ApifyLinkGetter
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_dir)

from ApifyLinkGetter import get_top_tiktok_videos


def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    pooler_url = os.getenv("DATABASE_POOLER_URL")
    if pooler_url:
        try:
            conn = psycopg2.connect(pooler_url)
            print("Successfully connected to the database via pooler URL.")
            return conn
        except psycopg2.ProgrammingError as e:
            print(f"Could not connect to database via pooler URL: {e}")
            print("Please ensure your DATABASE_POOLER_URL in the .env file is a valid PostgreSQL connection string.")
            print("It should look like: postgresql://[user]:[password]@[host]:[port]/[dbname]")
            return None
        except psycopg2.OperationalError as e:
            print(f"Could not connect to database via pooler URL: {e}")
            return None

    # Fallback to original direct connection method
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        print("Successfully connected to the database directly.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"Could not connect to database directly: {e}")
        return None


def get_embedding(text):
    """Generates an embedding for the given text using the Gemini API."""
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    try:
        result = genai.embed_content(
            model="gemini-embedding-001",
            content=text,
            task_type="retrieval_document", #3072
            output_dimensionality=1536
        )
        return result['embedding']
    except Exception as e:
        print(f"Failed to generate embedding: {e}")
        return None


def analyze_video_via_api(url, prompt):
    """
    Calls the local Flask app's /analyze endpoint to process a video.
    """
    api_url = "http://localhost:5000/analyze"
    payload = {"url": url, "prompt": prompt}
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed for {url}: {e}")
        return None


def insert_recommendation(conn, data, scraped_hashtag, embedding):
    """
    Inserts a recommendation and its related data into the database.
    """
    with conn.cursor() as cur:
        try:
            # Step 1: Insert recommendation and get its ID
            cur.execute(
                """
                INSERT INTO recommendations (name, location, neighborhood, summary, quote, source_url, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (source_url) DO NOTHING
                RETURNING id;
                """,
                (data.get('name', 'N/A'), data.get('location', 'N/A'), data.get('neighborhood', 'N/A'),
                 data.get('summary', 'N/A'), data.get('quote', 'N/A'), data['source_url'], embedding)
            )
            rec_id_tuple = cur.fetchone()

            if rec_id_tuple is None:
                cur.execute("SELECT id FROM recommendations WHERE source_url = %s;", (data['source_url'],))
                rec_id_tuple = cur.fetchone()

            if rec_id_tuple is None:
                print(f"Could not insert or find recommendation for {data['source_url']}")
                conn.rollback()
                return

            recommendation_id = rec_id_tuple[0]

            # Step 2: Insert the scraped hashtag and get its ID
            cur.execute(
                "INSERT INTO hashtags (tag) VALUES (%s) ON CONFLICT (tag) DO UPDATE SET tag=EXCLUDED.tag RETURNING id;",
                (scraped_hashtag,)
            )
            hashtag_id = cur.fetchone()[0]

            # Step 3: Link recommendation and scraped hashtag
            cur.execute(
                """
                INSERT INTO recommendation_hashtags (recommendation_id, hashtag_id)
                VALUES (%s, %s) ON CONFLICT DO NOTHING;
                """,
                (recommendation_id, hashtag_id)
            )

            # Step 4: Insert Gemini-provided tags and link them
            if 'tags' in data and isinstance(data['tags'], list):
                for tag in data['tags']:
                    cur.execute(
                        "INSERT INTO tags (tag) VALUES (%s) ON CONFLICT (tag) DO UPDATE SET tag=EXCLUDED.tag RETURNING id;",
                        (tag,)
                    )
                    tag_id = cur.fetchone()[0]
                    cur.execute(
                        """
                        INSERT INTO recommendation_tags (recommendation_id, tag_id)
                        VALUES (%s, %s) ON CONFLICT DO NOTHING;
                        """,
                        (recommendation_id, tag_id)
                    )

            # Step 5: Insert neighborhood if it exists
            neighborhood = data.get('neighborhood')
            if neighborhood and neighborhood != 'N/A':
                cur.execute(
                    "INSERT INTO neighborhoods (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;",
                    (neighborhood,)
                )

            conn.commit()
            print(f"Successfully processed and saved recommendation from {data['source_url']}")

        except psycopg2.Error as e:
            print(f"Database error: {e}")
            conn.rollback()


def main():
    """
    Main function to run the scraper and analyzer.
    """
    load_dotenv()

    conn = get_db_connection()
    if not conn:
        sys.exit("Could not connect to the database. Exiting.")

    # Hashtags to scrape
    hashtags = ["jerseycity"]

    print("Starting Jersey City TikTok scraper...")

    for hashtag in hashtags:
        print(f"Scraping for hashtag: #{hashtag}")
        video_urls = get_top_tiktok_videos(hashtag, days_back=90)

        for url in video_urls:
            print(f"Processing video: {url}")

            prompt = '''\
 Analyze this video and its metadata to systematically extract structured recommendation information, comprising the following core components:
 1. **Name**: Capture the primary recommendation entity (e.g., restaurant, park, museum)\
- Include establishment name
- For generic recommendations (e.g., 'best sunset spots'), describe the entity clearly
- Trim branding/slogans unless essential to identification
2. **Location**: Precisely identify physical location
- Use full address when available
- Alternate: Landmark-based description + nearest cross streets
- Include GPS coordinates if present in metadata
- Note: Avoid vague descriptors (e.g., replace 'downtown' with actual address or specific quadrant)
- this cannot be null so if its not in the video , use new york new york
3. **Neighborhood**: Geographic/communal context (if applicable)
- E.g., 'Fort Greene', 'East Village', 'Fishtown'
- Optional: Only include if explicitly mentioned in video or metadata
4. **Summary**: Semantically rich description optimized for retrieval
- Highlight core qualities: Cuisine type, architectural style, unique features
- Include temporal considerations: Best time to visit, seasonal offerings
- Note visitor context: Ideal audience (families, solo travelers, etc.)
- Use active verbs for key actions/results
- Maintain 2-3 sentence maximum, packed with retrievable keywords
5. **Tags**: Contextual categorization
- 3-5 standardized tags
- Prioritize: Cuisine (sushi, BBQ), Activity (hiking, nightlife), Venue Type (museum, bookstore)
- Avoid broad terms: Use 'Asian-fusion' instead of 'food'
6. **Quote**: Verbatim endorsement
- Select the most compelling description from speaker
- Prioritize superlatives, emotional language, or specific calls-to-action
- Shorten to essential statement (e.g., 'You MUST come here for the views!' → 'You MUST come here for the views')
Processing Guidance:
- Cross-check video timestamps for conflicting information
- Prefer textual metadata over visual analysis
- Normalize ampersands (& → 'and'), remove extra punctuation
- Handle missing data consistently: ['', null, 'N/A']
- Return a JSON object with the following keys: name, location, neighborhood, summary, tags, quote
- The JSON object should be in the following format:
{
    "name": "string",
    "location": "string",
    "neighborhood": "string",
    "summary": "string",
    "tags": ["string"],
    "quote": "string"
}
return the JSON object only, no other text or comments and do not use the ```json and ``` tags at the beginning or end of the JSON object
            '''

            analysis_result = analyze_video_via_api(url, prompt)

            if analysis_result and 'result' in analysis_result:
                cleaned_result = analysis_result['result'].strip().replace('```json', '').replace('```', '').strip()
                try:
                    print(cleaned_result)
                    data = json.loads(cleaned_result)
                    data['source_url'] = url

                    # Generate embedding
                    text_to_embed = f"{data.get('summary', '')} {data.get('neighborhood', '')} {data.get('quote', '')}"
                    embedding = get_embedding(text_to_embed)

                    insert_recommendation(conn, data, hashtag, embedding)
                except json.JSONDecodeError:
                    print(f"Could not parse JSON from Gemini for video {url}")
            else:
                print(f"Analysis failed for video {url}")

    conn.close()
    print("Scraping complete. Data saved to the database.")


if __name__ == "__main__":
    main()