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

# Restoranları tamamen yükle
scroll_until_all_restaurants_loaded()

# Tüm restoranları çek
restaurants = driver.find_elements(By.CSS_SELECTOR, '.Nv2PK')
restaurant_data = []  # Verileri saklayacağımız liste

for i, restaurant in enumerate(restaurants):
    try:
        ActionChains(driver).move_to_element(restaurant).perform()  # Restorana git
        restaurant.click()  # Restoranı aç
        time.sleep(5)  # Bilgilerin yüklenmesini bekle
        
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
            "Telefon": phone_number
        })
        
        print("\n------------------------------------")
        print(f"{i+1}. Restoran")
        print("Restoran Adı:", restaurant_name)
        print("Adres:", address)
        print("Telefon Numarası:", phone_number)
        print("------------------------------------\n")

        # Geri tuşuna basarak listeye dön
        driver.execute_script("window.history.go(-1)")
        time.sleep(5)  # Liste sayfasının yüklenmesini bekle
        
        # Listeyi tekrar çek (bazı öğeler kaybolabiliyor)
        restaurants = driver.find_elements(By.CSS_SELECTOR, '.Nv2PK')

    except Exception as e:
        print("Hata oluştu:", str(e))
        continue

# WebDriver'ı kapat
driver.quit()

# Çıktıyı CSV dosyasına kaydetmek istersen:
df = pd.DataFrame(restaurant_data)
df.to_csv(f"{city}_{district}_restoranlar.csv", index=False, encoding="utf-8")
print("Veriler CSV dosyasına kaydedildi.")
