import os
from pathlib import Path
import re
import tempfile
from flask import Flask, request, jsonify, render_template
import requests
from twilio.twiml.messaging_response import MessagingResponse
import instaloader
from moviepy.editor import VideoFileClip
from deepgram import Deepgram
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv
from infobipFuncs import sendMessage
import traceback
import pyktok as pyk
import pandas as pd
pyk.specify_browser('chrome')

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
# Set the directory to save the session file

# Initialize Instaloader instances for multiple accounts
accounts = [
    {"username": "MarinaraMen", "password": os.getenv('instaPass')},
    #{"username": "trystepchef", "password": os.getenv('instaPass2')},
    #{"username": "Hizzyharshpatel", "password": os.getenv('instaPass3')}
]

loaders = []
session_directory = Path("sessions/")
session_directory.mkdir(parents=True, exist_ok=True)

for account in accounts:
    loader = instaloader.Instaloader()
    username = account["username"]
    password = account["password"]

    # Create the session file path
    session_file = session_directory / f"session-{username}"

    # Log in and save the session
    loader.login(username, password)
    loader.save_session_to_file(session_file)

    loaders.append(loader)

print(f"Session files saved in: {session_directory}")

# Strategy implementation:
'''
    1. Credentials for 3 good accounts obtained (MarinaraMen, tryStepChef, jay2jp)
    2. Multiple loaders set up (loader->x)
    3. Loaders stored in the 'loaders' array
    4. When a 429 error occurs, pop the current loader and move to the next one
    5. When out of loaders, implement a function to email yourself to reset sessions manually

    This setup should help progress the POC to a point where investing in proxies becomes viable.
'''

# TODO: Implement error handling and loader rotation logic in the main application flow
# TODO: Implement email notification function for when all loaders are exhausted

#loader.load_session_from_file(username, session_file)

print(f"Session file saved to: {session_file}")
     # (login)
#L.interactive_login(USER)      # (ask password on terminal)
#L.load_session_from_file(USER) 
# Configure Deepgram and Google API
DEEPGRAM_API_KEY = os.getenv("dg_key")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)



def get_filename_from_url(url):
    # Extract username and video ID from the URL
    match = re.search(r'@([\w.]+)/video/(\d+)', url)
    if match:
        username, video_id = match.groups()
        return f'@{username}_video_{video_id}.mp4'
    else:
        raise ValueError("Invalid TikTok URL format")
    


def get_full_tiktok_url(short_url):
    # Send a request to the short URL and follow the redirect
    response = requests.get(short_url, allow_redirects=True)
    
    # The final redirected URL is stored in response.url
    return response.url
# ... (copy the generate_recipe function from the previous file) ...
def generate_recipe(tempDir):
    # Configure the Gemini model
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")#"gemini-1.5-pro")
    trans = os.path.join(tempDir, 'transcript.txt')

    # Read the transcript and other text files
    with open(trans, 'r') as f:
        transcript = f.read()
    
    # Read other text files (assuming there's only one other .txt file)
    other_text = ""
    for file in os.listdir(tempDir):
        if file.endswith(".txt") and file != "transcript.txt":
            try:
                with open(os.path.join(tempDir, file), 'r', encoding='utf-8') as f:
                    other_text = f.read()
                    break
            except UnicodeDecodeError:
                try:
                    with open(os.path.join(tempDir, file), 'r', encoding='latin-1') as f:
                        other_text = f.read()
                        break
                except Exception as e:
                    print(f"Error reading file {file}: {e}")
            except Exception as e:
                print(f"Error with other text: {e} {os.path.join(tempDir, file)}")
    # Combine the texts
    combined_text = f"Transcript:\n{transcript}\n\nAdditional Information:\n{other_text}"
    print("COMBIED TEXT")
    print(combined_text)
    # Generate recipe using Gemini
    chat = model.start_chat(history=[])
    response = chat.send_message(f"Based on the following information, create a step-by-step recipe instruction and a recipe list:\n\n{combined_text}. Do not reply in markdown")
    
    recipe = response.text
    recipe_dir = os.path.join(tempDir, "recipe.txt")

    # Save the recipe
    with open(recipe_dir, 'w', encoding='utf-8') as f:
        f.write(recipe)
    
    print("Recipe generated and saved as recipe.txt")
    return recipe

