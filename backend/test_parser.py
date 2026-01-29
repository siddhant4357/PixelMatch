"""
Test simple parser directly.
"""
import sys
sys.path.insert(0, '.')

from services.ai_search_service import AISearchService
from datetime import datetime

# Create service
service = AISearchService()

# Test simple parser directly
result = service._simple_parse_query("show me jan pics", [])

print(f"Current year: {datetime.now().year}")
print(f"Query: 'show me jan pics'")
print(f"Parsed result:")
print(f"  date_range: {result['date_range']}")
print(f"  show_all: {result['show_all']}")
print(f"  location: {result['location']}")
