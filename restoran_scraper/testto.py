import requests
from googlesearch import search
from bs4 import BeautifulSoup
import re

def find_restaurant_email(restaurant_name, city):
    # Google'da restoran adını ve şehri arama
    query = f"{restaurant_name} {city} site"
    search_results = search(query, num_results=5)  # İlk 5 sonucu al

    for url in search_results:
        try:
            # Sayfayı çekme
            response = requests.get(url)
            response.raise_for_status()

            # Sayfayı analiz etme
            soup = BeautifulSoup(response.text, 'html.parser')

            # E-posta adresini arama (HTML'de genellikle mailto: ile bulunur)
            emails = set(re.findall(r"mailto:([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", str(soup)))

            if emails:
                return emails  # Bulunduğu takdirde e-posta döndürülür
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            continue

    return None  # E-posta bulunamazsa None döner

def main():
    restaurant_name = input("Restoran adı: ")
    city = input("Şehir: ")

    emails = find_restaurant_email(restaurant_name, city)

    if emails:
        print(f"Bulunan e-posta adresleri: {emails}")
    else:
        print("E-posta adresi bulunamadı.")

if __name__ == "__main__":
    main()
