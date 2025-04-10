import time
import os
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.email_extractor import extract_emails_from_url
from utils.browser import get_driver

def get_restaurant_details(driver, link):
    driver.get(link)
    time.sleep(4)

    try:
        name = driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf").text
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

    email = extract_emails_from_url(website) if website != "N/A" else "Web sitesi yok"

    return {
        "Adı": name,
        "Adres": address,
        "Telefon": phone,
        "Web Sitesi": website,
        "E-Posta": email,
        "Google Maps Link": link
    }

def scrape_google_maps(city, district):
    driver = get_driver()
    driver.get("https://www.google.com/maps")

    wait = WebDriverWait(driver, 15)
    search_input = wait.until(EC.presence_of_element_located((By.ID, "searchboxinput")))
    search_input.clear()
    search_input.send_keys(f"{city} {district} restoran")
    search_input.send_keys(Keys.ENTER)
    time.sleep(5)

    try:
        sidebar = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']")))
    except:
        print(f"{city} {district} için sonuç bulunamadı.")
        driver.quit()
        return

    prev_height = 0
    while True:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", sidebar)
        time.sleep(2)
        new_height = driver.execute_script("return arguments[0].scrollHeight", sidebar)
        if new_height == prev_height:
            break
        prev_height = new_height

    cards = driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")
    links = []
    for card in cards:
        try:
            link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
            if link:
                links.append(link)
        except:
            continue

    print(f"{city} {district}: {len(links)} restoran bulundu.")

    results = []
    for link in links:
        data = get_restaurant_details(driver, link)
        results.append(data)
        print(data)

    # CSV olarak kaydet
    os.makedirs("outputs", exist_ok=True)
    filename = f"outputs/{city}_{district}_restoranlar.csv"
    pd.DataFrame(results).to_csv(filename, index=False, encoding="utf-8")
    print(f"\n✅ Kaydedildi: {filename}")

    driver.quit()