@app.route("/infobip", methods=['POST'])
def infobip():
    data= request.json
    print(data)
    return "infoBIP"



#@app.route("/webapp", methods=['POST'])
def webapp_webhook(data):
    #data = request.json

    #data = request.json
    print(data)
    result = data.get('results', '')

    content = result[0].get('content', '')
    print(content)
    incoming_url = content[0].get('text', '') #data.get('url', '')
    print(incoming_url)

    def process_request():
        if "instagram.com" in incoming_url:
            # Extract shortcode from the URL
            shortcode = incoming_url.split("/")[-2]
            print(shortcode)
            try:
                # Create a temporary directory
                temp_dir = tempfile.mkdtemp()
                insta_post_dir = os.path.join(temp_dir, f"{shortcode}")
                insta_post_dir = os.path.join(insta_post_dir, "instaPost")
                os.makedirs(insta_post_dir, exist_ok=True)

                # Try to download the post using each loader in the loaders array
                loaded = False
                for loader in loaders:
                    try:
                        # Initialize the loader with the temporary directory
                        loader.dirname_pattern = insta_post_dir
                        # Download the post
                        post = instaloader.Post.from_shortcode(loader.context, shortcode)
                        loaded = loader.download_post(post, insta_post_dir)
                        if loaded:
                            print(f"Successfully loaded with {loader.test_login()}")
                            break
                    except Exception as e:
                        print(f"Failed to load with {loader.test_login()}: {str(e)}")

                if not loaded:
                    raise Exception("Failed to download the post with all available loaders")

                print('downloaded')
                # Process video and generate recipe
                print(insta_post_dir)
                recipe = process_video_and_generate_recipe(insta_post_dir)
                print(recipe)
                return recipe, 200
            except Exception as e:
                print(e)
                error_traceback = traceback.format_exc()
                print(f"Error occurred:\n{error_traceback}")
                return f"An error occurred while processing your request. Error details:\n{str(e)}", 500
                #sendMessage(result[0].get('sender', ''), f"An error occurred while processing your request. Error details:\n{str(e)}")


        elif "tiktok.com" in incoming_url:
            print("tiktok")

            # Create a temporary directory
            temp_dir = tempfile.mkdtemp()
            url = incoming_url #'https://www.tiktok.com/@tiktok/video/7106594312292453675?is_copy_url=1&is_from_webapp=v1'
            # Generate the filename from the URL
            url = get_full_tiktok_url(url)
            video_filename = get_filename_from_url(url)
            video_id = os.path.splitext(video_filename)[0]

            temp_dir = tempfile.mkdtemp()
            insta_post_dir = os.path.join(temp_dir, f"{video_id}")
            insta_post_dir = os.path.join(insta_post_dir, "instaPost")
            os.makedirs(insta_post_dir, exist_ok=True)

            print(insta_post_dir)
            temp_dir = insta_post_dir
            # Save the TikTok video to the temporary directory
            pyk.save_tiktok(url,
                            True,
                            os.path.join(temp_dir, 'video_data.csv'),
                            'chrome')

            # Move the video file to the temporary directory
            if os.path.exists(video_filename):
                os.rename(video_filename, os.path.join(temp_dir, video_filename))
            else:
                print(f"Warning: Video file {video_filename} not found in the current directory.")

            print(f"Video saved to temporary directory: {temp_dir}")

            # Print out the contents of the temp directory
            print("Contents of the temporary directory:")
            for item in os.listdir(temp_dir):
                print(f"- {item}")
            # Print out the contents of the video_data.csv file as a dataframe
            caption = ""
            csv_file_path = os.path.join(temp_dir, 'video_data.csv')
            if os.path.exists(csv_file_path):
                print("\nContents of video_data.csv as a dataframe:")
                df = pd.read_csv(csv_file_path)
                print(df['video_description'].values[0])
                caption = df['video_description'].values[0]
                # Save the caption to a file in the temporary directory
                caption_file_path = os.path.join(temp_dir, 'caption.txt')
                with open(caption_file_path, 'w', encoding='utf-8') as caption_file:
                    caption_file.write(caption)

                print(f"Caption saved to: {caption_file_path}")

            else:
                print("video_data.csv not found in the temporary directory.")


            print("Contents of the temporary directory:")
            for item in os.listdir(temp_dir):
                print(f"- {item}")
            recipe = process_video_and_generate_recipe(temp_dir)
            print(recipe)
            return recipe, 200
            #sendMessage(result[0].get('sender', ''), recipe)
        
        else:
            #sendMessage(result[0].get('sender', ''), "Please send an Instagram reel link.")
            return "Please send an Instagram reel link.", 400
    
    return process_request()


