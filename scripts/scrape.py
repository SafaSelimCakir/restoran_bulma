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

def get_restaurant_info(driver, link):
    driver.get(link)
    time.sleep(3)
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

def main():
    city = input("Bir İl Gir: ").strip()
    district = input("Bir İlçe Gir (Boş bırakabilirsiniz): ").strip()
    location = "restoranlar"

    if district:
        service = f"{city} {district}"
        csv_filename = f"data/{city}_{district}_restoranlar.csv"
    else:
        service = city
        csv_filename = f"data/{city}_restoranlar.csv"

    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={get_random_user_agent()}")
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.google.com/maps')

    input_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="searchboxinput"]')))
    input_field.send_keys(service.lower() + ' ' + location.lower())
    input_field.send_keys(Keys.ENTER)

    divSideBar = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']")))

    previous_scroll_height = 0
    while True:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", divSideBar)
        time.sleep(3)
        new_scroll_height = driver.execute_script("return arguments[0].scrollHeight", divSideBar)
        if new_scroll_height == previous_scroll_height:
            break
        previous_scroll_height = new_scroll_height

    restaurants = driver.find_elements(By.CSS_SELECTOR, '.Nv2PK')
    restaurant_links = [r.find_element(By.TAG_NAME, 'a').get_attribute('href') for r in restaurants if r.find_element(By.TAG_NAME, 'a')]

    restaurant_data = []
    for link in restaurant_links:
        restaurant_data.append(get_restaurant_info(driver, link))

    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame(restaurant_data)
    df.to_csv(csv_filename, index=False, encoding="utf-8")
    print(f"{csv_filename} Veriler CSV dosyasına kaydedildi.")
    driver.quit()

if __name__ == "__main__":
    main()
