from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import pandas as pd

# Kullanıcıdan şehir ve ilçe bilgisi al
city = input("Bir İl Gir: ")
district = input("Bir İlçe Gir: ")

# WebDriver'ı başlat
driver = webdriver.Chrome()
driver.get('https://www.google.com/maps')

# Arama kutusuna restoran araması yap
search_query = f"{city} {district} restoranlar"
search_box = driver.find_element(By.ID, 'searchboxinput')
search_box.send_keys(search_query)
search_box.send_keys(Keys.RETURN)

time.sleep(5)  # Sonuçların yüklenmesini bekle

# Sayfa kaydırma fonksiyonu (Tüm restoranları yüklemek için)
def scroll_until_all_restaurants_loaded():
    scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd')
    last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
    current_restaurant_count = len(driver.find_elements(By.CSS_SELECTOR, '.Nv2PK'))  # Başlangıçtaki restoran sayısı

    while True:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        time.sleep(2)  # Yükleme süresi bekleniyor
        new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)

        new_restaurant_count = len(driver.find_elements(By.CSS_SELECTOR, '.Nv2PK'))  # Yeni restoran sayısı
        
        if new_restaurant_count == current_restaurant_count:  # Eğer restoran sayısı değişmediyse döngüyü bitir
            break
        
        current_restaurant_count = new_restaurant_count  # Restoran sayısını güncelle
        last_height = new_height  # Sayfa yüksekliğini güncelle

# **1. AŞAMA: Restoranları tamamen yükle**
scroll_until_all_restaurants_loaded()

# **2. AŞAMA: Restoran bağlantılarını al ve sponsorluları filtrele**
restaurants = driver.find_elements(By.CSS_SELECTOR, '.Nv2PK')
restaurant_links = []  # Restoran bağlantılarını saklayacağımız liste

for restaurant in restaurants:
    try:
        # **Sponsorlu restoranları kontrol et**
        if restaurant.find_elements(By.CSS_SELECTOR, '.HlvSq'):  # Google sponsor etiketi (varsa)
            continue  # Sponsorluları atla

        link = restaurant.find_element(By.TAG_NAME, 'a').get_attribute('href')  # Restoran bağlantısını al
        restaurant_links.append(link)
    except:
        continue

# Eğer hiç restoran yoksa işlemi durdur
if not restaurant_links:
    print("Hiç restoran bulunamadı.")
    driver.quit()
    exit()

print(f"Toplam {len(restaurant_links)} organik restoran bulundu.")

# Restoran bilgilerini saklamak için liste
restaurant_data = []  
checked_links = set()  # Kontrol edilen restoranları saklamak için

# **3. AŞAMA: Restoran bilgilerini çek**
def get_restaurant_info(link):
    driver.get(link)
    time.sleep(5)  # Sayfanın yüklenmesini bekle

    # Restoran ismini al
    try:
        name_element = driver.find_element(By.XPATH, "//h1[@class='DUwDvf lfPIob']")
        restaurant_name = name_element.text
    except:
        restaurant_name = "Restoran adı bulunamadı"

    # Adresi al
    try:
        address_element = driver.find_element(By.XPATH, "//span[text()='']/ancestor::div[@class='AeaXub']//div[@class='Io6YTe fontBodyMedium kR99db fdkmkc ']")
        address = address_element.text
    except:
        address = "Adres bulunamadı"

    # Telefon numarasını al
    try:
        phone_element = driver.find_element(By.XPATH, "//span[text()='']/ancestor::div[@class='AeaXub']//div[@class='Io6YTe fontBodyMedium kR99db fdkmkc ']")
        phone_number = phone_element.text
    except:
        phone_number = "Telefon bulunamadı"

    # Sonuçları listeye ekle
    restaurant_data.append({
        "Restoran Adı": restaurant_name,
        "Adres": address,
        "Telefon": phone_number,
        "Link": link
    })

    print("\n------------------------------------")
    print(f"Restoran Adı: {restaurant_name}")
    print("Adres:", address)
    print("Telefon Numarası:", phone_number)
    print("------------------------------------\n")

# **4. AŞAMA: Tüm restoranları sırayla kontrol et**
for link in restaurant_links:
    if link not in checked_links:
        get_restaurant_info(link)
        checked_links.add(link)

# **5. AŞAMA: Yeniden tüm restoranları yükleyip eksik olanları al**
while True:
    print("Tüm restoranlar kontrol edildi, tekrar kontrol ediliyor...")
    
    driver.get(f'https://www.google.com/maps/search/{city}+{district}+restoranlar')
    time.sleep(5)
    scroll_until_all_restaurants_loaded()
    
    # Yeni restoran bağlantılarını al
    new_restaurants = driver.find_elements(By.CSS_SELECTOR, '.Nv2PK')
    new_links = []
    
    for restaurant in new_restaurants:
        try:
            # **Sponsorlu restoranları kontrol et**
            if restaurant.find_elements(By.CSS_SELECTOR, '.HlvSq'):
                continue  # Sponsorluları atla

            link = restaurant.find_element(By.TAG_NAME, 'a').get_attribute('href')
            if link not in checked_links:
                new_links.append(link)
        except:
            continue
    
    if not new_links:
        print("Yeni restoran bulunamadı. İşlem tamamlandı.")
        break

    print(f"Yeni {len(new_links)} restoran bulundu. Bilgileri alınıyor...")

    for link in new_links:
        get_restaurant_info(link)
        checked_links.add(link)

# **6. AŞAMA: Verileri CSV'ye kaydet**
df = pd.DataFrame(restaurant_data)
df.to_csv(f"{city}_{district}_restoranlar.csv", index=False, encoding="utf-8")
print("Veriler CSV dosyasına kaydedildi.")

# WebDriver'ı kapat
driver.quit()
