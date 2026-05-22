from pathlib import Path
from bs4 import BeautifulSoup
import re

import logging
from playwright.sync_api import sync_playwright
from utils.logger_config import initiateLogging

URL = ["https://loveanddeepspace.fandom.com/wiki/Sylus"]
DATA_DIR = Path("data")
OUTPUT_FILE = DATA_DIR / "sylus_raw.txt"

def scrape(urls: list[str]) -> str:
    logger = logging.getLogger(__name__)
    logger.info("Scraping service started...")

    content: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for url in urls:
            logger.info(f"Scraping: {url}")
            page.goto(url, wait_until="domcontentloaded")

            logger.info("Waiting for content to load...")
            page.wait_for_selector("div.mw-parser-output", timeout=15000)

            html = page.inner_html("div.mw-parser-output")

            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator="\n", strip=True)

            content.append(text)
            logger.info(f"Extracted content from {url} with length {len(text)}.")

        browser.close()

    logger.info("Scraping service completed.")
    return "\n\n".join(content)

def main():
    # Initialize the logging system
    logDir: str = "logs"
    initiateLogging(logDir, "scraper")
    logger = logging.getLogger(__name__)

    # Create the data directory if it doesn't exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Start scraping
    content: str = scrape(URL)
    logger.info("Writing to file...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write(content)
    logger.info("File written successfully.")


if __name__ == "__main__":
    main()