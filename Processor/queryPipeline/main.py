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
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API key
gemini_api_key = os.getenv("GOOGLE_API_KEY")
if not gemini_api_key:
    sys.exit("GOOGLE_API_KEY not found in environment variables.")
genai.configure(api_key=gemini_api_key)

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    pooler_url = os.getenv("DATABASE_POOLER_URL")
    if pooler_url:
        try:
            conn = psycopg2.connect(pooler_url)
            logging.info("Successfully connected to the database via pooler URL.")
            return conn
        except psycopg2.ProgrammingError as e:
            logging.error(f"Could not connect to database via pooler URL: {e}")
            return None
        except psycopg2.OperationalError as e:
            logging.error(f"Could not connect to database via pooler URL: {e}")
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
        logging.info("Successfully connected to the database directly.")
        return conn
    except psycopg2.OperationalError as e:
        logging.error(f"Could not connect to database directly: {e}")
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
        logging.error(f"Failed to generate embedding: {e}")
        return None

def expand_query(query):
    """
    Expands the user's query into a set of related queries using a generative model.
    """
    logging.info(f"Expanding query: '{query}'")
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        Analyze the following user query and brainstorm a set of 3-5 related, but distinct, search queries that capture different facets of the user's intent.
        The queries should be optimized for a vector similarity search in a recommendation database.
        Return the queries as a JSON array of strings.

        User Query: "{query}"

        Expanded Queries (JSON):
        """
        logging.info(f"Prompt for query expansion:\n{prompt}")
        response = model.generate_content(prompt)
        logging.info(f"Raw response from model: {response.text}")
        import json

        text_response = response.text.strip()
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
        
        text_response = text_response.replace("'","\"")

        expanded_queries = json.loads(text_response)
        logging.info(f"Expanded queries: {expanded_queries}")
        return expanded_queries
    except Exception as e:
        logging.error(f"Failed to expand query: {e}")
        logging.warning("Falling back to original query.")
        return [query]

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
            logging.error(f"Database error: {e}")
            return None

def synthesize_answer(query, candidates):
    """
    Synthesizes a conversational answer from a list of candidate recommendations.
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')

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
        logging.error(f"Failed to synthesize answer: {e}")
        return "I found some recommendations, but I had trouble summarizing them."

def filter_candidates(query, candidates):
    """
    Filters a list of candidates based on the original query's constraints using a single model call.
    """
    logging.info("Filtering candidates based on user query (single call)...")
    if not candidates:
        return []

    model = genai.GenerativeModel('gemini-2.5-flash')

    candidate_details = []
    for i, candidate in enumerate(candidates):
        name, _, _, summary, quote, _, _ = candidate
        candidate_details.append(
            f"Candidate {i}:\n"
            f"  Name: {name}\n"
            f"  Summary: {summary}\n"
            f"  Quote: {quote}\n"
        )
    
    prompt = f"""
    Analyze the user query and the list of candidate recommendations.
    User Query: "{query}"

    Candidate Recommendations:
    {" ".join(candidate_details)}

    Identify which of the candidates directly violate any explicit negative constraints in the user query. 
    For example, if the user says "I don't want to eat", any food-related recommendation is a violation.

    Return a JSON object with a single key "valid_indices" which is a list of the integer indices of the candidates that are NOT in violation of the query.
    Example response for 3 candidates where candidate 1 is a violation: {{"valid_indices": [0, 2]}}
    """

    try:
        response = model.generate_content(prompt)
        logging.info(f"Raw filter response from model: {response.text}")
        
        import json
        # Find the JSON object in the response text
        text_response = response.text
        start_index = text_response.find('{')
        end_index = text_response.rfind('}') + 1
        
        if start_index != -1 and end_index != -1:
            json_str = text_response[start_index:end_index]
            result = json.loads(json_str)
            valid_indices = result.get("valid_indices", [])
            
            filtered_candidates = [candidates[i] for i in valid_indices if i < len(candidates)]
            
            logging.info(f"Filtered from {len(candidates)} down to {len(filtered_candidates)} candidates.")
            return filtered_candidates
        else:
            logging.warning("No JSON object found in the filter response.")
            return candidates


    except Exception as e:
        logging.error(f"Failed to filter candidates in a single call: {e}")
        logging.warning("Falling back to original (unfiltered) list of candidates.")
        return candidates

def main():
    """
    Main function to run the advanced recommendation pipeline.
    """
    parser = argparse.ArgumentParser(description="Advanced Recommendation Pipeline")
    parser.add_argument("query", type=str, help="The user's natural language query.")
    args = parser.parse_args()

    logging.info(f"Received query: {args.query}")

    conn = get_db_connection()
    if not conn:
        sys.exit("Could not connect to the database. Exiting.")

    expanded_queries = expand_query(args.query)
    logging.info("Expanded queries:")
    for q in expanded_queries:
        logging.info(f"- {q}")

    all_candidates = []
    for query in expanded_queries:
        embedding = get_embedding(query)
        if embedding:
            candidates = find_similar_recommendations(conn, embedding, top_k=3)
            if candidates:
                all_candidates.extend(candidates)
    logging.info(f"Found {len(all_candidates)} total candidates from all queries.")

    unique_candidates = []
    seen_urls = set()
    for candidate in all_candidates:
        if candidate[5] not in seen_urls:
            unique_candidates.append(candidate)
            seen_urls.add(candidate[5])
    logging.info(f"Found {len(unique_candidates)} unique candidates.")

    # Filter candidates based on the original query
    filtered_candidates = filter_candidates(args.query, unique_candidates)

    logging.info("\n--- Filtered Candidates ---")
    for candidate in filtered_candidates:
        logging.info(f"Name: {candidate[0]}, Similarity: {candidate[6]:.4f}")
    logging.info("-------------------------")

    synthesized_answer = synthesize_answer(args.query, filtered_candidates)

    logging.info("\n--- Synthesized Answer ---")
    logging.info(synthesized_answer)
    logging.info("--------------------------")

    logging.info("\n--- Sources ---")
    for candidate in filtered_candidates:
        logging.info(f"- {candidate[0]}: {candidate[5]}")
    logging.info("---------------")

    conn.close()

if __name__ == "__main__":
    main()
