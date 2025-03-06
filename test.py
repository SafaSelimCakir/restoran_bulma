import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 🚀 Tarayıcıyı başlat
def start_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Tam ekran aç
    options.add_argument("--disable-blink-features=AutomationControlled")  # Bot algılamayı azaltır
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# 🔍 Google Maps'ten restoranları çek
def get_restaurants(city, district=None):
    driver = start_driver()
    
    search_query = f"{city} {district} restoran" if district else f"{city} restoran"
    maps_url = f"https://www.google.com/maps/search/{search_query}"
    
    driver.get(maps_url)
    time.sleep(5)

    restaurants = []

    while True:
        try:
            restaurant_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'Nv2PK')]")
            if not restaurant_elements:
                print("❌ Hiç restoran bulunamadı!")
                break

            for element in restaurant_elements:
                try:
                    name = element.find_element(By.CLASS_NAME, "qBF1Pd").text

                    try:
                        address = element.find_element(By.CLASS_NAME, "Io6YTe").text
                    except:
                        address = "Adres Bulunamadı"

                    try:
                        rating = element.find_element(By.CLASS_NAME, "MW4etd").text
                    except:
                        rating = "Bilinmiyor"

                    try:
                        review_count = element.find_element(By.CLASS_NAME, "UY7F9").text.replace("(", "").replace(")", "")
                    except:
                        review_count = "Bilinmiyor"

                    # 🔗 Restoran detay sayfasına gir
                    element.click()
                    time.sleep(3)

                    try:
                        phone = driver.find_element(By.XPATH, "//button[contains(@data-item-id, 'phone')]").text
                    except:
                        phone = "Telefon Bulunamadı"

                    try:
                        email = driver.find_element(By.XPATH, "//a[contains(@href, 'mailto:')]").text
                    except:
                        email = "E-posta Bulunamadı"

                    # 🚀 Sonuçları kaydet
                    restaurants.append({
                        "İsim": name,
                        "Adres": address,
                        "Telefon": phone,
                        "E-posta": email,
                        "Puan": rating,
                        "Yorum Sayısı": review_count
                    })

                    print(f"✅ {name} eklendi!")

                except Exception as e:
                    print(f"⚠️ Hata: {e}")

            # 📜 Sayfanın sonuna gelindi mi?
            scrollable_div = driver.find_element(By.XPATH, "//div[contains(@class, 'm6QErb')]")
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scrollable_div)
            time.sleep(3)
            
            new_restaurants = driver.find_elements(By.XPATH, "//div[contains(@class, 'Nv2PK')]")
            if len(new_restaurants) == len(restaurant_elements):
                print("🚀 Tüm restoranlar yüklendi!")
                break

        except Exception as e:
            print(f"❌ Bir hata oluştu: {e}")
            break

    driver.quit()
    return restaurants

# 📂 CSV'ye kaydet
def save_to_csv(restaurants, city, district):
    filename = f"{city}_{district}_restoranlar.csv" if district else f"{city}_tum_restoranlar.csv"
    df = pd.DataFrame(restaurants)
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"✔️ {filename} başarıyla kaydedildi!")

# 🔥 Kod Başlatma
if __name__ == "__main__":
    city = input("Şehir adı girin: ")
    district = input("İlçe adı girin (boş bırakabilirsiniz): ")

    restaurants = get_restaurants(city, district)
    
    if restaurants:
        save_to_csv(restaurants, city, district)
    else:
        print("❌ Hiç restoran bulunamadı.")
