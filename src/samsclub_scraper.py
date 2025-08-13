"""
Sam's Club Category Scraper
- Paste any Sam's Club category page URL, get a CSV of products
- Uses Selenium for JavaScript-rendered content
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
# SETTINGS: CHANGE THESE
# --------------------------
URLS = [
    "https://www.samsclub.com/browse/pantry/1532",  # Pantry
    # Add more category URLs here
]
CHROMEDRIVER_PATH = "../chromedriver"                          # Update to your actual path!
OUTPUT_FILE = "../data/interim/samsclub_prices.csv"
HEADLESS_MODE = False
WAIT_TIME = 20

# --------------------------
# SCRAPER
# --------------------------

def get_html_selenium(url):
    """Load Sam's Club page in Selenium so JS products appear."""
    chrome_options = Options()
    if HEADLESS_MODE:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)

    # Wait for any product title to appear
    try:
        WebDriverWait(driver, WAIT_TIME).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.w_q67L"))
        )
    except:
        print(f"⚠ Timeout waiting for products at {url}")

    # Scroll to ensure all products load (if paginate/lazy load)
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(8):   # Adjust scroll tries as needed for page length
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    html = driver.page_source
    driver.quit()
    return html

def parse_products(html, category_url):
    """Extract product info from a Sam's Club category page."""
    soup = BeautifulSoup(html, "lxml")
    items = []

    # Each product tile often is inside role=group divs
    for product in soup.find_all("div", {"role": "group"}):
        # Product name
        name_tag = product.find("span", class_="w_q67L")
        name = name_tag.get_text(strip=True) if name_tag else ""

        # Price (current price, usually in div with b, black)
        price_tag = product.select_one("div.b.black")
        if not price_tag:
            price_tag = product.select_one("div.b.black.black")  # fallback
        price = price_tag.get_text(strip=True) if price_tag else ""

        # Price per unit (e.g. "$0.34/oz")
        ppu_tag = product.find("div", {"data-testid": "product-price-per-unit"})
        ppu_raw = ppu_tag.get_text(strip=True) if ppu_tag else ""
        ppu_value = ""
        ppu_unit = ""
        if ppu_raw:
            import re
            match = re.match(r"\$?([\d\.]+)[\/ ]*([a-zA-Z\.]+)", ppu_raw)
            if match:
                ppu_value = match.group(1)
                ppu_unit = match.group(2)

        # Rating
        rating_tag = product.find("span", {"data-testid": "product-ratings"})
        rating = rating_tag["data-value"] if rating_tag and rating_tag.has_attr("data-value") else ""

        # Reviews
        reviews_tag = product.find("span", {"data-testid": "product-reviews"})
        reviews = reviews_tag["data-value"] if reviews_tag and reviews_tag.has_attr("data-value") else ""

        # Size/Unit (try to extract from product name or ppu field)
        size_unit = ""
        size_value = ""
        try:
            import re
            size_match = re.search(r"(\d+(\.\d+)?)\s*([a-zA-Z\.]+)", name)
            if size_match:
                size_value = size_match.group(1)
                size_unit = size_match.group(3)
        except Exception:
            pass

        if name and price:
            items.append({
                "Category URL": category_url,
                "Product Name": name,
                "Price": price,
                "Size/Unit": f"{size_value} {size_unit}",
                "Size_value": size_value,
                "Size_unit": size_unit,
                "Rating": rating,
                "Reviews": reviews,
                "Price_per_unit_raw": ppu_raw,
                "Price_per_unit_value": ppu_value,
                "Price_per_unit_unit": ppu_unit
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
