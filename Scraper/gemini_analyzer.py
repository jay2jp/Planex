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