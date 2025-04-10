from scraper.google_maps import scrape_google_maps
#from scraper.linkedin import scrape_linkedin
#from scraper.generic_site import scrape_generic
from utils.logger import log_info

def main():
    log_info("Scraping başlıyor...")
    scrape_google_maps("İstanbul", "Kadıköy")
    #scrape_linkedin("yazılım geliştirici", "Türkiye")
    #scrape_generic("https://ornekfirma.com")

if __name__ == "__main__":
    main()
