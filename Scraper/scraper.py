# scraper.py
import os
import re
import tempfile
import shutil
from pathlib import Path
import instaloader
import pyktok as pyk
import pandas as pd

# Try to set the browser for pyktok (fallback gracefully if it fails)
try:
    pyk.specify_browser('chrome')
    print("✅ PyKTok: Using Chrome browser for TikTok downloads")
except Exception as e:
    print(f"⚠️  PyKTok: Could not access Chrome browser ({str(e)})")
    print("   Continuing without browser cookies (may have rate limits)")
    # pyktok will work without browser specification, just with more limitations

# --- Instaloader Setup ---
SESSION_DIR = Path("sessions/")
SESSION_DIR.mkdir(parents=True, exist_ok=True)
LOADERS = []

# Check if Instagram credentials are provided
insta_user = os.getenv('INSTA_USER')
insta_pass = os.getenv('INSTA_PASS')

# Check if credentials are provided and not placeholder values
def is_valid_credential(value):
    if not value:
        return False
    # Check for common placeholder values
    placeholder_values = [
        'your_instagram_username',
        'YOUR_INSTAGRAM_USERNAME', 
        'your_username',
        'username',
        'your_instagram_password',
        'YOUR_INSTAGRAM_PASSWORD',
        'your_password',
        'password'
    ]
    return value not in placeholder_values

if (insta_user and insta_pass and 
    is_valid_credential(insta_user) and is_valid_credential(insta_pass)):
    # Use authenticated loader if credentials are provided
    ACCOUNTS = [
        {"username": insta_user, "password": insta_pass},
    ]
    
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
    print(f"Instagram: Using authenticated loader with {len(LOADERS)} account(s)")
else:
    # Use unauthenticated loader if no credentials provided
    unauthenticated_loader = instaloader.Instaloader()
    LOADERS.append(unauthenticated_loader)
    print("Instagram: Using unauthenticated loader (public content only)")
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
            try:
                print(f"🎬 Downloading TikTok video from: {url}")
                pyk.save_tiktok(url, True, os.path.join(temp_dir, 'video_data.csv'), 'chrome')
                
                # pyktok saves to the current working directory, so we find and move it.
                video_files = [f for f in os.listdir('.') if f.endswith('.mp4')]
                if not video_files:
                    raise Exception("TikTok video file not found in current directory after download. This could be due to: 1) Video is private/restricted, 2) TikTok rate limiting, 3) Video URL is invalid")
                
                downloaded_video_name = video_files[0]
                video_path = os.path.join(temp_dir, downloaded_video_name)
                shutil.move(downloaded_video_name, video_path)
                print(f"✅ TikTok video downloaded: {downloaded_video_name}")

                # Extract description
                csv_path = os.path.join(temp_dir, 'video_data.csv')
                if os.path.exists(csv_path):
                    df = pd.read_csv(csv_path)
                    if not df.empty and 'video_description' in df.columns:
                        metadata_text = df['video_description'].values[0]
                        print(f"📝 Found description: {metadata_text[:100]}...")
                    else:
                        metadata_text = "No description available"
                        print("⚠️  No video description found in CSV")
                else:
                    metadata_text = "No metadata file found"
                    print("⚠️  No video data CSV found")
                    
            except Exception as tiktok_error:
                error_msg = str(tiktok_error)
                if 'itemInfo' in error_msg:
                    raise Exception(f"TikTok video access failed. Possible reasons: 1) Video is private/restricted, 2) TikTok changed their API, 3) Rate limiting, 4) Geographic restrictions. Original error: {error_msg}")
                elif 'not found' in error_msg.lower():
                    raise Exception(f"TikTok video not found or inaccessible. Check if the URL is correct and the video is public. Original error: {error_msg}")
                else:
                    raise Exception(f"TikTok download failed: {error_msg}")

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
            
            if caption_file:
                with open(caption_file, 'r', encoding='utf-8') as f:
                    metadata_text = f.read()
            else:
                metadata_text = "No caption file found"

        else:
            raise ValueError("Invalid URL. Must be a public TikTok or Instagram link.")

        return {"video_path": video_path, "metadata_text": metadata_text}

    except Exception as e:
        # Cleanup temp directory on any failure
        shutil.rmtree(temp_dir)
        # Re-raise the exception to be handled by the caller
        raise e 