#!/usr/bin/env python3
"""
Alternative TikTok test approaches to work around itemInfo issue
"""

import pyktok as pyk
import tempfile
import os
import shutil
import pandas as pd

TEST_URL = "https://www.tiktok.com/@marcusonthelow/video/7526360050126818591"

def test_pyktok_alternatives():
    """Test alternative pyktok approaches"""
    print("🔄 Testing Alternative PyKTok Approaches")
    print("=" * 50)
    
    temp_dir = tempfile.mkdtemp()
    print(f"📁 Temp directory: {temp_dir}")
    
    try:
        # Method 1: Try save_tiktok with error handling
        print("\n1. Testing save_tiktok with detailed error catching...")
        try:
            pyk.save_tiktok(TEST_URL, True, os.path.join(temp_dir, 'method1.csv'))
            print("✅ Method 1 (save_tiktok) worked!")
            
            # Check what was created
            files = os.listdir(temp_dir)
            current_files = [f for f in os.listdir('.') if f.endswith('.mp4')]
            print(f"📁 Files in temp dir: {files}")
            print(f"📁 MP4 files in current dir: {current_files}")
            
        except KeyError as e:
            print(f"❌ Method 1 KeyError: {e}")
            print("🔍 This confirms TikTok structure changed")
        except Exception as e:
            print(f"❌ Method 1 other error: {e}")
        
        # Method 2: Try multi URLs approach
        print("\n2. Testing save_tiktok_multi_urls...")
        try:
            pyk.save_tiktok_multi_urls([TEST_URL], False, os.path.join(temp_dir, 'method2.csv'), 1)
            print("✅ Method 2 (multi_urls) worked!")
        except Exception as e:
            print(f"❌ Method 2 failed: {e}")
        
        # Method 3: Try different URL format
        print("\n3. Testing with cleaned URL...")
        clean_url = TEST_URL.split('?')[0]  # Remove query params
        try:
            pyk.save_tiktok(clean_url, True, os.path.join(temp_dir, 'method3.csv'))
            print("✅ Method 3 (clean URL) worked!")
        except Exception as e:
            print(f"❌ Method 3 failed: {e}")
            
        # Method 4: Try getting just JSON without video
        print("\n4. Testing JSON-only retrieval...")
        try:
            json_data = pyk.alt_get_tiktok_json(TEST_URL)
            print(f"✅ Method 4 got JSON: {type(json_data)}")
            if isinstance(json_data, dict):
                print(f"📊 Keys available: {list(json_data.keys())[:10]}")
        except Exception as e:
            print(f"❌ Method 4 failed: {e}")
        
        # Method 5: Check if any CSV files were created despite errors
        print("\n5. Checking for any created files...")
        all_files = os.listdir(temp_dir)
        mp4_files = [f for f in os.listdir('.') if f.endswith('.mp4')]
        
        print(f"📁 Temp directory contents: {all_files}")
        print(f"📁 Current directory MP4s: {mp4_files}")
        
        # Check if any CSV files have content
        for file in all_files:
            if file.endswith('.csv'):
                file_path = os.path.join(temp_dir, file)
                try:
                    df = pd.read_csv(file_path)
                    print(f"📊 {file}: {df.shape[0]} rows, columns: {list(df.columns)}")
                    if not df.empty:
                        print(f"📝 Sample data: {df.iloc[0].to_dict()}")
                except Exception as e:
                    print(f"❌ Could not read {file}: {e}")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        # Clean up any MP4 files
        for f in os.listdir('.'):
            if f.endswith('.mp4'):
                try:
                    os.remove(f)
                    print(f"🗑️ Cleaned up: {f}")
                except:
                    pass

def test_working_examples():
    """Test with URLs from pyktok documentation that should work"""
    print("\n📖 Testing PyKTok Documentation Examples")
    print("=" * 50)
    
    # URLs from pyktok README that should work
    working_urls = [
        "https://www.tiktok.com/@tiktok/video/7106594312292453675?is_copy_url=1&is_from_webapp=v1",
        "https://www.tiktok.com/@tiktok/video/7011536772089924869?is_copy_url=1&is_from_webapp=v1"
    ]
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        for i, url in enumerate(working_urls):
            print(f"\n🎬 Testing documentation example {i+1}:")
            print(f"   URL: {url}")
            
            try:
                pyk.save_tiktok(url, True, os.path.join(temp_dir, f'doc_example_{i}.csv'))
                print(f"   ✅ Documentation example {i+1} worked!")
                
                # Check results
                csv_file = os.path.join(temp_dir, f'doc_example_{i}.csv')
                if os.path.exists(csv_file):
                    df = pd.read_csv(csv_file)
                    print(f"   📊 Got {df.shape[0]} rows with columns: {list(df.columns)}")
                
            except Exception as e:
                print(f"   ❌ Documentation example {i+1} failed: {e}")
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def check_pyktok_version():
    """Check if pyktok version might be the issue"""
    print("\n📦 PyKTok Version Check")
    print("=" * 30)
    
    try:
        import pyktok
        version = getattr(pyktok, '__version__', 'Unknown')
        print(f"📌 Current pyktok version: {version}")
        
        # Get the current version info
        import pkg_resources
        try:
            installed = pkg_resources.get_distribution('pyktok')
            print(f"📌 Installed version: {installed.version}")
        except:
            print("❓ Could not get installed version info")
            
        print("\n💡 To update pyktok: pip install --upgrade pyktok")
        
    except Exception as e:
        print(f"❌ Error checking version: {e}")

if __name__ == "__main__":
    print("🔄 Alternative TikTok Testing Approaches")
    print()
    
    check_pyktok_version()
    test_pyktok_alternatives()
    test_working_examples()
    
    print("\n🏁 Alternative testing complete!")
    print("\n💡 Summary:")
    print("   - If doc examples work: The issue is with your specific URL")
    print("   - If nothing works: PyKTok needs updating or TikTok blocked it")
    print("   - If JSON works but video fails: Can build workaround")
    print("\n🔧 Next steps:")
    print("   1. Run: pip install --upgrade pyktok")
    print("   2. Run: playwright install")
    print("   3. Try with different TikTok videos")
    print("   4. Consider using Instagram videos instead (more reliable)") 