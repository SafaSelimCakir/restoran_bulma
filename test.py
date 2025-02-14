import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Kullanıcıdan il ve ilçe bilgisi al
sehir = input("Şehir girin: ")
ilce = input("İlçe girin: ")

# Google Maps URL
url = f"https://www.google.com/maps/search/{sehir}+{ilce}+restoranlar"

# Selenium ayarları
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Headless mode
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Sayfayı yükle
driver.get(url)

# Sayfa yüklenene kadar bekle
try:
    WebDriverWait(driver, 60).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'hfpxzc')]"))
    )
except Exception as e:
    print("Arama sonuçları yüklenirken hata oluştu:", e)
    driver.quit()
    exit()

# Restoran bilgilerini al
restaurants = []
results = driver.find_elements(By.XPATH, "//div[contains(@class, 'Nv2PK')]")

for result in results:
    try:
        name = result.find_element(By.XPATH, ".//h3").text
    except Exception:
        name = "Bilinmiyor"

    try:
        address = result.find_element(By.XPATH, ".//span[@class='rllt__details']").text
    except Exception:
        address = "Bilinmiyor"

    try:
        review = result.find_element(By.XPATH, ".//span[contains(@class, 'e5lbc') or contains(@class, 'z3sf')]").text
    except Exception:
        review = "Bilinmiyor"

    restaurants.append([name, address, review])

driver.quit()

# Verileri CSV'ye kaydet
if restaurants:
    df = pd.DataFrame(restaurants, columns=["İsim", "Adres", "Yorum ve Puan"])
    df.to_csv("restoranlar.csv", index=False, encoding="utf-8")
    print("Restoran bilgileri 'restoranlar.csv' dosyasına kaydedildi.")
else:
    print("Hiçbir restoran bilgisi çekilemedi.")