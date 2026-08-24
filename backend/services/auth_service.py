import os
import jwt
from jwt.algorithms import RSAAlgorithm
import httpx
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any
from db.database import get_db
import json
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()
CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY")
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

class ClerkAuthService:
    def __init__(self):
        self.jwks = None
        
    async def fetch_jwks(self):
        if self.jwks:
            return self.jwks
            
        try:
            # You can find the JWKS URL in Clerk Dashboard -> API Keys -> Advanced
            # Usually it's https://clerk.<domain>/.well-known/jwks.json
            # For simplicity, we can fetch it via the frontend domain or Clerk backend API
            if not CLERK_PUBLISHABLE_KEY:
                logger.warning("CLERK_PUBLISHABLE_KEY not set. Auth will fail.")
                return None
                
            # Extract domain from publishable key (pk_test_... or pk_live_...)
            import base64
            # clerk pk is base64 encoded string of the domain with a prefix
            try:
                decoded = base64.b64decode(CLERK_PUBLISHABLE_KEY.split('_')[2]).decode('utf-8')
                domain = decoded.replace('$', '')
                jwks_url = f"https://{domain}/.well-known/jwks.json"
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(jwks_url)
                    if response.status_code == 200:
                        self.jwks = response.json()
                        return self.jwks
            except Exception as e:
                logger.error(f"Error parsing Clerk publishable key: {e}")
                
        except Exception as e:
            logger.error(f"Failed to fetch Clerk JWKS: {e}")
        return None

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify Clerk JWT and return payload"""
        jwks = await self.fetch_jwks()
        if not jwks:
            # Fallback if JWKS fetch fails, but requires SECRET_KEY setup in PyJWT 
            # Or just use the Clerk SDK / API endpoint to verify
            # As a fallback, if we have the secret key, we can call Clerk API to get user info
            if CLERK_SECRET_KEY:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "https://api.clerk.com/v1/users/me",
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    if response.status_code == 200:
                        # This works differently, actually /v1/users/me expects session token?
                        pass
            raise HTTPException(status_code=401, detail="Unable to verify auth token")
            
        try:
            # Get the unverified header to find the kid
            unverified_header = jwt.get_unverified_header(token)
            
            # Find the matching key in JWKS
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
                    
            if not rsa_key:
                # Force refresh JWKS if key not found
                self.jwks = None
                jwks = await self.fetch_jwks()
                if jwks:
                    for key in jwks["keys"]:
                        if key["kid"] == unverified_header["kid"]:
                            rsa_key = {
                                "kty": key["kty"],
                                "kid": key["kid"],
                                "use": key["use"],
                                "n": key["n"],
                                "e": key["e"]
                            }
                
            if rsa_key:
                # PyJWT v2.x: Use RSAAlgorithm.from_jwk() with a JSON string
                public_key = RSAAlgorithm.from_jwk(json.dumps(rsa_key))
                payload = jwt.decode(
                    token,
                    public_key,
                    algorithms=["RS256"],
                    options={"verify_aud": False},
                    leeway=60
                )
                return payload
            else:
                raise ValueError("Matching RSA key not found in JWKS")
                
        except Exception as e:
            logger.error(f"Token verification failed ({type(e).__name__}): {str(e)}")
            raise HTTPException(status_code=401, detail=f"Invalid auth token: {str(e)}")

    async def get_or_create_user(self, payload: Dict[str, Any], db: AsyncSession) -> Dict:
        """Upsert user in DB based on Clerk payload"""
        if not db:
            # Mock user if DB is down
            return {"id": "mock-uuid", "clerk_id": payload.get("sub")}
            
        clerk_id = payload.get("sub")
        
        # In a real Clerk JWT, email might not be directly in the payload depending on config,
        # but often it is, or we can fetch it. We will use a placeholder if not present.
        email = payload.get("email", "unknown@example.com")
        name = payload.get("name", "User")
        
        query = text("""
            INSERT INTO users (clerk_id, email, name) 
            VALUES (:clerk_id, :email, :name)
            ON CONFLICT (clerk_id) DO UPDATE SET email = EXCLUDED.email, name = EXCLUDED.name
            RETURNING id, clerk_id, email, name, avatar_url
        """)
        
        result = await db.execute(query, {"clerk_id": clerk_id, "email": email, "name": name})
        await db.commit()
        row = result.fetchone()
        return dict(row._mapping)

auth_service = ClerkAuthService()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db)
):
    """FastAPI Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = await auth_service.verify_token(token)
    user = await auth_service.get_or_create_user(payload, db)
    return user
