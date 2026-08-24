"""
Face Recognition Module using InsightFace ArcFace.
Replaces the heavy DeepFace TensorFlow ensemble with a fast ONNX CPU model.
"""

import numpy as np
from typing import Optional, List, Any
import config
import cv2
import logging
from models.face_detection import get_insightface_app

logger = logging.getLogger(__name__)

class InsightFaceRecognizer:
    """
    Face Recognition using InsightFace.
    """
    
    def __init__(self):
        """Initialize model."""
        self.app = get_insightface_app()
        print("InsightFace Recognizer ready.")

    def generate_embedding(self, face_image: np.ndarray, enable_tta: bool = False) -> Optional[np.ndarray]:
        """
        Generate 512-dimensional embedding using InsightFace.
        Note: InsightFace usually expects the whole image and a detected face object.
        If we are passing a crop, it might be tricky. The best way is to pass the whole image
        to `app.get()`, which does detection + recognition. 
        But since our pipeline separates them (detect -> crop -> embed), we can use the model directly, 
        or better yet, change the pipeline to just pass the face object returned by detection.
        Let's support passing the whole image or a pre-detected face.
        Actually, `admin_service.py` currently crops the face and passes it here. 
        We should change `admin_service.py` to NOT crop, but we'll implement this function to handle both for now,
        or just expect the full image and bounding box.
        """
        # If passed a small crop, we can just run app.get() on it. It will detect the face in the crop and embed it.
        try:
            # Prepare image (InsightFace expects BGR)
            if face_image.max() <= 1.0:
                img_uint8 = (((face_image + 1) / 2) * 255).astype(np.uint8)
            else:
                img_uint8 = face_image.astype(np.uint8)
            
            if len(img_uint8.shape) == 2:
                bgr_image = cv2.cvtColor(img_uint8, cv2.COLOR_GRAY2BGR)
            elif img_uint8.shape[2] == 4:
                bgr_image = cv2.cvtColor(img_uint8, cv2.COLOR_RGBA2BGR)
            else:
                bgr_image = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2BGR)
                
            faces = self.app.get(bgr_image)
            
            if not faces:
                print("No face detected in crop during embedding generation.")
                return None
                
            # Get largest face in crop
            faces.sort(key=lambda face: (face.bbox[2]-face.bbox[0])*(face.bbox[3]-face.bbox[1]), reverse=True)
            main_face = faces[0]
            
            embedding = main_face.embedding
            
            # Normalize for cosine similarity
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
                
            return embedding.astype(np.float32)
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
            
    def generate_embedding_from_face(self, bgr_image: np.ndarray, face_obj: Any) -> Optional[np.ndarray]:
        """
        Generate embedding directly from an InsightFace face object without re-detecting.
        (Optimal method if using InsightFace for both).
        The face_obj from app.get() already has .embedding populated!
        """
        if face_obj is None or not hasattr(face_obj, 'embedding'):
            return None
            
        embedding = face_obj.embedding
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        return embedding.astype(np.float32)

    def generate_embeddings_batch(self, face_images: list) -> list:
        """Batch generation."""
        if not face_images:
            return []
        
        embeddings = []
        for face_image in face_images:
            try:
                embedding = self.generate_embedding(face_image)
                if embedding is not None:
                    embeddings.append(embedding.tolist())
            except Exception:
                continue
        
        return embeddings

# Global instance
_facenet_instance = None

def get_facenet_model() -> InsightFaceRecognizer:
    global _facenet_instance
    if _facenet_instance is None:
        _facenet_instance = InsightFaceRecognizer()
    return _facenet_instance
