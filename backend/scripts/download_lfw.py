"""
Script to download LFW (Labeled Faces in the Wild) dataset for testing.
Downloads a subset of the dataset for initial testing.
"""

import urllib.request
import tarfile
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
import config


def download_lfw_dataset():
    """Download and extract LFW dataset."""
    
    # LFW dataset URL (using the aligned & cropped version)
    LFW_URL = "http://vis-www.cs.umass.edu/lfw/lfw.tgz"
    
    # Download directory
    download_dir = config.BASE_DIR / "data" / "lfw"
    download_dir.mkdir(parents=True, exist_ok=True)
    
    tar_path = download_dir / "lfw.tgz"
    
    print("=" * 60)
    print("LFW Dataset Downloader")
    print("=" * 60)
    
    # Check if already downloaded
    if (download_dir / "lfw").exists():
        print("✓ LFW dataset already exists")
        print(f"  Location: {download_dir / 'lfw'}")
        return
    
    # Download
    if not tar_path.exists():
        print(f"\nDownloading LFW dataset from {LFW_URL}")
        print("This is approximately 200MB and may take a few minutes...")
        
        try:
            def progress_hook(count, block_size, total_size):
                percent = int(count * block_size * 100 / total_size)
                sys.stdout.write(f"\r  Progress: {percent}%")
                sys.stdout.flush()
            
            urllib.request.urlretrieve(LFW_URL, str(tar_path), progress_hook)
            print("\n✓ Download complete")
            
        except Exception as e:
            print(f"\n✗ Download failed: {e}")
            return
    else:
        print("✓ Archive already downloaded")
    
    # Extract
    print("\nExtracting dataset...")
    try:
        with tarfile.open(tar_path, 'r:gz') as tar:
            tar.extractall(download_dir)
        print("✓ Extraction complete")
        
        # Remove tar file to save space
        tar_path.unlink()
        print("✓ Cleaned up archive file")
        
    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        return
    
    # Count images
    lfw_path = download_dir / "lfw"
    image_count = len(list(lfw_path.rglob("*.jpg")))
    person_count = len(list(lfw_path.iterdir()))
    
    print("\n" + "=" * 60)
    print("Dataset Ready!")
    print("=" * 60)
    print(f"  Location: {lfw_path}")
    print(f"  People: {person_count}")
    print(f"  Images: {image_count}")
    print("\nYou can now use these images to test the PhotoScan system.")
    print("Upload some images via the admin panel to build the database.")


if __name__ == "__main__":
    download_lfw_dataset()
