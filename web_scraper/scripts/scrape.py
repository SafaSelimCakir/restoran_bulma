from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

# Arama sonuçlarının yüklenmesini bekle
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '.Nv2PK'))
)

# Sayfa kaydırma fonksiyonu (Tüm restoranları yüklemek için)
def scroll_until_all_restaurants_loaded():
    scrollable_div = driver.find_element(By.XPATH, '//div[contains(@class, "m6QErb") and contains(@class, "DxyBCb")]')
    previous_count = 0
    max_attempts = 20  # Maksimum kaydırma denemesi (sonsuz döngüyü önlemek için)
    attempt = 0

    while attempt < max_attempts:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        time.sleep(3)  # Yeni içeriklerin yüklenmesini bekle
        
        current_count = len(driver.find_elements(By.CSS_SELECTOR, '.Nv2PK'))
        print(f"Şu anda yüklenen restoran sayısı: {current_count}")
        
        if current_count == previous_count and current_count > 0:  # Yeni restoran yüklenmediyse
            break
        
        previous_count = current_count
        attempt += 1

# Tüm restoranları yükle
print("Restoranlar yükleniyor...")
scroll_until_all_restaurants_loaded()

# Tüm restoranları çek
restaurants = driver.find_elements(By.CSS_SELECTOR, '.Nv2PK')
restaurant_data = []  # Verileri saklayacağımız liste
processed_restaurants = set()  # Tekrarları önlemek için bir küme

print(f"Toplam {len(restaurants)} restoran bulundu. Veri çekimi başlıyor...")

for i in range(len(restaurants)):
    try:
        # Her döngüde restoran listesini yeniden al
        restaurants = driver.find_elements(By.CSS_SELECTOR, '.Nv2PK')
        restaurant = restaurants[i]
        
        # Restoran adına göre tekrar kontrolü
        restaurant_name_element = restaurant.find_element(By.CSS_SELECTOR, '.fontHeadlineSmall')
        restaurant_name = restaurant_name_element.text.strip()
        if restaurant_name in processed_restaurants:
            continue
        
        ActionChains(driver).move_to_element(restaurant).perform()  # Restorana git
        restaurant.click()  # Restoranı aç
        time.sleep(3)  # Bilgilerin yüklenmesini bekle
        
        # Restoran ismini al
        try:
            name_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//h1[@class='DUwDvf lfPIob']"))
            )
            restaurant_name = name_element.text
        except:
            restaurant_name = "Restoran adı bulunamadı"
        
        # Adresi al
        try:
            address_element = driver.find_element(By.XPATH, "//div[contains(@class, 'Io6YTe') and contains(text(), ',')]")
            address = address_element.text
        except:
            address = "Adres bulunamadı"
        
        # Telefon numarasını al
        try:
            phone_element = driver.find_element(By.XPATH, "//div[contains(@class, 'Io6YTe') and contains(text(), '+')]")
            phone_number = phone_element.text
        except:
            phone_number = "Telefon bulunamadı"
        
        # Sonuçları listeye ekle
        restaurant_data.append({
            "Restoran Adı": restaurant_name,
            "Adres": address,
            "Telefon": phone_number
        })
        processed_restaurants.add(restaurant_name)
        
        print("\n------------------------------------")
        print(f"{i+1}. Restoran")
        print("Restoran Adı:", restaurant_name)
        print("Adres:", address)
        print("Telefon Numarası:", phone_number)
        print("------------------------------------\n")

        # Geri tuşuna basarak listeye dön
        driver.execute_script("window.history.go(-1)")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.Nv2PK'))
        )
        time.sleep(2)  # Liste sayfasının yüklenmesini bekle

    except Exception as e:
        print(f"Hata oluştu (Restoran {i+1}): {str(e)}")
        continue

# WebDriver'ı kapat
driver.quit()

# Çıktıyı CSV dosyasına kaydet
df = pd.DataFrame(restaurant_data)
df.to_csv(f"{city}_{district}_restoranlar.csv", index=False, encoding="utf-8")
print(f"Toplam {len(restaurant_data)} restoran CSV dosyasına kaydedildi.")