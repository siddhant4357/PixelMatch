"""
Test date parsing to see what's going wrong.
"""
from dateutil import parser as date_parser
from datetime import datetime

# Test the timestamp format from EXIF
timestamp = "2026:01:15 16:55:55"

print(f"Original timestamp: {timestamp}")

# Try different parsing methods
try:
    # Method 1: Direct parse
    parsed1 = date_parser.parse(timestamp)
    print(f"✅ Direct parse: {parsed1.date()}")
except Exception as e:
    print(f"❌ Direct parse failed: {e}")

try:
    # Method 2: Replace colons (what the code does)
    fixed = timestamp.replace(':', '-', 2)  # Replace first 2 colons
    print(f"Fixed format: {fixed}")
    parsed2 = date_parser.parse(fixed)
    print(f"✅ After replace: {parsed2.date()}")
except Exception as e:
    print(f"❌ Replace method failed: {e}")

# Test query date
query_date = "2026-01-15"
try:
    parsed_query = date_parser.parse(query_date).date()
    print(f"\n✅ Query date: {parsed_query}")
except Exception as e:
    print(f"❌ Query parse failed: {e}")

# Test comparison
try:
    photo_date = date_parser.parse(timestamp.replace(':', '-', 2)).date()
    query_start = date_parser.parse("2026-01-01").date()
    query_end = date_parser.parse("2026-01-31").date()
    
    print(f"\n📅 Comparison:")
    print(f"  Photo date: {photo_date}")
    print(f"  Query range: {query_start} to {query_end}")
    print(f"  In range? {query_start <= photo_date <= query_end}")
except Exception as e:
    print(f"❌ Comparison failed: {e}")
