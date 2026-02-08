
"""
Drive Service.
Handles downloading folders from Google Drive and triggering processing.
"""
import uuid
import shutil
import gdown
from pathlib import Path
from typing import Dict
import config
from services.admin_service import get_admin_service

# Global processing status
# {task_id: {"status": "downloading"|"processing"|"completed"|"failed", "progress": "0/0", "details": ...}}
tasks = {}

class DriveService:

    def __init__(self):
        self.download_dir = config.BASE_DIR / "temp_drive_downloads"
        self.download_dir.mkdir(exist_ok=True)
        # We don't bind admin_service here anymore, we get it per task

    async def process_drive_link(self, url: str, task_id: str, room_id: str = None):
        """
        Background task: Download -> Move -> Process.
        Handles both individual files and folders.
        """
        # Resolve dependencies based on room_id
        admin_service = get_admin_service(room_id)
        if room_id:
             from services.room_service import get_room_service
             room_path = get_room_service().get_room_path(room_id)
             target_upload_dir = room_path / "uploads"
        else:
             target_upload_dir = config.UPLOAD_DIR
             
        tasks[task_id] = {"status": "downloading", "progress": "0%", "message": "Downloading from Drive..."}
        
        task_dir = self.download_dir / task_id
        task_dir.mkdir(exist_ok=True)
        
        try:
            # Determine if URL is a file or folder
            is_folder = 'folders' in url or '/drive/folders/' in url
            
            if is_folder:
                # 1a. Download Folder
                print(f"[DRIVE] Downloading Drive folder: {url}")
                # gdown.download_folder returns list of files
                # Use fuzzy=True to handle permission issues better
                # Use remaining_ok=True to continue even if some files fail
                try:
                    files = gdown.download_folder(
                        url, 
                        output=str(task_dir), 
                        quiet=False,  # Show progress for debugging
                        use_cookies=False,
                        remaining_ok=True  # Continue even if some files fail
                    )
                except Exception as e:
                    print(f"[DRIVE] ERROR during folder download: {str(e)}")
                    # Try to salvage any files that were downloaded
                    files = []
                    if task_dir.exists():
                        files = [str(f) for f in task_dir.rglob('*') if f.is_file()]
                    
                    if not files:
                        tasks[task_id] = {
                            "status": "failed", 
                            "error": f"Failed to download folder. Error: {str(e)}. Make sure folder is shared as 'Anyone with the link'."
                        }
                        return
                
                if not files:
                    print(f"[DRIVE] ERROR: No files found or download failed")
                    tasks[task_id] = {"status": "failed", "error": "No files found or download failed. Make sure the folder is shared as 'Anyone with the link'."}
                    return
                
                print(f"[DRIVE] Downloaded {len(files)} files successfully")
            else:
                # 1b. Download Single File
                print(f"[DRIVE] Downloading single file from Drive: {url}")
                
                # Extract file ID from various URL formats
                file_id = None
                if '/file/d/' in url:
                    file_id = url.split('/file/d/')[1].split('/')[0]
                elif 'id=' in url:
                    file_id = url.split('id=')[1].split('&')[0]
                elif '/uc?id=' in url:
                    file_id = url.split('id=')[1].split('&')[0]
                
                if not file_id:
                    tasks[task_id] = {"status": "failed", "error": "Invalid Google Drive URL. Please use a valid file or folder link."}
                    return
                
                # Download the file
                output_path = task_dir / "downloaded_file"
                try:
                    gdown.download(id=file_id, output=str(output_path), quiet=False)
                    files = [str(output_path)]
                    print(f"[DRIVE] Downloaded file successfully")
                except Exception as e:
                    print(f"[DRIVE] ERROR: Failed to download file: {str(e)}")
                    tasks[task_id] = {"status": "failed", "error": f"Failed to download file. Make sure the file is shared as 'Anyone with the link'. Error: {str(e)}"}
                    return
            
            tasks[task_id]["status"] = "processing"
            tasks[task_id]["message"] = f"Downloaded {len(files)} file(s). Processing AI..."
            
            # 2. Move files to main Uploads dir
            # Let's move valid images to target_upload_dir to keep them permanent
            valid_images = []
            for f in files:
                path = Path(f)
                if config.is_allowed_file(path.name):
                    # Move to uploads
                    target = target_upload_dir / path.name
                    # Avoid overwrite collision
                    if target.exists():
                        target = target_upload_dir / f"{uuid.uuid4().hex[:6]}_{path.name}"
                    
                    try:
                        shutil.move(str(path), str(target))
                        valid_images.append(target)
                        print(f"[DRIVE] Moved {path.name} -> {target.name}")
                    except Exception as move_err:
                        print(f"[DRIVE] ERROR moving file {path.name}: {move_err}")

            
            # Cleanup temp
            if task_dir.exists():
                shutil.rmtree(task_dir)
            
            if not valid_images:
                print(f"[DRIVE] ERROR: No valid images found")
                tasks[task_id] = {"status": "failed", "error": "No valid images found. Supported formats: JPG, PNG, BMP, WEBP"}
                return
            
            print(f"[DRIVE] Starting face recognition processing for {len(valid_images)} images")
            
            # 3. Process Photos
            tasks[task_id]["total"] = len(valid_images)
            tasks[task_id]["processed"] = 0
            
            # We call process_local_files. But process_local_files is all-at-once.
            # To show progress, we might want to chunk it or update status inside?
            # For simplicity, let's call the batch function, and update status at end.
            # Or better: Iterate here and reuse logic?
            # But process_local_files calls _process_image_file.
            
            processed_count = 0
            stats = {
                'successful': 0, 
                'failed': 0, 
                'total_faces': 0
            }
            
            for img_path in valid_images:
                tasks[task_id]["message"] = f"Processing {img_path.name}..."
                tasks[task_id]["progress"] = f"{processed_count}/{len(valid_images)}"
                
                print(f"[DRIVE] Processing image {processed_count + 1}/{len(valid_images)}: {img_path.name}")
                
                try:
                    result = await admin_service._process_image_file(img_path)
                    
                    if result['success']:
                        stats['successful'] += 1
                        stats['total_faces'] += result['faces_detected']
                        print(f"[DRIVE] ✓ {img_path.name}: {result['faces_detected']} faces detected, {result.get('faces_stored', 0)} stored")
                    else:
                        stats['failed'] += 1
                        print(f"[DRIVE] ✗ {img_path.name}: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    stats['failed'] += 1
                    print(f"[DRIVE] ✗ {img_path.name}: Exception - {str(e)}")
                
                processed_count += 1
                tasks[task_id]["processed"] = processed_count
            
            tasks[task_id] = {
                "status": "completed",
                "progress": "100%",
                "stats": stats
            }
            
        except Exception as e:
            print(f"Drive processing failed: {e}")
            tasks[task_id] = {"status": "failed", "error": str(e)}
            # Cleanup
            if task_dir.exists():
                shutil.rmtree(task_dir)

_drive_service = None
def get_drive_service():
    global _drive_service
    if _drive_service is None:
        _drive_service = DriveService()
    return _drive_service
