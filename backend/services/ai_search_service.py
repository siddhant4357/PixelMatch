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
    
    def __init__(self, room_id: str = None):
        """Initialize AI search service."""
        self.room_id = room_id
        self.vector_db = get_vector_db(room_id)
        self.location_db = get_location_db(room_id)
        
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
        
        First classifies intent as 'chat' (greetings, thanks, help) or 'search'.
        If 'chat', returns a friendly reply. If 'search', extracts filters.
        Auto-corrects typos before extraction.
        
        Args:
            user_query: User's search query
            available_locations: List of available location names
            
        Returns:
            Parsed criteria dict with 'intent' field.
        """
        client = self._get_groq_client()
        
        if not client:
            logger.warning("Groq AI not available, using simple parsing")
            return self._simple_parse_query(user_query, available_locations)
        
        current_year = datetime.now().year
        system_prompt = f"""You are a photo search assistant embedded in PixelMatch. Parse the user's message.

STEP 1: Auto-correct any typos in the message before analyzing. E.g. "jasalmer" → "Jaisalmer", "januray" → "January".

STEP 2: Classify the intent:
- "chat" = greetings, thanks, help requests, questions about the app, or anything NOT asking to search for specific photos. Examples: "hi", "hello", "thanks", "what can you do?", "how does this work?", "help"
- "search" = any request to find, show, display, or get photos. Examples: "show me photos from Jaisalmer", "find my January photos", "photos from my iPhone", "show all", "all pics of 2026"

STEP 3: If intent is "search", extract filters:
- location: city/place name mentioned (e.g. "Jaisalmer", "Paris") — raw place name, NOT matched to list
- date_start / date_end: ISO date range.
  - If user mentions a FULL YEAR only (e.g. "2026", "pics of 2025"), set date_start="YYYY-01-01" and date_end="YYYY-12-31".
  - If user mentions a YEAR RANGE (e.g. "2025 to 2026", "from 2024 to 2026"), set date_start="YYYY-01-01" and date_end="YYYY-12-31" covering the full range.
  - If user mentions MONTH + YEAR (e.g. "January 2025"), set exact month range.
  - Leave null ONLY if user gives NO time reference at all.
- year_specified: true if user mentioned any year explicitly.
- month_only: true if user mentioned ONLY a month name with no year. In this case set month_number (1-12) and leave date_start/date_end null.
- month_number: integer 1-12 if month_only is true, else null.
- device_make: camera brand if mentioned (e.g. "Apple", "Samsung", "OnePlus"). Normalize to brand name.
- device_model: specific model if mentioned.
- show_all: true ONLY if user explicitly says "all photos", "everything", "all my photos", "all pics" WITH NO date/location filter. If user says "all pics of 2026" that is NOT show_all — it is a year filter.
- keywords: other activity/event keywords (beach, party, wedding, etc.)

Available known photo locations for context: {', '.join([loc for loc in available_locations if loc]) if available_locations else 'None'}

