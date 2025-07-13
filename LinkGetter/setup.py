#!/usr/bin/env python3
"""
Setup script for the video scraping service.
This script installs all required dependencies and sets up Playwright browsers.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command with proper error handling"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("Setting up Video Scraping Service...")
    print("=" * 50)
    
    # Install Python requirements
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        sys.exit(1)
    
    # Install Playwright browsers
    if not run_command("playwright install", "Installing Playwright browsers"):
        sys.exit(1)
    
    # Install system dependencies for Playwright
    if not run_command("playwright install-deps", "Installing system dependencies"):
        print("⚠️  System dependencies installation failed (this is normal on some systems)")
    
    print("\n" + "=" * 50)
    print("✓ Setup completed successfully!")
    print("\nYou can now run the video scraper:")
    print("  python video_scraper.py")
    print("\nOr use it programmatically:")
    print("  from video_scraper import get_top_videos")
    print("  result = get_top_videos('dance')")

if __name__ == "__main__":
    main() 