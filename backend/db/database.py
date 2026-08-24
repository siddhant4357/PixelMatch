import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

engine = None
async_session_maker = None

if DATABASE_URL:
    # Auto-correct the scheme if the user accidentally copied the default 'postgresql://'
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        
    from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
    
    # Parse the URL to clean up query parameters for asyncpg
    parsed = urlparse(DATABASE_URL)
    query_params = dict(parse_qsl(parsed.query))
    
    # asyncpg expects 'ssl=require' not 'sslmode=require'
    if 'sslmode' in query_params:
        query_params['ssl'] = query_params.pop('sslmode')
    
    # Neon serverless requires ssl
    if parsed.hostname and "neon.tech" in parsed.hostname and 'ssl' not in query_params:
        query_params['ssl'] = 'require'
        
    # Remove unsupported asyncpg parameters (like channel_binding)
    unsupported_keys = ['channel_binding', 'options']
    for key in unsupported_keys:
        query_params.pop(key, None)
        
    # Reconstruct the URL
    new_query = urlencode(query_params)
    DATABASE_URL = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
    
    engine = create_async_engine(
        DATABASE_URL, 
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300
    )
    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
else:
    logger.warning("DATABASE_URL is not set. Database integration will be disabled.")

async def get_db():
    """Dependency for FastAPI to get a DB session."""
    if not async_session_maker:
        yield None
        return
        
    async with async_session_maker() as session:
        yield session

async def init_db():
    """Run schema.sql to initialize tables."""
    if not engine:
        return
    try:
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path, "r") as f:
            sql = f.read()
            
        async with engine.begin() as conn:
            # We can execute multiple statements safely in asyncpg if we split them
            # or execute the whole block if using text() properly
            # In sqlalchemy 2.0 with asyncpg, running a large block of text might fail
            # Let's split by ';'
            statements = [s.strip() for s in sql.split(';') if s.strip()]
            for stmt in statements:
                await conn.execute(text(stmt))
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
