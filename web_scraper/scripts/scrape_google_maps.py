import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# WebDriver'i başlat (Chrome kullanıyorsan)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Google Haritalar'da belirli bir yer arat
search_query = "Restoranlar Kadıköy İstanbul"
driver.get(f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}/")

# Sayfanın yüklenmesini bekle
time.sleep(5)

# Sayfanın kaynağını al ve BeautifulSoup ile işle
soup = BeautifulSoup(driver.page_source, "html.parser")

# Restoranları bul
places = soup.find_all("div", class_="qBF1Pd")

# CSV dosyasına yazma
with open('restoranlar.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Restoran Adı"])  # Başlık satırı
    for place in places:
        name = place.text
        writer.writerow([name])  # Restoran adını yaz

# Tarayıcıyı kapat
driver.quit()

print("Veri CSV dosyasına kaydedildi.")
