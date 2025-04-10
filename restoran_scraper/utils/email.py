import re
import requests
from selenium.webdriver.common.by import By
import time

from utils.user_agent import get_random_user_agent

def extract_email(website_url):
    if website_url == "N/A":
        return ""
    try:
        headers = {"User-Agent": get_random_user_agent()}
        response = requests.get(website_url, headers=headers, timeout=10)
        emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", response.text)
        return ", ".join(set(emails)) if emails else ""
    except:
        return ""

def extract_emails_from_map_popup(driver):
    # Harita üzerindeki pop-up açıklamalarını kontrol et
    emails = []
    try:
        email_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '@')]")
        for email_element in email_elements:
            email = email_element.text.strip()
            if re.match(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", email):
                emails.append(email)
    except Exception as e:
        print(f"Pop-up'tan e-posta çıkarma hatası: {e}")
    return emails

def get_restaurant_info(driver, link):
    driver.get(link)
    time.sleep(5)
    try:
        name = driver.find_element(By.CSS_SELECTOR, 'h1.DUwDvf').text
    except:
        name = ""
    try:
        address = driver.find_element(By.XPATH, "//button[contains(@data-tooltip, 'Adres')]//div[2]").text
    except:
        address = ""
    try:
        phone = driver.find_element(By.XPATH, "//button[contains(@data-tooltip, 'Telefon')]//div[2]").text
    except:
        phone = ""
    try:
        website = driver.find_element(By.XPATH, "//a[contains(@aria-label, 'Web sitesi')]").get_attribute("href")
    except:
        website = "N/A"
    
    emails = extract_emails_from_map_popup(driver)  # Pop-up'lardan e-posta al
    email = extract_email(website) if website != "N/A" else ""
    email += ", ".join(emails)
    
    return {
        "Ad": name,
        "Adres": address,
        "Telefon": phone,
        "E-posta": email,
        "Web Sitesi": website,
        "Google Maps Link": link,
    }
