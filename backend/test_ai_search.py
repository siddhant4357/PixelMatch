"""
Direct test of AI search to see what's happening.
"""
import sys
sys.path.insert(0, '.')

from services.ai_search_service import get_ai_search_service
from models.vector_db import get_vector_db
import numpy as np

# Get services
ai_service = get_ai_search_service()
vector_db = get_vector_db()

# Create a fake session with a random embedding
fake_embedding = np.random.rand(1024).tolist()
session_id = ai_service.create_session(fake_embedding, "test_selfie.jpg")

print(f"Created session: {session_id}\n")

# Test query
query = "show me photos of january"
print(f"Testing query: '{query}'\n")

result = ai_service.search_photos(session_id, query)

print(f"\nResults:")
print(f"  Success: {result.get('success')}")
print(f"  AI Message: {result.get('ai_message')}")
print(f"  Photo count: {result.get('count')}")
print(f"  Criteria: {result.get('criteria')}")
print(f"  Photos returned: {len(result.get('photos', []))}")

if result.get('photos'):
    print(f"\nPhotos:")
    for photo in result['photos'][:3]:
        print(f"  - {photo.get('photo_path')}")
        print(f"    Timestamp: {photo.get('timestamp', 'None')}")
