
"""
Room Service Layer.
Handles creating and validating event rooms.
"""

import json
import random
import string
import shutil
from pathlib import Path
from typing import Dict, Optional, List
import config

import hashlib

ROOMS_DIR = Path("data/rooms")

class RoomService:
    """Service for managing Event Rooms."""
    
    def __init__(self):
        ROOMS_DIR.mkdir(parents=True, exist_ok=True)
    
    def _generate_room_id(self, length: int = 6) -> str:
        """Generate a random alphanumeric room ID (e.g., A7X92B)."""
        chars = string.ascii_uppercase + string.digits
        # Ensure at least one letter and one number
        while True:
            code = ''.join(random.choices(chars, k=length))
            if any(c.isdigit() for c in code) and any(c.isalpha() for c in code):
                return code

    def create_room(self, event_name: str, password: str = None) -> Dict:
        """
        Create a new event room.
        
        Returns:
            Dict containing room_id and event_name
        """
        # Generate unique ID
        while True:
            room_id = self._generate_room_id()
            room_path = ROOMS_DIR / room_id
            if not room_path.exists():
                break
        
        # Create directory structure
        room_path.mkdir()
        (room_path / "uploads").mkdir()
        (room_path / "chromadb").mkdir()
        
        # Hash password if provided
        password_hash = None
        if password:
            password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Save metadata
        metadata = {
            "room_id": room_id,
            "event_name": event_name,
            "created_at_ts": config.get_current_timestamp() if hasattr(config, 'get_current_timestamp') else 0,
            "password_hash": password_hash
        }
        
        with open(room_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
            
        print(f"[ROOM] Created new room: {event_name} ({room_id})")
        return metadata

    def get_room(self, room_id: str) -> Optional[Dict]:
        """Validate if a room exists and return its metadata."""
        if not room_id:
            return None
            
        room_path = ROOMS_DIR / room_id.upper() # Case insensitive ID
        meta_path = room_path / "metadata.json"
        
        if not room_path.exists() or not meta_path.exists():
            return None
            
        try:
            with open(meta_path, "r") as f:
                return json.load(f)
        except Exception:
            return None

    def verify_password(self, room_id: str, password: str) -> bool:
        """Verify room password."""
        room = self.get_room(room_id)
        if not room:
            return False
            
        stored_hash = room.get("password_hash")
        
        # If no password set, return True (or False depending on policy, but usually rooms without passwords are open/unprotected or shouldn't exist in this new model. 
        # For backward compatibility, if no password set, we might allow reset? 
        # Let's say if password IS set, we verify. If NOT set, we allow (or maybe fail safe).
        # Requirement says "password will be used". 
        if not stored_hash:
            return True # No password protected
            
        if not password:
            return False # Password required but not provided
            
        input_hash = hashlib.sha256(password.encode()).hexdigest()
        return input_hash == stored_hash

    def get_room_path(self, room_id: str) -> Optional[Path]:
        """Get the absolute path to a room's data directory."""
        if not room_id: return None
        return ROOMS_DIR / room_id.upper()

# Global instance
_room_service = None

def get_room_service() -> RoomService:
    global _room_service
    if _room_service is None:
        _room_service = RoomService()
    return _room_service
