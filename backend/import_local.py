"""
Alternative Google Drive Import Script
Use this if the built-in import has issues with gdown.

This script manually downloads files from Google Drive using alternative methods.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("""
╔══════════════════════════════════════════════════════════════╗
║  Alternative Google Drive Import Method                      ║
╚══════════════════════════════════════════════════════════════╝

WORKAROUND for gdown permission issues:

1. Download your photos manually from Google Drive to your computer
2. Place them in: backend/data/uploads/
3. Run this script to process them

This bypasses gdown entirely and processes local files directly.
""")

import asyncio
from services.admin_service import get_admin_service
import config

async def process_local_photos():
    """Process all photos in the uploads directory."""
    
    admin_service = get_admin_service()
    
    # Get all image files from uploads directory
    upload_dir = config.UPLOAD_DIR
    photo_files = [
        f for f in upload_dir.iterdir() 
        if f.is_file() and config.is_allowed_file(f.name) and f.name != '.gitkeep'
    ]
    
    if not photo_files:
        print(f"\n❌ No photos found in {upload_dir}")
        print(f"\nPlease:")
        print(f"1. Download photos from Google Drive to your computer")
        print(f"2. Copy them to: {upload_dir.absolute()}")
        print(f"3. Run this script again")
        return
    
    print(f"\n✅ Found {len(photo_files)} photos to process")
    print(f"📁 Location: {upload_dir.absolute()}\n")
    
    # Ask for confirmation
    response = input(f"Process these {len(photo_files)} photos? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Cancelled")
        return
    
    print("\n" + "="*60)
    print("PROCESSING PHOTOS")
    print("="*60 + "\n")
    
    # Process each photo
    stats = {
        'successful': 0,
        'failed': 0,
        'total_faces': 0
    }
    
    for i, photo_path in enumerate(photo_files, 1):
        print(f"[{i}/{len(photo_files)}] Processing: {photo_path.name}")
        
        try:
            result = await admin_service._process_image_file(photo_path)
            
            if result['success']:
                stats['successful'] += 1
                stats['total_faces'] += result.get('faces_detected', 0)
                print(f"  ✅ {result.get('faces_detected', 0)} faces detected")
            else:
                stats['failed'] += 1
                print(f"  ❌ {result.get('error', 'Unknown error')}")
        except Exception as e:
            stats['failed'] += 1
            print(f"  ❌ Exception: {str(e)}")
    
    # Print summary
    print("\n" + "="*60)
    print("PROCESSING COMPLETE")
    print("="*60)
    print(f"✅ Successful: {stats['successful']}")
    print(f"❌ Failed: {stats['failed']}")
    print(f"👤 Total faces detected: {stats['total_faces']}")
    
    # Show database stats
    db_stats = admin_service.get_database_stats()
    print(f"\n📊 Database now contains:")
    print(f"   - {db_stats['total_photos']} photos")
    print(f"   - {db_stats['total_faces']} faces")
    print("\n✨ Ready for guest search!")

if __name__ == "__main__":
    asyncio.run(process_local_photos())
