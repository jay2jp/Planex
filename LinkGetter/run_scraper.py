#!/usr/bin/env python3
"""
Command-line utility for running the video scraper with custom hashtags.
"""

import argparse
import sys
import json
from video_scraper import get_top_videos

def main():
    """Main command-line interface"""
    parser = argparse.ArgumentParser(
        description="Scrape top videos from Instagram and TikTok for a given hashtag",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_scraper.py dance
  python run_scraper.py music --json
  python run_scraper.py travel --output results.json
  python run_scraper.py art --verbose
        """
    )
    
    parser.add_argument(
        'hashtag',
        help='Hashtag to search for (without the # symbol)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Save results to a file'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed progress information'
    )
    
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty print JSON output'
    )
    
    args = parser.parse_args()
    
    # Validate hashtag
    hashtag = args.hashtag.strip().lstrip('#')
    if not hashtag:
        print("Error: Please provide a valid hashtag")
        sys.exit(1)
    
    # Set up logging level
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.INFO)
    
    print(f"🔍 Searching for top videos with hashtag: #{hashtag}")
    print("⏳ This may take a few minutes...")
    
    try:
        # Run the scraper
        result = get_top_videos(hashtag)
        
        # Process results
        instagram_count = len(result['instagram'])
        tiktok_count = len(result['tiktok'])
        total_count = instagram_count + tiktok_count
        
        if args.json:
            # JSON output
            if args.pretty:
                output = json.dumps(result, indent=2, ensure_ascii=False)
            else:
                output = json.dumps(result, ensure_ascii=False)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"✅ Results saved to {args.output}")
            else:
                print(output)
        else:
            # Human-readable output
            print(f"\n📊 Results for #{hashtag}:")
            print(f"   Instagram videos: {instagram_count}")
            print(f"   TikTok videos: {tiktok_count}")
            print(f"   Total videos: {total_count}")
            
            if instagram_count > 0:
                print(f"\n📱 Instagram Videos:")
                for i, url in enumerate(result['instagram'], 1):
                    print(f"   {i:2d}. {url}")
            
            if tiktok_count > 0:
                print(f"\n🎵 TikTok Videos:")
                for i, url in enumerate(result['tiktok'], 1):
                    print(f"   {i:2d}. {url}")
            
            if args.output:
                # Save human-readable format
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(f"Results for #{hashtag}\n")
                    f.write(f"{'='*50}\n\n")
                    f.write(f"Summary:\n")
                    f.write(f"  Instagram videos: {instagram_count}\n")
                    f.write(f"  TikTok videos: {tiktok_count}\n")
                    f.write(f"  Total videos: {total_count}\n\n")
                    
                    if instagram_count > 0:
                        f.write("Instagram Videos:\n")
                        for i, url in enumerate(result['instagram'], 1):
                            f.write(f"  {i:2d}. {url}\n")
                        f.write("\n")
                    
                    if tiktok_count > 0:
                        f.write("TikTok Videos:\n")
                        for i, url in enumerate(result['tiktok'], 1):
                            f.write(f"  {i:2d}. {url}\n")
                        f.write("\n")
                
                print(f"✅ Results saved to {args.output}")
        
        if total_count == 0:
            print("⚠️  No videos found for this hashtag")
            print("   This might be due to:")
            print("   - The hashtag has no recent videos (last 2 weeks)")
            print("   - The hashtag doesn't exist")
            print("   - Rate limiting or platform restrictions")
            sys.exit(1)
        else:
            print(f"✅ Successfully found {total_count} videos!")
    
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 