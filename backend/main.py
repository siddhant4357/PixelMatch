"""
PixelMatch Backend API
FastAPI application for facial recognition-based photo retrieval.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends, BackgroundTasks, Header, Query, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional
import uvicorn
import uuid
import numpy as np
import base64
import logging
from pathlib import Path
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from services.admin_service import get_admin_service, AdminService
from services.guest_service import get_guest_service, GuestService
from services.ai_search_service import get_ai_search_service, AISearchService
from services.room_service import get_room_service, RoomService
from services.drive_service import get_drive_service
from services.auth_service import get_current_user
from services.user_service import user_service
from db.database import init_db, get_db

import config

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown (if needed)

_startup_logger = logging.getLogger("startup")

# Create FastAPI app
app = FastAPI(
    title="PixelMatch API",
    description="Facial recognition-based photo retrieval system",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
# Note: allow_credentials=True is incompatible with allow_origins=["*"].
# We use the explicit list from ALLOWED_ORIGINS env var.
_origins = config.ALLOWED_ORIGINS
_startup_logger.warning(f"CORS ALLOWED_ORIGINS = {_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependency Injection for Room Context ---
async def get_current_room_admin_service(
    x_room_id: str = Header(None, alias="X-Room-ID")
) -> AdminService:
    return get_admin_service(x_room_id)

async def get_current_room_guest_service(
    x_room_id: str = Header(None, alias="X-Room-ID")
) -> GuestService:
    return get_guest_service(x_room_id)

async def get_current_room_ai_service(
    x_room_id: str = Header(None, alias="X-Room-ID")
) -> AISearchService:
    return get_ai_search_service(x_room_id)


# --- Auth Endpoints (Phase 2) ---

@app.get("/auth/profile")
async def get_profile(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    has_embedding = await user_service.has_embedding(user['id'], db)
    return {
        "user": user,
        "has_embedding": has_embedding
    }

@app.post("/auth/upload-selfie")
async def upload_selfie(
    selfie: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    import gc
    from models.face_detection import FaceDetector
    from utils.image_processing import load_image_from_bytes, crop_face
    import cv2
    
    file_bytes = await selfie.read()
    image = load_image_from_bytes(file_bytes)
    
    detector = FaceDetector()
    faces = detector.detect_faces(image)
    
    if not faces:
        del image, file_bytes, faces
        gc.collect()
        raise HTTPException(status_code=400, detail="No face detected in the image")
        
    face = faces[0]  # Largest face
    bbox, confidence, landmarks, embedding = face
    
    if embedding is None:
        del image, file_bytes, faces
        gc.collect()
        raise HTTPException(status_code=400, detail="Failed to extract face embedding")
        
    # Create thumbnail
    face_img = crop_face(image, bbox)
    thumb = cv2.resize(face_img, (100, 100))
    _, buffer = cv2.imencode('.jpg', cv2.cvtColor(thumb, cv2.COLOR_RGB2BGR))
    thumb_b64 = base64.b64encode(buffer).decode('utf-8')
    
    # Free large objects immediately to avoid OOM on free tier
    del image, file_bytes, faces, face_img, thumb, buffer
    gc.collect()
    
    await user_service.save_embedding(user['id'], embedding, thumb_b64, db)
    return {"success": True, "message": "Selfie saved successfully"}

@app.put("/auth/update-selfie")
async def update_selfie(
    selfie: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Same as upload
    return await upload_selfie(selfie, user, db)

@app.delete("/auth/delete-data")
async def delete_my_data(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await user_service.delete_user_data(user['id'], db)
    return {"success": True, "message": "All selfie data deleted"}


# --- Room Endpoints (Phase 2) ---

class CreateRoomRequest(BaseModel):
    event_name: str
    password: Optional[str] = None

class JoinRoomRequest(BaseModel):
    room_code: str

@app.post("/api/rooms/create")
async def create_room(
    request: CreateRoomRequest, 
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = get_room_service()
    return await service.create_room(request.event_name, user['id'], db)

@app.post("/api/rooms/join")
async def join_room(
    request: JoinRoomRequest, 
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = get_room_service()
    try:
        room = await service.join_room(request.room_code, user['id'], db)
        return room
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/rooms/my-rooms")
async def get_my_rooms(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = get_room_service()
    return await service.get_user_rooms(user['id'], db)

@app.get("/api/rooms/{room_code}")
async def get_room_details(
    room_code: str,
    db: AsyncSession = Depends(get_db)
):
    service = get_room_service()
    room = await service.get_room(room_code, db)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@app.get("/api/rooms/{room_code}/consent")
async def check_consent(
    room_code: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from services.privacy_service import privacy_service
    service = get_room_service()
    room = await service.get_room(room_code, db)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
        
    has_consent = await privacy_service.has_consent(user['id'], room['id'], db)
    return {"has_consent": has_consent}

@app.post("/api/rooms/{room_code}/consent")
async def grant_consent(
    room_code: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from services.privacy_service import privacy_service
    service = get_room_service()
    room = await service.get_room(room_code, db)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
        
    await privacy_service.create_consent(user['id'], room['id'], db)
    return {"success": True, "message": "Consent recorded"}


# --- General Endpoints ---

@app.get("/")
async def root():
    return {"message": "PixelMatch API", "version": "2.0.0", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/ping")
async def ping():
    return {"status": "ok"}


# --- Admin Endpoints (Photos) ---
# Keeping X-Room-ID for now as frontend still uses it for photo upload

@app.post("/admin/upload")
async def admin_upload(
    files: List[UploadFile] = File(...),
    admin_service: AdminService = Depends(get_current_room_admin_service),
    db: AsyncSession = Depends(get_db)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    photo_files = []
    for file in files:
        file_bytes = await file.read()
        if len(file_bytes) > config.MAX_UPLOAD_SIZE_BYTES:
             raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds max size")
        photo_files.append((file.filename, file_bytes))
    
    results = await admin_service.process_bulk_upload(photo_files)
    
    # Update photo count in DB
    if results['successful'] > 0 and admin_service.room_id:
        from sqlalchemy import text
        await db.execute(
            text("UPDATE rooms SET photo_count = photo_count + :count WHERE room_code = :room_code"),
            {"count": results['successful'], "room_code": admin_service.room_id}
        )
        await db.commit()
        
    return {"message": "Photos processed successfully", "statistics": results}

@app.get("/admin/stats")
async def get_stats(admin_service: AdminService = Depends(get_current_room_admin_service)):
    return admin_service.get_database_stats()

@app.delete("/admin/photos/{filename}")
async def delete_photo(
    filename: str,
    admin_service: AdminService = Depends(get_current_room_admin_service)
):
    photo_path = admin_service.upload_dir / filename
    result = admin_service.delete_photo(str(photo_path))
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Deletion failed'))
    return result

@app.post("/admin/database/reset")
async def reset_database(
    admin_service: AdminService = Depends(get_current_room_admin_service),
    x_room_id: str = Header(None, alias="X-Room-ID")
):
    if not x_room_id:
        raise HTTPException(status_code=400, detail="Room ID required")
    result = admin_service.reset_database()
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Reset failed'))
    return result


# --- Guest Endpoints (Search) ---

@app.post("/guest/search")
async def guest_search_authenticated(
    top_k: int = Query(default=50),
    similarity_threshold: Optional[float] = Query(default=None),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    guest_service: GuestService = Depends(get_current_room_guest_service)
):
    """Authenticated guest search using DB embedding."""
    embedding = await user_service.get_embedding(user['id'], db)
    if embedding is None:
        raise HTTPException(status_code=400, detail="No selfie found for user. Please complete onboarding.")
        
    results = await guest_service.search_photos_by_embedding(
        embedding=embedding,
        top_k=top_k,
        similarity_threshold=similarity_threshold
    )
    return results

@app.post("/guest/search-with-selfie")
async def guest_search_with_selfie(
    selfie: UploadFile = File(...),
    top_k: int = Form(default=50),
    similarity_threshold: Optional[float] = Form(default=None),
    guest_service: GuestService = Depends(get_current_room_guest_service)
):
    """Legacy/One-off guest search using uploaded file."""
    if not config.is_allowed_file(selfie.filename):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    selfie_bytes = await selfie.read()
    results = await guest_service.search_photos_by_selfie(
        selfie_bytes=selfie_bytes,
        filename=selfie.filename,
        top_k=top_k,
        similarity_threshold=similarity_threshold
    )
    return results

@app.get("/guest/photos/{room_code}/{filename}")
async def get_photo_in_room(room_code: str, filename: str):
    from services.room_service import get_room_service
    from services.storage_service import get_storage_service
    from fastapi.responses import RedirectResponse
    
    room_path = get_room_service().get_room_path(room_code)
    photo_path = room_path / "uploads" / filename
    
    if photo_path.exists():
        return FileResponse(photo_path)
        
    # Fallback to cloud storage
    storage = get_storage_service()
    if storage.is_configured:
        object_key = f"{room_code.upper()}/{filename}"
        url = storage.get_presigned_url(object_key)
        if url:
            return RedirectResponse(url)
            
    raise HTTPException(status_code=404, detail="Photo not found")

@app.get("/guest/photos/{filename}")
async def get_photo(
    filename: str,
    guest_service: GuestService = Depends(get_current_room_guest_service)
):
    from services.room_service import get_room_service
    from services.storage_service import get_storage_service
    from fastapi.responses import RedirectResponse
    
    # Fallback if room_id is found from header, else default
    room_id = guest_service.room_id or "default"
    room_path = get_room_service().get_room_path(room_id)
    photo_path = room_path / "uploads" / filename
    
    if photo_path.exists():
        return FileResponse(photo_path)
        
    # Fallback to cloud storage
    storage = get_storage_service()
    if storage.is_configured:
        object_key = f"{room_id.upper()}/{filename}"
        url = storage.get_presigned_url(object_key)
        if url:
            return RedirectResponse(url)
            
    raise HTTPException(status_code=404, detail="Photo not found")

from pydantic import BaseModel
class DownloadZipRequest(BaseModel):
    filenames: List[str]

@app.post("/guest/photos/{room_code}/download-zip")
async def download_zip(room_code: str, request: DownloadZipRequest):
    import zipfile
    import io
    from services.room_service import get_room_service
    from services.storage_service import get_storage_service
    from fastapi.responses import StreamingResponse
    
    room_path = get_room_service().get_room_path(room_code)
    upload_dir = room_path / "uploads"
    storage = get_storage_service()
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for filename in request.filenames:
            photo_path = upload_dir / filename
            if photo_path.exists():
                zip_file.write(photo_path, filename)
            elif storage.is_configured:
                # Fallback to cloud
                object_key = f"{room_code.upper()}/{filename}"
                file_bytes = storage.get_file_bytes(object_key)
                if file_bytes:
                    zip_file.writestr(filename, file_bytes)
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        iter([zip_buffer.getvalue()]), 
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=photos_{room_code}.zip"}
    )

# --- AI Endpoints ---
@app.post("/ai/query")
async def ai_query(
    request: dict,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    ai_service: AISearchService = Depends(get_current_room_ai_service)
):
    query = request.get("query")
    
    if not query:
         raise HTTPException(status_code=400, detail="Query is required")
         
    # Fetch user's stored embedding
    from services.user_service import user_service
    embedding = await user_service.get_embedding(user['id'], db)
    
    if embedding is None:
         raise HTTPException(status_code=400, detail="No selfie found for user. Please complete onboarding.")
         
    # search_photos handles the AI querying and photo searching
    results = ai_service.search_photos(embedding, query)
    return results

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
