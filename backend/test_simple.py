"""
Simple test - no unicode issues.
"""
import sys
sys.path.insert(0, '.')

from services.ai_search_service import get_ai_search_service
import numpy as np
import json

# Get service
ai_service = get_ai_search_service()

# Create session
fake_embedding = np.random.rand(1024).tolist()
session_id = ai_service.create_session(fake_embedding, "test.jpg")

# Test query
result = ai_service.search_photos(session_id, "show me jan pics")

# Write results to file
with open('test_results.json', 'w') as f:
    json.dump({
        'success': result.get('success'),
        'count': result.get('count'),
        'criteria': result.get('criteria'),
        'photo_count': len(result.get('photos', []))
    }, f, indent=2)

print("Results written to test_results.json")
