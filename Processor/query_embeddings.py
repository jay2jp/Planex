#!/usr/bin/env python3
"""
Query Embeddings CLI

This script provides a command-line interface to query the recommendation embeddings
in the PostgreSQL database.
"""

import os
import sys
import argparse
import psycopg2
from dotenv import load_dotenv
import google.generativeai as genai
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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
    try:
        result = genai.embed_content(
            model="gemini-embedding-001",
            content=text,
            task_type="retrieval_query",
            output_dimensionality=1536
        )
        return result['embedding']
    except Exception as e:
        print(f"Failed to generate embedding: {e}")
        return None

def find_most_similar(conn, query_embedding):
    """Finds the most similar recommendation using cosine similarity."""
    with conn.cursor() as cur:
        try:
            embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
            cur.execute(
                """
                SELECT name, location, neighborhood, summary, quote, source_url, 1 - (embedding <=> %s) AS similarity
                FROM recommendations
                WHERE embedding IS NOT NULL
                ORDER BY similarity DESC
                LIMIT 1;
                """,
                (embedding_str,)
            )
            return cur.fetchone()
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return None

def main():
    """
    Main function to run the query CLI.
    """
    load_dotenv()

    parser = argparse.ArgumentParser(description="Query recommendation embeddings.")
    parser.add_argument("query", type=str, help="The text query to search for.")
    args = parser.parse_args()

    conn = get_db_connection()
    if not conn:
        sys.exit("Could not connect to the database. Exiting.")

    query_embedding = get_embedding(args.query)

    if query_embedding:
        most_similar = find_most_similar(conn, query_embedding)
        if most_similar:
            name, location, neighborhood, summary, quote, source_url, similarity = most_similar
            print("\n--- Most Similar Recommendation ---")
            print(f"Name: {name}")
            print(f"Location: {location}")
            print(f"Neighborhood: {neighborhood}")
            print(f"Summary: {summary}")
            print(f"Quote: {quote}")
            print(f"Source URL: {source_url}")
            print(f"Similarity: {similarity:.4f}")
            print("-----------------------------------")
        else:
            print("Could not find any similar recommendations.")

    conn.close()

if __name__ == "__main__":
    main()
