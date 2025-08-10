#!/usr/bin/env python3
"""
Advanced Recommendation Pipeline

This script implements a multi-step pipeline to provide users with synthesized,
context-aware answers to their queries.
"""

import os
import sys
import argparse
import psycopg2
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API key
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    sys.exit("GEMINI_API_KEY not found in environment variables.")
genai.configure(api_key=gemini_api_key)

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

def get_embedding(text, task_type="retrieval_query"):
    """Generates an embedding for the given text using the Gemini API."""
    try:
        result = genai.embed_content(
            model="gemini-embedding-001",
            content=text,
            task_type=task_type,
            output_dimensionality=1536
        )
        return result['embedding']
    except Exception as e:
        print(f"Failed to generate embedding: {e}")
        return None

def expand_query(query):
    """
    Expands the user's query into a set of related queries using a generative model.
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""
        Analyze the following user query and brainstorm a set of 3-5 related, but distinct, search queries that capture different facets of the user's intent.
        The queries should be optimized for a vector similarity search in a recommendation database.
        Return the queries as a Python list of strings.

        User Query: "{query}"

        Expanded Queries:
        """
        response = model.generate_content(prompt)
        # The response will be a string that looks like a Python list.
        # We can use ast.literal_eval to safely parse it into a list.
        import ast
        expanded_queries = ast.literal_eval(response.text)
        return expanded_queries
    except Exception as e:
        print(f"Failed to expand query: {e}")
        return [query] # Fallback to the original query

def find_similar_recommendations(conn, query_embedding, top_k=3):
    """
    Finds the most similar recommendations using cosine similarity.
    """
    with conn.cursor() as cur:
        try:
            embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
            cur.execute(
                """
                SELECT name, location, neighborhood, summary, quote, source_url, 1 - (embedding <=> %s) AS similarity
                FROM recommendations
                WHERE embedding IS NOT NULL
                ORDER BY similarity DESC
                LIMIT %s;
                """,
                (embedding_str, top_k)
            )
            return cur.fetchall()
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return None

def synthesize_answer(query, candidates):
    """
    Synthesizes a conversational answer from a list of candidate recommendations.
    """
    try:
        model = genai.GenerativeModel('gemini-pro')

        # Format the candidates for the prompt
        candidate_details = []
        for i, candidate in enumerate(candidates):
            name, location, neighborhood, summary, quote, source_url, similarity = candidate
            candidate_details.append(
                f"{i+1}. Name: {name}\n"
                f"   Location: {location}\n"
                f"   Neighborhood: {neighborhood}\n"
                f"   Summary: {summary}\n"
                f"   Quote: {quote}\n"
                f"   Source URL: {source_url}\n"
            )

        prompt = f"""
        You are a helpful local guide. A user has asked the following question: "{query}"

        I have found a few potential recommendations that might be relevant. Here are the details:

        {candidate_details}

        Please synthesize this information into a conversational and helpful text answer that directly addresses the user's query.
        - Explain why certain places are good recommendations, drawing from their summary or quote data.
        - The generated text must explicitly reference the specific recommendations it discusses. For example: "For a classic, no-frills slice, you should check out Tony's Pizza, which is famous for its 'crispy crust and fresh ingredients'."
        - Do not include the source URLs in the answer. They will be listed separately.
        """

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Failed to synthesize answer: {e}")
        return "I found some recommendations, but I had trouble summarizing them."

def main():
    """
    Main function to run the advanced recommendation pipeline.
    """
    parser = argparse.ArgumentParser(description="Advanced Recommendation Pipeline")
    parser.add_argument("query", type=str, help="The user's natural language query.")
    args = parser.parse_args()

    print(f"Received query: {args.query}")

    conn = get_db_connection()
    if not conn:
        sys.exit("Could not connect to the database. Exiting.")

    expanded_queries = expand_query(args.query)
    print("Expanded queries:")
    for q in expanded_queries:
        print(f"- {q}")

    all_candidates = []
    for query in expanded_queries:
        embedding = get_embedding(query)
        if embedding:
            candidates = find_similar_recommendations(conn, embedding, top_k=3)
            if candidates:
                all_candidates.extend(candidates)

    # Remove duplicates
    unique_candidates = []
    seen_urls = set()
    for candidate in all_candidates:
        if candidate[5] not in seen_urls: # Use source_url to identify duplicates
            unique_candidates.append(candidate)
            seen_urls.add(candidate[5])

    print("\n--- Unique Candidates ---")
    for candidate in unique_candidates:
        print(f"Name: {candidate[0]}, Similarity: {candidate[6]:.4f}")
    print("-------------------------")

    synthesized_answer = synthesize_answer(args.query, unique_candidates)

    print("\n--- Synthesized Answer ---")
    print(synthesized_answer)
    print("--------------------------")

    print("\n--- Sources ---")
    for candidate in unique_candidates:
        print(f"- {candidate[0]}: {candidate[5]}")
    print("---------------")


    conn.close()

if __name__ == "__main__":
    main()
