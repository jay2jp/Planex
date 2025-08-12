#!/usr/bin/env python3
"""
Simple test client for the Flask chat API.
"""

import requests
import json

BASE_URL = "http://localhost:5001"

def test_chat(query):
    """Test the chat endpoint with a query."""
    response = requests.post(
        f"{BASE_URL}/chat",
        headers={"Content-Type": "application/json"},
        json={"query": query}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"AI: {data['response']}")
        if data.get('sources'):
            print("\nSources:")
            for source in data['sources']:
                print(f"- {source['name']}: {source['url']}")
    else:
        print(f"Error {response.status_code}: {response.text}")

def reset_chat():
    """Reset the chat session."""
    response = requests.post(f"{BASE_URL}/reset")
    if response.status_code == 200:
        print("Chat session reset successfully")
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    print("Flask Chat API Test Client")
    print("Type 'exit' to quit, 'reset' to reset the conversation")
    
    while True:
        query = input("\nYou: ")
        
        if query.lower() == 'exit':
            break
        elif query.lower() == 'reset':
            reset_chat()
        else:
            test_chat(query)