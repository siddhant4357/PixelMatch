"""
Image processing utilities for PhotoScan application.
Handles image loading, cropping, resizing, and normalization.
"""

import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional


def load_image(image_path: str) -> Optional[np.ndarray]:
    """
    Load an image from file path.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Image as numpy array in RGB format, or None if loading fails
    """
    try:
        image = cv2.imread(str(image_path))
        if image is None:
            return None
        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None


def load_image_from_bytes(image_bytes: bytes) -> Optional[np.ndarray]:
    """
    Load an image from bytes.
    
    Args:
        image_bytes: Image data as bytes
        
    Returns:
        Image as numpy array in RGB format, or None if loading fails
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            return None
        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image
    except Exception as e:
        print(f"Error loading image from bytes: {e}")
        return None


def crop_face(image: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
    """
    Crop a face from an image using bounding box coordinates.
    
    Args:
        image: Input image as numpy array
        bbox: Bounding box as (x, y, width, height)
        
    Returns:
        Cropped face image, or None if cropping fails
    """
    try:
        x, y, w, h = bbox
        # Ensure coordinates are within image bounds
        height, width = image.shape[:2]
        x = max(0, x)
        y = max(0, y)
        w = min(w, width - x)
        h = min(h, height - y)
        
        if w <= 0 or h <= 0:
            return None
            
        cropped = image[y:y+h, x:x+w]
        return cropped
    except Exception as e:
        print(f"Error cropping face: {e}")
        return None


def resize_image(image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
    """
    Resize an image to target size.
    
    Args:
        image: Input image as numpy array
        target_size: Target size as (width, height)
        
    Returns:
        Resized image
    """
    return cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)


def normalize_image(image: np.ndarray) -> np.ndarray:
    """
    Normalize image pixel values to [-1, 1] range for FaceNet.
    
    Args:
        image: Input image as numpy array with values in [0, 255]
        
    Returns:
        Normalized image with values in [-1, 1]
    """
    # Convert to float and normalize to [0, 1]
    normalized = image.astype(np.float32) / 255.0
    # Standardize to [-1, 1]
    normalized = (normalized - 0.5) * 2.0
    return normalized


def preprocess_face(face_image: np.ndarray, target_size: int = 160) -> np.ndarray:
    """
    Preprocess a face image for FaceNet model.
    Resizes to target size and normalizes pixel values.
    
    Args:
        face_image: Input face image as numpy array
        target_size: Target size for both width and height (default: 160 for FaceNet)
        
    Returns:
        Preprocessed face image ready for model input
    """
    # Resize to target size
    resized = resize_image(face_image, (target_size, target_size))
    # Normalize
    normalized = normalize_image(resized)
    return normalized


def save_image(image: np.ndarray, save_path: str) -> bool:
    """
    Save an image to file.
    
    Args:
        image: Image as numpy array in RGB format
        save_path: Path to save the image
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert RGB to BGR for OpenCV
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(save_path), image_bgr)
        return True
    except Exception as e:
        print(f"Error saving image to {save_path}: {e}")
        return False


def draw_bounding_box(
    image: np.ndarray,
    bbox: Tuple[int, int, int, int],
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2
) -> np.ndarray:
    """
    Draw a bounding box on an image.
    
    Args:
        image: Input image as numpy array
        bbox: Bounding box as (x, y, width, height)
        color: Box color as RGB tuple (default: green)
        thickness: Line thickness (default: 2)
        
    Returns:
        Image with bounding box drawn
    """
    x, y, w, h = bbox
    image_copy = image.copy()
    cv2.rectangle(image_copy, (x, y), (x + w, y + h), color, thickness)
    return image_copy
