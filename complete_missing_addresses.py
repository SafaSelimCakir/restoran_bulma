import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config.settings import DATA_DIR

# Selenium WebDriver Başlatma
def start_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Tarayıcıyı görünmez yapma
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Eksik adresleri Google üzerinden aratıp tamamlama
def complete_missing_addresses(restaurants, city, district):
    driver = start_driver()

    for restaurant in restaurants:
        if restaurant["Adres"]:  # Adresi olan restoranları atla
            continue

        search_query = f"{city} {district} {restaurant['İsim']} restoran"
        google_search_url = f"https://www.google.com/search?q={search_query}"

        driver.get(google_search_url)
        time.sleep(3)

        try:
            # Arama sonuçlarını bekle
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='g']"))
            )

            first_result = driver.find_element(By.XPATH, "//div[@class='g']")

            # Restoran ismi ve adresini bulma
            try:
                name = first_result.find_element(By.XPATH, ".//h3").text
                address = first_result.find_element(By.XPATH, ".//span[@class='BNeawe iBp4i AP7Wnd']").text
                restaurant["İsim"] = name
                restaurant["Adres"] = address
            except Exception as e:
                print(f"Adres bulunamadı: {restaurant['İsim']} - {e}")

        except Exception as e:
            print(f"Hata: {restaurant['İsim']} için veri bulunamadı - {e}")

        time.sleep(2)  # IP engellenmesini önlemek için bekleme süresi

    driver.quit()
    return restaurants

# CSV'yi güncelleme fonksiyonu
def update_csv_with_addresses(city, district=None):
    csv_path = f"{DATA_DIR}{city}_{district}_restoranlar.csv" if district else f"{DATA_DIR}{city}_tum_restoranlar.csv"

    # CSV dosyası yoksa işlem yapma
    if not os.path.exists(csv_path):
        print("CSV dosyası bulunamadı!")
        return

    # CSV dosyasını oku
    df = pd.read_csv(csv_path).fillna("")  # Boş değerleri "" ile doldur
    print("CSV dosyasının ilk 5 satırı:")
    print(df.head())  # İlk 5 satırı yazdırarak kontrol et

    # Eksik adresleri tamamlama
    restaurants = df.to_dict(orient="records")
    restaurants = complete_missing_addresses(restaurants, city, district)

    # Güncellenmiş DataFrame oluştur
    updated_df = pd.DataFrame(restaurants)

    # CSV'yi güncelle
    updated_df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"{city} - {district if district else 'Tüm Şehir'} eksik adresler tamamlandı ve güncellendi: {csv_path}")
    print("Yeni veriler:")
    print(updated_df.head())  # Güncellenen ilk 5 veriyi yazdır

# Kod başlatma
if __name__ == "__main__":
    # Şehir ve ilçe bilgilerini al
    city = input("Şehir adı girin: ")
    district = input("İlçe adı girin (boş bırakabilirsiniz): ")

    # İlçe girilmediyse şehir bazında işlem yap
    if not district:
        update_csv_with_addresses(city)
    else:
        update_csv_with_addresses(city, district)
