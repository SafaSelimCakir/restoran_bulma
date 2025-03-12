import time
import re
import csv
import random
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

CITY = "Kocaeli Başiskele"
CATEGORY = "resoranlar"
SEARCH_QUERY = f"{CATEGORY} in {CITY}"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]

options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
driver = webdriver.Chrome(options=options)

def google_maps_search(query):
    """Google Haritalar'da işletmeleri arar ve bilgileri çeker."""
    driver.get("https://www.google.com/maps")
    time.sleep(3)

    search_box = driver.find_element(By.XPATH, "//input[@id='searchboxinput']")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)

    businesses = []
    elements = driver.find_elements(By.CSS_SELECTOR, '.hfpxzc')  # İşletme listesi

    for el in elements[:10]:  # İlk 10 işletmeyi çek
        try:
            el.click()
            time.sleep(3)

            name = driver.find_element(By.CSS_SELECTOR, 'h1.DUwDvf').text

            try:
                website = driver.find_element(By.XPATH, "//a[contains(@aria-label, 'Web sitesi')]").get_attribute("href")
            except:
                website = "N/A"

            businesses.append({"name": name, "website": website})
        except Exception as e:
            print("Hata:", e)

    return businesses

def extract_email_from_website(url):
    """Web sitesinden e-posta adreslerini çeker."""
    if url == "N/A":
        return "No Website"

    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", response.text)
            return ", ".join(set(emails)) if emails else "No Email Found"
    except:
        return "Error Accessing Site"

    return "No Email Found"

businesses = google_maps_search(SEARCH_QUERY)

with open("emails.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "Website", "Email"])

    for business in businesses:
        email = extract_email_from_website(business["website"])
        writer.writerow([business["name"], business["website"], email])

print("İşlem tamamlandı. 'emails.csv' dosyasına kaydedildi.")
driver.quit()
