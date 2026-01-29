"""
Quick script to check if a photo has GPS metadata.
"""

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import sys

def check_photo_metadata(image_path):
    """Check what metadata a photo has."""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        
        if not exif_data:
            print(f"❌ NO EXIF DATA FOUND in {image_path}")
            print("   This photo has been stripped of all metadata.")
            return
        
        print(f"✅ EXIF data found in {image_path}\n")
        
        has_gps = False
        has_datetime = False
        
        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)
            
            if tag_name == 'DateTime' or tag_name == 'DateTimeOriginal':
                has_datetime = True
                print(f"📅 Date/Time: {value}")
            elif tag_name == 'Make':
                print(f"📷 Camera Make: {value}")
            elif tag_name == 'Model':
                print(f"📷 Camera Model: {value}")
            elif tag_name == 'GPSInfo':
                has_gps = True
                print(f"📍 GPS Data: FOUND")
                
                # Parse GPS details
                gps_info = {}
                for gps_tag_id, gps_value in value.items():
                    gps_tag_name = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_info[gps_tag_name] = gps_value
                
                if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
                    lat = gps_info['GPSLatitude']
                    lon = gps_info['GPSLongitude']
                    lat_ref = gps_info.get('GPSLatitudeRef', 'N')
                    lon_ref = gps_info.get('GPSLongitudeRef', 'E')
                    
                    # Convert to decimal
                    lat_decimal = lat[0] + lat[1]/60 + lat[2]/3600
                    lon_decimal = lon[0] + lon[1]/60 + lon[2]/3600
                    
                    if lat_ref == 'S':
                        lat_decimal = -lat_decimal
                    if lon_ref == 'W':
                        lon_decimal = -lon_decimal
                    
                    print(f"   Latitude: {lat_decimal:.6f}°")
                    print(f"   Longitude: {lon_decimal:.6f}°")
        
        print()
        if not has_gps:
            print("❌ NO GPS DATA - Photo was likely sent via WhatsApp/Telegram")
        if not has_datetime:
            print("⚠️  NO DATE/TIME - Metadata stripped")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_metadata.py <image_path>")
        print("\nExample:")
        print("  python check_metadata.py data/uploads/IMG_1448.JPG.jpeg")
    else:
        check_photo_metadata(sys.argv[1])
