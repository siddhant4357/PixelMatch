"""
Configuration module for PhotoScan application.
Loads settings from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# CORS Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000").split(",")

# Upload Configuration
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", 50))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
UPLOAD_DIR = BASE_DIR / os.getenv("UPLOAD_DIR", "data/uploads")
SELFIE_DIR = BASE_DIR / os.getenv("SELFIE_DIR", "data/selfies")

# Model Configuration
MODEL_DIR = BASE_DIR / os.getenv("MODEL_DIR", "data/models")
FACENET_MODEL_URL = os.getenv(
    "FACENET_MODEL_URL",
    "https://github.com/serengil/deepface_models/releases/download/v1.0/facenet_weights.h5"
)
FACENET_MODEL_PATH = MODEL_DIR / "facenet_weights.h5"

# Vector Database Configuration
CHROMA_PERSIST_DIR = BASE_DIR / os.getenv("CHROMA_PERSIST_DIR", "data/chromadb")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "face_embeddings")

# Face Recognition Settings
FACE_SIZE = 160  # Standard face image size for preprocessing
MIN_FACE_CONFIDENCE = float(os.getenv("MIN_FACE_CONFIDENCE", 0.5))
# Super-Ensemble Settings
ENABLE_ENSEMBLE = True
EMBEDDING_DIM = 1024  # ArcFace (512) + FaceNet512 (512)
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.55))  # Read from .env
MAX_FACES_PER_IMAGE = 50  # Maximum number of faces to detect per image

# Privacy & Security
ENABLE_PRIVACY_MODE = os.getenv("ENABLE_PRIVACY_MODE", "true").lower() == "true"
MAX_RESULTS = int(os.getenv("MAX_RESULTS", 100))

# Create necessary directories
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
SELFIE_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)

# Allowed image extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS
