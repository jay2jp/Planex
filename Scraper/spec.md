Of course. Here is the combined plan.md and spec.md in a single markdown block, with references to stepChefExample.py and containing only the Python definitions as requested.

Gemini Video Analysis App: Plan and Specification

This document outlines the development plan and technical specifications for creating a web application that scrapes video content from TikTok and Instagram and uses the Google Gemini API to perform analysis based on a user's prompt. The implementation will be based on the concepts demonstrated in stepChefExample.py.

Part 1: Development Plan (plan.md)

This is the high-level, step-by-step plan for the project.

Milestone 1: Project Setup and Environment

Initialize Project Structure: Create a new project directory with a main app.py.

Dependency Management: Create a requirements.txt file listing all necessary Python libraries: Flask, google-generativeai, instaloader, pyktok, python-dotenv, pandas.

Configuration: Set up a .env file to securely store credentials like GOOGLE_API_KEY, INSTA_USER, and INSTA_PASS.

Basic Flask App: Create app.py with a basic Flask server and an endpoint for analysis.

Milestone 2: Unified Scraper Module

Create scraper.py: Develop a Python module dedicated to downloading video content.

Implement download_video function: This function will:

Accept a URL as input.

Detect if the URL is for TikTok or Instagram.

Use pyktok to download the video and its description for TikTok links.

Use instaloader to download the video and its caption for Instagram Reel links.

Incorporate the multi-account and session-handling logic from stepChefExample.py for instaloader to ensure robustness.

Return a dictionary containing the local path to the downloaded video file and any extracted text metadata (caption/description).

Temporary File Management: Ensure all downloaded files are stored in a temporary directory that is cleaned up after processing.

Milestone 3: Gemini Vision Analyzer Module

Create gemini_analyzer.py: Develop a module to handle all interactions with the Gemini API.

Implement analyze_video function: This function will:

Accept a video file path, a user-defined text prompt, and the scraped metadata as arguments.

Initialize the Gemini client with a video-capable model (e.g., gemini-1.5-pro).

Upload the video file to the Gemini API.

Construct a comprehensive prompt for the model, combining the user's question with the context from the video's metadata.

Send the uploaded video and the prompt to the model for analysis.

Return the text-based response from the API.

Milestone 4: Backend API and Integration

Develop the /analyze Endpoint in app.py:

Create a Flask route that accepts POST requests.

The endpoint will expect a JSON payload containing the url and prompt.

Orchestration Logic:

Call the download_video function from the scraper module.

If successful, call the analyze_video function from the Gemini module, passing the video path and prompt.

Handle any errors from the scraping or analysis steps gracefully.

Return the final analysis from Gemini as a JSON response.

Milestone 5: Finalization and Review

End-to-End Testing: Thoroughly test the application with various TikTok and Instagram Reel links and different prompts.

Refine Error Handling: Ensure that API responses for errors are clear (e.g., "Invalid URL," "Failed to download video").

Code Cleanup and Documentation: Add comments to the code, finalize the README.md, and ensure the .env.example file is clear.

Part 2: Technical Specification (spec.md)

This section provides the technical specifications and Python definitions for the application's backend components.

2.1. scraper.py Definition

This module abstracts the video downloading process, adapting the session management logic from stepChefExample.py.

Generated python
# scraper.py
import os
import re
import tempfile
import shutil
from pathlib import Path
import instaloader
import pyktok as pyk
import pandas as pd

# It's recommended to set the browser for pyktok
pyk.specify_browser('chrome')

# --- Instaloader Setup (adapted from stepChefExample.py) ---
ACCOUNTS = [
    {"username": os.getenv('INSTA_USER'), "password": os.getenv('INSTA_PASS')},
    # Add more accounts for rotation if needed
]
SESSION_DIR = Path("sessions/")
SESSION_DIR.mkdir(parents=True, exist_ok=True)
LOADERS = []
for account in ACCOUNTS:
    loader = instaloader.Instaloader()
    username = account["username"]
    password = account["password"]
    session_file = SESSION_DIR / f"session-{username}"
    try:
        loader.load_session_from_file(username, str(session_file))
        print(f"Loaded session for {username}")
    except FileNotFoundError:
        print(f"No session file for {username}, logging in...")
        loader.login(username, password)
        loader.save_session_to_file(str(session_file))
    LOADERS.append(loader)
# --- End Instaloader Setup ---

