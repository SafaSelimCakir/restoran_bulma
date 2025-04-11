from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def get_instagram_location_posts(location_url, max_scrolls=3):
    options = Options()
    # GÖRÜNÜR çalıştır, anti-bot'u daha az tetikler
    # options.add_argument("--headless=new")  # opsiyonel
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)
    driver.get(location_url)

    try:
        # Gönderi galerisi yüklenene kadar bekle
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
        )
    except:
        print("Sayfa yüklenemedi veya giriş ekranı geldi.")
        driver.quit()
        return []

    time.sleep(3)
    post_urls = set()

    for _ in range(max_scrolls):
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            href = link.get_attribute("href")
            if href and "/p/" in href:
                post_urls.add(href)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    driver.quit()
    return list(post_urls)

# Kadıköy için örnek kullanım
if __name__ == "__main__":
    location_url = "https://www.instagram.com/explore/locations/213418880/kadikoy-istanbul-turkey/"
    posts = get_instagram_location_posts(location_url)

    if posts:
        print(f"{len(posts)} gönderi bulundu:")
        for url in posts:
            print(url)
    else:
        print("Gönderi bulunamadı.")
