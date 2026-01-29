"""
AI-Powered Search Service.
Uses Groq AI to understand natural language queries and search photos.
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import logging

from models.vector_db import get_vector_db
from models.location_db import get_location_db
from utils.exif_extractor import EXIFExtractor

logger = logging.getLogger(__name__)

# Session storage (in-memory for now, use Redis for production)
_sessions = {}


class AISearchService:
    """Service for AI-powered photo search with natural language."""
    
    def __init__(self):
        """Initialize AI search service."""
        self.vector_db = get_vector_db()
        self.location_db = get_location_db()
        
        # Initialize Groq client (lazy loading)
        self.groq_client = None
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.ai_model = os.getenv("AI_MODEL", "llama-3.3-70b-versatile")
        
        logger.info("AI Search Service initialized")
    
    def _get_groq_client(self):
        """Get or create Groq client (lazy loading)."""
        if self.groq_client is None and self.groq_api_key and self.groq_api_key != "your_groq_api_key_here":
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_api_key)
                logger.info("Groq AI client initialized")
            except ImportError:
                logger.error("Groq library not installed. Run: pip install groq")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        return self.groq_client
    
    def create_session(self, face_embedding: List[float], selfie_filename: str) -> str:
        """
        Create a search session with user's face embedding.
        
        Args:
            face_embedding: User's face embedding from selfie
            selfie_filename: Original selfie filename
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        
        _sessions[session_id] = {
            'face_embedding': face_embedding,
            'selfie_filename': selfie_filename,
            'created_at': datetime.now(),
            'chat_history': []
        }
        
        logger.info(f"Created session {session_id} for {selfie_filename}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data."""
        session = _sessions.get(session_id)
        
        if session:
            # Check timeout
            timeout_minutes = int(os.getenv("SESSION_TIMEOUT_MINUTES", 30))
            if datetime.now() - session['created_at'] > timedelta(minutes=timeout_minutes):
                del _sessions[session_id]
                logger.info(f"Session {session_id} expired")
                return None
        
        return session
    
    def parse_query_with_ai(self, user_query: str, available_locations: List[str]) -> Dict:
        """
        Use Groq AI to parse user's natural language query.
        
        Args:
            user_query: User's search query
            available_locations: List of available location names
            
        Returns:
            Parsed criteria: {
                'location': str or None,
                'date_range': tuple or None,
                'keywords': list,
                'show_all': bool
            }
        """
        client = self._get_groq_client()
        
        if not client:
            # Fallback to simple parsing if AI not available
            logger.warning("Groq AI not available, using simple parsing")
            return self._simple_parse_query(user_query, available_locations)
        
        # Build system prompt
        current_year = datetime.now().year
        system_prompt = f"""You are a photo search assistant. Parse the user's query and extract search criteria.

IMPORTANT: Current year is {current_year}. If user mentions a month without a year, assume {current_year}.

Available photo locations: {', '.join([loc for loc in available_locations if loc]) if available_locations else 'None'}

Extract:
1. Location (if mentioned, match to available locations)
2. Date/time range (if mentioned, convert to ISO format)
3. Keywords (event types, activities, etc.)
4. If user wants all photos (no specific criteria)

Respond ONLY with valid JSON:
{{
    "location": "location name or null",
    "date_start": "YYYY-MM-DD or null",
    "date_end": "YYYY-MM-DD or null",
    "keywords": ["keyword1", "keyword2"],
    "show_all": true/false,
    "confidence": 0.0-1.0
}}"""
        
        try:
            response = client.chat.completions.create(
                model=self.ai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.1,  # Low temperature for consistent parsing
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if "```json" in ai_response:
                ai_response = ai_response.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response:
                ai_response = ai_response.split("```")[1].split("```")[0].strip()
            
            parsed = json.loads(ai_response)
            
            logger.info(f"AI parsed query: {parsed}")
            return {
                'location': parsed.get('location'),
                'date_range': (parsed.get('date_start'), parsed.get('date_end')),
                'keywords': parsed.get('keywords', []),
                'show_all': parsed.get('show_all', False),
                'confidence': parsed.get('confidence', 0.8)
            }
            
        except Exception as e:
            logger.error(f"AI parsing failed: {e}, falling back to simple parsing")
            return self._simple_parse_query(user_query, available_locations)
    
    def _simple_parse_query(self, user_query: str, available_locations: List[str]) -> Dict:
        """
        Simple keyword-based query parsing (fallback).
        
        Args:
            user_query: User's query
            available_locations: Available locations
            
        Returns:
            Parsed criteria
        """
        query_lower = user_query.lower()
        
        logger.info(f"[SIMPLE PARSER] Parsing query: '{user_query}'")
        
        # Check for location match (filter out None values)
        location = None
        valid_locations = [loc for loc in available_locations if loc]
        for loc in valid_locations:
            if loc.lower() in query_lower:
                location = loc
                break
        
        # Check for \"all photos\" intent
        show_all = any(phrase in query_lower for phrase in [
            'all photos', 'all my photos', 'everything', 'show all'
        ])
        
        # Simple date parsing
        date_start, date_end = None, None
        current_year = datetime.now().year
        
        # Month names
        months = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9, 'sept': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12
        }
        
        # Check for month names
        for month_name, month_num in months.items():
            if month_name in query_lower:
                # Extract year if present
                import re
                year_match = re.search(r'20\d{2}', user_query)
                year = int(year_match.group()) if year_match else current_year
                
                # Set date range for the entire month
                date_start = f"{year}-{month_num:02d}-01"
                # Last day of month
                if month_num == 12:
                    date_end = f"{year}-12-31"
                else:
                    from calendar import monthrange
                    last_day = monthrange(year, month_num)[1]
                    date_end = f"{year}-{month_num:02d}-{last_day}"
                
                logger.info(f"[SIMPLE PARSER] Detected month: {month_name} -> {date_start} to {date_end}")
                break
        
        # Extract simple keywords
        keywords = []
        keyword_patterns = ['beach', 'party', 'wedding', 'birthday', 'vacation', 'trip']
        for kw in keyword_patterns:
            if kw in query_lower:
                keywords.append(kw)
        
        result = {
            'location': location,
            'date_range': (date_start, date_end),
            'keywords': keywords,
            'show_all': show_all,
            'confidence': 0.5
        }
        
        logger.info(f"[SIMPLE PARSER] Result: {result}")
        return result
    
    def generate_ai_response(
        self,
        user_query: str,
        search_results: List[Dict],
        search_criteria: Dict
    ) -> str:
        """
        Generate natural language response using AI.
        
        Args:
            user_query: User's original query
            search_results: Search results
            search_criteria: Parsed search criteria
            
        Returns:
            AI-generated response text
        """
        client = self._get_groq_client()
        
        if not client:
            # Fallback to simple response
            return self._simple_response(user_query, search_results, search_criteria)
        
        # Build context
        result_count = len(search_results)
        locations_found = set()
        dates_found = set()
        
        for result in search_results[:10]:  # Sample first 10
            if result.get('location_name'):
                locations_found.add(result['location_name'])
            if result.get('timestamp'):
                dates_found.add(result['timestamp'][:10])  # Just date
        
        context = f"""User query: "{user_query}"
Search criteria: {json.dumps(search_criteria, indent=2)}
Results found: {result_count} photos
Locations in results: {', '.join(locations_found) if locations_found else 'No location data'}
Dates in results: {', '.join(sorted(dates_found)[:5]) if dates_found else 'No date data'}"""
        
        system_prompt = """You are a friendly photo search assistant. 
Generate a SHORT, natural response (1 sentence max, 15 words or less).
Be helpful and encouraging.
NO suggestions about "show_all" or technical terms.
Use 1 emoji max.

Examples:
- Found photos: "Found 5 photos from Paris! 📸"
- No results: "No photos from that date. Try 'show all my photos'?"
- Location + date: "Found 3 photos from Paris in January! 🎉"
"""
        
        try:
            response = client.chat.completions.create(
                model=self.ai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"AI generated response: {ai_response}")
            return ai_response
            
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return self._simple_response(user_query, search_results, search_criteria)
    
    def _simple_response(
        self,
        user_query: str,
        search_results: List[Dict],
        search_criteria: Dict
    ) -> str:
        """Generate simple response without AI."""
        count = len(search_results)
        
        if count == 0:
            return "No photos found. Try 'show all my photos'? 📸"
        
        location = search_criteria.get('location')
        if location:
            return f"Found {count} photo{'s' if count != 1 else ''} from {location}! 📸"
        
        return f"Found {count} photo{'s' if count != 1 else ''}! 📸"
    
    def search_photos(
        self,
        session_id: str,
        user_query: str
    ) -> Dict:
        """
        Main search function combining AI understanding + photo search.
        
        Args:
            session_id: User's session ID
            user_query: Natural language query
            
        Returns:
            {
                'success': bool,
                'ai_message': str,
                'photos': list,
                'count': int,
                'criteria': dict,
                'error': str (if failed)
            }
        """
        # Get session
        session = self.get_session(session_id)
        if not session:
            return {
                'success': False,
                'error': 'Session expired. Please upload your selfie again.'
            }
        
        face_embedding = session['face_embedding']
        
        # Get available locations
        all_locations = self.location_db.get_all_locations()
        available_location_names = [loc['location_name'] for loc in all_locations]
        
        logger.info(f"[AI SEARCH] User query: '{user_query}'")
        logger.info(f"[AI SEARCH] Available locations: {available_location_names}")
        
        # Parse query with AI
        criteria = self.parse_query_with_ai(user_query, available_location_names)
        logger.info(f"[AI SEARCH] Parsed criteria: {criteria}")
        
        # Search by face first
        face_matches = self.vector_db.search_similar_faces(
            query_embedding=face_embedding,
            top_k=100,
            similarity_threshold=0.50
        )
        logger.info(f"[AI SEARCH] Face matches: {len(face_matches)} photos")
        
        # Filter by location if specified
        if criteria['location']:
            logger.info(f"[AI SEARCH] Filtering by location: {criteria['location']}")
            face_matches = self._filter_by_location(face_matches, criteria['location'])
            logger.info(f"[AI SEARCH] After location filter: {len(face_matches)} photos")
        
        # Filter by date if specified
        if criteria['date_range'][0] or criteria['date_range'][1]:
            logger.info(f"[AI SEARCH] Filtering by date range: {criteria['date_range']}")
            face_matches = self._filter_by_date(face_matches, criteria['date_range'])
            logger.info(f"[AI SEARCH] After date filter: {len(face_matches)} photos")
        
        # Generate AI response
        ai_message = self.generate_ai_response(user_query, face_matches, criteria)
        
        # Add to chat history
        session['chat_history'].append({
            'user': user_query,
            'ai': ai_message,
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'success': True,
            'ai_message': ai_message,
            'photos': face_matches[:50],  # Limit to 50 results
            'count': len(face_matches),
            'criteria': criteria
        }
    
    def _filter_by_location(self, matches: List[Dict], location_query: str) -> List[Dict]:
        """Filter matches by location."""
        filtered = []
        query_lower = location_query.lower()
        
        for match in matches:
            photo_path = match.get('photo_path')
            if not photo_path:
                continue
            
            # Get location from location_db
            location_data = self.location_db.locations.get(photo_path)
            if location_data:
                location_name = location_data.get('location_name')
                # Skip if location_name is None or empty
                if location_name and query_lower in location_name.lower():
                    match['location_name'] = location_name
                    match['latitude'] = location_data.get('latitude')
                    match['longitude'] = location_data.get('longitude')
                    filtered.append(match)
        
        return filtered
    
    def _filter_by_date(self, matches: List[Dict], date_range: Tuple) -> List[Dict]:
        """Filter matches by date range."""
        start_date, end_date = date_range
        filtered = []
        
        logger.info(f"Filtering {len(matches)} photos by date range: {start_date} to {end_date}")
        
        for match in matches:
            photo_path = match.get('photo_path')
            if not photo_path:
                continue
            
            # Get timestamp from location_db
            location_data = self.location_db.locations.get(photo_path)
            timestamp = None
            
            if location_data and location_data.get('timestamp'):
                timestamp = location_data['timestamp']
            else:
                # Fallback: Try to extract timestamp directly from EXIF
                try:
                    from utils.exif_extractor import EXIFExtractor
                    metadata = EXIFExtractor.extract_metadata(photo_path)
                    timestamp = metadata.get('timestamp')
                except Exception as e:
                    logger.debug(f"Could not extract timestamp from {photo_path}: {e}")
            
            if timestamp:
                try:
                    # Parse timestamp (format: "2026:01:15 16:55:58")
                    photo_date = date_parser.parse(timestamp.replace(':', '-', 2)).date()
                    
                    # Check date range
                    if start_date:
                        start = date_parser.parse(start_date).date()
                        if photo_date < start:
                            logger.debug(f"Photo {photo_path} date {photo_date} before {start}")
                            continue
                    
                    if end_date:
                        end = date_parser.parse(end_date).date()
                        if photo_date > end:
                            logger.debug(f"Photo {photo_path} date {photo_date} after {end}")
                            continue
                    
                    match['timestamp'] = timestamp
                    filtered.append(match)
                    logger.debug(f"Photo {photo_path} matches date range: {photo_date}")
                    
                except Exception as e:
                    logger.warning(f"Failed to parse date for {photo_path}: {e}")
                    continue
            else:
                logger.debug(f"No timestamp found for {photo_path}")
        
        logger.info(f"Date filter: {len(filtered)} photos match out of {len(matches)}")
        return filtered
        
        return filtered


# Global instance
_ai_search_service = None


def get_ai_search_service() -> AISearchService:
    """Get or create global AI search service instance."""
    global _ai_search_service
    if _ai_search_service is None:
        _ai_search_service = AISearchService()
    return _ai_search_service
