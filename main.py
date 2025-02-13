from src.save_data import save_restaurants_to_csv

if __name__ == "__main__":
    city = input("Şehir adı girin: ").strip()
    district = input("İlçe adı girin (boş bırakabilirsiniz): ").strip()

    if district == "":
        district = None  # Eğer ilçe girilmezse None olarak ayarla
    
    save_restaurants_to_csv(city, district)
