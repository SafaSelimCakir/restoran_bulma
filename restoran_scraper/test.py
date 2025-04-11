import os
import shutil
import csv
import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from datetime import datetime

UNDTECTED_CHROMEDRIVER_FOLDER = os.path.expanduser("~\\AppData\\Roaming\\undetected_chromedriver\\undetected\\chromedriver-win32")

def cleanup_driver_cache():
    if os.path.exists(UNDTECTED_CHROMEDRIVER_FOLDER):
        shutil.rmtree(UNDTECTED_CHROMEDRIVER_FOLDER, ignore_errors=True)

def start_driver():
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options)
    return driver

def scroll_to_bottom(driver, container):
    prev_height = 0
    while True:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
        time.sleep(2)
        new_height = driver.execute_script("return arguments[0].scrollHeight", container)
        if new_height == prev_height:
            break
        prev_height = new_height

def wait_for_results_panel(driver, timeout=30):
    possible_labels = [
        "//div[contains(@aria-label, 'Results')]",
        "//div[contains(@aria-label, 'Sonuçlar')]",
        "//div[contains(@aria-label, 'search results')]",
        "//div[contains(@aria-label, 'Liste')]"
    ]
    for label in possible_labels:
        try:
            return WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, label))
            )
        except:
            continue
    raise Exception("Sonuç paneli bulunamadı.")

def scroll_results(driver):
    scrollable_div_xpath = "//div[contains(@aria-label, 'Results') or contains(@aria-label, 'Sonuçlar') or contains(@aria-label, 'Liste')]"
    scrollable_div = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, scrollable_div_xpath)))
    scroll_to_bottom(driver, scrollable_div)

def extract_email_from_text(text):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    matches = re.findall(email_pattern, text)
    return matches[0] if matches else None

def parse_result_block(driver, block):
    href = block.get_attribute("href")
    driver.get(href)
    time.sleep(3)

    try:
        name = driver.find_element(By.XPATH, "//h1").text
    except:
        name = ""

    try:
        address = driver.find_element(By.XPATH, "//button[@data-item-id='address']").text
    except:
        address = ""

    try:
        phone = driver.find_element(By.XPATH, "//button[@data-item-id='phone']").text
    except:
        phone = ""

    try:
        website = driver.find_element(By.XPATH, "//a[@data-item-id='authority']").get_attribute("href")
    except:
        website = ""

    email = ""
    if website:
        try:
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(website)
            time.sleep(5)
            page_source = driver.page_source
            email = extract_email_from_text(page_source)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except:
            pass

    return {
        "İsim": name,
        "Adres": address,
        "Telefon": phone,
        "Web Sitesi": website,
        "E-posta": email
    }

def scrape_maps_results(il, ilce=None):
    query = f"{il} {ilce} restoranları" if ilce else f"{il} restoranları"
    url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"

    retry_count = 3
    for attempt in range(retry_count):
        driver = start_driver()
        try:
            print(f"→ {query} sayfası açılıyor (deneme {attempt + 1})...")
            driver.get(url)
            wait_for_results_panel(driver)
            scroll_results(driver)

            result_blocks = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@aria-label, 'More info')]"))
            )

            results = []
            for block in result_blocks:
                driver.execute_script("arguments[0].scrollIntoView();", block)
                try:
                    result = parse_result_block(driver, block)
                    results.append(result)
                except Exception as e:
                    print(f"Hata oluştu: {e}")
                    continue
                driver.back()
                time.sleep(2)

            return results

        except Exception as e:
            print(f"HATA: {e}")
            time.sleep(5)
        finally:
            try:
                driver.quit()
            except:
                pass

    raise Exception(f"{query} için sonuçlar alınamadı. 3 deneme başarısız.")

def save_to_csv(data, il, ilce=None):
    if not data:
        print(f"Veri bulunamadı: {il}, {ilce}")
        return
    filename = f"{il}_{ilce}_restoranlar.csv" if ilce else f"{il}_restoranlar.csv"
    filename = filename.replace(" ", "_")
    with open(filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["İsim", "Adres", "Telefon", "Web Sitesi", "E-posta"])
        writer.writeheader()
        writer.writerows(data)
    print(f"{filename} dosyasına kaydedildi.")

def main():
    cleanup_driver_cache()

    iller_ve_ilceler = {
        "İstanbul": ["Kadıköy", "Beşiktaş"],
        "Ankara": ["Çankaya"]
    }

    for il, ilceler in iller_ve_ilceler.items():
        for ilce in ilceler:
            print(f"\n{il} {ilce} için veri toplanıyor...")
            try:
                data = scrape_maps_results(il, ilce)
                save_to_csv(data, il, ilce)
            except Exception as e:
                print(f"{il} {ilce} için hata: {e}")

if __name__ == "__main__":
    main()
