import requests

def get_restaurants(city, district):
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
    
    url = "http://overpass-api.de/api/interpreter"
    response = requests.get(url, params={"data": query})
    
    if response.status_code == 200:
        return response.json()
    else:
        print("API Hatası:", response.status_code)
        return None
