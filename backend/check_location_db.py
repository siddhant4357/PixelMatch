"""
Quick script to check what's in the location database.
"""
import pickle
from pathlib import Path

db_path = Path("data/chromadb/location_db.pkl")

if db_path.exists():
    with open(db_path, 'rb') as f:
        locations = pickle.load(f)
    
    print(f"\n📊 Location Database Stats:")
    print(f"Total photos with location data: {len(locations)}")
    print(f"\n📸 Photos in database:")
    
    for photo_path, metadata in locations.items():
        filename = Path(photo_path).name
        print(f"\n  • {filename}")
        print(f"    GPS: {metadata.get('latitude')}, {metadata.get('longitude')}")
        print(f"    Location: {metadata.get('location_name', 'None')}")
        print(f"    Timestamp: {metadata.get('timestamp', 'None')}")
        print(f"    Camera: {metadata.get('camera_make', 'None')} {metadata.get('camera_model', 'None')}")
else:
    print("❌ Location database not found!")
    print("   Run: python main.py and upload photos via Admin panel")
