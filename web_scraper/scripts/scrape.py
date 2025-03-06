from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup

# Önceki adımda toplanan verileri oku
df = pd.read_csv("Kocaeli_Başiskele_restoranlar.csv")
restaurant_names = df["Restoran Adı"].tolist()

# Chrome sürücüsünü başlat
driver = webdriver.Chrome()
driver.get('https://www.yemeksepeti.com')

# Yemek Sepeti’nde restoranları ara ve e-posta bul
restaurant_data_with_email = []

for name in restaurant_names:
    try:
        search_box = driver.find_element(By.ID, 'search-term-global')
        search_box.clear()
        search_box.send_keys(name + " Kocaeli Başiskele")
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)

        # Restoran profiline git
        try:
            restaurant_link = driver.find_element(By.XPATH, "//a[contains(@class, 'restaurant-name')]")
            restaurant_link.click()
            time.sleep(3)
        except:
            print(f"{name} için Yemek Sepeti’nde profil bulunamadı.")
            restaurant_data_with_email.append({"Restoran Adı": name, "E-posta": "Bulunamadı"})
            continue

        # Web sitesi bağlantısını kontrol et
        email = "Bulunamadı"
        try:
            website_link = driver.find_element(By.XPATH, "//a[contains(@href, 'http')]")
            website_url = website_link.get_attribute('href')
            
            # Web sitesinden e-posta kazı
            response = urlopen(website_url)
            soup = BeautifulSoup(response, 'html.parser')
            text = soup.get_text()
            email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
            emails = email_pattern.findall(text)
            email = emails[0] if emails else "Bulunamadı"
        except:
            pass

        restaurant_data_with_email.append({"Restoran Adı": name, "E-posta": email})
        print(f"{name}: {email}")

        driver.get('https://www.yemeksepeti.com')
        time.sleep(3)

    except Exception as e:
        print(f"Hata oluştu ({name}): {str(e)}")
        restaurant_data_with_email.append({"Restoran Adı": name, "E-posta": "Bulunamadı"})
        continue

# Sürücüyü kapat
driver.quit()

# Verileri CSV’ye kaydet
df_emails = pd.DataFrame(restaurant_data_with_email)
df_emails.to_csv("Kocaeli_Başiskele_restoranlar_emails.csv", index=False, encoding="utf-8")
print("Yemek Sepeti verileri CSV dosyasına kaydedildi.")