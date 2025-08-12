"""
Wegmans Multi-Category Scraper
- Give it a list of Wegmans category URLs
- Scrapes product name, price, size/unit, rating, and reviews
- Adds a 'Category URL' column to output
"""

import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --------------------------
# SETTINGS
# --------------------------
URLS = [
    "https://www.wegmans.com/shop/categories/2957350",  # Fruit
    "https://www.wegmans.com/shop/categories/2957333", # Vegetables
    "https://www.wegmans.com/shop/categories/2957104",  # Chicken
    "https://www.wegmans.com/shop/categories/2957425", # Butter
    "https://www.wegmans.com/shop/categories/2957426", # Cheese
    "https://www.wegmans.com/shop/categories/2957472", # Baking

    # Add more URLs here
]
CHROMEDRIVER_PATH = "../chromedriver"
OUTPUT_FILE = "../data/interim/wegmans_multi_prices.csv"
HEADLESS_MODE = True
WAIT_TIME = 20

# --------------------------
# SCRAPER FUNCTIONS
# --------------------------

def get_html_selenium(url):
    """Load a Wegmans category page in Selenium."""
    chrome_options = Options()
    if HEADLESS_MODE:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)

    # Wait for at least one product tile
    try:
        WebDriverWait(driver, WAIT_TIME).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "component--product-tile"))
        )
    except:
        print(f"⚠ Timeout waiting for products at {url}")

    # Scroll until all products are loaded
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    html = driver.page_source
    driver.quit()
    return html

def parse_products(html, category_url):
    """Extract products from HTML and return list of dicts."""
    soup = BeautifulSoup(html, "lxml")
    items = []

    for product in soup.find_all("div", class_="component--product-tile"):
        name_tag = product.find("h3", class_="component--base-heading")
        name = name_tag.get_text(strip=True) if name_tag else ""

        price_tag = product.find("span", attrs={"data-testid": "best-price-container"})
        if not price_tag:
            price_tag = product.select_one("div.component--product-price span")
        price = price_tag.get_text(strip=True) if price_tag else ""

        size_tag = product.find("span", class_="price-per-unit")
        size = size_tag.get_text(strip=True) if size_tag else ""

        rating_tag = product.find("div", itemprop="ratingValue")
        rating = rating_tag.get_text(strip=True) if rating_tag else ""

        review_tag = product.find("meta", itemprop="reviewCount")
        reviews = review_tag['content'] if review_tag else ""

        if name:
            items.append({
                "Category URL": category_url,
                "Product Name": name,
                "Price": price,
                "Size/Unit": size,
                "Rating": rating,
                "Reviews": reviews
            })

    return items

def main():
    all_data = []
    for url in URLS:
        print(f"[*] Loading category: {url}")
        html = get_html_selenium(url)
        print("[*] Extracting products...")
        products = parse_products(html, url)
        print(f"✔ Found {len(products)} products in {url}")
        all_data.extend(products)

    df = pd.DataFrame(all_data)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Saved {len(df)} total products from {len(URLS)} categories to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
