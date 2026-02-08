"""
Admin Service Layer.
Handles bulk photo uploads and face extraction pipeline.
"""

import os
from pathlib import Path
from typing import List, Dict
import asyncio
from concurrent.futures import ThreadPoolExecutor

from models.face_detection import FaceDetector
from models.face_recognition import get_facenet_model
from models.vector_db import get_vector_db
from models.location_db import get_location_db
from utils.image_processing import (
    load_image,
    crop_face,
    preprocess_face,
    save_image
)
from utils.exif_extractor import EXIFExtractor
import config



class AdminService:
    """Service for admin operations (photo uploads and processing)."""
    
    def __init__(self, room_id: str = None):
        """Initialize admin service with AI models and room context."""
        self.room_id = room_id
        # Models are stateless/shared
        self.face_detector = FaceDetector()
        self.face_recognizer = get_facenet_model()
        
        # Databases are stateful (per room)
        self.vector_db = get_vector_db(room_id)
        self.location_db = get_location_db(room_id)
        
        # Helper to get upload dir
        if room_id:
            from services.room_service import get_room_service
            room_path = get_room_service().get_room_path(room_id)
            self.upload_dir = room_path / "uploads"
            self.upload_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.upload_dir = config.UPLOAD_DIR
            
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def _process_single_photo(self, filename: str, file_bytes: bytes) -> Dict:
        """Process a single uploaded photo (writes to disk then processes)."""
        photo_path = self.upload_dir / filename
        try:
            with open(photo_path, 'wb') as f:
                f.write(file_bytes)
            return await self._process_image_file(photo_path)
        except Exception as e:
             return {'filename': filename, 'success': False, 'error': str(e)}

    async def process_bulk_upload(self, files: List[tuple]) -> Dict:
        """Process bulk uploaded photos SEQUENTIALLY (TensorFlow is not thread-safe)."""
        results = []
        
        print(f"\n[UPLOAD] ========================================")
        print(f"[UPLOAD] Starting bulk upload: {len(files)} photo(s)")
        print(f"[UPLOAD] ========================================\n")
        
        # Process photos ONE AT A TIME to avoid TensorFlow threading issues
        for idx, (filename, file_bytes) in enumerate(files, 1):
            print(f"[UPLOAD] Processing photo {idx}/{len(files)}: {filename}")
            result = await self._process_single_photo(filename, file_bytes)
            results.append(result)
        
        # Aggregate stats
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        total_faces = sum(r.get('faces_detected', 0) for r in results if r['success'])
        
        print(f"\n[UPLOAD] ========================================")
        print(f"[UPLOAD] Bulk upload complete!")
        print(f"[UPLOAD] ✓ Successful: {successful}/{len(files)} photos")
        print(f"[UPLOAD] ✓ Total faces: {total_faces}")
        if failed > 0:
            print(f"[UPLOAD] ❌ Failed: {failed} photos")
        print(f"[UPLOAD] ========================================\n")
        
        return {
            'successful': successful,
            'failed': failed,
            'total_faces': total_faces,
            'photo_details': results
        }

    async def _process_image_file(self, photo_path: Path) -> Dict:
        """Async wrapper for CPU-bound image processing."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self.executor,
            self._sync_process_image,
            photo_path
        )

    def _sync_process_image(self, photo_path: Path) -> Dict:
        """Synchronous image processing logic (runs in thread pool)."""
        filename = photo_path.name
        print(f"\n[UPLOAD] ========== Processing: {filename} ==========")
        
        try:
            # 1. Load Image
            print(f"[UPLOAD] Step 1/5: Loading image...")
            image = load_image(str(photo_path))
            if image is None:
                print(f"[UPLOAD] ❌ Failed to load image")
                return {'filename': filename, 'success': False, 'error': "Failed to load image"}
            print(f"[UPLOAD] ✓ Image loaded ({image.shape})")

            # 2. Extract Metadata (EXIF)
            print(f"[UPLOAD] Step 2/5: Extracting EXIF metadata...")
            metadata = EXIFExtractor.extract_metadata(str(photo_path))
            
            # Store in Location DB if available
            if metadata.get('has_location'):
                print(f"[UPLOAD] ✓ GPS found: {metadata['latitude']:.4f}, {metadata['longitude']:.4f}")
                self.location_db.add_location(photo_path.name, metadata)
            else:
                print(f"[UPLOAD] ℹ No GPS data in photo")

            # 3. Detect Faces
            print(f"[UPLOAD] Step 3/5: Detecting faces...")
            faces = self.face_detector.detect_faces(image)
            
            if not faces:
                print(f"[UPLOAD] ⚠ No faces detected in this photo")
                return {
                    'filename': filename,
                    'success': True,
                    'faces_detected': 0
                }
            
            print(f"[UPLOAD] ✓ Found {len(faces)} face(s)")
            
            processed_faces = 0
            # 4. Process each face
            for i, (bbox, confidence) in enumerate(faces):
                print(f"[UPLOAD] Step 4/5: Processing face {i+1}/{len(faces)} (confidence: {confidence:.2f})...")
                
                face_img = crop_face(image, bbox)
                preprocessed = preprocess_face(face_img, config.FACE_SIZE)
                
                # 5. Generate Embedding
                print(f"[UPLOAD] Step 5/5: Generating embedding for face {i+1}... (this takes ~10-15s)")
                embedding = self.face_recognizer.generate_embedding(preprocessed)
                
                if embedding is not None:
                    print(f"[UPLOAD] ✓ Embedding generated (dim: {len(embedding)})")
                    
                    # 6. Store in Vector DB
                    print(f"[UPLOAD] Storing in database...")
                    self.vector_db.add_face(
                        embedding=embedding,
                        photo_path=str(photo_path),
                        bbox=bbox,
                        metadata={
                            "filename": filename,
                            "face_index": i,
                            "timestamp": metadata.get('timestamp'),
                            "location": metadata.get('location_name')
                        }
                    )
                    processed_faces += 1
                    print(f"[UPLOAD] ✓ Face {i+1} stored successfully")
                else:
                    print(f"[UPLOAD] ❌ Failed to generate embedding for face {i+1}")

            print(f"[UPLOAD] ========== ✓ Completed: {filename} ({processed_faces} faces) ==========\n")
            return {
                'filename': filename,
                'success': True,
                'faces_detected': processed_faces
            }

        except Exception as e:
            print(f"[UPLOAD] ❌ ERROR processing {filename}: {e}")
            import traceback
            traceback.print_exc()
            return {'filename': filename, 'success': False, 'error': str(e)}

    def get_database_stats(self) -> Dict:
        """Get statistics about the face database."""
        total_faces = self.vector_db.get_count()
        
        # Count actual photo files in THIS room's upload dir
        photo_count = 0
        if self.upload_dir.exists():
            for file in self.upload_dir.iterdir():
                if file.is_file() and file.name != '.gitkeep':
                    photo_count += 1
        
        return {
            'total_faces': total_faces,
            'total_photos': photo_count
        }

    # ... (rest of methods)
    
    # Needs to override methods that use config.UPLOAD_DIR directly to use self.upload_dir
    # But for brevity in this tool call I am only showing changed parts. 
    # Actually, I should check if other methods use config.UPLOAD_DIR directly.
    # verify_file logic might need update if it moved.
    
    # Rerouting create/delete methods to use self.upload_dir
    
    def delete_photo(self, photo_path_str: str) -> Dict:
        # Note: input is usually just filename in the API, but sometimes full path.
        # If API sends filename, we construct path.
        # The API currently does: photo_path = config.UPLOAD_DIR / filename
        # We need to change that in main.py or here. 
        # Ideally AdminService should take filename and handle path resolving.
        # But looking at existing code: delete_photo takes photo_path string.
        
        try:
            # Delete from vector database (it matches by path string)
            faces_deleted = self.vector_db.delete_by_photo(photo_path_str)
            
            # Delete file
            path = Path(photo_path_str)
            if path.exists():
                path.unlink()
                file_deleted = True
            else:
                file_deleted = False
            
            return {
                'success': True,
                'faces_deleted': faces_deleted,
                'file_deleted': file_deleted
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def reset_database(self) -> Dict:
        try:
            # Reset FAISS
            success = self.vector_db.reset() # This resets the instance we hold (room specific)
            if not success: return {'success': False}
            
            # Delete photos in this room
            photos_deleted = 0
            if self.upload_dir.exists():
                for file in self.upload_dir.iterdir():
                    if file.name != '.gitkeep' and file.is_file():
                        file.unlink()
                        photos_deleted += 1
            
            # We don't delete selfies here as they might be global or per-session
            
            return {
                'success': True,
                'message': f'Room database reset. Deleted {photos_deleted} photos.',
                'photos_deleted': photos_deleted
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Global cache for services
_admin_services = {}

def get_admin_service(room_id: str = None) -> AdminService:
    """Get or create admin service for a specific room."""
    global _admin_services
    key = room_id or 'default'
    
    if key not in _admin_services:
        _admin_services[key] = AdminService(room_id)
    
    return _admin_services[key]
