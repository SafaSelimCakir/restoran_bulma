import os
import requests
import re
import time
import random
import pandas as pd
from googlesearch import search

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.64 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
]

def get_emails_from_google(query, num_results=5):
    """Google'dan e-posta adreslerini çeker."""
    emails = set()
    print(f"\nGoogle'da '{query}' sorgusu yapılıyor...")

    for url in search(query, num_results=num_results):
        print(f"Site kontrol ediliyor: {url}")

        try:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            response = requests.get(url, headers=headers, timeout=10, verify=False)  

            if response.status_code == 200:
                page_content = response.text
                found_emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", page_content)

                if found_emails:
                    emails.update(found_emails)
                    print(f"Bulunan e-postalar: {found_emails}")

            time.sleep(random.randint(2, 5))  

        except requests.exceptions.RequestException as e:
            print(f"Hata: {e}")

    return emails

def update_missing_emails(csv_path):
    """CSV dosyasındaki eksik e-postaları Google'dan arayarak günceller ve yeni dosya olarak 'guncellenmiş data' klasörüne kaydeder."""
    if not os.path.exists(csv_path):
        print(f"Hata: {csv_path} bulunamadı!")
        return
    
    df = pd.read_csv(csv_path)

    required_columns = ["Restoran Adı", "Adres", "Telefon", "E-posta", "Web Sitesi", "Link"]
    for col in required_columns:
        if col not in df.columns:
            print(f"Hata: CSV dosyasında '{col}' sütunu eksik!")
            return

    missing_email_rows = df[df["E-posta"].isna() | (df["E-posta"] == "No Email Found") | (df["E-posta"] == "Error Accessing Site")]

    if missing_email_rows.empty:
        print("Tüm restoranların e-posta adresleri var, işlem yapılmadı.")
        return
    
    for index, row in missing_email_rows.iterrows():
        business_name = row["Restoran Adı"]
        city = row["Adres"]
        query = f"{business_name} {city} email OR contact OR iletişim OR mail"

        found_emails = get_emails_from_google(query)

        if found_emails:
            df.at[index, "E-posta"] = list(found_emails)[0]  

    output_dir = "guncellenmiş data"
    os.makedirs(output_dir, exist_ok=True)  

    new_file_name = f"guncellenmis_{os.path.splitext(os.path.basename(csv_path))[0]}.csv"
    new_csv_path = os.path.join(output_dir, new_file_name)

    df.to_csv(new_csv_path, index=False, encoding="utf-8")

    print(f"\nGüncellenmiş CSV dosyası kaydedildi: {new_csv_path}")

csv_file = input("filtrelemek istediğiniz CSV dosyasının adını girin (data klasöründe olmalı): ")
csv_path = os.path.join("data", csv_file)

update_missing_emails(csv_path)
