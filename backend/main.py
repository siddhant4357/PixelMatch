"""
PixelMatch Backend API
FastAPI application for facial recognition-based photo retrieval.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends, BackgroundTasks, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional
import uvicorn
import uuid
from pathlib import Path
from pydantic import BaseModel

from services.admin_service import get_admin_service, AdminService
from services.guest_service import get_guest_service, GuestService
from services.ai_search_service import get_ai_search_service, AISearchService
from services.room_service import get_room_service, RoomService
from services.drive_service import get_drive_service

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
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Dependency Injection for Room Context ---

async def get_current_room_admin_service(
    x_room_id: str = Header(None, alias="X-Room-ID")
) -> AdminService:
    """Dependency: Get AdminService context-aware of the Room ID header."""
    return get_admin_service(x_room_id)


async def get_current_room_guest_service(
    x_room_id: str = Header(None, alias="X-Room-ID")
) -> GuestService:
    """Dependency: Get GuestService context-aware of the Room ID header."""
    return get_guest_service(x_room_id)


async def get_current_room_ai_service(
    x_room_id: str = Header(None, alias="X-Room-ID")
) -> AISearchService:
    """Dependency: Get AISearchService context-aware of the Room ID header."""
    # AI service needs room context for location db and vector db
    return get_ai_search_service(x_room_id)


# --- Room Endpoints ---

class CreateRoomRequest(BaseModel):
    event_name: str
    password: str = None

class ResetDatabaseRequest(BaseModel):
    password: str = None

class JoinRoomRequest(BaseModel):
    room_id: str

@app.post("/api/rooms/create")
async def create_room(request: CreateRoomRequest):
    """Create a new event room."""
    service = get_room_service()
    return service.create_room(request.event_name, request.password)

@app.post("/api/rooms/join")
async def join_room(request: JoinRoomRequest):
    """Validate and join a room."""
    service = get_room_service()
    room = service.get_room(request.room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found. Check the ID and try again.")
    return room


# --- General Endpoints ---

@app.post("/admin/import-drive")
async def import_drive(
    request: dict, # {"url": "..."}
    background_tasks: BackgroundTasks,
    drive_service = Depends(get_drive_service),
    x_room_id: str = Header(None, alias="X-Room-ID")
):
    url = request.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL required")
    
    task_id = str(uuid.uuid4())
    background_tasks.add_task(drive_service.process_drive_link, url, task_id, x_room_id)
    
    return {"task_id": task_id, "message": "Background processing started"}

@app.get("/")
async def root():
    return {
        "message": "PixelMatch API",
        "version": "2.0.0", # Bumped version for Rooms support
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/ping")
async def ping():
    return {"status": "ok"}


# --- Admin Endpoints ---

@app.post("/admin/upload")
async def admin_upload(
    files: List[UploadFile] = File(...),
    admin_service: AdminService = Depends(get_current_room_admin_service)
):
    """
    Admin endpoint: Upload bulk photos for processing.
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
    results = await admin_service.process_bulk_upload(photo_files)
    
    return {
        "message": "Photos processed successfully",
        "statistics": results
    }

@app.get("/admin/stats")
async def get_stats(
    admin_service: AdminService = Depends(get_current_room_admin_service)
):
    """Admin endpoint: Get database statistics."""
    return admin_service.get_database_stats()

@app.delete("/admin/photos/{filename}")
async def delete_photo(
    filename: str,
    admin_service: AdminService = Depends(get_current_room_admin_service)
):
    """Admin endpoint: Delete a photo and its embeddings."""
    # We need to resolve the path relative to the room (or global)
    # The service expects a path string. 
    # But wait, admin_service.delete_photo expects the full path string stored in vector DB.
    # The vector DB stores whatever path we gave it.
    # In process_bulk_upload, we construct path: self.upload_dir / filename
    
    photo_path = admin_service.upload_dir / filename
    
    result = admin_service.delete_photo(str(photo_path))
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Deletion failed'))
    
    return result

@app.post("/admin/database/reset")
async def reset_database(
    request: ResetDatabaseRequest,
    admin_service: AdminService = Depends(get_current_room_admin_service),
    x_room_id: str = Header(None, alias="X-Room-ID")
):
    """
    Admin endpoint: Reset the database for the current room context.
    WARNING: This deletes all face embeddings and photos!
    Requires password verification.
    """
    if not x_room_id:
        raise HTTPException(status_code=400, detail="Room ID required")

    # Verify password
    room_service = get_room_service()
    if not room_service.verify_password(x_room_id, request.password):
        raise HTTPException(status_code=403, detail="Invalid room password")

    result = admin_service.reset_database()
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Reset failed'))
    
    return result


# --- Guest Endpoints ---

@app.post("/guest/search")
async def guest_search(
    selfie: UploadFile = File(...),
    top_k: int = Form(default=50),
    similarity_threshold: float = Form(default=None),
    guest_service: GuestService = Depends(get_current_room_guest_service)
):
    """
    Guest endpoint: Upload selfie and search for matching photos.
    """
    # Validate file type
    if not config.is_allowed_file(selfie.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {config.ALLOWED_EXTENSIONS}"
        )
    
    selfie_bytes = await selfie.read()
    
    if len(selfie_bytes) > config.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum size of {config.MAX_UPLOAD_SIZE_MB}MB"
        )
    
    # Search
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
async def guest_validate(
    selfie: UploadFile = File(...),
    guest_service: GuestService = Depends(get_current_room_guest_service)
):
    """Guest endpoint: Validate selfie before search."""
    if not config.is_allowed_file(selfie.filename):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    selfie_bytes = await selfie.read()
    result = guest_service.validate_selfie(selfie_bytes)
    
    if not result['valid']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Invalid selfie'))
    
    return result




