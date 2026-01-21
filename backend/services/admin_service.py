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
from utils.image_processing import (
    load_image,
    crop_face,
    preprocess_face,
    save_image
)
import config


class AdminService:
    """Service for admin operations (photo uploads and processing)."""
    
    def __init__(self):
        """Initialize admin service with AI models."""
        self.face_detector = FaceDetector()
        self.face_recognizer = get_facenet_model()
        self.vector_db = get_vector_db()
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def process_bulk_upload(
        self,
        photo_files: List[tuple]  # List of (filename, file_bytes) tuples
    ) -> Dict:
        """
        Process bulk photo upload from admin.
        
        Args:
            photo_files: List of tuples containing (filename, file_bytes)
            
        Returns:
            Dict with processing statistics:
                - total_photos: Number of photos uploaded
                - total_faces: Total faces detected
                - successful: Number of successfully processed photos
                - failed: Number of failed photos
                - photo_details: List of details for each photo
        """
        stats = {
            'total_photos': len(photo_files),
            'total_faces': 0,
            'successful': 0,
            'failed': 0,
            'photo_details': []
        }
        
        # Process each photo
        for filename, file_bytes in photo_files:
            try:
                result = await self._process_single_photo(filename, file_bytes)
                
                if result['success']:
                    stats['successful'] += 1
                    stats['total_faces'] += result['faces_detected']
                else:
                    stats['failed'] += 1
                
                stats['photo_details'].append(result)
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                stats['failed'] += 1
                stats['photo_details'].append({
                    'filename': filename,
                    'success': False,
                    'error': str(e)
                })
        
        return stats
    
    async def process_local_files(self, file_paths: List[Path]) -> Dict:
        """
        Process a list of local files (already on disk).
        Used by DriveService after downloading.
        """
        stats = {
            'total_photos': len(file_paths),
            'total_faces': 0,
            'successful': 0,
            'failed': 0,
            'photo_details': []
        }
        
        for file_path in file_paths:
            try:
                # Use common processing logic (skipping save step)
                result = await self._process_image_file(file_path)
                
                if result['success']:
                    stats['successful'] += 1
                    stats['total_faces'] += result['faces_detected']
                else:
                    stats['failed'] += 1
                
                stats['photo_details'].append(result)
            except Exception as e:
                stats['failed'] += 1
                stats['photo_details'].append({
                    'filename': file_path.name,
                    'success': False,
                    'error': str(e)
                })
        
        return stats

    async def _process_image_file(self, photo_path: Path) -> Dict:
        """Core logic to process an image file given its path."""
        filename = photo_path.name
        
        print(f"[ADMIN] Processing: {filename}")
        
        # Load image
        from utils.image_processing import load_image
        image = load_image(str(photo_path))
        
        if image is None:
            print(f"[ADMIN] ERROR: Failed to load image {filename}")
            return {
                'filename': filename,
                'success': False,
                'error': 'Failed to load image'
            }
        
        print(f"[ADMIN] Image loaded successfully: {filename} (shape: {image.shape})")
        
        # Detect faces
        faces = self.face_detector.detect_faces(image)
        
        if not faces:
            print(f"[ADMIN] No faces detected in {filename}")
            return {
                'filename': filename,
                'success': True,
                'faces_detected': 0,
                'message': 'No faces detected in image',
                'photo_path': str(photo_path)
            }
        
        print(f"[ADMIN] Detected {len(faces)} face(s) in {filename}")
        
        # Process faces
        embeddings_data = []
        for i, (bbox, confidence) in enumerate(faces):
            face_img = crop_face(image, bbox)
            if face_img is None:
                print(f"[ADMIN] WARNING: Failed to crop face {i+1} in {filename}")
                continue
            
            preprocessed = preprocess_face(face_img, config.FACE_SIZE)
            
            # Enable TTA for better accuracy (worth the extra processing time)
            # TTA improves matching accuracy by 15-20%
            embedding = self.face_recognizer.generate_embedding(preprocessed, enable_tta=True)
            
            if embedding is not None:
                embeddings_data.append({
                    'embedding': embedding,
                    'bbox': bbox,
                    'confidence': confidence
                })
                print(f"[ADMIN] Generated embedding for face {i+1}/{len(faces)} in {filename} (confidence: {confidence:.2f})")
            else:
                print(f"[ADMIN] WARNING: Failed to generate embedding for face {i+1} in {filename}")
        
        # Store in DB
        face_ids = []
        if embeddings_data:
            print(f"[ADMIN] Storing {len(embeddings_data)} embedding(s) in vector database for {filename}")
            embeddings = [data['embedding'] for data in embeddings_data]
            bboxes = [data['bbox'] for data in embeddings_data]
            photo_paths = [str(photo_path)] * len(embeddings)
            metadata_list = [{'confidence': data['confidence']} for data in embeddings_data]
            
            try:
                face_ids = self.vector_db.add_faces_batch(
                    embeddings=embeddings,
                    photo_paths=photo_paths,
                    bboxes=bboxes,
                    metadata_list=metadata_list
                )
                print(f"[ADMIN] ✓ Successfully stored {len(face_ids)} face(s) for {filename}")
                print(f"[ADMIN] Vector DB now contains {self.vector_db.get_count()} total embeddings")
            except Exception as e:
                print(f"[ADMIN] ERROR: Failed to store embeddings in DB for {filename}: {str(e)}")
                return {
                    'filename': filename,
                    'success': False,
                    'error': f'Failed to store embeddings: {str(e)}'
                }
        
        return {
            'filename': filename,
            'success': True,
            'faces_detected': len(faces),
            'faces_stored': len(face_ids),
            'photo_path': str(photo_path)
        }

    async def _process_single_photo(self, filename: str, file_bytes: bytes) -> Dict:
        """Process a single uploaded photo (writes to disk then processes)."""
        photo_path = config.UPLOAD_DIR / filename
        try:
            with open(photo_path, 'wb') as f:
                f.write(file_bytes)
            return await self._process_image_file(photo_path)
        except Exception as e:
             return {'filename': filename, 'success': False, 'error': str(e)}
    
    def get_database_stats(self) -> Dict:
        """
        Get statistics about the face database.
        
        Returns:
            Dict with database statistics
        """
        total_faces = self.vector_db.get_count()
        
        # Count actual photo files (exclude .gitkeep)
        photo_count = 0
        if config.UPLOAD_DIR.exists():
            for file in config.UPLOAD_DIR.iterdir():
                if file.is_file() and file.name != '.gitkeep':
                    photo_count += 1
        
        return {
            'total_faces': total_faces,
            'total_photos': photo_count
        }
    
    def delete_photo(self, photo_path: str) -> Dict:
        """
        Delete a photo and all associated face embeddings.
        
        Args:
            photo_path: Path to photo to delete
            
        Returns:
            Dict with deletion result
        """
        try:
            # Delete from vector database
            faces_deleted = self.vector_db.delete_by_photo(photo_path)
            
            # Delete file
            path = Path(photo_path)
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
            return {
                'success': False,
                'error': str(e)
            }
    
    def reset_database(self) -> Dict:
        """
        Reset the entire database (delete all faces and photos).
        Use with caution!
        
        Returns:
            Dict with reset result
        """
        try:
            # Reset FAISS vector database
            success = self.vector_db.reset()
            
            if not success:
                return {
                    'success': False,
                    'error': 'Failed to reset FAISS database'
                }
            
            # Delete all uploaded photos
            photos_deleted = 0
            if config.UPLOAD_DIR.exists():
                for file in config.UPLOAD_DIR.iterdir():
                    if file.name != '.gitkeep' and file.is_file():
                        file.unlink()
                        photos_deleted += 1
            
            # Delete all selfies
            selfies_deleted = 0
            if config.SELFIE_DIR.exists():
                for file in config.SELFIE_DIR.iterdir():
                    if file.name != '.gitkeep' and file.is_file():
                        file.unlink()
                        selfies_deleted += 1
            
            return {
                'success': True,
                'message': f'Database reset successfully. Deleted {photos_deleted} photos, {selfies_deleted} selfies, and all face embeddings.',
                'photos_deleted': photos_deleted,
                'selfies_deleted': selfies_deleted
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Global service instance
_admin_service = None


def get_admin_service() -> AdminService:
    """Get or create global admin service instance."""
    global _admin_service
    
    if _admin_service is None:
        _admin_service = AdminService()
    
    return _admin_service
