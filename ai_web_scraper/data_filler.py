import requests
from bs4 import BeautifulSoup
import re
import time

def search_google(query):
    """ Google araması yaparak restoran bilgilerini toplar. """
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Google'dan telefon numarası veya adres arıyoruz
    phone = None
    address = None
    
    # Telefon numarası arama (Google'dan çıkan telefon numaralarını toplar)
    phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3}[-.\s]?\d{4}", soup.get_text())
    if phone_match:
        phone = phone_match.group(0)

    # Adres arama (Google arama sonuçlarındaki adresleri toplar)
    address_match = soup.find("span", {"class": "LrzXr"})
    if address_match:
        address = address_match.get_text(strip=True)
    
    # Debugging: Çekilen verileri yazdır
    print(f"Google Araması - Sorgu: {query}")
    print(f"Telefon: {phone}")
    print(f"Adres: {address}")
    
    return phone, address

def fill_missing_data(restaurants):
    """ Eksik verileri tamamlar (Telefon ve adres) """
    for restaurant in restaurants:
        if not restaurant["phone"] or not restaurant["address"]:
            print(f"⏳ {restaurant['name']} için eksik veriler aranıyor...")
            query = f"{restaurant['name']} {restaurant['address'] or ''}"
            phone, address = search_google(query)

            # Telefon ve adresi güncelle
            if phone and not restaurant["phone"]:
                restaurant["phone"] = phone
            if address and not restaurant["address"]:
                restaurant["address"] = address

            time.sleep(2)  # Google'a çok hızlı istek göndermemek için bekleme

    return restaurants
