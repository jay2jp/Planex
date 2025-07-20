#!/usr/bin/env python3
"""
Batch video analysis script
Processes multiple TikTok/Instagram URLs and saves results to CSV
"""

import requests
import pandas as pd
import time
from datetime import datetime
import json
import os

# Configuration
API_URL = "http://localhost:5000/analyze"
OUTPUT_CSV = "video_analysis_results.csv"
REQUEST_TIMEOUT = 300  # 5 minutes per video
DELAY_BETWEEN_REQUESTS = 2  # seconds

# Sample URLs - replace with your own
URLS_TO_ANALYZE = [
    "https://www.tiktok.com/@tiktok/video/7106594312292453675?is_copy_url=1&is_from_webapp=v1",
    "https://www.tiktok.com/@tiktok/video/7011536772089924869?is_copy_url=1&is_from_webapp=v1",
    # Add your URLs here
    # "https://www.instagram.com/reel/ABC123/",
    # "https://www.tiktok.com/@username/video/1234567890",
]

# Analysis prompts to run for each video
ANALYSIS_PROMPTS = [
    "What is the main topic or subject of this video?",
    "Describe what you see happening in this video.",
    "What is the overall mood or tone of this video?",
    # "List any products, brands, or items mentioned in this video.",
    # "What type of content category does this video belong to?",
]

def check_server_health():
    """Check if the Flask server is running"""
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        return True
    except:
        return False

def analyze_single_video(url, prompt):
    """Analyze a single video with a specific prompt"""
    payload = {
        "url": url,
        "prompt": prompt
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"   📝 Prompt: {prompt[:50]}...")
        start_time = time.time()
        
        response = requests.post(API_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            return {
                'status': 'success',
                'result': result.get('result', ''),
                'duration': duration,
                'error': None
            }
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"error": response.text}
            return {
                'status': 'error',
                'result': None,
                'duration': duration,
                'error': error_data.get('error', 'Unknown error')
            }
            
    except requests.exceptions.Timeout:
        return {
            'status': 'timeout',
            'result': None,
            'duration': REQUEST_TIMEOUT,
            'error': 'Request timed out'
        }
    except requests.exceptions.ConnectionError:
        return {
            'status': 'connection_error',
            'result': None,
            'duration': 0,
            'error': 'Could not connect to server'
        }
    except Exception as e:
        return {
            'status': 'error',
            'result': None,
            'duration': 0,
            'error': str(e)
        }

def batch_analyze():
    """Process all URLs with all prompts and save to CSV"""
    print("🚀 Batch Video Analysis")
    print("=" * 50)
    print(f"📹 URLs to process: {len(URLS_TO_ANALYZE)}")
    print(f"📝 Prompts per video: {len(ANALYSIS_PROMPTS)}")
    print(f"📊 Total analyses: {len(URLS_TO_ANALYZE) * len(ANALYSIS_PROMPTS)}")
    print(f"💾 Output file: {OUTPUT_CSV}")
    print()
    
    # Check server
    if not check_server_health():
        print("❌ Server not reachable!")
        print("💡 Start the server first: python app.py")
        return
    
    print("✅ Server is responding")
    print()
    
    # Prepare results list
    results = []
    total_analyses = len(URLS_TO_ANALYZE) * len(ANALYSIS_PROMPTS)
    current_analysis = 0
    
    # Process each URL
    for url_index, url in enumerate(URLS_TO_ANALYZE, 1):
        print(f"🎬 Processing video {url_index}/{len(URLS_TO_ANALYZE)}: {url}")
        
        # Extract video info for better tracking
        if "tiktok.com" in url:
            platform = "TikTok"
            video_id = url.split("/video/")[1].split("?")[0] if "/video/" in url else "unknown"
        elif "instagram.com" in url:
            platform = "Instagram"
            video_id = url.split("/reel/")[1].rstrip("/") if "/reel/" in url else "unknown"
        else:
            platform = "Unknown"
            video_id = "unknown"
        
        # Process each prompt for this URL
        for prompt_index, prompt in enumerate(ANALYSIS_PROMPTS, 1):
            current_analysis += 1
            
            print(f"   🔍 Analysis {current_analysis}/{total_analyses} (Prompt {prompt_index}/{len(ANALYSIS_PROMPTS)})")
            
            # Analyze video
            analysis_result = analyze_single_video(url, prompt)
            
            # Create result record
            result_record = {
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'platform': platform,
                'video_id': video_id,
                'prompt': prompt,
                'status': analysis_result['status'],
                'result': analysis_result['result'],
                'duration_seconds': round(analysis_result['duration'], 2),
                'error_message': analysis_result['error']
            }
            
            results.append(result_record)
            
            # Show result
            if analysis_result['status'] == 'success':
                result_preview = analysis_result['result'][:100] + "..." if len(analysis_result['result']) > 100 else analysis_result['result']
                print(f"   ✅ Success ({analysis_result['duration']:.1f}s): {result_preview}")
            else:
                print(f"   ❌ {analysis_result['status']}: {analysis_result['error']}")
            
            # Save progress incrementally
            if current_analysis % 5 == 0 or current_analysis == total_analyses:
                save_results_to_csv(results)
                print(f"   💾 Progress saved ({current_analysis}/{total_analyses})")
            
            # Delay between requests (be nice to the server)
            if current_analysis < total_analyses:
                print(f"   ⏳ Waiting {DELAY_BETWEEN_REQUESTS}s...")
                time.sleep(DELAY_BETWEEN_REQUESTS)
        
        print()
    
    # Final save
    save_results_to_csv(results)
    
    # Summary
    print("🎉 Batch analysis complete!")
    print("=" * 50)
    
    df = pd.DataFrame(results)
    success_count = len(df[df['status'] == 'success'])
    error_count = len(df[df['status'] != 'success'])
    
    print(f"📊 Results Summary:")
    print(f"   ✅ Successful analyses: {success_count}")
    print(f"   ❌ Failed analyses: {error_count}")
    print(f"   📈 Success rate: {success_count/len(results)*100:.1f}%")
    print(f"   💾 Results saved to: {OUTPUT_CSV}")
    
    if error_count > 0:
        print(f"\n🔍 Error breakdown:")
        error_summary = df[df['status'] != 'success']['status'].value_counts()
        for error_type, count in error_summary.items():
            print(f"   {error_type}: {count}")

