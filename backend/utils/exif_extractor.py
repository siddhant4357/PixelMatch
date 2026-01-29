"""
EXIF Metadata Extractor for Photos.
Extracts GPS location, timestamp, and other metadata from images.
"""

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from typing import Dict, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class EXIFExtractor:
    """Extract EXIF metadata from images."""
    
    @staticmethod
    def _get_decimal_coordinates(gps_info: dict) -> Optional[Tuple[float, float]]:
        """
        Convert GPS coordinates from degrees/minutes/seconds to decimal format.
        
        Args:
            gps_info: GPS information dictionary from EXIF
            
        Returns:
            Tuple of (latitude, longitude) in decimal format, or None
        """
        try:
            # Get latitude
            lat_deg = gps_info.get('GPSLatitude')
            lat_ref = gps_info.get('GPSLatitudeRef')
            
            # Get longitude
            lon_deg = gps_info.get('GPSLongitude')
            lon_ref = gps_info.get('GPSLongitudeRef')
            
            if not all([lat_deg, lat_ref, lon_deg, lon_ref]):
                return None
            
            # Convert to decimal
            lat = lat_deg[0] + lat_deg[1] / 60 + lat_deg[2] / 3600
            lon = lon_deg[0] + lon_deg[1] / 60 + lon_deg[2] / 3600
            
            # Apply direction (N/S, E/W)
            if lat_ref == 'S':
                lat = -lat
            if lon_ref == 'W':
                lon = -lon
                
            return (lat, lon)
            
        except Exception as e:
            logger.warning(f"Failed to parse GPS coordinates: {e}")
            return None
    
    @staticmethod
    def extract_metadata(image_path: str) -> Dict:
        """
        Extract all relevant metadata from an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing metadata:
            {
                'has_location': bool,
                'latitude': float or None,
                'longitude': float or None,
                'location_name': str or None,  # Reverse geocoded later
                'timestamp': str or None,
                'camera_make': str or None,
                'camera_model': str or None,
                'altitude': float or None
            }
        """
        metadata = {
            'has_location': False,
            'latitude': None,
            'longitude': None,
            'location_name': None,
            'timestamp': None,
            'camera_make': None,
            'camera_model': None,
            'altitude': None
        }
        
        try:
            image = Image.open(image_path)
            exif_data = image._getexif()
            
            if not exif_data:
                logger.info(f"No EXIF data found in {Path(image_path).name}")
                return metadata
            
            # Parse standard EXIF tags
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                
                if tag_name == 'DateTime' or tag_name == 'DateTimeOriginal':
                    metadata['timestamp'] = str(value)
                elif tag_name == 'Make':
                    metadata['camera_make'] = str(value)
                elif tag_name == 'Model':
                    metadata['camera_model'] = str(value)
                elif tag_name == 'GPSInfo':
                    # Parse GPS data
                    gps_info = {}
                    for gps_tag_id, gps_value in value.items():
                        gps_tag_name = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps_info[gps_tag_name] = gps_value
                    
                    # Extract coordinates
                    coords = EXIFExtractor._get_decimal_coordinates(gps_info)
                    if coords:
                        metadata['has_location'] = True
                        metadata['latitude'] = coords[0]
                        metadata['longitude'] = coords[1]
                        
                        # Extract altitude if available
                        if 'GPSAltitude' in gps_info:
                            metadata['altitude'] = float(gps_info['GPSAltitude'])
            
            logger.info(f"Extracted metadata from {Path(image_path).name}: "
                       f"Location={'Yes' if metadata['has_location'] else 'No'}, "
                       f"Timestamp={metadata['timestamp']}")
            
        except Exception as e:
            logger.error(f"Failed to extract EXIF from {image_path}: {e}")
        
        return metadata
    
    @staticmethod
    def reverse_geocode(latitude: float, longitude: float) -> Optional[str]:
        """
        Convert GPS coordinates to human-readable location name.
        Uses offline reverse_geocoder library (fast, no API limits).
        
        Args:
            latitude: Latitude in decimal format
            longitude: Longitude in decimal format
            
        Returns:
            Location name string (City, State, Country), or None if failed
        """
        try:
            import reverse_geocoder as rg
            
            # Query offline database
            result = rg.search((latitude, longitude), mode=1)  # mode=1 = single result
            
            if result and len(result) > 0:
                location = result[0]
                # Build location string: City, State, Country
                parts = []
                
                if location.get('name'):  # City name
                    parts.append(location['name'])
                if location.get('admin1'):  # State/Province
                    parts.append(location['admin1'])
                if location.get('cc'):  # Country code
                    parts.append(location['cc'])
                
                location_str = ', '.join(parts)
                logger.info(f"Reverse geocoded ({latitude:.4f}, {longitude:.4f}) -> {location_str}")
                return location_str
            
            return None
            
        except ImportError:
            logger.warning("reverse_geocoder not installed. Install with: pip install reverse_geocoder")
            # Fallback to geopy (online, slower)
            try:
                from geopy.geocoders import Nominatim
                geolocator = Nominatim(user_agent="pixelmatch_app")
                location = geolocator.reverse(f"{latitude}, {longitude}", timeout=5)
                if location:
                    return location.address
            except Exception as e:
                logger.warning(f"Geopy fallback also failed: {e}")
            return None
            
        except Exception as e:
            logger.warning(f"Reverse geocoding failed: {e}")
            return None
    
    @staticmethod
    def get_location_name(image_path: str) -> Optional[str]:
        """
        Extract location name from image (combines extraction + geocoding).
        
        Args:
            image_path: Path to image file
            
        Returns:
            Human-readable location name, or None
        """
        metadata = EXIFExtractor.extract_metadata(image_path)
        
        if metadata['has_location']:
            location_name = EXIFExtractor.reverse_geocode(
                metadata['latitude'],
                metadata['longitude']
            )
            return location_name
        
        return None


# Convenience function
def extract_photo_metadata(image_path: str) -> Dict:
    """
    Quick function to extract metadata from a photo.
    
    Args:
        image_path: Path to image
        
    Returns:
        Metadata dictionary
    """
    return EXIFExtractor.extract_metadata(image_path)
