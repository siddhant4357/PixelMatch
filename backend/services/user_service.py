import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional, Dict, Any

class UserService:
    async def has_embedding(self, user_id: str, db: AsyncSession) -> bool:
        if not db:
            return False
        query = text("SELECT 1 FROM user_embeddings WHERE user_id = :user_id")
        result = await db.execute(query, {"user_id": user_id})
        return result.fetchone() is not None

    async def save_embedding(self, user_id: str, embedding: np.ndarray, thumbnail_b64: str, db: AsyncSession) -> None:
        if not db:
            return
            
        embedding_bytes = embedding.tobytes()
        query = text("""
            INSERT INTO user_embeddings (user_id, embedding, selfie_thumbnail)
            VALUES (:user_id, :embedding, :thumbnail)
            ON CONFLICT (user_id) DO UPDATE 
            SET embedding = EXCLUDED.embedding, selfie_thumbnail = EXCLUDED.selfie_thumbnail
        """)
        await db.execute(query, {
            "user_id": user_id, 
            "embedding": embedding_bytes,
            "thumbnail": thumbnail_b64
        })
        await db.commit()

    async def get_embedding(self, user_id: str, db: AsyncSession) -> Optional[np.ndarray]:
        if not db:
            return None
            
        query = text("SELECT embedding FROM user_embeddings WHERE user_id = :user_id")
        result = await db.execute(query, {"user_id": user_id})
        row = result.fetchone()
        
        if row:
            embedding_bytes = row[0]
            # Convert back to numpy array
            embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
            return embedding
        return None
        
    async def delete_user_data(self, user_id: str, db: AsyncSession) -> None:
        if not db:
            return
            
        # Delete embedding
        await db.execute(text("DELETE FROM user_embeddings WHERE user_id = :user_id"), {"user_id": user_id})
        # Delete consent records
        await db.execute(text("DELETE FROM consent_records WHERE user_id = :user_id"), {"user_id": user_id})
        await db.commit()

user_service = UserService()
