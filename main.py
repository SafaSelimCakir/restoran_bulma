from src.save_data import save_restaurants_to_csv

if __name__ == "__main__":
    city = input("Şehir adı girin: ")
    district = input("İlçe adı girin: ")
    
    save_restaurants_to_csv(city, district)
