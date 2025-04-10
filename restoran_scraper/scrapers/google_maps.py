import os
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor

from utils.browser import get_driver
from utils.email import get_restaurant_info
from utils.user_agent import get_random_user_agent

def scroll_to_bottom(driver, container):
    prev_height = 0
    while True:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
        time.sleep(2)
        new_height = driver.execute_script("return arguments[0].scrollHeight", container)
        if new_height == prev_height:
            break
        prev_height = new_height

def scrape_city_district(driver, city, district):
    terms = ["restoran", "cafe", "lokanta"]
    location = f"{city} {district}".strip()
    all_links = set()

    for term in terms:
        searchbox = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "searchboxinput")))
        searchbox.clear()
        searchbox.send_keys(f"{location} {term}")
        searchbox.send_keys(Keys.ENTER)
        time.sleep(5)

        try:
            sidebar = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']")))
            scroll_to_bottom(driver, sidebar)

            places = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
            for place in places:
                href = place.get_attribute("href")
                if href:
                    all_links.add(href)
        except:
            continue

    print(f"{location} - {len(all_links)} sonuç bulundu.")

    data = [get_restaurant_info(driver, link) for link in all_links]

    os.makedirs("outputs", exist_ok=True)
    filename = f"outputs/{city}_{district or 'genel'}_restoranlar.csv"
    pd.DataFrame(data).to_csv(filename, index=False, encoding="utf-8")
    print(f"{filename} kaydedildi.\n")

def run_scraper():
    cities = input("Şehir(ler): ").strip().split(",")
    districts = input("İlçe(ler): ").strip().split(",") or [""] * len(cities)

    if len(cities) != len(districts):
        print("Şehir ve ilçe sayısı eşleşmiyor!")
        return

    driver = get_driver()
    driver.get("https://www.google.com/maps")
    time.sleep(3)

    start = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(lambda city, district: scrape_city_district(driver, city.strip(), district.strip()), cities, districts)

    driver.quit()
    print(f"Toplam süre: {time.time() - start:.2f}s")
