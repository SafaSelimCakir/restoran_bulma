import pandas as pd
from src.fetch_osm import get_restaurants

def save_restaurants_to_csv(city, district):
    data = get_restaurants(city, district)
    
    if not data:
        return
    
    restaurants = []
    for element in data["elements"]:
        tags = element.get("tags", {})
        name = tags.get("name", "Bilinmiyor")
        address = tags.get("addr:street", "Adres yok")
        phone = tags.get("contact:phone", tags.get("phone", "Numara yok"))
        
        restaurants.append({
            "İsim": name,
            "Adres": address,
            "Telefon": phone
        })
    
    df = pd.DataFrame(restaurants)
    df.to_csv(f"data/{city}_{district}_restoranlar.csv", index=False, encoding="utf-8")
    print(f"{city} - {district} restoran bilgileri kaydedildi.")
