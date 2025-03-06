import csv
from scraper import get_restaurants
from verifier import verify_data
from data_filler import fill_missing_data

def save_to_csv(restaurants, filename="restoranlar.csv"):
    """ Restoran verilerini CSV dosyasına kaydeder. """
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["İsim", "Adres", "Telefon"])  # Başlık satırı

        for rest in restaurants:
            # Eğer restoran bilgileri eksikse kaydetme
            if not rest["name"] or not rest["address"] or not rest["phone"]:
                continue

            writer.writerow([rest["name"], rest["address"], rest["phone"]])
    
    print(f"\n✅ Veriler '{filename}' dosyasına kaydedildi.")


def main():
    city = input("Lütfen şehir girin: ")
    district = input("Lütfen ilçe girin: ")

    print("\n📡 Restoran bilgileri çekiliyor...")
    restaurants = get_restaurants(city, district)

    print("\n✅ Yapay zeka doğrulaması yapılıyor...")
    verified_restaurants = verify_data(restaurants)

    # Eksik veriyi doldur
    print("\n🔄 Eksik veriler dolduruluyor...")
    filled_restaurants = fill_missing_data(verified_restaurants)

    # Sonuçları yazdır
    print("\n📌 Doğrulanan ve Doldurulmuş Restoranlar:")
    for rest in filled_restaurants:
        print(f"🍽️ {rest['name']}")
        print(f"📍 Adres: {rest['address']}")
        print(f"📞 Telefon: {rest['phone']}")
        print("-" * 50)

    # CSV'ye kaydet
    save_to_csv(filled_restaurants)

if __name__ == "__main__":
    main()