from threading import Thread
import time

@app.route("/whatsapp", methods=['POST'])
def whatsapp_webhook():
    data = request.json
    print(data)
    result = data.get('results', '')

    content = result[0].get('content', '')
    print(content)
    incoming_url = content[0].get('text', '') #data.get('url', '')
    print(incoming_url)

    def process_request():
        if "instagram.com" in incoming_url:
            # Extract shortcode from the URL
            shortcode = incoming_url.split("/")[-2]
            print(shortcode)
            try:
                # Create a temporary directory
                temp_dir = tempfile.mkdtemp()
                insta_post_dir = os.path.join(temp_dir, f"{shortcode}")
                insta_post_dir = os.path.join(insta_post_dir, "instaPost")
                os.makedirs(insta_post_dir, exist_ok=True)
                # Initialize the loader with the temporary directory
                loader = instaloader.Instaloader(dirname_pattern=insta_post_dir)
                # Download the post
                post = instaloader.Post.from_shortcode(loader.context, shortcode)
                loader.download_post(post, insta_post_dir)
                print('downloaded')
                # Process video and generate recipe
                print(insta_post_dir)
                recipe = process_video_and_generate_recipe(insta_post_dir)
                print(recipe)
                sendMessage(result[0].get('sender',''), recipe)
            except Exception as e:
                print(e)
                error_traceback = traceback.format_exc()
                print(f"Error occurred:\n{error_traceback}")
                sendMessage(result[0].get('sender', ''), f"An error occurred while processing your request. Error details:\n{str(e)}")
        elif "tiktok.com" in incoming_url:
            print("tiktok")
            # Create a temporary directory
            temp_dir = tempfile.mkdtemp()
            url = 'https://www.tiktok.com/@tiktok/video/7106594312292453675?is_copy_url=1&is_from_webapp=v1'
            # Generate the filename from the URL
            video_filename = get_filename_from_url(url)
            video_id = os.path.splitext(video_filename)[0]

            temp_dir = tempfile.mkdtemp()
            insta_post_dir = os.path.join(temp_dir, f"{video_id}")
            insta_post_dir = os.path.join(insta_post_dir, "instaPost")
            os.makedirs(insta_post_dir, exist_ok=True)

            print(insta_post_dir)
            temp_dir = insta_post_dir
            # Save the TikTok video to the temporary directory
            pyk.save_tiktok(url,
                            True,
                            os.path.join(temp_dir, 'video_data.csv'),
                            'chrome')

            # Move the video file to the temporary directory
            if os.path.exists(video_filename):
                os.rename(video_filename, os.path.join(temp_dir, video_filename))
            else:
                print(f"Warning: Video file {video_filename} not found in the current directory.")

            print(f"Video saved to temporary directory: {temp_dir}")

            # Print out the contents of the temp directory
            print("Contents of the temporary directory:")
            for item in os.listdir(temp_dir):
                print(f"- {item}")
            # Print out the contents of the video_data.csv file as a dataframe
            caption = ""
            csv_file_path = os.path.join(temp_dir, 'video_data.csv')
            if os.path.exists(csv_file_path):
                print("\nContents of video_data.csv as a dataframe:")
                df = pd.read_csv(csv_file_path)
                print(df['video_description'].values[0])
                caption = df['video_description'].values[0]
                # Save the caption to a file in the temporary directory
                caption_file_path = os.path.join(temp_dir, 'caption.txt')
                with open(caption_file_path, 'w', encoding='utf-8') as caption_file:
                    caption_file.write(caption)

                print(f"Caption saved to: {caption_file_path}")

            else:
                print("video_data.csv not found in the temporary directory.")


            print("Contents of the temporary directory:")
            for item in os.listdir(temp_dir):
                print(f"- {item}")
            recipe = process_video_and_generate_recipe(temp_dir)
            print(recipe)
            sendMessage(result[0].get('sender', ''), recipe)
        else:
            sendMessage(result[0].get('sender', ''), "Please send an Instagram reel link or a tiktok video link.")

    # Start processing in a separate thread
    thread = Thread(target=process_request)
    thread.start()

    # Wait for 5 seconds or until the thread completes
    thread.join(timeout=7)

    if thread.is_alive():
        # If the thread is still running after 5 seconds, send a quick response
        sendMessage(result[0].get('sender',''), "we are working on it!")

        return '', 200
    else:
        # If the thread completed within 5 seconds, the response has already been sent via sendMessage
        return jsonify({"message": "Request processed successfully"}), 200