def download_video(url: str) -> dict:
    """
    Downloads a video from a TikTok or Instagram URL.

    Args:
        url: The URL of the video.

    Returns:
        A dictionary containing 'video_path' and 'metadata_text'.
        Raises an exception if the download fails.
    """
    temp_dir = tempfile.mkdtemp()
    
    try:
        if "tiktok.com" in url:
            # Handle TikTok
            pyk.save_tiktok(url, True, os.path.join(temp_dir, 'video_data.csv'), 'chrome')
            
            # pyktok saves to the current working directory, so we find and move it.
            video_files = [f for f in os.listdir('.') if f.endswith('.mp4')]
            if not video_files:
                raise Exception("TikTok video file not found in current directory after download.")
            
            downloaded_video_name = video_files[0]
            video_path = os.path.join(temp_dir, downloaded_video_name)
            shutil.move(downloaded_video_name, video_path)

            # Extract description
            df = pd.read_csv(os.path.join(temp_dir, 'video_data.csv'))
            metadata_text = df['video_description'].values[0]

        elif "instagram.com" in url:
            # Handle Instagram using the first available loader
            active_loader = LOADERS[0]
            shortcode = url.split("/")[-2].strip()
            post = instaloader.Post.from_shortcode(active_loader.context, shortcode)
            
            # Download to the temp directory
            active_loader.download_post(post, target=Path(temp_dir))
            
            # Find the downloaded files within the temp directory
            video_path = next((os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith(".mp4")), None)
            caption_file = next((os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith(".txt")), None)

            if not video_path:
                raise Exception("Instagram video file (.mp4) not found in the download directory.")
            
            with open(caption_file, 'r', encoding='utf-8') as f:
                metadata_text = f.read()

        else:
            raise ValueError("Invalid URL. Must be a public TikTok or Instagram link.")

        return {"video_path": video_path, "metadata_text": metadata_text}

    except Exception as e:
        # Cleanup temp directory on any failure
        shutil.rmtree(temp_dir)
        # Re-raise the exception to be handled by the caller
        raise e

2.2. gemini_analyzer.py Definition

This module handles all video analysis and interaction with the Google Gemini API.

Generated python
# gemini_analyzer.py
import os
import time
import google.generativeai as genai

# Configure the API key from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

def analyze_video(video_path: str, prompt: str, metadata_text: str) -> str:
    """
    Analyzes a video using the Gemini API based on a user prompt.

    Args:
        video_path: The local path to the video file.
        prompt: The user's question or instruction for analysis.
        metadata_text: The caption or description scraped from the post.

    Returns:
        The text response from the Gemini model.
    """
    print("Uploading file to Gemini...")
    video_file = genai.upload_file(path=video_path)
    
    # Wait for the upload to complete before proceeding
    while video_file.state.name == "PROCESSING":
        print('.', end='', flush=True)
        time.sleep(2)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
      raise ValueError("Gemini file processing failed.")

    print(f"\nFile uploaded successfully: {video_file.name}")
    
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

    # Construct the final prompt, providing context to the model
    full_prompt = f"""
    Analyze the provided video file based on the user's request.

    USER REQUEST:
    "{prompt}"

    ADDITIONAL CONTEXT (from the video's original description/caption):
    "{metadata_text}"

    Please provide a clear and direct answer to the user's request based on the visual information in the video and the provided context.
    """

    try:
        print("Generating content with Gemini...")
        response = model.generate_content([full_prompt, video_file])
        return response.text
    finally:
        # Ensure the uploaded file is deleted from Gemini's servers
        print(f"Deleting uploaded file: {video_file.name}")
        genai.delete_file(video_file.name)
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END
2.3. app.py Definition

This is the main server file that connects the scraper and analyzer modules.

Generated python
# app.py
import os
import shutil
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from scraper import download_video
from gemini_analyzer import analyze_video

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

@app.route("/analyze", methods=['POST'])
def analyze():
    """
    API endpoint to handle video analysis requests.
    Expects a JSON body with 'url' and 'prompt'.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415

    data = request.json
    url = data.get('url')
    prompt = data.get('prompt')

    if not url or not prompt:
        return jsonify({"error": "Both 'url' and 'prompt' are required fields."}), 400

    scraped_data = None
    try:
        # 1. Scrape video and metadata
        print(f"Downloading video from: {url}")
        scraped_data = download_video(url)
        print("Download successful. Starting analysis...")
        
        # 2. Analyze with Gemini
        result_text = analyze_video(
            video_path=scraped_data['video_path'],
            prompt=prompt,
            metadata_text=scraped_data['metadata_text']
        )
        
        return jsonify({"result": result_text})

    except Exception as e:
        # Catch errors from scraping or analysis
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500

    finally:
        # 3. Cleanup: Ensure the temporary directory is always removed
        if scraped_data and os.path.exists(scraped_data['video_path']):
            temp_dir = os.path.dirname(scraped_data['video_path'])
            print(f"Cleaning up temporary directory: {temp_dir}")
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    # The app runs on the port defined by the environment or defaults to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END