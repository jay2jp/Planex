#!/usr/bin/env python3
"""
Debug script to test TikTok video downloading and diagnose issues
"""

import os
import tempfile
import shutil
import pyktok as pyk
import pandas as pd

# Test URL
TEST_URL = "https://www.tiktok.com/@marcusonthelow/video/7526360050126818591"

def debug_tiktok_download():
    """Debug TikTok download process step by step"""
    print("🔍 TikTok Download Debug")
    print("=" * 40)
    print(f"📹 Testing URL: {TEST_URL}")
    print()
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    print(f"📁 Temp directory: {temp_dir}")
    
    try:
        # Test 1: Basic pyktok functionality
        print("\n1. Testing basic pyktok download...")
        try:
            print("   - Calling pyk.save_tiktok()...")
            pyk.save_tiktok(
                TEST_URL, 
                True, 
                os.path.join(temp_dir, 'video_data.csv'), 
                'chrome'
            )
            print("   ✅ pyk.save_tiktok() completed without error")
            
        except Exception as e:
            print(f"   ❌ pyk.save_tiktok() failed: {e}")
            print(f"   🔍 Error type: {type(e).__name__}")
            
            # Try without browser
            print("\n   🔄 Trying without browser specification...")
            try:
                pyk.save_tiktok(
                    TEST_URL, 
                    True, 
                    os.path.join(temp_dir, 'video_data_no_browser.csv')
                )
                print("   ✅ No-browser download worked!")
            except Exception as e2:
                print(f"   ❌ No-browser download also failed: {e2}")
                return
        
        # Test 2: Check what files were created
        print("\n2. Checking downloaded files...")
        current_dir_files = [f for f in os.listdir('.') if f.endswith('.mp4')]
        temp_dir_files = os.listdir(temp_dir)
        
        print(f"   📂 Files in current directory: {current_dir_files}")
        print(f"   📂 Files in temp directory: {temp_dir_files}")
        
        # Test 3: Check CSV data
        print("\n3. Analyzing CSV data...")
        csv_files = [f for f in temp_dir_files if f.endswith('.csv')]
        
        for csv_file in csv_files:
            csv_path = os.path.join(temp_dir, csv_file)
            print(f"   📊 Reading {csv_file}...")
            
            try:
                df = pd.read_csv(csv_path)
                print(f"      - Shape: {df.shape}")
                print(f"      - Columns: {list(df.columns)}")
                
                if 'video_description' in df.columns:
                    desc = df['video_description'].values[0] if not df.empty else "Empty"
                    print(f"      - Description: {desc[:100]}...")
                else:
                    print("      - No 'video_description' column found")
                    
            except Exception as e:
                print(f"      ❌ Error reading CSV: {e}")
        
        # Test 4: Try alternative URL formats
        print("\n4. Testing alternative URL formats...")
        
        alternative_urls = [
            TEST_URL,
            TEST_URL.replace('?', ''),  # Remove query params
            TEST_URL.split('?')[0],     # Clean URL
        ]
        
        for i, alt_url in enumerate(alternative_urls):
            if alt_url != TEST_URL:
                print(f"   🔄 Trying alternative URL {i}: {alt_url}")
                try:
                    pyk.save_tiktok(
                        alt_url, 
                        True, 
                        os.path.join(temp_dir, f'alt_video_data_{i}.csv')
                    )
                    print(f"   ✅ Alternative URL {i} worked!")
                except Exception as e:
                    print(f"   ❌ Alternative URL {i} failed: {e}")
    
    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up temp directory: {temp_dir}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Clean up any MP4 files in current directory
        current_mp4s = [f for f in os.listdir('.') if f.endswith('.mp4')]
        for mp4_file in current_mp4s:
            try:
                os.remove(mp4_file)
                print(f"   🗑️  Removed: {mp4_file}")
            except:
                pass

def test_tiktok_without_browser():
    """Test TikTok download without browser specification"""
    print("\n🔄 Testing TikTok download without browser...")
    
    # Reset pyktok browser (if possible)
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Don't specify browser
        pyk.save_tiktok(
            TEST_URL, 
            True, 
            os.path.join(temp_dir, 'no_browser_data.csv')
        )
        print("✅ Download without browser specification worked!")
        
        # Check results
        files = os.listdir(temp_dir)
        mp4s = [f for f in os.listdir('.') if f.endswith('.mp4')]
        print(f"Files created: {files}")
        print(f"MP4s in current dir: {mp4s}")
        
    except Exception as e:
        print(f"❌ Download without browser failed: {e}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    print("🐛 TikTok Download Debugging Tool")
    print()
    
    # Test browser setup first
    try:
        pyk.specify_browser('chrome')
        print("✅ Chrome browser specification works")
    except Exception as e:
        print(f"⚠️  Chrome browser issue: {e}")
    
    # Run main debug
    debug_tiktok_download()
    
    # Test without browser
    test_tiktok_without_browser()
    
    print("\n🏁 Debug complete!")
    print()
    print("💡 Next steps:")
    print("   - If all tests fail: The video might be private/restricted")
    print("   - If some work: Update scraper.py with working approach")  
    print("   - If none work: Try a different TikTok video URL") 