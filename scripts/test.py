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
from concurrent.futures import ThreadPoolExecutor

def get_random_user_agent():
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.64 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0"
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

def get_restaurant_info(link):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={get_random_user_agent()}")
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(link)
        wait = WebDriverWait(driver, 10)

        try:
            name = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.DUwDvf'))).text
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

        email = extract_email_from_website(website) if website != "N/A" else "No Website"

        return {
            "Restoran Adı": name,
            "Adres": address,
            "Telefon": phone,
            "E-posta": email,
            "Web Sitesi": website,
            "Link": link
        }

    finally:
        driver.quit()

def scroll_to_load_all_results(driver, divSideBar):
    wait = WebDriverWait(driver, 5)
    previous_scroll_height = 0
    while True:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", divSideBar)
        time.sleep(2)
        try:
            new_scroll_height = driver.execute_script("return arguments[0].scrollHeight", divSideBar)
            if new_scroll_height == previous_scroll_height:
                break
            previous_scroll_height = new_scroll_height
        except:
            break

def main():
    start_time = time.time()
    
    city = input("Bir İl Gir: ").strip()
    district = input("Bir İlçe Gir (Boş bırakabilirsiniz): ").strip()
    location = "restoranlar"

    if district:
        service = f"{city} {district}"
        csv_filename = f"test/test1/{city}_{district}_restoranlar.csv"
    else:
        service = city
        csv_filename = f"test/test1/{city}_restoranlar.csv"
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={get_random_user_agent()}")
    
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.google.com/maps')
    
    input_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="searchboxinput"]')))
    input_field.clear()
    input_field.send_keys(service.lower() + ' ' + location.lower())
    input_field.send_keys(Keys.ENTER)

    divSideBar = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']")))
    
    scroll_to_load_all_results(driver, divSideBar)

    restaurant_links = []
    for r in driver.find_elements(By.CSS_SELECTOR, '.Nv2PK'):
        try:
            link = r.find_element(By.TAG_NAME, 'a').get_attribute('href')
            if link and link not in restaurant_links:
                restaurant_links.append(link)
        except:
            continue

    driver.quit()
    
    restaurant_links = list(set(restaurant_links))  # yinelenenleri temizle

    print(f"{len(restaurant_links)} restoran bulundu, bilgiler çekiliyor...")

    os.makedirs("test/test1", exist_ok=True)
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        restaurant_data = list(executor.map(get_restaurant_info, restaurant_links))
    
    df = pd.DataFrame(restaurant_data)
    df.to_csv(csv_filename, index=False, encoding="utf-8")
    
    end_time = time.time()
    print(f"{csv_filename} Veriler CSV dosyasına kaydedildi.")
    print(f"Çalışma süresi: {end_time - start_time:.2f} saniye")

if __name__ == "__main__":
    main()
