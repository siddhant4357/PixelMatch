import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PrivacyService:
    async def create_consent(self, user_id: str, room_id: str, db: AsyncSession) -> None:
        """
        Record user consent for a specific room and bump global embedding expiration.
        """
        if not db:
            return
            
        # 1. Insert/update consent record
        consent_query = text("""
            INSERT INTO consent_records (user_id, room_id, purpose, expires_at)
            VALUES (:user_id, :room_id, 'photo_search', now() + interval '7 days')
            ON CONFLICT (id) DO NOTHING -- wait, id is uuid. We shouldn't conflict on id.
            -- Actually, let's just insert a new record or rely on a unique constraint if we had one.
            -- Since we don't have a unique constraint on (user_id, room_id) in consent_records, 
            -- we'll just insert a new one and maybe clean up old ones later.
        """)
        
        # Wait, let's do a simple insert. If they consent again, we just insert another record.
        await db.execute(text("""
            INSERT INTO consent_records (user_id, room_id, purpose, expires_at)
            VALUES (:user_id, :room_id, 'photo_search', now() + interval '7 days')
        """), {
            "user_id": user_id,
            "room_id": room_id
        })
        
        # 2. Bump user's global embedding expiration to now + 7 days
        # We only push the expiration FORWARD, never backwards.
        bump_query = text("""
            UPDATE user_embeddings
            SET expires_at = GREATEST(expires_at, now() + interval '7 days')
            WHERE user_id = :user_id
        """)
        # Note: If expires_at is NULL initially, GREATEST might return NULL.
        # Let's handle the NULL case explicitly.
        bump_query = text("""
            UPDATE user_embeddings
            SET expires_at = CASE 
                WHEN expires_at IS NULL THEN now() + interval '7 days'
                ELSE GREATEST(expires_at, now() + interval '7 days')
            END
            WHERE user_id = :user_id
        """)
        await db.execute(bump_query, {"user_id": user_id})
        await db.commit()

    async def has_consent(self, user_id: str, room_id: str, db: AsyncSession) -> bool:
        """
        Check if the user has an active (unexpired, unrevoked) consent for this room.
        """
        if not db:
            return True # Mock for local dev
            
        query = text("""
            SELECT 1 FROM consent_records
            WHERE user_id = :user_id 
              AND room_id = :room_id
              AND revoked_at IS NULL
              AND expires_at > now()
            LIMIT 1
        """)
        result = await db.execute(query, {
            "user_id": user_id,
            "room_id": room_id
        })
        return result.fetchone() is not None

privacy_service = PrivacyService()
