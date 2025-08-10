#!/usr/bin/env python3
"""
Conversational Chat Interface for the Advanced Recommendation Pipeline.
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Import functions from the main pipeline script
from main import (
    get_db_connection,
    expand_query,
    get_embedding,
    find_similar_recommendations,
    filter_candidates,
)

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API key
gemini_api_key = os.getenv("GOOGLE_API_KEY")
if not gemini_api_key:
    sys.exit("GOOGLE_API_KEY not found in environment variables.")
genai.configure(api_key=gemini_api_key)

def synthesize_chat_answer(query, history, candidates):
    """
    Synthesizes a conversational answer, considering chat history.
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Format the candidates for the prompt
        candidate_details = []
        if candidates:
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
        
        candidate_text = "\n".join(candidate_details) if candidate_details else "No specific recommendations found."


        # Format the history for the prompt
        formatted_history = ""
        for entry in history:
            formatted_history += f"User: {entry['user']}\nAI: {entry['ai']}\n"


        prompt = f"""
        You are a helpful local guide. You are having a conversation with a user.

        Here is the history of your conversation so far:
        {formatted_history}

        Here is the user's latest query: "{query}"

        I have found a few potential recommendations that might be relevant to the user's latest query. Here are the details:

        {candidate_text}

        Please synthesize this information into a conversational and helpful text answer that directly addresses the user's latest query, keeping the conversation history in mind.
        - If you found recommendations, explain why they are good, drawing from their summary or quote data.
        - The generated text must explicitly reference the specific recommendations it discusses if any were found.
        - Do not include the source URLs in the answer. They will be listed separately.
        - If no recommendations were found, provide a helpful response based on the conversation history and the query.
        """

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Failed to synthesize answer: {e}")
        return "I found some recommendations, but I had trouble summarizing them."


def chat():
    """
    Main chat loop for the conversational interface.
    """
    print("Welcome to the Recommendation Chat! Type 'exit' or 'quit' to end.")
    
    conn = get_db_connection()
    if not conn:
        sys.exit("Could not connect to the database. Exiting.")

    chat_history = []

    while True:
        user_query = input("\nYou: ")
        if user_query.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Run the pipeline
        expanded_queries = expand_query(user_query)
        print("...thinking...")

        all_candidates = []
        for q in expanded_queries:
            embedding = get_embedding(q)
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

        # Filter candidates
        filtered_candidates = filter_candidates(user_query, unique_candidates)

        # Get the synthesized answer
        ai_response = synthesize_chat_answer(user_query, chat_history, filtered_candidates)

        print(f"\nAI: {ai_response}")

        if filtered_candidates:
            print("\n--- Sources ---")
            for candidate in filtered_candidates:
                print(f"- {candidate[0]}: {candidate[5]}")
            print("---------------")

        # Update history
        chat_history.append({"user": user_query, "ai": ai_response})

    conn.close()

if __name__ == "__main__":
    chat()