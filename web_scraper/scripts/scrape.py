import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import re

# Kullanıcıdan şehir ve ilçe bilgisi al
city = input("Bir İl Gir: ")
district = input("Bir İlçe Gir: ")

# User-Agent'lar için listeyi ekliyoruz
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.64 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0"
]

# WebDriver'ı başlat
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument('--headless=new')
options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
driver = webdriver.Chrome(options=options)
driver.get('https://www.google.com/maps')

# Arama kutusuna restoran araması yap
search_query = f"{city} {district} restoranlar"
search_box = driver.find_element(By.ID, 'searchboxinput')
search_box.send_keys(search_query)
search_box.send_keys(Keys.RETURN)
time.sleep(5)  # Sonuçların yüklenmesini bekle

# Sayfa kaydırma fonksiyonu
def scroll_until_min_restaurants_loaded(min_count=10, max_scrolls=20):
    # Sidebar elemanını buluyoruz (kaydırma yapılacak alan)
    divSideBar = driver.find_element(By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd')
    
    # Kaydırma işlemi için gerekli olan önceki scroll height
    previous_scroll_height = driver.execute_script("return arguments[0].scrollHeight", divSideBar)

    # Sayfa kaydırma işlemi
    print("Scrolling the sidebar to load")

# Restoranları kaydırarak yükle
scroll_until_min_restaurants_loaded(10)

# Restoran bağlantılarını al
restaurants = driver.find_elements(By.CSS_SELECTOR, '.Nv2PK')
restaurant_links = []
for restaurant in restaurants:
    try:
        link = restaurant.find_element(By.TAG_NAME, 'a').get_attribute('href')
        restaurant_links.append(link)
        if len(restaurant_links) >= 10:  # İlk 10 restoranı al
            break
    except:
        continue

print(f"Toplam {len(restaurant_links)} restoran bulundu.")

# Restoran bilgilerini saklamak için liste
restaurant_data = []

# Web sitesinden e-posta adreslerini çeken fonksiyon
def extract_email_from_website(url):
    """Web sitesinden e-posta adreslerini çeker."""
    if url == "N/A":
        return "No Website"

    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        response = requests.get(url, headers=headers, timeout=10)  # Timeout süresini artırdım
        if response.status_code == 200:
            emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", response.text)
            return ", ".join(set(emails)) if emails else "No Email Found"
    except requests.exceptions.RequestException as e:
        print(f"Error accessing the site: {e}")
        return "Error Accessing Site"

    return "No Email Found"


# Web sitesinden e-posta çekme fonksiyonu
def get_restaurant_info(link):
    driver.get(link)
    time.sleep(3)  # Sayfanın yüklenmesini bekle

    try:
        name = driver.find_element(By.CSS_SELECTOR, 'h1.DUwDvf').text
    except:
        name = "Bilinmiyor"
    try:
        address = driver.find_element(By.XPATH, "//button[contains(@data-tooltip, 'Adres')]//div[2]").text
    except:
        address = "Adres Yok"
    try:
        phone = driver.find_element(By.XPATH, "//button[contains(@data-tooltip, 'Telefon')]//div[2]").text
    except:
        phone = "Telefon Yok"
    try:
        website = driver.find_element(By.XPATH, "//a[contains(@aria-label, 'Web sitesi')]").get_attribute("href")
    except:
        website = "N/A"
    
    # Web sitesinden e-posta adresini çek
    email = extract_email_from_website(website)

    # Verileri listeye ekle
    restaurant_data.append({"Restoran Adı": name, "Adres": address, "Telefon": phone, "Web Sitesi": website, "E-posta": email, "Link": link})

    print(f"\n{name} | {address} | {phone} | {website} | {email}")

# İlk 10 restoranın bilgilerini çek
for link in restaurant_links:
    get_restaurant_info(link)

# CSV'ye kaydet
df = pd.DataFrame(restaurant_data)
df.to_csv(f"{city}_{district}_restoranlar.csv", index=False, encoding="utf-8")
print(f"{city}_{district}_restoranlar.csv Veriler CSV dosyasına kaydedildi.")

# WebDriver'ı kapat
driver.quit()