def save_results_to_csv(results):
    """Save results to CSV file"""
    try:
        df = pd.DataFrame(results)
        df.to_csv(OUTPUT_CSV, index=False)
    except Exception as e:
        print(f"❌ Error saving CSV: {e}")

def load_urls_from_file(filename):
    """Load URLs from a text file (one URL per line)"""
    try:
        with open(filename, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return urls
    except FileNotFoundError:
        print(f"❌ File {filename} not found")
        return []
    except Exception as e:
        print(f"❌ Error reading {filename}: {e}")
        return []

def create_sample_urls_file():
    """Create a sample URLs file for users"""
    sample_content = """# Video URLs to analyze (one per line)
# Lines starting with # are comments and will be ignored

# TikTok examples (these work reliably)
https://www.tiktok.com/@tiktok/video/7106594312292453675?is_copy_url=1&is_from_webapp=v1
https://www.tiktok.com/@tiktok/video/7011536772089924869?is_copy_url=1&is_from_webapp=v1

# Add your URLs below:
# https://www.tiktok.com/@username/video/1234567890
# https://www.instagram.com/reel/ABC123DEF456/
"""
    
    with open('urls_to_analyze.txt', 'w') as f:
        f.write(sample_content)
    
    print("📝 Created sample file: urls_to_analyze.txt")
    print("💡 Edit this file to add your URLs, then run:")
    print("   python batch_analyze.py --file urls_to_analyze.txt")

if __name__ == "__main__":
    import sys
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--create-sample":
            create_sample_urls_file()
            exit(0)
        elif sys.argv[1] == "--file" and len(sys.argv) > 2:
            # Load URLs from file
            filename = sys.argv[2]
            file_urls = load_urls_from_file(filename)
            if file_urls:
                print(f"📁 Loaded {len(file_urls)} URLs from {filename}")
                URLS_TO_ANALYZE = file_urls
            else:
                print("❌ No valid URLs found in file")
                exit(1)
        elif sys.argv[1] == "--help":
            print("🔧 Batch Video Analysis Tool")
            print()
            print("Usage:")
            print("  python batch_analyze.py                    # Use URLs defined in script")
            print("  python batch_analyze.py --file urls.txt    # Load URLs from file")
            print("  python batch_analyze.py --create-sample    # Create sample URLs file")
            print("  python batch_analyze.py --help             # Show this help")
            print()
            print("File format: One URL per line, # for comments")
            exit(0)
    
    # Run the batch analysis
    batch_analyze() 