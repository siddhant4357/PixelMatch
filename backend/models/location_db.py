"""
Location Database for storing and searching photo locations.
Enables location-based photo search.
"""

import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import config
import logging

logger = logging.getLogger(__name__)


class LocationDB:
    """Database for storing photo locations and metadata."""
    
    def __init__(self, persist_dir: str = None):
        """
        Initialize location database.
        
        Args:
            persist_dir: Directory to persist the database
        """
        self.persist_dir = Path(persist_dir or config.CHROMA_PERSIST_DIR)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.persist_dir / "location_db.pkl"
        
        # Database structure:
        # {
        #     photo_path: {
        #         'latitude': float,
        #         'longitude': float,
        #         'location_name': str,
        #         'timestamp': str,
        #         'camera_make': str,
        #         'camera_model': str,
        #         'altitude': float
        #     }
        # }
        self.locations = {}
        
        # Load existing database
        self._load_db()
    
    def _load_db(self):
        """Load database from disk."""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'rb') as f:
                    self.locations = pickle.load(f)
                logger.info(f"Loaded location database with {len(self.locations)} photos")
            except Exception as e:
                logger.error(f"Failed to load location database: {e}")
                self.locations = {}
        else:
            logger.info("No existing location database found, starting fresh")
    
    def _save_db(self):
        """Save database to disk."""
        try:
            with open(self.db_path, 'wb') as f:
                pickle.dump(self.locations, f)
            logger.debug(f"Saved location database with {len(self.locations)} photos")
        except Exception as e:
            logger.error(f"Failed to save location database: {e}")
    
    def add_location(self, photo_path: str, metadata: Dict):
        """
        Add location metadata for a photo.
        
        Args:
            photo_path: Path to the photo
            metadata: Metadata dictionary from EXIF extractor
        """
        if metadata.get('has_location'):
            # Convert all values to JSON-serializable types (Fraction -> float)
            self.locations[photo_path] = {
                'latitude': float(metadata['latitude']) if metadata['latitude'] is not None else None,
                'longitude': float(metadata['longitude']) if metadata['longitude'] is not None else None,
                'location_name': metadata.get('location_name'),
                'timestamp': str(metadata.get('timestamp')) if metadata.get('timestamp') else None,
                'camera_make': str(metadata.get('camera_make')) if metadata.get('camera_make') else None,
                'camera_model': str(metadata.get('camera_model')) if metadata.get('camera_model') else None,
                'altitude': float(metadata.get('altitude')) if metadata.get('altitude') is not None else None
            }
            self._save_db()
            logger.info(f"Added location for {Path(photo_path).name}: "
                       f"{metadata['latitude']:.4f}, {metadata['longitude']:.4f}")
    
    def search_by_location(
        self,
        target_lat: float,
        target_lon: float,
        radius_km: float = 1.0
    ) -> List[Dict]:
        """
        Search for photos within a radius of target coordinates.
        
        Args:
            target_lat: Target latitude
            target_lon: Target longitude
            radius_km: Search radius in kilometers
            
        Returns:
            List of matching photos with metadata
        """
        matches = []
        
        for photo_path, metadata in self.locations.items():
            distance = self._calculate_distance(
                target_lat, target_lon,
                metadata['latitude'], metadata['longitude']
            )
            
            if distance <= radius_km:
                matches.append({
                    'photo_path': photo_path,
                    'distance_km': distance,
                    **metadata
                })
        
        # Sort by distance
        matches.sort(key=lambda x: x['distance_km'])
        
        logger.info(f"Found {len(matches)} photos within {radius_km}km of "
                   f"({target_lat:.4f}, {target_lon:.4f})")
        
        return matches
    
    def search_by_location_name(self, location_query: str) -> List[Dict]:
        """
        Search for photos by location name (fuzzy matching).
        
        Args:
            location_query: Location name to search for
            
        Returns:
            List of matching photos
        """
        matches = []
        query_lower = location_query.lower()
        
        for photo_path, metadata in self.locations.items():
            location_name = metadata.get('location_name', '')
            if location_name and query_lower in location_name.lower():
                matches.append({
                    'photo_path': photo_path,
                    **metadata
                })
        
        logger.info(f"Found {len(matches)} photos matching location '{location_query}'")
        
        return matches
    
    def get_all_locations(self) -> List[Dict]:
        """
        Get all unique locations with photo counts.
        
        Returns:
            List of locations with photo counts
        """
        location_groups = {}
        
        for photo_path, metadata in self.locations.items():
            location_name = metadata.get('location_name', 'Unknown')
            
            if location_name not in location_groups:
                location_groups[location_name] = {
                    'location_name': location_name,
                    'latitude': metadata['latitude'],
                    'longitude': metadata['longitude'],
                    'photo_count': 0,
                    'photos': []
                }
            
            location_groups[location_name]['photo_count'] += 1
            location_groups[location_name]['photos'].append(photo_path)
        
        return list(location_groups.values())
    
    def delete_by_photo(self, photo_path: str) -> bool:
        """
        Delete location data for a photo.
        
        Args:
            photo_path: Path to the photo
            
        Returns:
            True if deleted, False if not found
        """
        if photo_path in self.locations:
            del self.locations[photo_path]
            self._save_db()
            logger.info(f"Deleted location data for {Path(photo_path).name}")
            return True
        return False
    
    def reset(self):
        """Reset the entire location database."""
        self.locations = {}
        self._save_db()
        logger.info("Location database reset")
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        photos_with_location = len(self.locations)
        unique_locations = len(set(
            m.get('location_name', 'Unknown') 
            for m in self.locations.values()
        ))
        
        return {
            'total_photos_with_location': photos_with_location,
            'unique_locations': unique_locations
        }
    
    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two GPS coordinates using Haversine formula.
        
        Args:
            lat1, lon1: First coordinate
            lat2, lon2: Second coordinate
            
        Returns:
            Distance in kilometers
        """
        from math import radians, sin, cos, sqrt, atan2
        
        # Earth radius in kilometers
        R = 6371.0
        
        # Convert to radians
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        # Differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine formula
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        distance = R * c
        return distance


# Global instance
_location_db_instance = None


def get_location_db() -> LocationDB:
    """Get or create global location database instance."""
    global _location_db_instance
    if _location_db_instance is None:
        _location_db_instance = LocationDB()
    return _location_db_instance
