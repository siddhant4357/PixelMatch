import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

# Load env before DB connects
load_dotenv()

# Add the parent directory to sys.path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from db.database import get_db, async_session_maker, init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("cleanup_cron")

async def run_cleanup():
    logger.info("Starting TTL cleanup cron job...")
    
    if not async_session_maker:
        logger.error("Database connection not initialized. Exiting.")
        return
        
    async with async_session_maker() as db:
        # 1. Delete expired user embeddings
        # (This implies the user has no active events extending their TTL)
        embedding_query = text("""
            DELETE FROM user_embeddings 
            WHERE expires_at < now()
            RETURNING user_id
        """)
        
        result = await db.execute(embedding_query)
        deleted_embeddings = result.fetchall()
        logger.info(f"Deleted {len(deleted_embeddings)} expired user embeddings.")
        
        # 2. Optionally delete expired consent records
        # If a consent record itself expired, we delete it.
        consent_query = text("""
            DELETE FROM consent_records
            WHERE expires_at < now()
            RETURNING id
        """)
        result = await db.execute(consent_query)
        deleted_consents = result.fetchall()
        logger.info(f"Deleted {len(deleted_consents)} expired consent records.")
        
        await db.commit()

    logger.info("TTL cleanup cron job finished successfully.")

if __name__ == "__main__":
    # Ensure the DB URL is picked up correctly from environment
    asyncio.run(run_cleanup())
