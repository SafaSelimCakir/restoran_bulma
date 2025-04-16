import os
import time
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.browser import get_driver
from utils.email import get_restaurant_info


from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

def scroll_to_bottom(driver, container_xpath="//div[@role='feed']", pause_time=1.2, max_stable_scrolls=3):
    last_height = -1
    stable_scrolls = 0

    while stable_scrolls < max_stable_scrolls:
        try:
            container = driver.find_element(By.XPATH, container_xpath)
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
            time.sleep(pause_time)
            new_height = driver.execute_script("return arguments[0].scrollHeight", container)

            if new_height == last_height:
                stable_scrolls += 1
            else:
                stable_scrolls = 0
            last_height = new_height

        except (StaleElementReferenceException, NoSuchElementException):
            print("Scroll sırasında element kayboldu, tekrar deneniyor...")
            time.sleep(1)
            continue



def scrape_city_district(driver, city, district):
    terms = ["restoran", "cafe", "yemek"]
    location = f"{city} {district}".strip()
    all_links = set()

    for term in terms:
        try:
            searchbox = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "searchboxinput")))
            searchbox.clear()
            searchbox.send_keys(f"{location} {term}")
            searchbox.send_keys(Keys.ENTER)
            time.sleep(2)

            sidebar = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
            )
            scroll_to_bottom(driver, container_xpath="//div[@role='feed']")

            places = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
            for place in places:
                href = place.get_attribute("href")
                if href and "www.google.com/maps/place" in href:
                    all_links.add(href)
        except TimeoutException:
            print(f"{location} - Arama veya liste yüklenemedi.")
            continue

    print(f"{location} - {len(all_links)} sonuç bulundu.")

    def fetch_info(link):
        try:
            return get_restaurant_info(driver, link)
        except Exception as e:
            print(f"Hata: {link} -> {e}")
            return {}

    with ThreadPoolExecutor(max_workers=3) as executor:
        data = list(executor.map(fetch_info, all_links))

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

    start_time = time.time()

    driver = get_driver()
    driver.get("https://www.google.com/maps")
    time.sleep(2)

    for city, district in zip(cities, districts):
        scrape_city_district(driver, city.strip(), district.strip())

    driver.quit()

    total_time = time.time() - start_time
    print(f"Toplam çalışma süresi: {total_time:.2f} saniye")


if __name__ == "__main__":
    run_scraper()
