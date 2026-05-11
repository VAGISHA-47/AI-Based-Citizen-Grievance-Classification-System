"""Static coordinate-to-ward mapping helpers.

TODO: Replace with real polygon/GeoJSON lookup using shapely when GeoJSON ward boundaries are available
"""

from __future__ import annotations

import re


def get_ward_from_coordinates(lat: float, lng: float) -> str:
    """Map latitude/longitude to a ward name using static bounding boxes."""
    
    CITY_ZONES = [
        # BHOPAL (Madhya Pradesh)
        {"name": "Ward 01 - Bhopal North", "lat": (23.28, 23.35), "lng": (77.38, 77.48)},
        {"name": "Ward 02 - Bhopal Central", "lat": (23.22, 23.28), "lng": (77.38, 77.48)},
        {"name": "Ward 03 - Bhopal South", "lat": (23.15, 23.22), "lng": (77.38, 77.48)},
        {"name": "Ward 04 - Bhopal East", "lat": (23.20, 23.30), "lng": (77.48, 77.58)},
        {"name": "Ward 05 - Bhopal West", "lat": (23.20, 23.30), "lng": (77.28, 77.38)},
        {"name": "Ward 06 - Bhopal Kolar", "lat": (23.15, 23.22), "lng": (77.44, 77.55)},
        {"name": "Ward 07 - Bhopal Bairagarh", "lat": (23.28, 23.38), "lng": (77.28, 77.40)},
        
        # MUMBAI (Maharashtra)
        {"name": "Ward 05 - Andheri West", "lat": (19.10, 19.15), "lng": (72.82, 72.88)},
        {"name": "Ward 06 - Andheri East", "lat": (19.10, 19.15), "lng": (72.88, 72.95)},
        {"name": "Ward 07 - Kurla", "lat": (19.05, 19.10), "lng": (72.88, 72.95)},
        {"name": "Ward 03 - Borivali", "lat": (19.15, 19.22), "lng": (72.83, 72.90)},
        {"name": "Ward 12 - Dadar", "lat": (18.90, 18.96), "lng": (72.82, 72.88)},
        {"name": "Ward 08 - Bandra", "lat": (19.04, 19.08), "lng": (72.82, 72.87)},
        
        # DELHI (NCT)
        {"name": "Ward 01 - Connaught Place", "lat": (28.62, 28.65), "lng": (77.20, 77.23)},
        {"name": "Ward 02 - South Delhi", "lat": (28.52, 28.58), "lng": (77.18, 77.25)},
        {"name": "Ward 03 - East Delhi", "lat": (28.62, 28.68), "lng": (77.28, 77.35)},
        {"name": "Ward 04 - North Delhi", "lat": (28.68, 28.75), "lng": (77.18, 77.25)},
        {"name": "Ward 05 - West Delhi", "lat": (28.62, 28.68), "lng": (77.08, 77.18)},
        {"name": "Ward 06 - Dwarka", "lat": (28.56, 28.62), "lng": (77.02, 77.10)},
        
        # PUNE (Maharashtra)
        {"name": "Ward 01 - Pune Central", "lat": (18.51, 18.55), "lng": (73.85, 73.90)},
        {"name": "Ward 02 - Kothrud", "lat": (18.50, 18.54), "lng": (73.80, 73.85)},
        {"name": "Ward 03 - Hadapsar", "lat": (18.49, 18.53), "lng": (73.92, 73.98)},
        {"name": "Ward 04 - Pimpri", "lat": (18.61, 18.65), "lng": (73.78, 73.84)},
        
        # BANGALORE (Karnataka)
        {"name": "Ward 01 - Bangalore South", "lat": (12.90, 12.95), "lng": (77.56, 77.62)},
        {"name": "Ward 02 - Bangalore North", "lat": (13.02, 13.08), "lng": (77.56, 77.62)},
        {"name": "Ward 03 - Bangalore East", "lat": (12.96, 13.02), "lng": (77.62, 77.70)},
        {"name": "Ward 04 - Bangalore West", "lat": (12.96, 13.02), "lng": (77.50, 77.56)},
        {"name": "Ward 05 - Electronic City", "lat": (12.83, 12.90), "lng": (77.66, 77.72)},
        
        # HYDERABAD (Telangana)
        {"name": "Ward 01 - Hyderabad Central", "lat": (17.38, 17.43), "lng": (78.46, 78.52)},
        {"name": "Ward 02 - Secunderabad", "lat": (17.43, 17.48), "lng": (78.49, 78.55)},
        {"name": "Ward 03 - HITEC City", "lat": (17.43, 17.47), "lng": (78.36, 78.42)},
        
        # CHENNAI (Tamil Nadu)
        {"name": "Ward 01 - Chennai Central", "lat": (13.08, 13.12), "lng": (80.27, 80.32)},
        {"name": "Ward 02 - Anna Nagar", "lat": (13.08, 13.12), "lng": (80.20, 80.26)},
        {"name": "Ward 03 - Velachery", "lat": (12.97, 13.01), "lng": (80.21, 80.26)},
        
        # LUCKNOW (Uttar Pradesh)
        {"name": "Ward 01 - Hazratganj", "lat": (26.84, 26.88), "lng": (80.93, 80.97)},
        {"name": "Ward 02 - Gomti Nagar", "lat": (26.84, 26.88), "lng": (81.00, 81.05)},
        
        # JAIPUR (Rajasthan)
        {"name": "Ward 01 - Jaipur Central", "lat": (26.90, 26.95), "lng": (75.80, 75.86)},
        {"name": "Ward 02 - Mansarovar", "lat": (26.84, 26.90), "lng": (75.74, 75.80)},
        
        # KOLKATA (West Bengal)
        {"name": "Ward 01 - Kolkata Central", "lat": (22.56, 22.60), "lng": (88.35, 88.40)},
        {"name": "Ward 02 - Salt Lake", "lat": (22.58, 22.62), "lng": (88.40, 88.45)},
        
        # AHMEDABAD (Gujarat)
        {"name": "Ward 01 - Ahmedabad Central", "lat": (23.02, 23.06), "lng": (72.57, 72.62)},
        {"name": "Ward 02 - Satellite", "lat": (23.02, 23.06), "lng": (72.51, 72.57)},
        
        # INDORE (Madhya Pradesh)
        {"name": "Ward 01 - Indore Central", "lat": (22.71, 22.75), "lng": (75.85, 75.90)},
        {"name": "Ward 02 - Vijay Nagar", "lat": (22.74, 22.78), "lng": (75.88, 75.94)},
        
        # NAGPUR (Maharashtra)
        {"name": "Ward 01 - Nagpur Central", "lat": (21.14, 21.18), "lng": (79.08, 79.14)},
    ]
    
    for zone in CITY_ZONES:
        lat_min, lat_max = zone["lat"]
        lng_min, lng_max = zone["lng"]
        if lat_min <= lat <= lat_max and lng_min <= lng <= lng_max:
            return zone["name"]
    
    # If no zone found — detect city from coordinates and return generic
    if 23.10 <= lat <= 23.40 and 77.20 <= lng <= 77.60:
        return "Ward 00 - Bhopal General Zone"
    elif 28.40 <= lat <= 28.90 and 76.80 <= lng <= 77.50:
        return "Ward 00 - Delhi General Zone"
    elif 18.85 <= lat <= 19.30 and 72.75 <= lng <= 73.00:
        return "Ward 00 - Mumbai General Zone"
    elif 12.80 <= lat <= 13.10 and 77.45 <= lng <= 77.75:
        return "Ward 00 - Bangalore General Zone"
    elif 17.30 <= lat <= 17.55 and 78.35 <= lng <= 78.60:
        return "Ward 00 - Hyderabad General Zone"
    elif 18.45 <= lat <= 18.65 and 73.78 <= lng <= 74.00:
        return "Ward 00 - Pune General Zone"
    elif 13.00 <= lat <= 13.20 and 80.18 <= lng <= 80.35:
        return "Ward 00 - Chennai General Zone"
    elif 26.80 <= lat <= 26.95 and 80.88 <= lng <= 81.10:
        return "Ward 00 - Lucknow General Zone"
    elif 26.85 <= lat <= 27.00 and 75.75 <= lng <= 75.90:
        return "Ward 00 - Jaipur General Zone"
    elif 22.50 <= lat <= 22.70 and 88.30 <= lng <= 88.50:
        return "Ward 00 - Kolkata General Zone"
    elif 22.95 <= lat <= 23.10 and 72.50 <= lng <= 72.70:
        return "Ward 00 - Ahmedabad General Zone"
    elif 22.65 <= lat <= 22.80 and 75.80 <= lng <= 75.95:
        return "Ward 00 - Indore General Zone"
    else:
        return f"Ward 00 - General Zone ({round(lat,2)}°N, {round(lng,2)}°E)"


def get_zone_room(ward: str) -> str:
    """Convert a ward string into a Socket.io room name."""
    normalized = re.sub(r"[^a-z0-9]+", "-", ward.strip().lower()).strip("-")
    return f"zone:{normalized}"


if __name__ == "__main__":
    assert get_ward_from_coordinates(19.12, 72.85) == "Ward 05 - Andheri West"
    assert get_ward_from_coordinates(19.08, 72.90) == "Ward 07 - Kurla"
    assert get_ward_from_coordinates(19.18, 72.86) == "Ward 03 - Borivali"
    assert get_ward_from_coordinates(18.92, 72.85) == "Ward 12 - Dadar"
    assert get_ward_from_coordinates(20.0, 73.0) == "Ward 00 - General Zone"
    assert get_zone_room("Ward 05 - Andheri West") == "zone:ward-05-andheri-west"
    print("geo_mapper.py self-test passed")
