"""
Guest Service Layer.
Handles selfie uploads and photo matching.
"""

from pathlib import Path
from typing import List, Dict, Optional
import uuid

from models.face_detection import FaceDetector
from models.face_recognition import get_facenet_model
from models.vector_db import get_vector_db
from utils.image_processing import (
    load_image_from_bytes,
    crop_face,
    preprocess_face,
    save_image
)
import config


class GuestService:
    """Service for guest operations (selfie upload and photo search)."""
    
    def __init__(self):
        """Initialize guest service with AI models."""
        self.face_detector = FaceDetector()
        self.face_recognizer = get_facenet_model()
        self.vector_db = get_vector_db()
    
    async def search_photos_by_selfie(
        self,
        selfie_bytes: bytes,
        filename: str = "selfie.jpg",
        top_k: int = None,
        similarity_threshold: float = None
    ) -> Dict:
        """
        Search for photos containing the person in the selfie.
        
        Args:
            selfie_bytes: Selfie image bytes
            filename: Original filename (optional)
            top_k: Maximum number of results (default: config.MAX_RESULTS)
            similarity_threshold: Minimum similarity score (default: config.SIMILARITY_THRESHOLD)
            
        Returns:
            Dict containing:
                - success: Whether search was successful
                - matches: List of matched photos with details
                - total_matches: Number of unique photos found
                - error: Error message if failed
        """
        # Save selfie
        selfie_id = str(uuid.uuid4())
        selfie_path = config.SELFIE_DIR / f"{selfie_id}_{filename}"
        
        try:
            with open(selfie_path, 'wb') as f:
                f.write(selfie_bytes)
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to save selfie: {e}'
            }
        
        # Load image
        image = load_image_from_bytes(selfie_bytes)
        
        if image is None:
            return {
                'success': False,
                'error': 'Failed to load selfie image'
            }
        
        # Detect face in selfie
        print(f"[GUEST] Detecting face in selfie: {filename}")
        face_result = self.face_detector.detect_single_face(image)
        
        if face_result is None:
            print(f"[GUEST] ERROR: No face detected in selfie")
            return {
                'success': False,
                'error': 'No face detected in selfie. Please upload a clear photo of your face.'
            }
        
        bbox, confidence = face_result
        print(f"[GUEST] Face detected with confidence: {confidence:.2f}")
        
        # Crop and preprocess face
        face_img = crop_face(image, bbox)
        
        if face_img is None:
            return {
                'success': False,
                'error': 'Failed to extract face from selfie'
            }
        
        preprocessed = preprocess_face(face_img, config.FACE_SIZE)
        
        # Generate embedding with TTA enabled for maximum accuracy
        # TTA (Test Time Augmentation) improves matching by ~15-20%
        print(f"[GUEST] Generating embedding for selfie (TTA enabled for accuracy)")
        embedding = self.face_recognizer.generate_embedding(preprocessed, enable_tta=True)
        
        if embedding is None:
            print(f"[GUEST] ERROR: Failed to generate embedding")
            return {
                'success': False,
                'error': 'Failed to generate face embedding'
            }
        
        print(f"[GUEST] Embedding generated successfully (dim: {len(embedding)})")
        
        # Multi-Stage Search for better recall
        # Stage 1: High confidence matches (strict threshold)
        # Stage 2: If few results, lower threshold to find difficult photos
        
        max_results = top_k or config.MAX_RESULTS
        primary_threshold = similarity_threshold or config.SIMILARITY_THRESHOLD
        
        print(f"[GUEST] Starting Multi-Stage Search")
        print(f"[GUEST] Database contains {self.vector_db.get_count()} total embeddings")
        
        # Stage 1: High confidence search
        print(f"[GUEST] Stage 1: Searching with threshold {primary_threshold:.2f} (high confidence)")
        matches_stage1 = self.vector_db.search_similar_faces(
            query_embedding=embedding,
            top_k=max_results,
            similarity_threshold=primary_threshold
        )
        
        print(f"[GUEST] Stage 1: Found {len(matches_stage1)} high-confidence matches")
        
        # Stage 2: Smart Expand (Recursive Search)
        
        all_matches = matches_stage1.copy()
        
        if matches_stage1:
            print(f"[GUEST] Stage 2: Smart Expand - Using top matches to find related photos...")
            
            # Smart Expand Strategy:
            # If we found at least one photo, we trust the person is present at the event.
            # We can aggressively lower the threshold for "related" searches.
            
            secondary_threshold = max(0.42, primary_threshold - 0.10) 
            
            if len(matches_stage1) < 8:
                 print(f"[GUEST] Smart Expand: detailed broad search at {secondary_threshold:.2f}")
                 matches_stage2 = self.vector_db.search_similar_faces(
                    query_embedding=embedding,
                    top_k=max_results,
                    similarity_threshold=secondary_threshold
                )
                
                 existing_ids = {m['id'] for m in all_matches}
                 new_matches = [m for m in matches_stage2 if m['id'] not in existing_ids]
                 
                 for m in new_matches:
                     m['is_expanded'] = True
                     
                 all_matches.extend(new_matches)
                 print(f"[GUEST] Smart Expand: Found {len(new_matches)} additional photos")
            
        else:
             # Fallback: excessive aggressive search if NO matches found initially
             # User said "solo photos not identified" -> they need a lower floor
             fallback_threshold = 0.30  # Deep dive to 30% as requested
             print(f"[GUEST] Stage 2: Deep Fallback search at {fallback_threshold:.2f}")
             
             matches_fallback = self.vector_db.search_similar_faces(
                query_embedding=embedding,
                top_k=max_results,
                similarity_threshold=fallback_threshold
            )
             all_matches.extend(matches_fallback)
             print(f"[GUEST] Fallback: Found {len(matches_fallback)} photos")
        
        # Sort all matches by similarity
        all_matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        print(f"[GUEST] Total matches found: {len(all_matches)}")
        if all_matches:
            print(f"[GUEST] Top match similarity: {all_matches[0]['similarity']:.4f}")
            print(f"[GUEST] Lowest match similarity: {all_matches[-1]['similarity']:.4f}")
        
        if not all_matches:
            return {
                'success': True,
                'matches': [],
                'total_matches': 0,
                'message': 'No matching photos found. You may not be in the uploaded photos.'
            }
        
        # Group matches by photo (for privacy mode and deduplication)
        if config.ENABLE_PRIVACY_MODE:
            photo_matches = self._group_matches_by_photo(all_matches)
        else:
            photo_matches = self._group_matches_by_photo(all_matches)
        
        print(f"[GUEST] Grouped into {len(photo_matches)} unique photos")
        for i, photo in enumerate(photo_matches[:3]):  # Show top 3
            print(f"[GUEST]   #{i+1}: {photo['photo_name']} (similarity: {photo['max_similarity']:.4f}, faces: {photo['face_count']})")
        
        return {
            'success': True,
            'matches': photo_matches,
            'total_matches': len(photo_matches),
            'selfie_path': str(selfie_path)
        }
    
    def _group_matches_by_photo(self, matches: List[Dict]) -> List[Dict]:
        """
        Group face matches by photo and aggregate information.
        
        Args:
            matches: List of face matches from vector database
            
        Returns:
            List of photo-level matches with aggregated data
        """
        photo_dict = {}
        
        for match in matches:
            photo_path = match['photo_path']
            
            if photo_path not in photo_dict:
                photo_dict[photo_path] = {
                    'photo_path': photo_path,
                    'photo_name': Path(photo_path).name,
                    'faces_found': [],
                    'max_similarity': 0.0,
                    'avg_similarity': 0.0
                }
            
            # Add face info
            photo_dict[photo_path]['faces_found'].append({
                'bbox': match['bbox'],
                'similarity': match['similarity']
            })
            
            # Update max similarity
            if match['similarity'] > photo_dict[photo_path]['max_similarity']:
                photo_dict[photo_path]['max_similarity'] = match['similarity']
        
        # Calculate average similarities and convert to list
        photo_matches = []
        for photo_data in photo_dict.values():
            similarities = [face['similarity'] for face in photo_data['faces_found']]
            photo_data['avg_similarity'] = sum(similarities) / len(similarities)
            photo_data['face_count'] = len(photo_data['faces_found'])
            photo_matches.append(photo_data)
        
        # Sort by max similarity (best matches first)
        photo_matches.sort(key=lambda x: x['max_similarity'], reverse=True)
        
        return photo_matches
    
    def get_photo_file(self, photo_path: str) -> Optional[bytes]:
        """
        Get photo file bytes for download.
        
        Args:
            photo_path: Path to photo
            
        Returns:
            Photo file bytes, or None if not found
        """
        try:
            path = Path(photo_path)
            
            if not path.exists():
                return None
            
            with open(path, 'rb') as f:
                return f.read()
                
        except Exception as e:
            print(f"Error reading photo {photo_path}: {e}")
            return None
    
    def validate_selfie(self, selfie_bytes: bytes) -> Dict:
        """
        Validate a selfie before processing (quick check).
        
        Args:
            selfie_bytes: Selfie image bytes
            
        Returns:
            Dict with validation result
        """
        # Load image
        image = load_image_from_bytes(selfie_bytes)
        
        if image is None:
            return {
                'valid': False,
                'error': 'Invalid image file'
            }
        
        # Check if face is detected
        face_result = self.face_detector.detect_single_face(image)
        
        if face_result is None:
            return {
                'valid': False,
                'error': 'No face detected. Please upload a clear selfie.'
            }
        
        bbox, confidence = face_result
        
        return {
            'valid': True,
            'confidence': confidence,
            'message': 'Selfie validated successfully'
        }


# Global service instance
_guest_service = None


def get_guest_service() -> GuestService:
    """Get or create global guest service instance."""
    global _guest_service
    
    if _guest_service is None:
        _guest_service = GuestService()
    
    return _guest_service
