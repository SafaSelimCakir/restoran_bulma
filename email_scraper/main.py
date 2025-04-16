from scraper.google_maps import scrape_google_maps
from utils.logger import log_info

def main():
    log_info("Scraping başlıyor...")
    scrape_google_maps("Kocaeli", "Başiskele")

if __name__ == "__main__":
    main()
