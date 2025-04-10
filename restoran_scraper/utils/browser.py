from selenium import webdriver
from utils.user_agent import get_random_user_agent

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={get_random_user_agent()}")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    options.add_argument("--headless=new")
    return webdriver.Chrome(options=options)
