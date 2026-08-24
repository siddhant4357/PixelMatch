import string
import random
from pathlib import Path
from typing import Dict, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import hashlib
import os

ROOMS_DIR = Path("data/rooms")

class RoomService:
    """Service for managing Event Rooms via Postgres."""
    
    def __init__(self):
        ROOMS_DIR.mkdir(parents=True, exist_ok=True)
    
    def get_room_path(self, room_code: str) -> Path:
        return ROOMS_DIR / room_code.upper()

    def _generate_room_code(self, length: int = 6) -> str:
        chars = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(chars, k=length))
            if any(c.isdigit() for c in code) and any(c.isalpha() for c in code):
                return code

    async def create_room(self, event_name: str, user_id: str, db: AsyncSession) -> Dict:
        """Create room in DB and add creator as admin."""
        # Fast path generation (we can retry on conflict)
        room_code = self._generate_room_code()
        
        query = text("""
            INSERT INTO rooms (room_code, event_name, created_by)
            VALUES (:room_code, :event_name, :created_by)
            RETURNING id, room_code, event_name, photo_count, created_at
        """)
        
        result = await db.execute(query, {
            "room_code": room_code,
            "event_name": event_name,
            "created_by": user_id
        })
        room = dict(result.fetchone()._mapping)
        
        # Add as admin
        member_query = text("""
            INSERT INTO room_members (user_id, room_id, role)
            VALUES (:user_id, :room_id, 'admin')
        """)
        await db.execute(member_query, {
            "user_id": user_id,
            "room_id": room['id']
        })
        
        await db.commit()
        
        # Create physical directories for local FAISS (if needed)
        room_path = self.get_room_path(room_code)
        room_path.mkdir(exist_ok=True)
        (room_path / "uploads").mkdir(exist_ok=True)
        
        return room

    async def get_room(self, room_code: str, db: AsyncSession) -> Optional[Dict]:
        """Get room details by code."""
        if not db:
            return {"room_code": room_code, "event_name": "Test Room"}
            
        query = text("SELECT * FROM rooms WHERE room_code = :room_code")
        result = await db.execute(query, {"room_code": room_code.upper()})
        row = result.fetchone()
        
        if row:
            return dict(row._mapping)
        return None

    async def join_room(self, room_code: str, user_id: str, db: AsyncSession) -> Optional[Dict]:
        """Join a room as a guest."""
        room = await self.get_room(room_code, db)
        if not room:
            raise ValueError("Room not found")
            
        # Add to members (upsert in case they already joined)
        member_query = text("""
            INSERT INTO room_members (user_id, room_id, role)
            VALUES (:user_id, :room_id, 'guest')
            ON CONFLICT (user_id, room_id) DO NOTHING
        """)
        await db.execute(member_query, {
            "user_id": user_id,
            "room_id": room['id']
        })
        await db.commit()
        return room

    async def get_user_rooms(self, user_id: str, db: AsyncSession) -> List[Dict]:
        """Get all rooms a user is part of (admin or guest)."""
        if not db:
            return []
            
        query = text("""
            SELECT r.room_code, r.event_name, r.cover_emoji, r.photo_count, r.event_date, rm.role
            FROM rooms r
            JOIN room_members rm ON r.id = rm.room_id
            WHERE rm.user_id = :user_id
            ORDER BY rm.joined_at DESC
        """)
        result = await db.execute(query, {"user_id": user_id})
        return [dict(row._mapping) for row in result.fetchall()]

# Global Instance
_room_service_instance = RoomService()

def get_room_service() -> RoomService:
    return _room_service_instance
