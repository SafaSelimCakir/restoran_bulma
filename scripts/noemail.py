import pandas as pd
import os

def is_valid_email(email):
    blacklist_domains = ["sentry.wixpress.com", "sentry-next.wixpress.com"]
    return not any(domain in email for domain in blacklist_domains)

def filter_no_email_entries():
    csv_file = input("Filtrelemek istediğiniz CSV dosyasının adını girin (data veya guncellenmiş data klasöründe olmalı): ")

    csv_paths = [
        os.path.join("data", csv_file),
        os.path.join("guncellenmiş data", csv_file)
    ]

    csv_path = next((path for path in csv_paths if os.path.exists(path)), None)

    if not csv_path:
        print(f"Hata: {csv_file} dosyası 'data' veya 'guncellenmiş data' klasörlerinde bulunamadı!")
        return
    
    df = pd.read_csv(csv_path)

    print("CSV Dosyasındaki Sütunlar:")
    print(df.columns)

    if "E-posta" not in df.columns:
        print("Hata: CSV dosyasında 'E-posta' sütunu bulunamadı!")
        return

    df_filtered = df[df["E-posta"].notna() & 
                     (df["E-posta"] != "No Email Found") & 
                     (df["E-posta"] != "Error Accessing Site") &  
                     (df["E-posta"] != "No Website") & 
                     df["E-posta"].apply(is_valid_email)]  

    output_dir = "filtrelenmis_data"
    os.makedirs(output_dir, exist_ok=True)

    new_file_name = f"filtreli_{os.path.splitext(csv_file)[0]}.csv"
    new_csv_path = os.path.join(output_dir, new_file_name)

    df_filtered.to_csv(new_csv_path, index=False, encoding="utf-8")

    print(f"\nGüncellenmiş veriler '{new_csv_path}' olarak kaydedildi! (Geçersiz e-posta adresleri çıkarıldı)")

filter_no_email_entries()
