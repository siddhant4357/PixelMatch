"""
Face Detection Module using InsightFace.
Uses SCRFD backend for maximum accuracy and speed on CPU.
"""

import cv2
import numpy as np
from insightface.app import FaceAnalysis
from typing import List, Tuple, Optional, Any
import config

# Global singleton for InsightFace app to avoid reloading
_insightface_app = None

def get_insightface_app() -> FaceAnalysis:
    """Get or initialize the global InsightFace FaceAnalysis app."""
    global _insightface_app
    if _insightface_app is None:
        print(f"Loading InsightFace model: {config.INSIGHTFACE_MODEL}...")
        _insightface_app = FaceAnalysis(
            name=config.INSIGHTFACE_MODEL,
            providers=['CPUExecutionProvider']
        )
        # Use 320x320 instead of 640x640 — saves ~250MB RAM on free-tier servers.
        # Accuracy is slightly reduced but still excellent for single-person selfies.
        _insightface_app.prepare(ctx_id=-1, det_size=(320, 320))
        print("InsightFace model loaded successfully.")
    return _insightface_app


class FaceDetector:
    """
    Face detector using InsightFace.
    """
    
    def __init__(self, min_detection_confidence: float = None):
        """
        Initialize face detector.
        """
        self.min_confidence = min_detection_confidence or config.MIN_FACE_CONFIDENCE
        self.app = get_insightface_app()
        print(f"Face detection initialized (InsightFace SCRFD)")
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[Tuple[int, int, int, int], float, Any, np.ndarray]]:
        """
        Detect faces in image.
        
        Args:
            image: Input image (RGB or BGR)
            
        Returns:
            List of (bbox, confidence, landmarks) tuples
        """
        if image is None or image.size == 0:
            return []
        
        try:
            # InsightFace expects BGR image (OpenCV default)
            # If we know it's RGB from Pillow, we should convert to BGR, 
            # but usually deepface handled it. We need to check how load_image returns.
            # Assuming it's RGB from Pillow, convert to BGR:
            if len(image.shape) == 2:
                bgr_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            elif image.shape[2] == 4: # RGBA
                bgr_image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
            else:
                # If RGB to BGR
                bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Detect faces
            faces = self.app.get(bgr_image)
            
            if not faces:
                return []
            
            detected_faces = []
            height, width = image.shape[:2]
            
            for face in faces:
                confidence = float(face.det_score)
                bbox = face.bbox.astype(int)
                landmarks = face.kps # 5 landmarks
                embedding = face.embedding
                
                x, y, x2, y2 = bbox
                w = x2 - x
                h = y2 - y
                
                # Sanity check
                x = max(0, x)
                y = max(0, y)
                w = min(w, width - x)
                h = min(h, height - y)
                
                # Minimum face size filter
                if w * h < config.MIN_FACE_SIZE_PX ** 2:
                    continue
                
                if w > 0 and h > 0 and confidence >= self.min_confidence:
                    detected_faces.append(((x, y, w, h), confidence, landmarks, embedding))
            
            # Sort by area
            detected_faces.sort(key=lambda item: item[0][2] * item[0][3], reverse=True)
            
            return detected_faces
            
        except Exception as e:
            print(f"Error detecting faces: {e}")
            return []
    
    def detect_single_face(self, image: np.ndarray) -> Optional[Tuple[Tuple[int, int, int, int], float, Any]]:
        """Detect the most prominent face."""
        faces = self.detect_faces(image)
        return faces[0] if faces else None

def detect_faces_in_image(image: np.ndarray, min_confidence: float = None) -> List[Tuple[Tuple[int, int, int, int], float]]:
    detector = FaceDetector(min_detection_confidence=min_confidence)
    # the old signature returned list of (bbox, confidence). We should strip landmarks for backward compat if needed,
    # but the new pipeline uses landmarks. Let's return full tuple if someone needs it, or just strip it.
    faces = detector.detect_faces(image)
    return [(bbox, conf) for bbox, conf, _, _ in faces]

def detect_single_face_in_image(image: np.ndarray, min_confidence: float = None) -> Optional[Tuple[Tuple[int, int, int, int], float]]:
    detector = FaceDetector(min_detection_confidence=min_confidence)
    face = detector.detect_single_face(image)
    if face:
        return (face[0], face[1])
    return None
