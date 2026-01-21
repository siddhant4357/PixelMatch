"""
Face Recognition Module using Super-Ensemble (ArcFace + FaceNet512).
Implements Test Time Augmentation (TTA) for SOTA accuracy.

Architecture:
1. Preprocess: Align face
2. Branch A: ArcFace (ResNet100) -> 512-dim
3. Branch B: FaceNet512 (Inception) -> 512-dim
4. TTA: Run both branches on Flipped image
5. Fusion: Average TTA, Concatenate Branches -> 1024-dim Super-Vector
"""

import numpy as np
from deepface import DeepFace
from typing import Optional, List
import config
import cv2
import logging

logger = logging.getLogger(__name__)

class FaceNet:
    """
    Super-Ensemble Face Recognition.
    Combines ArcFace and FaceNet512 with TTA.
    """
    
    def __init__(self):
        """Initialize both models and pre-load them to memory."""
        # Corrected model names (Facenet512 instead of FaceNet512)
        self.models = ["ArcFace", "Facenet512"]
        # Weights for weighted concatenation
        self.weights = [0.7, 0.3] 
        self.input_size = (160, 160)
        
        self.loaded_models = {}
        
        print("Loading Super-Ensemble Models into Memory (This runs once)...")
        for model_name in self.models:
            print(f"Loading {model_name}...")
            try:
                self.loaded_models[model_name] = DeepFace.build_model(model_name)
                print(f"Loaded {model_name} successfully.")
            except Exception as e:
                print(f"CRITICAL ERROR loading {model_name}: {e}")
        
        print(f"Feature Weighting: {self.weights}")
        print("Models loaded. Ready for fast inference.")

    def _apply_clahe(self, img: np.ndarray) -> np.ndarray:
        """
        Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        to normalize illumination (Wedding photos, bright/dark scenes).
        """
        try:
            # Convert to LAB color space
            lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE to L-channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            cl = clahe.apply(l)
            
            # Merge and convert back to RGB
            limg = cv2.merge((cl,a,b))
            return cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
        except Exception as e:
            print(f"CLAHE Warning: {e}")
            return img

    def generate_embedding(self, face_image: np.ndarray, enable_tta: bool = True) -> Optional[np.ndarray]:
        """
        Generate 1024-dimensional Super-Vector.
        
        Args:
            face_image: Input face crop
            enable_tta: Enable Test Time Augmentation (Flip) - Disable for faster uploads
        """
        if face_image is None:
            return None
        
        try:
            # Prepare image
            if face_image.max() <= 1.0:
                img_uint8 = (((face_image + 1) / 2) * 255).astype(np.uint8)
            else:
                img_uint8 = face_image.astype(np.uint8)
            
            if len(img_uint8.shape) == 2:
                img_uint8 = cv2.cvtColor(img_uint8, cv2.COLOR_GRAY2RGB)
            elif img_uint8.shape[2] == 4:
                img_uint8 = cv2.cvtColor(img_uint8, cv2.COLOR_RGBA2RGB)
            
            # --- Illumination Normalization (CLAHE) ---
            img_uint8 = self._apply_clahe(img_uint8)
            
            # --- Test Time Augmentation (TTA) ---
            images = [img_uint8]
            if enable_tta:
                img_flipped = cv2.flip(img_uint8, 1)
                images.append(img_flipped)
            
            super_vector_parts = []
            
            # --- Run Ensemble ---
            for i, model_name in enumerate(self.models):
                embeddings = []
                loaded_model = self.loaded_models.get(model_name)
                
                if not loaded_model:
                     print(f"Model {model_name} not loaded! Skipping.")
                     return None

                for img in images:
                    try:
                        embedding_obj = DeepFace.represent(
                            img_path=img,
                            model_name=model_name,
                            enforce_detection=False,
                            detector_backend='skip',
                            align=False
                        )
                        
                        if isinstance(embedding_obj, list) and len(embedding_obj) > 0:
                            emb = np.array(embedding_obj[0]['embedding'])
                            embeddings.append(emb)
                    except Exception as e:
                        print(f"Model {model_name} inference failed: {e}")
                        
                if embeddings:
                    # Average TTA results
                    avg_emb = np.mean(embeddings, axis=0)
                    
                    # Normalize first
                    norm = np.linalg.norm(avg_emb)
                    if norm > 0:
                        avg_emb = avg_emb / norm
                        
                    # Apply Feature Weighting
                    # Weighted Concatenation: Multiply by weight before concat
                    weight = self.weights[i]
                    weighted_emb = avg_emb * weight
                    
                    super_vector_parts.append(weighted_emb)
                else:
                    print(f"Failed to generate embedding for {model_name}")
                    return None
            
            if len(super_vector_parts) != 2:
                return None
            
            # --- Fusion ---
            # Concatenate weighted vectors
            super_vector = np.concatenate(super_vector_parts)
            
            # Final Normalization (essential for Cosine Similarity)
            norm = np.linalg.norm(super_vector)
            if norm > 0:
                super_vector = super_vector / norm
                
            return super_vector.astype(np.float32)
            
        except Exception as e:
            print(f"Error generating super-embedding: {e}")
            return None
    
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

def get_facenet_model() -> FaceNet:
    global _facenet_instance
    if _facenet_instance is None:
        _facenet_instance = FaceNet()
    return _facenet_instance
