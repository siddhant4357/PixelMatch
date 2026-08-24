"""
Guest Service Layer.
Handles selfie uploads and photo matching.
"""

from pathlib import Path
from typing import List, Dict, Optional
import uuid
import gc

from models.face_detection import FaceDetector, get_insightface_app
from models.vector_db import get_vector_db
from utils.image_processing import (
    load_image_from_bytes,
    crop_face,
    save_image
)
import numpy as np
import config


class GuestService:
    """Service for guest operations (selfie upload and photo search)."""
    
    def __init__(self, room_id: str = None):
        """Initialize guest service with room context.
        
        Note: FaceDetector is NOT stored as instance variable to save memory.
        It is retrieved via the global singleton when needed.
        """
        self.room_id = room_id
        # Only store vector_db — do NOT store FaceDetector/FaceNet as instance vars
        self.vector_db = get_vector_db(room_id)
        
        if room_id:
            from services.room_service import get_room_service
            room_path = get_room_service().get_room_path(room_id)
            self.selfie_dir = room_path / "selfies"
            self.selfie_dir.mkdir(exist_ok=True)
        else:
            self.selfie_dir = config.SELFIE_DIR

    async def search_photos_by_embedding(
        self,
        embedding: np.ndarray,
        top_k: int = None,
        similarity_threshold: float = None
    ) -> Dict:
        """Search photos using a pre-computed embedding from the database."""
        if top_k is None:
            top_k = getattr(config, 'MAX_RESULTS', 100)
            
        print(f"[GUEST] Searching DB with stored embedding in room {self.room_id}")
        
        matches = self.vector_db.search_similar_faces(
            query_embedding=embedding,
            top_k=top_k,
            similarity_threshold=similarity_threshold
        )
        
        results = []
        for match in matches:
            results.append({
                "photo_name": match.get("filename"),
                "similarity": match.get("similarity"),
                "face_index": match.get("face_index"),
                "bbox": match.get("bbox")
            })
            
        return {
            "success": True,
            "total_matches": len(results),
            "matches": results,
            "room_id": self.room_id
        }
    
    async def search_photos_by_selfie(
        self,
        selfie_bytes: bytes,
        filename: str = "selfie.jpg",
        top_k: int = None,
        similarity_threshold: float = None
    ) -> Dict:
        """
        Search for photos containing the person in the selfie.
        Uses InsightFace embedding directly (no extra FaceNet model needed).
        """
        image = load_image_from_bytes(selfie_bytes)
        
        if image is None:
            return {'success': False, 'error': 'Failed to load selfie image'}
        
        # Detect face using the global singleton detector (memory-safe)
        print(f"[GUEST] Detecting face in selfie: {filename}")
        detector = FaceDetector()
        faces = detector.detect_faces(image)
        
        if not faces:
            del image, selfie_bytes, faces
            gc.collect()
            return {
                'success': False,
                'error': 'No face detected in selfie. Please upload a clear photo of your face.'
            }
        
        face = faces[0]
        bbox, confidence, landmarks, embedding = face
        print(f"[GUEST] Face detected with confidence: {confidence:.2f}")
        
        if embedding is None:
            del image, selfie_bytes, faces
            gc.collect()
            return {'success': False, 'error': 'Failed to generate face embedding'}
        
        # Free image memory now that we have the embedding
        del image, selfie_bytes, faces
        gc.collect()
        
        print(f"[GUEST] Embedding generated successfully (dim: {len(embedding)})")
        
        max_results = top_k or config.MAX_RESULTS
        primary_threshold = similarity_threshold or config.SIMILARITY_THRESHOLD
        
        print(f"[GUEST] Starting search — threshold: {primary_threshold:.2f}")
        print(f"[GUEST] Database contains {self.vector_db.get_count()} total embeddings")
        
        # Stage 1: High confidence
        matches_stage1 = self.vector_db.search_similar_faces(
            query_embedding=embedding,
            top_k=max_results,
            similarity_threshold=primary_threshold
        )
        print(f"[GUEST] Stage 1: Found {len(matches_stage1)} high-confidence matches")
        
        all_matches = matches_stage1.copy()
        
        if matches_stage1:
            secondary_threshold = max(0.42, primary_threshold - 0.10) 
            if len(matches_stage1) < 8:
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
                print(f"[GUEST] Stage 2: Found {len(new_matches)} additional photos")
        else:
            fallback_threshold = 0.30
            print(f"[GUEST] Fallback search at {fallback_threshold:.2f}")
            matches_fallback = self.vector_db.search_similar_faces(
                query_embedding=embedding,
                top_k=max_results,
                similarity_threshold=fallback_threshold
            )
            all_matches.extend(matches_fallback)
        
        all_matches.sort(key=lambda x: x['similarity'], reverse=True)
        print(f"[GUEST] Total matches found: {len(all_matches)}")
        
        if not all_matches:
            return {
                'success': True,
                'matches': [],
                'total_matches': 0,
                'message': 'No matching photos found. You may not be in the uploaded photos.'
            }
        
        photo_matches = self._group_matches_by_photo(all_matches)
        print(f"[GUEST] Grouped into {len(photo_matches)} unique photos")
        
        return {
            'success': True,
            'matches': photo_matches,
            'total_matches': len(photo_matches),
        }
    
    def _group_matches_by_photo(self, matches: List[Dict]) -> List[Dict]:
        """Group face matches by photo and aggregate information."""
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
            
            photo_dict[photo_path]['faces_found'].append({
                'bbox': match['bbox'],
                'similarity': match['similarity']
            })
            
            if match['similarity'] > photo_dict[photo_path]['max_similarity']:
                photo_dict[photo_path]['max_similarity'] = match['similarity']
        
        photo_matches = []
        for photo_data in photo_dict.values():
            similarities = [face['similarity'] for face in photo_data['faces_found']]
            photo_data['avg_similarity'] = sum(similarities) / len(similarities)
            photo_data['face_count'] = len(photo_data['faces_found'])
            photo_matches.append(photo_data)
        
        photo_matches.sort(key=lambda x: x['max_similarity'], reverse=True)
        return photo_matches
    

# --- Singleton cache (per room) ---
# Note: We limit the cache size to avoid unbounded memory growth.
_guest_services: Dict[str, GuestService] = {}
_MAX_CACHED_ROOMS = 5  # Only keep the 5 most recently accessed rooms


def get_guest_service(room_id: str = None) -> GuestService:
    """Get or create guest service instance for a specific room.
    
    Limits cache to _MAX_CACHED_ROOMS entries to prevent memory leaks
    on free-tier servers.
    """
    global _guest_services
    
    key = room_id or 'default'
    if key not in _guest_services:
        # Evict oldest entry if cache is full
        if len(_guest_services) >= _MAX_CACHED_ROOMS:
            oldest_key = next(iter(_guest_services))
            del _guest_services[oldest_key]
            gc.collect()
        _guest_services[key] = GuestService(room_id)
    
    return _guest_services[key]
