import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from src.fetch_osm import get_restaurants
from config.settings import DATA_DIR


# **Selenium Başlat**
def start_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


# **Eksik Bilgileri Google Maps ile Tamamla**
def complete_missing_data(restaurants, city, district):
    driver = start_driver()

    for restaurant in restaurants:
        eksik_bilgiler = not restaurant["İsim"] or not restaurant["Adres"] or not restaurant["Telefon"] or not restaurant["E-posta"]
        if not eksik_bilgiler:
            continue  # Eğer eksik bilgi yoksa atla

        search_query = f"{restaurant['İsim']} {city} {district} restoran"
        google_maps_url = f"https://www.google.com/maps/search/{search_query}"

        driver.get(google_maps_url)
        time.sleep(3)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'Nv2PK')]"))
            )

            first_result = driver.find_element(By.XPATH, "//div[contains(@class, 'Nv2PK')]")

            # **Restoran İsmi**
            try:
                name = first_result.find_element(By.XPATH, ".//h3").text
                if not restaurant["İsim"]:
                    restaurant["İsim"] = name
            except:
                pass

            # **Adres**
            try:
                address = first_result.find_element(By.XPATH, ".//span[@class='rllt__details']").text
                if not restaurant["Adres"]:
                    restaurant["Adres"] = address
            except:
                pass

            # **Telefon ve E-posta bilgisi**
            try:
                details = first_result.text.split("\n")
                for detail in details:
                    if detail.startswith("+90") and not restaurant["Telefon"]:  # Türkiye için telefon formatı
                        restaurant["Telefon"] = detail
                    elif "@" in detail and not restaurant["E-posta"]:  # E-posta içeren satır
                        restaurant["E-posta"] = detail
            except:
                pass

        except Exception as e:
            print(f"Hata: {restaurant['İsim']} için veri bulunamadı - {e}")

        time.sleep(2)  # IP engellenmesini önlemek için bekleme süresi

    driver.quit()
    return restaurants


# **Restoranları CSV'ye Kaydet**
def save_restaurants_to_csv(city, district=None):
    data = get_restaurants(city, district)

    if not data:
        return

    restaurants = []
    for element in data["elements"]:
        tags = element.get("tags", {})
        name = tags.get("name", "").strip()
        address = tags.get("addr:street", "").strip()
        phone = tags.get("contact:phone", tags.get("phone", "")).strip()
        email = tags.get("contact:email", tags.get("email", "")).strip()

        restaurants.append({
            "İsim": name,
            "Adres": address,
            "Telefon": phone,
            "E-posta": email
        })

    # **Eksik bilgileri tamamlama işlemi**
    restaurants = complete_missing_data(restaurants, city, district)

    # **Klasör yoksa oluştur**
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # **Dosya adını belirle**
    csv_path = f"{DATA_DIR}{city}_{district}_restoranlar.csv" if district else f"{DATA_DIR}{city}_tum_restoranlar.csv"

    # **Eğer CSV dosyası zaten varsa, yeni verileri eskiyle birleştir**
    if os.path.exists(csv_path):
        existing_df = pd.read_csv(csv_path)
        new_df = pd.DataFrame(restaurants)

        # **Aynı isimde restoran varsa güncelle**
        updated_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=["İsim"], keep="last")
    else:
        updated_df = pd.DataFrame(restaurants)

    # **CSV'yi güncelle**
    updated_df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"{city} - {district if district else 'Tüm Şehir'} restoran bilgileri güncellendi: {csv_path}")
