"""
Test script to verify Google Drive import functionality.
This script tests the complete workflow:
1. Import photos from Google Drive
2. Process faces and generate embeddings
3. Store embeddings in FAISS
4. Search with a selfie
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.drive_service import get_drive_service, tasks
from services.admin_service import get_admin_service
from services.guest_service import get_guest_service
import config

async def test_drive_import():
    """Test Google Drive import functionality."""
    print("=" * 60)
    print("TESTING GOOGLE DRIVE IMPORT FUNCTIONALITY")
    print("=" * 60)
    
    # Get services
    drive_service = get_drive_service()
    admin_service = get_admin_service()
    
    # Check initial stats
    print("\n1. Checking initial database stats...")
    stats = admin_service.get_database_stats()
    print(f"   - Total photos: {stats['total_photos']}")
    print(f"   - Total faces: {stats['total_faces']}")
    
    # Test with a sample Drive URL (user needs to provide this)
    print("\n2. Testing Drive import...")
    print("   NOTE: You need to provide a public Google Drive folder URL")
    print("   Example: https://drive.google.com/drive/folders/YOUR_FOLDER_ID")
    
    drive_url = input("\n   Enter Google Drive folder URL (or press Enter to skip): ").strip()
    
    if not drive_url:
        print("   ⚠️  Skipping Drive import test")
        return
    
    # Start import
    task_id = "test_import_001"
    print(f"\n   Starting import with task ID: {task_id}")
    
    # Run import in background
    await drive_service.process_drive_link(drive_url, task_id)
    
    # Check task status
    print("\n3. Checking import status...")
    if task_id in tasks:
        task_status = tasks[task_id]
        print(f"   Status: {task_status.get('status')}")
        print(f"   Message: {task_status.get('message', 'N/A')}")
        
        if task_status.get('status') == 'completed':
            print("\n   ✅ Import completed successfully!")
            if 'stats' in task_status:
                stats = task_status['stats']
                print(f"   - Successful: {stats.get('successful', 0)}")
                print(f"   - Failed: {stats.get('failed', 0)}")
                print(f"   - Total faces: {stats.get('total_faces', 0)}")
        elif task_status.get('status') == 'failed':
            print(f"\n   ❌ Import failed: {task_status.get('error', 'Unknown error')}")
    
    # Check final stats
    print("\n4. Checking final database stats...")
    final_stats = admin_service.get_database_stats()
    print(f"   - Total photos: {final_stats['total_photos']}")
    print(f"   - Total faces: {final_stats['total_faces']}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

async def test_manual_upload():
    """Test manual photo upload and processing."""
    print("\n" + "=" * 60)
    print("TESTING MANUAL PHOTO PROCESSING")
    print("=" * 60)
    
    admin_service = get_admin_service()
    
    # Check if there are any photos in the upload directory
    upload_dir = config.UPLOAD_DIR
    photo_files = [f for f in upload_dir.iterdir() if f.is_file() and f.suffix.lower() in config.ALLOWED_EXTENSIONS]
    
    if not photo_files:
        print("\n   ⚠️  No photos found in upload directory")
        print(f"   Upload directory: {upload_dir}")
        print("   Please add some test photos to this directory")
        return
    
    print(f"\n   Found {len(photo_files)} photos in upload directory")
    print(f"   Processing first photo: {photo_files[0].name}")
    
    # Process the first photo
    result = await admin_service._process_image_file(photo_files[0])
    
    print("\n   Processing result:")
    print(f"   - Success: {result.get('success')}")
    print(f"   - Faces detected: {result.get('faces_detected', 0)}")
    print(f"   - Faces stored: {result.get('faces_stored', 0)}")
    
    if not result.get('success'):
        print(f"   - Error: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)

async def test_guest_search():
    """Test guest search functionality."""
    print("\n" + "=" * 60)
    print("TESTING GUEST SEARCH FUNCTIONALITY")
    print("=" * 60)
    
    guest_service = get_guest_service()
    admin_service = get_admin_service()
    
    # Check if there are faces in the database
    stats = admin_service.get_database_stats()
    if stats['total_faces'] == 0:
        print("\n   ⚠️  No faces in database. Please import photos first.")
        return
    
    print(f"\n   Database contains {stats['total_faces']} faces from {stats['total_photos']} photos")
    
    # Check if there are any selfies to test with
    selfie_dir = config.SELFIE_DIR
    selfie_files = [f for f in selfie_dir.iterdir() if f.is_file() and f.suffix.lower() in config.ALLOWED_EXTENSIONS]
    
    if not selfie_files:
        print("\n   ⚠️  No selfies found for testing")
        print(f"   Selfie directory: {selfie_dir}")
        print("   Please add a test selfie to this directory")
        return
    
    print(f"\n   Found {len(selfie_files)} test selfies")
    print(f"   Testing with: {selfie_files[0].name}")
    
    # Read selfie bytes
    with open(selfie_files[0], 'rb') as f:
        selfie_bytes = f.read()
    
    # Perform search
    print("\n   Searching for matches...")
    result = await guest_service.search_photos_by_selfie(
        selfie_bytes=selfie_bytes,
        filename=selfie_files[0].name,
        top_k=10
    )
    
    print("\n   Search result:")
    print(f"   - Success: {result.get('success')}")
    
    if result.get('success'):
        matches = result.get('matches', [])
        print(f"   - Matches found: {len(matches)}")
        
        if matches:
            print("\n   Top matches:")
            for i, match in enumerate(matches[:5], 1):
                print(f"   {i}. {match.get('photo_path')} (similarity: {match.get('similarity', 0):.3f})")
    else:
        print(f"   - Error: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)

async def main():
    """Run all tests."""
    print("\n🔍 PixelMatch Backend Test Suite\n")
    
    # Test 1: Manual photo processing
    await test_manual_upload()
    
    # Test 2: Google Drive import
    await test_drive_import()
    
    # Test 3: Guest search
    await test_guest_search()
    
    print("\n✅ All tests complete!\n")

if __name__ == "__main__":
    asyncio.run(main())