Respond ONLY with valid JSON, no other text:
{{
    "intent": "chat" | "search",
    "chat_reply": "friendly response if intent is chat, else null",
    "corrected_query": "the typo-corrected version of the user query",
    "location": "place name or null",
    "date_start": "YYYY-MM-DD or null",
    "date_end": "YYYY-MM-DD or null",
    "year_specified": false,
    "month_only": false,
    "month_number": null,
    "device_make": "brand name or null",
    "device_model": "model name or null",
    "keywords": [],
    "show_all": false,
    "confidence": 0.0
}}"""
        
        try:
            response = client.chat.completions.create(
                model=self.ai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.1,
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

            # Determine filtering mode:
            month_only = parsed.get('month_only', False)
            month_number = parsed.get('month_number')
            year_specified = parsed.get('year_specified', False)
            date_start = parsed.get('date_start')
            date_end = parsed.get('date_end')

            # If AI gave a date range but year was NOT explicitly specified,
            # convert to month_only mode so we don't filter on the wrong year.
            if date_start and not year_specified and not month_only:
                try:
                    month_number = int(date_start[5:7])
                    month_only = True
                    date_start = None
                    date_end = None
                    logger.info(f"[AI PARSE] Year not specified — switching to month_only mode (month={month_number})")
                except Exception:
                    pass

            return {
                'intent': parsed.get('intent', 'search'),
                'chat_reply': parsed.get('chat_reply'),
                'corrected_query': parsed.get('corrected_query', user_query),
                'location': parsed.get('location'),
                'date_range': (date_start, date_end),
                'month_only': month_only,
                'month_number': month_number,
                'device_make': parsed.get('device_make'),
                'device_model': parsed.get('device_model'),
                'keywords': parsed.get('keywords', []),
                'show_all': parsed.get('show_all', False),
                'confidence': parsed.get('confidence', 0.8)
            }
            
        except Exception as e:
            logger.error(f"AI parsing failed: {e}, falling back to simple parsing")
            return self._simple_parse_query(user_query, available_locations)
    
    def _simple_parse_query(self, user_query: str, available_locations: List[str]) -> Dict:
        """
        Simple keyword-based query parsing (fallback when AI not available).
        """
        query_lower = user_query.lower().strip()
        
        logger.info(f"[SIMPLE PARSER] Parsing query: '{user_query}'")
        
        # Detect conversational intent
        chat_triggers = [
            'hi', 'hello', 'hey', 'hie', 'helo', 'howdy',
            'thanks', 'thank you', 'ty', 'thx',
            'help', 'what can you do', 'how does this work',
            'good morning', 'good evening', 'good night',
            'bye', 'goodbye', 'ok', 'okay', 'cool', 'nice'
        ]
        is_chat = any(query_lower == trigger or query_lower.startswith(trigger + ' ') or query_lower.startswith(trigger + '!') for trigger in chat_triggers)
        
        if is_chat:
            return {
                'intent': 'chat',
                'chat_reply': "Hello! 👋 Ask me to find your photos by location, date, or device. Try: \"Show my Jaisalmer photos\" or \"Show January photos\".",
                'corrected_query': user_query,
                'location': None,
                'date_range': (None, None),
                'device_make': None,
                'device_model': None,
                'keywords': [],
                'show_all': False,
                'confidence': 0.9
            }
        
        # Check for location match (filter out None values)
        location = None
        valid_locations = [loc for loc in available_locations if loc]
        for loc in valid_locations:
            if loc.lower() in query_lower:
                location = loc
                break
        
        # If no known location matched, try to extract any place name from query
        # (simple heuristic: word after "from"/"in"/"at" that's capitalized)
        if not location:
            import re
            place_match = re.search(r'\b(?:from|in|at|near)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', user_query)
            if place_match:
                location = place_match.group(1)

        # Check for "all photos" intent
        show_all = any(phrase in query_lower for phrase in [
            'all photos', 'all my photos', 'everything', 'show all'
        ])
        
        # Device detection
        device_make = None
        device_model = None
        device_brands = {
            'iphone': 'Apple', 'apple': 'Apple',
            'samsung': 'Samsung', 'galaxy': 'Samsung',
            'oneplus': 'OnePlus', 'one plus': 'OnePlus',
            'xiaomi': 'Xiaomi', 'mi ': 'Xiaomi', 'redmi': 'Xiaomi',
            'pixel': 'Google', 'google': 'Google',
            'oppo': 'OPPO', 'vivo': 'vivo', 'realme': 'realme',
        }
        for keyword, brand in device_brands.items():
            if keyword in query_lower:
                device_make = brand
                break
        
        # Simple date parsing — handle year-only and year-range queries too
        date_start, date_end = None, None
        month_only_flag = False
        month_number_val = None
        current_year = datetime.now().year

        import re as _re
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

        # Detect year-range: "2025 to 2026", "from 2024 to 2026"
        year_range_match = _re.search(r'(20\d{2})\s*(?:to|-|through|until)\s*(20\d{2})', query_lower)
        # Detect single year: "2026", "pics of 2025"
        single_year_match = _re.search(r'\b(20\d{2})\b', user_query) if not year_range_match else None

        # Check for month name first
        found_month = False
        for month_name, month_num in months.items():
            if month_name in query_lower:
                year_match = _re.search(r'20\d{2}', user_query)
                if year_match:
                    year = int(year_match.group())
                    from calendar import monthrange
                    last_day = monthrange(year, month_num)[1]
                    date_start = f"{year}-{month_num:02d}-01"
                    date_end = f"{year}-{month_num:02d}-{last_day}"
                    month_only_flag = False
                    month_number_val = None
                    logger.info(f"[SIMPLE PARSER] Month+year: {month_name} {year} -> {date_start} to {date_end}")
                else:
                    month_only_flag = True
                    month_number_val = month_num
                    logger.info(f"[SIMPLE PARSER] Month only: {month_name} -> month_number={month_num}")
                found_month = True
                break

        if not found_month:
            if year_range_match:
                year_start = int(year_range_match.group(1))
                year_end = int(year_range_match.group(2))
                date_start = f"{year_start}-01-01"
                date_end = f"{year_end}-12-31"
                logger.info(f"[SIMPLE PARSER] Year range: {year_start}-{year_end}")
            elif single_year_match:
                year = int(single_year_match.group(1))
                date_start = f"{year}-01-01"
                date_end = f"{year}-12-31"
                logger.info(f"[SIMPLE PARSER] Year only: {year}")


        keywords = []
        keyword_patterns = ['beach', 'party', 'wedding', 'birthday', 'vacation', 'trip', 'concert', 'festival']
        for kw in keyword_patterns:
            if kw in query_lower:
                keywords.append(kw)
        
        result = {
            'intent': 'search',
            'chat_reply': None,
            'corrected_query': user_query,
            'location': location,
            'date_range': (date_start, date_end),
            'month_only': month_only_flag,
            'month_number': month_number_val,
            'device_make': device_make,
            'device_model': device_model,
            'keywords': keywords,
            'show_all': show_all,
            'confidence': 0.5
        }
    
    def generate_ai_response(
        self,
        user_query: str,
        search_results: List[Dict],
        search_criteria: Dict
    ) -> str:
        """
        Generate natural language response using AI.
        """
        client = self._get_groq_client()
        
        if not client:
            return self._simple_response(user_query, search_results, search_criteria)
        
        result_count = len(search_results)
        locations_found = set()
        dates_found = set()
        
        for result in search_results[:10]:
            if result.get('location_name'):
                locations_found.add(result['location_name'])
            if result.get('timestamp'):
                dates_found.add(result['timestamp'][:10])
        
        context = f"""User query: "{user_query}"
