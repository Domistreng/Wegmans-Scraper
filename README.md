# Wegmans Category Web Scraper

## Overview
This project is a **Python-based web scraper** that extracts product names, prices, and size/unit information from Wegmans category pages.  
It uses **Selenium** to render JavaScript-heavy content and **BeautifulSoup** for HTML parsing.

⚠ **Note:**  
This repository contains only the scraper **code** — no scraped data is included.  
Users are responsible for ensuring any scraping activity complies with Wegmans’ Terms of Service and applicable laws.

---

## Features
- Supports any Wegmans category page (just paste the URL into the script).
- Extracts:
  - Product Name  
  - Price  
  - Size/Unit (if available)
- Works with JavaScript-generated pricing using Selenium.
- Infinite scroll handling for long category lists.
- Saves results to a CSV file (if enabled).

---

## Requirements

Install dependencies:

```python
pip install selenium beautifulsoup4 pandas lxml
```

You also need **ChromeDriver** for your version of Chrome:  
[https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)

---

## Usage

1. **Set your Wegmans store location** by logging into Wegmans.com in a regular browser so you get accurate local prices.  
2. Edit the script variables:

```python
URL = "PASTE_CATEGORY_URL_HERE"
CHROMEDRIVER_PATH = "/path/to/chromedriver"
OUTPUT_FILE = "wegmans_prices.csv"
```
3. Run: python wegmans_scraper.py

If you wish to avoid saving data in your repo, add the CSV output file to your `.gitignore`:

```
Ignore output data
*.csv
```


---

## Legal & Ethical Disclaimer
- This project is provided **for educational purposes only**.  
- Scraping any website **may** violate its [Terms of Service](https://www.wegmans.com/service/terms/) — check and comply before use.
- The author is **not responsible** for any misuse of this project.
- Do not overload Wegmans’ servers — use respectful scraping practices (minimal requests, pauses, etc.).
- No scraped data from Wegmans is included in this repository.

---

## Future Improvements
- Support multiple category URLs in a single run.
- Add category tagging to output.
- Option to read category URLs from a file.

---

## License
This project is released under the **MIT License**. You are free to use, modify, and share the code — but at your own responsibility.
