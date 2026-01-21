"""
Face Detection Module using DeepFace (Kwikpic Stack).
Uses RetinaFace backend for maximum accuracy.
"""

import cv2
import numpy as np
from deepface import DeepFace
from typing import List, Tuple, Optional
import config


class FaceDetector:
    """
    Face detector using DeepFace with RetinaFace backend.
    """
    
    def __init__(self, min_detection_confidence: float = None):
        """
        Initialize face detector.
        """
        self.min_confidence = min_detection_confidence or config.MIN_FACE_CONFIDENCE
        # Use RetinaFace for Kwikpic-level accuracy
        # Falls back to opencv/mtcnn if retinaface not installed
        self.detector_backend = 'retinaface'
        print(f"Face detection initialized (DeepFace {self.detector_backend})")
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """
        Detect faces in image.
        
        Args:
            image: Input image (RGB)
            
        Returns:
            List of (bbox, confidence) tuples
        """
        if image is None or image.size == 0:
            return []
        
        try:
            # Ensure RGB
            if len(image.shape) == 2:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            else:
                rgb_image = image
            
            # Detect faces
            # DeepFace.extract_faces returns list of dicts with 'facial_area' and 'confidence'
            try:
                face_objs = DeepFace.extract_faces(
                    img_path=rgb_image,
                    detector_backend=self.detector_backend,
                    enforce_detection=False,
                    align=False
                )
            except Exception as e:
                print(f"RetinaFace failed, falling back to opencv: {e}")
                face_objs = DeepFace.extract_faces(
                    img_path=rgb_image,
                    detector_backend='opencv',
                    enforce_detection=False,
                    align=False
                )
            
            if not face_objs:
                return []
            
            faces = []
            height, width = image.shape[:2]
            
            for face_obj in face_objs:
                facial_area = face_obj['facial_area']
                x = facial_area['x']
                y = facial_area['y']
                w = facial_area['w']
                h = facial_area['h']
                
                confidence = face_obj.get('confidence', 0.95)
                
                # Sanity check
                x = max(0, x)
                y = max(0, y)
                w = min(w, width - x)
                h = min(h, height - y)
                
                if w > 0 and h > 0 and confidence >= self.min_confidence:
                    faces.append(((x, y, w, h), confidence))
            
            # Sort by area
            faces.sort(key=lambda x: x[0][2] * x[0][3], reverse=True)
            
            return faces
            
        except Exception as e:
            print(f"Error detecting faces: {e}")
            return []
    
    def detect_single_face(self, image: np.ndarray) -> Optional[Tuple[Tuple[int, int, int, int], float]]:
        """Detect the most prominent face."""
        faces = self.detect_faces(image)
        return faces[0] if faces else None


def detect_faces_in_image(image: np.ndarray, min_confidence: float = None) -> List[Tuple[Tuple[int, int, int, int], float]]:
    detector = FaceDetector(min_detection_confidence=min_confidence)
    return detector.detect_faces(image)


def detect_single_face_in_image(image: np.ndarray, min_confidence: float = None) -> Optional[Tuple[Tuple[int, int, int, int], float]]:
    detector = FaceDetector(min_detection_confidence=min_confidence)
    return detector.detect_single_face(image)
