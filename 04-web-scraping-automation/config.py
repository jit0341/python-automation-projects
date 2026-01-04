CLIENT_NAME = "Quotes Collection"
PROJECT_NAME = "Web Scraping - Quotes"
BASE_URL = "https://quotes.toscrape.com"
NUM_PAGES = 3  # Scrape 3 pages (30 quotes)
OUTPUT_FILE = "quotes_data.csv"
LOG_FILE = "logs/scraper.log"

# Request Headers (Ethical Scraping)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AutomationBot/1.0)"
}
