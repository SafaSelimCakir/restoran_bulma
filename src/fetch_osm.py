import requests
from config.settings import OVERPASS_API_URL

def get_restaurants(city, district=None):
    
    
    if district:
        query = f"""
        [out:json];
        area[name="{city}"]->.city;
        area[name="{district}"]->.district;
        (
          node["amenity"="restaurant"](area.district);
          way["amenity"="restaurant"](area.district);
          relation["amenity"="restaurant"](area.district);
        );
        out center;
        """
    else:
        query = f"""
        [out:json];
        area[name="{city}"]->.city;
        (
          node["amenity"="restaurant"](area.city);
          way["amenity"="restaurant"](area.city);
          relation["amenity"="restaurant"](area.city);
        );
        out center;
        """
    
    response = requests.get(OVERPASS_API_URL, params={"data": query})
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"API Hatası: {response.status_code}")
        return None
