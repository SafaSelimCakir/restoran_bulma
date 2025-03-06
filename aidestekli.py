import requests
from bs4 import BeautifulSoup
import csv
import time

def get_restaurants(city, district):
    search_query = f"{city} {district} restoranları"
    url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ Google'a bağlanılamadı. Durum kodu:", response.status_code)
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    restaurant_list = []
    names = soup.find_all("div", class_="BNeawe vvjwJb AP7Wnd")
    addresses = soup.find_all("span", string=lambda text: text and "·" in text)

    if not names:
        print("\n❌ Hiç restoran ismi bulunamadı. Google HTML yapısı değişmiş olabilir.")
    
    if not addresses:
        print("\n❌ Hiç adres bulunamadı. Google HTML yapısı değişmiş olabilir.")

    for i in range(min(len(names), len(addresses))):
        name = names[i].get_text(strip=True)
        address = addresses[i].find_next("span").get_text(strip=True)

        restaurant_list.append({
            "name": name,
            "address": address,
            "phone": None
        })

    return restaurant_list

def search_google(query):
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    phone_match = soup.find(string=lambda text: text and text.startswith("+90"))
    phone = phone_match.strip() if phone_match else "Telefon Bulunamadı"
    return phone

def fill_missing_data(restaurants):
    for restaurant in restaurants:
        if not restaurant["phone"]:
            query = f"{restaurant['name']} {restaurant['address']} telefon numarası"
            phone = search_google(query)
            if phone:
                restaurant["phone"] = phone
            time.sleep(2)
    return restaurants

def save_to_csv(restaurants, filename="restoranlar.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["İsim", "Adres", "Telefon"])
        empty_rows = 0
        for rest in restaurants:
            if not rest["name"] or not rest["address"]:
                empty_rows += 1
                continue
            writer.writerow([rest["name"], rest["address"], rest["phone"] or "Telefon Bulunamadı"])
        if empty_rows > 0:
            print(f"\n⚠️ {empty_rows} boş restoran bilgisi CSV'ye kaydedilmedi.")
    print(f"\n✅ Veriler '{filename}' dosyasına kaydedildi.")

def main():
    city = "İstanbul"
    district = "Kadıköy"
    restaurants = get_restaurants(city, district)
    filled_restaurants = fill_missing_data(restaurants)
    save_to_csv(filled_restaurants)

if __name__ == "__main__":
    main()
