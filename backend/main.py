"""
PixelMatch Backend API
FastAPI application for facial recognition-based photo retrieval.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import List
import uvicorn
import uuid
from pathlib import Path

from services.admin_service import get_admin_service, AdminService
from services.guest_service import get_guest_service
import config

# Create FastAPI app
app = FastAPI(
    title="PixelMatch API",
    description="Facial recognition-based photo retrieval system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev server
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "PhotoScan API",
        "version": "1.0.0",
        "endpoints": {
            "admin_upload": "/admin/upload",
            "guest_search": "/guest/search",
            "guest_validate": "/guest/validate",
            "photo_download": "/photos/{filename}",
            "stats": "/admin/stats",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Used for keep-alive pings to prevent backend sleep on free tier hosting.
    """
    admin_service = get_admin_service()
    stats = admin_service.get_database_stats()
    
    return {
        "status": "healthy",
        "timestamp": "2026-01-21T13:58:00Z",  # Will be replaced by actual timestamp
        "database": {
            "total_faces": stats['total_faces'],
            "total_photos": stats['total_photos']
        }
    }


@app.get("/ping")
async def ping():
    """
    Lightweight ping endpoint for keep-alive.
    Returns minimal response to keep server awake.
    """
    return {"status": "ok", "timestamp": "2026-01-21T13:58:00Z"}


@app.post("/admin/upload")
async def admin_upload(files: List[UploadFile] = File(...)):
    """
    Admin endpoint: Upload bulk photos for processing.
    
    Accepts multiple image files, detects faces, generates embeddings,
    and stores them in the vector database.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    # Validate file types
    for file in files:
        if not config.is_allowed_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.filename}. Allowed: {config.ALLOWED_EXTENSIONS}"
            )
    
    # Read file bytes
    photo_files = []
    for file in files:
        file_bytes = await file.read()
        
        # Check file size
        if len(file_bytes) > config.MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} exceeds maximum size of {config.MAX_UPLOAD_SIZE_MB}MB"
            )
        
        photo_files.append((file.filename, file_bytes))
    
    # Process photos
    admin_service = get_admin_service()
    results = await admin_service.process_bulk_upload(photo_files)
    
    return {
        "message": "Photos processed successfully",
        "statistics": results
    }


@app.post("/guest/search")
async def guest_search(
    selfie: UploadFile = File(...),
    top_k: int = Form(default=50),
    similarity_threshold: float = Form(default=None)
):
    """
    Guest endpoint: Upload selfie and search for matching photos.
    
    Detects face in selfie, generates embedding, and searches
    for similar faces in the database.
    """
    # Validate file type
    if not config.is_allowed_file(selfie.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {config.ALLOWED_EXTENSIONS}"
        )
    
    # Read file bytes
    selfie_bytes = await selfie.read()
    
    # Check file size
    if len(selfie_bytes) > config.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum size of {config.MAX_UPLOAD_SIZE_MB}MB"
        )
    
    # Search for matching photos
    guest_service = get_guest_service()
    results = await guest_service.search_photos_by_selfie(
        selfie_bytes=selfie_bytes,
        filename=selfie.filename,
        top_k=top_k,
        similarity_threshold=similarity_threshold
    )
    
    if not results['success']:
        raise HTTPException(status_code=400, detail=results.get('error', 'Search failed'))
    
    return results


@app.post("/guest/validate")
async def guest_validate(selfie: UploadFile = File(...)):
    """
    Guest endpoint: Validate selfie before search.
    
    Quick check to ensure selfie contains a detectable face.
    """
    # Validate file type
    if not config.is_allowed_file(selfie.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {config.ALLOWED_EXTENSIONS}"
        )
    
    # Read file bytes
    selfie_bytes = await selfie.read()
    
    # Validate selfie
    guest_service = get_guest_service()
    result = guest_service.validate_selfie(selfie_bytes)
    
    if not result['valid']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Invalid selfie'))
    
    return result


@app.get("/photos/{filename}")
async def get_photo(filename: str):
    """
    Get a photo file by filename.
    
    Returns the photo file for download/display.
    """
    photo_path = config.UPLOAD_DIR / filename
    
    if not photo_path.exists():
        raise HTTPException(status_code=404, detail="Photo not found")
    
    return FileResponse(
        path=str(photo_path),
        media_type="image/jpeg",
        filename=filename
    )


@app.get("/admin/stats")
async def get_stats():
    """
    Admin endpoint: Get database statistics.
    """
    admin_service = get_admin_service()
    stats = admin_service.get_database_stats()
    
    return stats


@app.delete("/admin/photos/{filename}")
async def delete_photo(filename: str):
    """
    Admin endpoint: Delete a photo and its embeddings.
    """
    photo_path = config.UPLOAD_DIR / filename
    
    if not photo_path.exists():
        raise HTTPException(status_code=404, detail="Photo not found")
    
    admin_service = get_admin_service()
    result = admin_service.delete_photo(str(photo_path))
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Deletion failed'))
    
    return result

# --- Google Drive Routes ---

from services.drive_service import get_drive_service, tasks

@app.post("/admin/import-drive")
async def import_drive(
    request: dict, # {"url": "..."}
    background_tasks: BackgroundTasks,
    drive_service = Depends(get_drive_service)
):
    url = request.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL required")
    
    task_id = str(uuid.uuid4())
    background_tasks.add_task(drive_service.process_drive_link, url, task_id)
    
    return {"task_id": task_id, "message": "Background processing started"}

@app.get("/admin/task-status/{task_id}")
async def get_task_status(task_id: str):
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.delete("/admin/database")
async def reset_database(service: AdminService = Depends(get_admin_service)):
    """
    Admin endpoint: Reset the entire database.
    WARNING: This deletes all face embeddings, photos, and selfies!
    """
    result = service.reset_database()
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Reset failed'))
    
    return result


# Startup Event to Pre-Load Models
@app.on_event("startup")
async def startup_event():
    print("Pre-warming AI models...")
    # Force initialization of services to load models into memory
    get_admin_service()
    get_guest_service()
    print("System verified and ready.")

if __name__ == "__main__":
    import uvicorn
    print(f"Starting PhotoScan API on {config.HOST}:{config.PORT}")
    print(f"Upload directory: {config.UPLOAD_DIR}")
    print(f"Selfie directory: {config.SELFIE_DIR}")
    print(f"Model directory: {config.MODEL_DIR}")
    
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True
    )