Search criteria: {json.dumps({k: v for k, v in search_criteria.items() if k not in ('chat_reply', 'corrected_query')}, indent=2)}
Results found: {result_count} photos
Locations in results: {', '.join(locations_found) if locations_found else 'No location data'}
Dates in results: {', '.join(sorted(dates_found)[:5]) if dates_found else 'No date data'}"""
        
        system_prompt = """You are a friendly photo search assistant. 
Generate a SHORT, natural response (1-2 sentences max, 20 words or less).
Be helpful and encouraging. Use 1 emoji max.

Examples:
- Found photos: "Found 5 photos from Jaisalmer! 📸"
- No results: "No photos found for that. Try asking differently!"
- Location + date: "Found 3 photos from Paris in January! 🎉"
- Device: "Found 8 photos taken on your iPhone! 📱"
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
            return "No photos found for that search. Try asking with a different date, location, or just say 'show all'! 📸"
        
        location = search_criteria.get('location')
        device = search_criteria.get('device_make')
        date_range = search_criteria.get('date_range', (None, None))
        show_all = search_criteria.get('show_all', False)

        if show_all:
            return f"Here are all {count} of your photo{'s' if count != 1 else ''}! 🎉"
        if location and date_range[0]:
            # Check if it's a full year range
            if date_range[0].endswith('-01-01') and (date_range[1] or '').endswith('-12-31'):
                year_s = date_range[0][:4]
                year_e = (date_range[1] or '')[:4]
                label = year_s if year_s == year_e else f"{year_s}–{year_e}"
                return f"Found {count} photo{'s' if count != 1 else ''} from {location} in {label}! 📍"
            month = date_range[0][5:7]
            month_name = datetime(1900, int(month), 1).strftime('%B')
            return f"Found {count} photo{'s' if count != 1 else ''} from {location} in {month_name}! 📸"
        if location:
            return f"Found {count} photo{'s' if count != 1 else ''} from {location}! 📍"
        if device:
            return f"Found {count} photo{'s' if count != 1 else ''} from your {device}! 📱"
        if date_range[0]:
            if date_range[0].endswith('-01-01') and (date_range[1] or '').endswith('-12-31'):
                year_s = date_range[0][:4]
                year_e = (date_range[1] or '')[:4]
                label = year_s if year_s == year_e else f"{year_s}–{year_e}"
                return f"Found {count} photo{'s' if count != 1 else ''} from {label}! 📅"
            month = date_range[0][5:7]
            month_name = datetime(1900, int(month), 1).strftime('%B')
            return f"Found {count} photo{'s' if count != 1 else ''} from {month_name}! 📅"
        if search_criteria.get('month_only') and search_criteria.get('month_number'):
            month_name = datetime(1900, search_criteria['month_number'], 1).strftime('%B')
            return f"Found {count} photo{'s' if count != 1 else ''} from {month_name}! 📅"
        
        return f"Found {count} photo{'s' if count != 1 else ''}! 📸"
    
    def search_photos(
        self,
        face_embedding: List[float],
        user_query: str
    ) -> Dict:
        """
        Main search function combining AI understanding + photo search.
        """
        
        # We don't have chat history anymore in session, so just create an empty list or ignore it
        chat_history = []
        
        # Get available locations
        all_locations = self.location_db.get_all_locations()
        available_location_names = [loc['location_name'] for loc in all_locations]
        
        logger.info(f"[AI SEARCH] User query: '{user_query}'")
        logger.info(f"[AI SEARCH] Available locations: {available_location_names}")
        
        # Parse query with AI
        criteria = self.parse_query_with_ai(user_query, available_location_names)
        logger.info(f"[AI SEARCH] Parsed criteria: {criteria}")
        
        # --- SHORT-CIRCUIT: Conversational / Chat intent ---
        if criteria.get('intent') == 'chat':
            chat_reply = criteria.get('chat_reply') or "Hello! 👋 Ask me to find your photos. Try: \"Show my Jaisalmer photos\" or \"Show January photos\"."
            chat_history.append({
                'user': user_query,
                'ai': chat_reply,
                'timestamp': datetime.now().isoformat()
            })
            return {
                'success': True,
                'intent': 'chat',
                'ai_message': chat_reply,
                'photos': [],        # Empty — no photo search triggered
                'count': 0,
                'criteria': criteria
            }
        
        # --- SEARCH INTENT: perform face + filter search ---

        # Step 0: show_all short-circuit — return all face matches with no filters
        if criteria.get('show_all') and not criteria.get('location') and not criteria['date_range'][0] and not criteria.get('device_make'):
            face_matches = self.vector_db.search_similar_faces(
                query_embedding=face_embedding,
                top_k=200,
                similarity_threshold=0.50
            )
            logger.info(f"[AI SEARCH] show_all: returning all {len(face_matches)} face matches")
            ai_message = self.generate_ai_response(user_query, face_matches, criteria)
            return {
                'success': True,
                'intent': 'search',
                'ai_message': ai_message,
                'photos': face_matches[:100],
                'count': len(face_matches),
                'criteria': criteria
            }

        # Step 1: Face match (baseline pool)
        face_matches = self.vector_db.search_similar_faces(
            query_embedding=face_embedding,
            top_k=200,
            similarity_threshold=0.50
        )
        logger.info(f"[AI SEARCH] Face matches: {len(face_matches)} photos")
        
        # Step 2: Location filter
        if criteria.get('location'):
            logger.info(f"[AI SEARCH] Filtering by location: {criteria['location']}")
            face_matches = self._filter_by_location(face_matches, criteria['location'])
            logger.info(f"[AI SEARCH] After location filter: {len(face_matches)} photos")
        
        # Step 3: Date filter
        # Three modes:
        #   show_all=True           → no date filter at all (handled above)
        #   month_only=True         → match photos by month number regardless of year
        #   date_range is set       → explicit date range (year specified, or year-only range)
        if criteria.get('month_only') and criteria.get('month_number'):
            logger.info(f"[AI SEARCH] Month-only filter: month={criteria['month_number']}")
            face_matches = self._filter_by_month(face_matches, criteria['month_number'])
            logger.info(f"[AI SEARCH] After month filter: {len(face_matches)} photos")
        elif criteria['date_range'][0] or criteria['date_range'][1]:
            logger.info(f"[AI SEARCH] Filtering by date range: {criteria['date_range']}")
            face_matches = self._filter_by_date(face_matches, criteria['date_range'])
            logger.info(f"[AI SEARCH] After date filter: {len(face_matches)} photos")
        
        # Step 4: Device filter
        if criteria.get('device_make') or criteria.get('device_model'):
            logger.info(f"[AI SEARCH] Filtering by device: {criteria.get('device_make')} {criteria.get('device_model')}")
            face_matches = self._filter_by_device(face_matches, criteria.get('device_make'), criteria.get('device_model'))
            logger.info(f"[AI SEARCH] After device filter: {len(face_matches)} photos")
        
        # Step 5: Generate AI response
        ai_message = self.generate_ai_response(user_query, face_matches, criteria)
        
        return {
            'success': True,
            'intent': 'search',
            'ai_message': ai_message,
            'photos': face_matches[:50],
            'count': len(face_matches),
            'criteria': criteria
        }
    
    def _filter_by_location(self, matches: List[Dict], location_query: str) -> List[Dict]:
        """
        Filter matches by location using both:
        1. GPS haversine radius matching (50 km radius) — resolves typed city name to coords
        2. String substring match on stored location_name — fallback / confirmation
        """
        query_lower = location_query.lower().strip()
        
        # Try to resolve the typed place name to GPS coordinates using reverse_geocoder
        query_coords = None
        try:
            import reverse_geocoder as rg
            # reverse_geocoder.search accepts lat/lon tuples, but we can search by name
            # by querying its internal city DB. We use a trick: search nearby major cities.
            # Actually reverse_geocoder doesn't support name->coords natively.
            # So we use geopy (online) or a simple lookup from our own stored data.
            pass
        except ImportError:
            pass
        
        # Try geopy to convert place name to coords (with timeout)
        try:
            from geopy.geocoders import Nominatim
            from geopy.exc import GeocoderTimedOut, GeocoderServiceError
            geolocator = Nominatim(user_agent="pixelmatch_search", timeout=3)
            geo_result = geolocator.geocode(location_query)
            if geo_result:
                query_coords = (geo_result.latitude, geo_result.longitude)
                logger.info(f"[LOCATION FILTER] Resolved '{location_query}' -> {query_coords}")
        except Exception as e:
            logger.warning(f"[LOCATION FILTER] Geocoding failed for '{location_query}': {e}")
        
        filtered = []
        seen_paths = set()
        
        for match in matches:
            photo_path = match.get('photo_path')
            if not photo_path:
                continue
            
            # Try filename-based lookup first (location_db keys may be just filename)
            import os
            photo_filename = os.path.basename(photo_path)
            location_data = self.location_db.locations.get(photo_path) or \
                            self.location_db.locations.get(photo_filename)
            
            if not location_data:
                continue
            
            matched = False
            
            # Method 1: GPS haversine match (if we resolved query coords AND photo has GPS)
            if query_coords and location_data.get('latitude') and location_data.get('longitude'):
                distance_km = self.location_db._calculate_distance(
                    query_coords[0], query_coords[1],
                    location_data['latitude'], location_data['longitude']
                )
                if distance_km <= 75:  # 75km radius — covers city + surrounding areas
                    matched = True
                    match['location_name'] = location_data.get('location_name')
                    match['latitude'] = location_data.get('latitude')
                    match['longitude'] = location_data.get('longitude')
                    match['distance_km'] = round(distance_km, 1)
                    logger.debug(f"[LOCATION FILTER] GPS match: {photo_filename} ({distance_km:.1f} km)")
            
            # Method 2: String substring match on stored location_name (fallback/supplement)
            if not matched:
                location_name = location_data.get('location_name', '')
                if location_name and query_lower in location_name.lower():
                    matched = True
                    match['location_name'] = location_name
                    match['latitude'] = location_data.get('latitude')
                    match['longitude'] = location_data.get('longitude')
                    logger.debug(f"[LOCATION FILTER] Name match: {photo_filename} in '{location_name}'")
            
            if matched and photo_path not in seen_paths:
                filtered.append(match)
                seen_paths.add(photo_path)
        
        return filtered
    
    def _filter_by_month(self, matches: List[Dict], month_number: int) -> List[Dict]:
        """
        Filter matches by month number only — ignoring the year completely.
        Used when user says "January" without specifying a year.
        """
        import os
        filtered = []
        logger.info(f"Month-only filter: looking for photos taken in month {month_number} (any year)")

        for match in matches:
            photo_path = match.get('photo_path')
            if not photo_path:
                continue

            photo_filename = os.path.basename(photo_path)
            location_data = self.location_db.locations.get(photo_path) or \
                            self.location_db.locations.get(photo_filename)
            timestamp = None

            if location_data and location_data.get('timestamp'):
                timestamp = location_data['timestamp']
            else:
                try:
                    from utils.exif_extractor import EXIFExtractor
                    metadata = EXIFExtractor.extract_metadata(photo_path)
                    timestamp = metadata.get('timestamp')
                except Exception:
                    pass

            if timestamp:
                try:
                    photo_date = date_parser.parse(timestamp.replace(':', '-', 2)).date()
                    if photo_date.month == month_number:
                        match['timestamp'] = timestamp
                        filtered.append(match)
                        logger.debug(f"Month match: {photo_filename} ({photo_date})")
                except Exception as e:
                    logger.warning(f"Failed to parse date for {photo_path}: {e}")
            else:
                logger.debug(f"No timestamp for {photo_filename} — skipping month filter")

        logger.info(f"Month filter (month={month_number}): {len(filtered)} photos matched out of {len(matches)}")
        return filtered

    def _filter_by_date(self, matches: List[Dict], date_range: Tuple) -> List[Dict]:
        """Filter matches by an EXPLICIT date range (year was specified by the user)."""
        start_date, end_date = date_range
        filtered = []
        
        logger.info(f"Filtering {len(matches)} photos by date range: {start_date} to {end_date}")
        
        for match in matches:
            photo_path = match.get('photo_path')
            if not photo_path:
                continue
            
            import os
            photo_filename = os.path.basename(photo_path)
            
            # Look up in location_db (try both full path and filename)
            location_data = self.location_db.locations.get(photo_path) or \
                            self.location_db.locations.get(photo_filename)
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
                    # Parse timestamp (EXIF format: "2025:01:15 16:55:58")
                    photo_date = date_parser.parse(timestamp.replace(':', '-', 2)).date()
                    
                    if start_date:
                        start = date_parser.parse(start_date).date()
                        if photo_date < start:
                            continue
                    
                    if end_date:
                        end = date_parser.parse(end_date).date()
                        if photo_date > end:
                            continue
                    
                    match['timestamp'] = timestamp
                    filtered.append(match)
                    logger.debug(f"Photo {photo_filename} matches date range: {photo_date}")
                    
                except Exception as e:
                    logger.warning(f"Failed to parse date for {photo_path}: {e}")
                    continue
            else:
                logger.debug(f"No timestamp found for {photo_path}")
        
        logger.info(f"Date filter: {len(filtered)} photos match out of {len(matches)}")
        return filtered
    
    def _filter_by_device(
        self,
        matches: List[Dict],
        device_make: Optional[str] = None,
        device_model: Optional[str] = None
    ) -> List[Dict]:
        """
        Filter matches by camera make/model stored in location_db.
        Case-insensitive substring match so "Apple" matches "Apple" or "APPLE".
        """
        filtered = []
        make_lower = device_make.lower().strip() if device_make else None
        model_lower = device_model.lower().strip() if device_model else None
        
        # Brand aliases (common user terms → stored EXIF values)
        make_aliases = {
            'apple': ['apple'],
            'samsung': ['samsung'],
            'oneplus': ['oneplus', 'one plus'],
            'google': ['google'],
            'xiaomi': ['xiaomi', 'redmi'],
            'oppo': ['oppo'],
            'vivo': ['vivo'],
            'realme': ['realme'],
            'huawei': ['huawei'],
            'nokia': ['nokia'],
            'motorola': ['motorola', 'moto'],
            'sony': ['sony'],
        }
        
        for match in matches:
            photo_path = match.get('photo_path')
            if not photo_path:
                continue
            
            import os
            photo_filename = os.path.basename(photo_path)
            location_data = self.location_db.locations.get(photo_path) or \
                            self.location_db.locations.get(photo_filename)
            
            if not location_data:
                continue
            
            stored_make = (location_data.get('camera_make') or '').lower()
            stored_model = (location_data.get('camera_model') or '').lower()
            
            make_ok = True
            model_ok = True
            
            if make_lower:
                # Check aliases
                aliases = make_aliases.get(make_lower, [make_lower])
                make_ok = any(alias in stored_make for alias in aliases)
            
            if model_lower:
                model_ok = model_lower in stored_model
            
            if make_ok and model_ok and (make_lower or model_lower):
                # At least one filter was set and both passed
                match['camera_make'] = location_data.get('camera_make')
                match['camera_model'] = location_data.get('camera_model')
                filtered.append(match)
                logger.debug(f"[DEVICE FILTER] Match: {photo_filename} ({stored_make} {stored_model})")
        
        return filtered


# Global instances (room_id -> instance)
_ai_search_services = {}


def get_ai_search_service(room_id: str = None) -> AISearchService:
    """Get or create AI search service instance for specific room."""
    global _ai_search_services
    key = room_id or 'default'
    
    if key not in _ai_search_services:
        _ai_search_services[key] = AISearchService(room_id)
        
    return _ai_search_services[key]
