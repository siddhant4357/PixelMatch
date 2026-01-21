
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
        self.admin_service = get_admin_service()

    async def process_drive_link(self, url: str, task_id: str):
        """
        Background task: Download -> Move -> Process.
        """
        tasks[task_id] = {"status": "downloading", "progress": "0%", "message": "Downloading from Drive..."}
        
        task_dir = self.download_dir / task_id
        task_dir.mkdir(exist_ok=True)
        
        try:
            # 1. Download Folder
            print(f"[DRIVE] Downloading Drive folder: {url}")
            # gdown.download_folder returns list of files
            # Set quiet=True to suppress per-file download messages
            files = gdown.download_folder(url, output=str(task_dir), quiet=True, use_cookies=False)
            
            if not files:
                 print(f"[DRIVE] ERROR: No files found or download failed")
                 tasks[task_id] = {"status": "failed", "error": "No files found or download failed (Check if link is Public)."}
                 return

            print(f"[DRIVE] Downloaded {len(files)} files successfully")
            tasks[task_id]["status"] = "processing"
            tasks[task_id]["message"] = f"Downloaded {len(files)} files. Processing AI..."
            
            # 2. Move files to main Uploads dir? 
            # Or just process them from temp and move valid ones?
            # Let's move valid images to config.UPLOAD_DIR to keep them permanent
            valid_images = []
            for f in files:
                path = Path(f)
                if config.is_allowed_file(path.name):
                    # Move to uploads
                    target = config.UPLOAD_DIR / path.name
                    # Avoid overwrite collision
                    if target.exists():
                        target = config.UPLOAD_DIR / f"{uuid.uuid4().hex[:6]}_{path.name}"
                    
                    shutil.move(str(path), str(target))
                    valid_images.append(target)
                    print(f"[DRIVE] Moved {path.name} -> {target.name}")
            
            # Cleanup temp
            shutil.rmtree(task_dir)
            
            if not valid_images:
                print(f"[DRIVE] ERROR: No valid images found in folder")
                tasks[task_id] = {"status": "failed", "error": "No valid images found in folder."}
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
                    result = await self.admin_service._process_image_file(img_path)
                    
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