def process_video_and_generate_recipe(tempDir):
    # Find the MP4 file
    mp4_file = next((f for f in os.listdir(tempDir) if f.endswith(".mp4")), None)
    
    if mp4_file:
        mp4_path = os.path.join(tempDir, mp4_file)
        mp3_path = os.path.join(tempDir, "audio.mp3")

        # Extract audio
        video = VideoFileClip(mp4_path)
        video.audio.write_audiofile(mp3_path)
        video.close()
        print("TRANSCRIBIG")
        # Transcribe audio
        transcirpt = asyncio.run(transcribe_audio(mp3_path,tempDir))
        print(mp3_path)
        print(transcirpt)
        # Generate recipe
        temp = generate_recipe(tempDir)
        return temp
    else:
        raise Exception("No MP4 file found in the instaPost folder")

async def transcribe_audio(mp3_path,tempDir):
    dg_client = Deepgram(DEEPGRAM_API_KEY)
    
    with open(mp3_path, 'rb') as audio:
        source = {'buffer': audio, 'mimetype': 'audio/mp3'}
        response = await dg_client.transcription.prerecorded(source, {'punctuate': True})
        
        transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
        transcripty = os.path.join(tempDir, "transcript.txt")

        with open(transcripty, 'w') as f:
            f.write(transcript)
        return transcript

@app.route("/", methods=['GET'])
def home():
    return render_template('chat.html')

@app.route("/send_message", methods=['POST'])
def send_message():
    message = request.form['message']
    # Process the message as if it was received from WhatsApp
    data = {
        'results': [
            {
                'content': [{'text': message}],
                'sender': request.remote_addr
            }
        ]
    }
    return webapp_webhook(data)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
    '''
    temp_dir = tempfile.mkdtemp()
    insta_post_dir = os.path.join(temp_dir, "instaPost")
    os.makedirs(insta_post_dir, exist_ok=True)
    # Initialize the loader with the temporary directory
    loader = instaloader.Instaloader(dirname_pattern=insta_post_dir)
    # Download the post
    post = instaloader.Post.from_shortcode(loader.context, "C9k1xfiSNNn")
    loader.download_post(post, insta_post_dir)
    print('downloaded')
    # Process video and generate recipe
    print(insta_post_dir)
    bean = process_video_and_generate_recipe(insta_post_dir)
    print(bean)
    '''