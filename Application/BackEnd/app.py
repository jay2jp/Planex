#!/usr/bin/env python3
"""
Flask application for the Advanced Recommendation Pipeline chat interface.
"""

import os
import sys
import json
import logging
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
import psycopg2

# Add Processor to the Python path to access pipeline functions
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
processor_dir = os.path.join(root_dir, 'Processor', 'queryPipeline')
sys.path.insert(0, processor_dir)

# Import functions from the main pipeline script
try:
    from main import (
        get_db_connection,
        expand_query,
        get_embedding,
        find_similar_recommendations,
        filter_candidates,
    )
except ImportError as e:
    print(f"Error importing from main pipeline: {e}")
    sys.exit(1)

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure the Gemini API key
gemini_api_key = os.getenv("GOOGLE_API_KEY")
if not gemini_api_key:
    sys.exit("GOOGLE_API_KEY not found in environment variables.")
genai.configure(api_key=gemini_api_key)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback_secret_key_for_development")  # Change for production
CORS(app)  # Enable CORS for all routes

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
        logging.error(f"Failed to synthesize answer: {e}")
        return "I found some recommendations, but I had trouble summarizing them."

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """
    Main chat endpoint for the conversational interface.
    Expects JSON with 'query' field and optional 'session_id' field.
    """
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' in request body"}), 400
    
    user_query = data['query']
    
    # Initialize or retrieve chat history from session
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    chat_history = session['chat_history']
    
    # Connect to database
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Could not connect to the database"}), 500

    try:
        # Run the pipeline
        expanded_queries = expand_query(user_query)
        logging.info("...thinking...")

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

        # Update history (keep only last 10 exchanges to prevent session overload)
        chat_history.append({"user": user_query, "ai": ai_response})
        if len(chat_history) > 10:
            chat_history = chat_history[-10:]
        session['chat_history'] = chat_history

        # Prepare sources if any candidates
        sources = []
        if filtered_candidates:
            for candidate in filtered_candidates:
                sources.append({
                    "name": candidate[0],
                    "url": candidate[5]
                })

        return jsonify({
            "response": ai_response,
            "sources": sources
        })
    
    except Exception as e:
        logging.error(f"Error processing chat request: {e}")
        return jsonify({"error": "An error occurred while processing your request"}), 500
    
    finally:
        conn.close()

@app.route('/reset', methods=['POST'])
def reset_chat():
    """
    Reset the chat session.
    """
    session.pop('chat_history', None)
    return jsonify({"message": "Chat session reset successfully"})

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    """
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)