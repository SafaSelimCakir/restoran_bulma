import requests
import re
from utils.headers import get_random_user_agent

def extract_emails_from_url(url):
    try:
        headers = {"User-Agent": get_random_user_agent()}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", response.text)
            return ", ".join(set(emails)) if emails else "E-posta bulunamadı"
        else:
            return "Siteye erişilemedi"
    except:
        return "Site hatası"
