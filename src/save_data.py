import pandas as pd
import os
from src.fetch_osm import get_restaurants
from config.settings import DATA_DIR

def save_restaurants_to_csv(city, district=None):
    
    
    data = get_restaurants(city, district)
    
    if not data:
        return
    
    restaurants = []
    for element in data["elements"]:
        tags = element.get("tags", {})
        name = tags.get("name", " --- ")
        address = tags.get("addr:street", " --- ")
        phone = tags.get("contact:phone", tags.get("phone", " --- "))
        email = tags.get("contact:email", tags.get("email", " --- "))
        
        restaurants.append({
            "İsim": name,
            "Adres": address,
            "Telefon": phone,
            "E-posta": email
        })
    
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if district:
        csv_path = f"{DATA_DIR}{city}_{district}_restoranlar.csv"
    else:
        csv_path = f"{DATA_DIR}{city}_tum_restoranlar.csv"
    
    df = pd.DataFrame(restaurants)
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"{city} - {district if district else 'Tüm Şehir'} restoran bilgileri kaydedildi: {csv_path}")
