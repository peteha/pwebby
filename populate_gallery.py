#!/usr/bin/env python3
"""
Live Image Downloader and Uploader for Flask Gallery
Downloads images from multiple web sources and uploads them immediately to the Flask app
"""

import requests
import os
import random
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_random_url():
    """Get a random image URL from various web sources"""
    sources = [
        # Lorem Picsum - High quality photos
        lambda: f"https://picsum.photos/800/600?random={random.randint(1, 10000)}",
        
        # Unsplash Source - Professional photos  
        lambda: f"https://source.unsplash.com/800x600/?nature,landscape,architecture&sig={random.randint(1, 10000)}",
        
        # PlaceIMG - Various categories
        lambda: f"https://placeimg.com/800/600/{random.choice(['nature', 'arch', 'tech', 'people'])}/{random.randint(1, 1000)}",
        
        # DummyImage - Clean placeholders
        lambda: f"https://dummyimage.com/800x600/{random.choice(['ff7f7f', '7f7fff', '7fff7f', 'ffff7f', 'ff7fff'])}/000000&text=Photo+{random.randint(1, 1000)}",
        
        # Placeholder.com - Colorful placeholders
        lambda: f"https://via.placeholder.com/800x600/{random.choice(['FF6B6B', '4ECDC4', '45B7D1', 'F39C12', '6C5CE7'])}/FFFFFF?text=Image+{random.randint(1, 1000)}",
    ]
    
    return random.choice(sources)()

def upload_to_gallery(filepath, flask_url="http://localhost:5001"):
    """Upload an image to the Flask gallery"""
    try:
        with open(filepath, 'rb') as f:
            files = {'file': (os.path.basename(filepath), f, 'image/jpeg')}
            data = {
                'title': f'Auto-uploaded {os.path.basename(filepath)}',
                'description': 'Automatically downloaded and uploaded image'
            }
            
            response = requests.post(f"{flask_url}/upload", files=files, data=data, timeout=30)
            
            if response.status_code == 200 or response.status_code == 302:
                return True
            else:
                return False
                
    except Exception:
        return False

def download_and_upload_image(url, index, flask_url="http://localhost:5001"):
    """Download an image and immediately upload it to the gallery"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15, stream=True)
        
        if response.status_code == 200:
            os.makedirs('temp_images', exist_ok=True)
            
            filename = f"image_{index:03d}.jpg"
            filepath = f"temp_images/{filename}"
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
                if upload_to_gallery(filepath, flask_url):
                    os.remove(filepath)
                    return f"Downloaded and uploaded: {filename} from {url.split('/')[2]}"
                else:
                    os.remove(filepath) if os.path.exists(filepath) else None
                    
    except Exception:
        pass
        
    return None

def check_flask_app(flask_url="http://localhost:5001"):
    """Check if the Flask app is running"""
    try:
        response = requests.get(flask_url, timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    parser = argparse.ArgumentParser(description='Download and upload images in real-time')
    parser.add_argument('--target', type=int, default=100,
                       help='Target number of images to upload (default: 100)')
    parser.add_argument('--workers', type=int, default=10,
                       help='Number of parallel workers (default: 10)')
    parser.add_argument('--flask-url', default='http://localhost:5001',
                       help='Flask app URL (default: http://localhost:5001)')
    args = parser.parse_args()
    
    flask_url = args.flask_url
    target_uploads = args.target
    max_workers = args.workers
    
    print(f"🚀 Live Image Gallery Populator")
    print(f"🎯 Target: {target_uploads} images")
    print(f"📊 Using {max_workers} parallel workers")
    print(f"🌐 Flask URL: {flask_url}")
    print(f"📤 Images uploaded immediately after download")
    
    if not check_flask_app(flask_url):
        print(f"❌ Flask app not accessible at {flask_url}")
        print("💡 Make sure your Flask app is running with: python app.py")
        return
    
    print("✅ Flask app is running!")
    
    successful_uploads = 0
    attempt = 1
    
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            while successful_uploads < target_uploads:
                batch_size = min(max_workers * 2, target_uploads - successful_uploads)
                futures = []
                
                for i in range(batch_size):
                    url = get_random_url()
                    future = executor.submit(download_and_upload_image, url, attempt + i, flask_url)
                    futures.append(future)
                
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if result:
                            successful_uploads += 1
                            print(f"✅ [{successful_uploads}/{target_uploads}] {result}")
                            
                            if successful_uploads >= target_uploads:
                                for f in futures:
                                    if not f.done():
                                        f.cancel()
                                break
                    except Exception:
                        continue
                
                attempt += batch_size
                
                if successful_uploads < target_uploads:
                    time.sleep(1)
                    
    except KeyboardInterrupt:
        print(f"\n⏹️  Stopped by user. Uploaded {successful_uploads} images.")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n🎉 SUCCESS! Uploaded {successful_uploads} images to your gallery!")
    print(f"🌐 View your gallery at: {flask_url}")
    
    # Clean up temp directory
    if os.path.exists('temp_images'):
        import shutil
        shutil.rmtree('temp_images')

if __name__ == "__main__":
    main()
