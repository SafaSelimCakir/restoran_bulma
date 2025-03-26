import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

def get_random_user_agent():
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.64 Safari/537.36"
    ]
    return random.choice(USER_AGENTS)

def extract_email_from_website(url):
    if url == "N/A":
        return "No Website"
    try:
        headers = {'User-Agent': get_random_user_agent()}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", response.text)
            if emails:
                return ", ".join(set(emails))
        return "No Email Found"
    except requests.exceptions.RequestException:
        return "Error Accessing Site"

def get_restaurant_info(driver, link):
    driver.get(link)
    time.sleep(5)
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
    email = extract_email_from_website(website)
    return {"Restoran Adı": name, "Adres": address, "Telefon": phone, "E-posta": email, "Web Sitesi": website, "Link": link}

def get_districts(city):
    """Girilen ilin ilçelerini internetten çeker."""
    try:
        url = f"https://nominatim.openstreetmap.org/search?city={city}&country=Turkey&format=json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return list(set([d["display_name"].split(",")[0] for d in data if "display_name" in d]))
    except:
        print(f"{city} için ilçeler bulunamadı.")
    return []

def get_all_restaurants(city, districts):
    search_terms = ["restoran", "cafe", "lokanta", "yemek", "restaurant"]
    restaurant_links = set()  

    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument(f"user-agent={get_random_user_agent()}")
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.google.com/maps')

    for district in districts:
        service = f"{city} {district}"
        print(f"{district} ilçesinden veri çekiliyor...")

        for term in search_terms:
            input_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="searchboxinput"]')))
            input_field.clear()
            input_field.send_keys(f"{service} {term}")
            input_field.send_keys(Keys.ENTER)
            time.sleep(5)

            try:
                divSideBar = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']")))
            except:
                print(f"{district} için sonuç bulunamadı.")
                continue

            previous_scroll_height = 0
            while True:
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", divSideBar)
                time.sleep(4)
                new_scroll_height = driver.execute_script("return arguments[0].scrollHeight", divSideBar)
                if new_scroll_height == previous_scroll_height:
                    break
                previous_scroll_height = new_scroll_height

            restaurants = driver.find_elements(By.CSS_SELECTOR, '.Nv2PK')
            for r in restaurants:
                try:
                    link = r.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    if link and link not in restaurant_links:
                        restaurant_links.add(link)
                except:
                    continue

    print(f"Toplam {len(restaurant_links)} restoran bulundu.")

    restaurant_data = []
    for link in restaurant_links:
        restaurant_data.append(get_restaurant_info(driver, link))

    os.makedirs("data", exist_ok=True)
    csv_filename = f"data/{city}_tum_restoranlar.csv"
    df = pd.DataFrame(restaurant_data)
    df.to_csv(csv_filename, index=False, encoding="utf-8")
    print(f"Tüm ilçelerdeki restoranlar {csv_filename} dosyasına kaydedildi.")
    driver.quit()

if __name__ == "__main__":
    city = input("Bir İl Gir: ").strip()
    districts = get_districts(city)
    
    if not districts:
        district = input("Bir İlçe Gir (Boş bırakabilirsiniz): ").strip()
        districts = [district] if district else [city]

    get_all_restaurants(city, districts)
