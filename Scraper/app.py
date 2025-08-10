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
    '''
    scraped_data = download_video("https://www.tiktok.com/@reserve.nyc/video/7528541796184460575")
    print(scraped_data)
    prompt = """

    """
    result_text = analyze_video(
            video_path=scraped_data['video_path'],
            prompt=prompt,
            metadata_text=scraped_data['metadata_text']
        )
    print(result_text)
    '''

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True) 