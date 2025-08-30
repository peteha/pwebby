#!/usr/bin/env python3
"""
Command line image upload utility
Usage: python cli_upload.py <image_file> [server_url]
"""

import sys
import os
import requests
from pathlib import Path

def upload_image(image_path, server_url="http://localhost:5000"):
    """Upload image to the server via API"""
    
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"❌ Error: File '{image_path}' not found")
        return False
    
    # Check if file is an image
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
    file_extension = Path(image_path).suffix.lower()
    
    if file_extension not in image_extensions:
        print(f"❌ Error: '{image_path}' is not a supported image format")
        print("Supported formats: JPEG, PNG, GIF")
        return False
    
    try:
        # Prepare the file for upload
        with open(image_path, 'rb') as file:
            files = {'file': (os.path.basename(image_path), file)}
            
            print(f"📤 Uploading {os.path.basename(image_path)} to {server_url}...")
            
            # Make the API request
            response = requests.post(f"{server_url}/api/upload", files=files)
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Upload successful!")
                print(f"   Image ID: {result.get('image_id')}")
                print(f"   Message: {result.get('message')}")
                return True
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                print(f"❌ Upload failed (HTTP {response.status_code})")
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
                return False
                
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to server at {server_url}")
        print("   Make sure the server is running and accessible")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_usage():
    """Show usage information"""
    print("📸 Image Gallery CLI Upload Tool")
    print("")
    print("Usage:")
    print("  python cli_upload.py <image_file> [server_url]")
    print("")
    print("Examples:")
    print("  python cli_upload.py photo.jpg")
    print("  python cli_upload.py photo.png http://myserver.com:5000")
    print("")
    print("Supported formats: JPEG, PNG, GIF")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)
    
    image_path = sys.argv[1]
    server_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:5000"
    
    # Remove trailing slash from server URL
    server_url = server_url.rstrip('/')
    
    success = upload_image(image_path, server_url)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