# ...

@app.get("/photos/{filename}")
async def get_photo(
    filename: str,
    x_room_id: str = Header(None, alias="X-Room-ID"),
    room_id: str = Query(None)
):
    """
    Get a photo file by filename. 
    Context-aware: looks in room folder if room ID provided (via Header or Query).
    """
    actual_room_id = x_room_id or room_id
    
    if actual_room_id:
        room_service = get_room_service()
        room_path = room_service.get_room_path(actual_room_id)
        if not room_path:
             raise HTTPException(status_code=404, detail="Room not found")
        photo_path = room_path / "uploads" / filename
    else:
        photo_path = config.UPLOAD_DIR / filename
    
    if not photo_path.exists():
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Create FileResponse with CORS headers for ZIP download support
    response = FileResponse(
        path=str(photo_path),
        media_type="image/jpeg",
        filename=filename
    )
    
    # Add CORS headers to allow fetch from frontend
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    return response


# --- AI Search Endpoints ---

class AIQueryRequest(BaseModel):
    session_id: str
    query: str

@app.post("/guest/ai-search/upload-selfie")
async def ai_search_upload_selfie(
    selfie: UploadFile = File(...),
    guest_service: GuestService = Depends(get_current_room_guest_service),
    ai_service: AISearchService = Depends(get_current_room_ai_service)
):
    """
    AI Search: Upload selfie and create search session.
    """
    if not config.is_allowed_file(selfie.filename):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    selfie_bytes = await selfie.read()
    
    # 1. Validate Face via Guest Service
    validation = guest_service.validate_selfie(selfie_bytes)
    if not validation['valid']:
        raise HTTPException(status_code=400, detail=validation.get('error', 'No face detected'))
    
    # 2. Generate Embedding (using code from Main logic or helper)
    # We can reuse the logic from GuestService or do it here.
    # To keep it DRY, let's duplicate the logic slightly or see if GuestService can give us embedding.
    # GuestService doesn't expose embedding generation directly in public API efficiently (it does search).
    # We can use the lower level models directly since we are in backend.
    
    from utils.image_processing import load_image_from_bytes, crop_face, preprocess_face
    from models.face_recognition import get_facenet_model
    
    image = load_image_from_bytes(selfie_bytes)
    faces = guest_service.face_detector.detect_faces(image)
    if not faces:
         raise HTTPException(status_code=400, detail="No face detected")
    
    bbox, confidence = faces[0]
    face_img = crop_face(image, bbox)
    preprocessed = preprocess_face(face_img, config.FACE_SIZE)
    
    facenet = get_facenet_model()
    embedding = facenet.generate_embedding(preprocessed, enable_tta=True)
    
    if embedding is None:
        raise HTTPException(status_code=500, detail="Failed to generate embedding")
        
    # 3. Create Session
    session_id = ai_service.create_session(
        face_embedding=embedding.tolist(),
        selfie_filename=selfie.filename
    )
    
    return {
        'success': True,
        'session_id': session_id,
        'message': 'Session created.',
        'face_detected': True
    }

@app.post("/guest/ai-search/query")
async def ai_search_query(
    request: AIQueryRequest,
    ai_service: AISearchService = Depends(get_current_room_ai_service)
):
    """
    AI Search: Process natural language query and search photos.
    """
    result = ai_service.search_photos(
        session_id=request.session_id,
        user_query=request.query
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Search failed'))
    
    return result

@app.get("/guest/ai-search/locations")
async def get_available_locations(
    ai_service: AISearchService = Depends(get_current_room_ai_service)
):
    """
    Get all available photo locations for AI context.
    """
    # ai_service has location_db
    locations = ai_service.location_db.get_all_locations()
    return {
        'success': True,
        'locations': locations,
        'count': len(locations)
    }

@app.get("/admin/stats/metadata")
async def get_metadata_stats(
    admin_service: AdminService = Depends(get_current_room_admin_service)
):
    """
    Get metadata statistics.
    """
    location_db = admin_service.location_db
    stats = location_db.get_stats()
    locations = location_db.get_all_locations()
    return {
        'success': True,
        'stats': stats,
        'locations': locations[:10]
    }


# --- Google Drive Routes (Admin) ---
# Note: Google Drive Service might need room awareness too if it saves files.
# But for now let's assume it downloads to a temp folder and then calls AdminService.
# If AdminService is injected, it should be the room-aware one.

# We need to check services/drive_service.py to see how it calls AdminService.
# It probably calls get_admin_service() directly, which would get the 'default' one.
# This is a caveat. Google Drive import might need refactoring to accept room_id.
# For now, let's leave it as is, or pass room_id in the request and forward it.

if __name__ == "__main__":
    print(f"Starting PixelMatch API on {config.HOST}:{config.PORT}")
    print(f"Room Mode: Enabled")
    
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True
    )
