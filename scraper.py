from pathlib import Path
from bs4 import BeautifulSoup
import re

import logging
from playwright.sync_api import sync_playwright
from utils.logger_config import initiateLogging

URLS: dict[str, list[str]] = {
    "sylus": [
        "https://loveanddeepspace.fandom.com/wiki/Sylus",
        "https://lads.wiki/wiki/Sylus/About_Him",
        "https://syluslorelads.substack.com/p/beyond-cloudfall-fan-translation",
        "https://syluslorelads.substack.com/p/chapter-2-massacre-in-the-sanctuary",
        "https://syluslorelads.substack.com/p/chapter-3-kindred-spirits",
        "https://syluslorelads.substack.com/p/chapter-4-the-prophecy",
        "https://syluslorelads.substack.com/p/chapter-5-foreshadowing"
    ],
}
DATA_DIR = Path("data")
OUTPUT_FILE = DATA_DIR / "sylus_raw.txt"

def main():
    # Initialize the logging system
    logDir: str = "logs"
    initiateLogging(logDir, "scraper")
    logger = logging.getLogger(__name__)

    # Ensure the data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Scrape each character's data'
    for character, urls in URLS.items():
        if not urls:
            logger.info(f"No URLs for {character}, skipping.")
            continue

        logger.info(f"Starting scrape for: {character}")
        content = scrape(urls)

        outputFile = DATA_DIR / f"{character}_raw.txt"
        with open(outputFile, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Saved {character} data to {outputFile}")

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

            # Try wiki selector first, fall back to common article selectors
            html = None
            for selector in ["div.mw-parser-output", "article", "div.post-content", "main"]:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    html = page.inner_html(selector)
                    logger.info(f"Content found using selector: {selector}")
                    break
                except Exception:
                    continue

            if html is None:
                logger.warning(f"No content selector matched for {url}, skipping.")
                continue

            soup = BeautifulSoup(html, "html.parser")

            # Remove common wiki noise
            for tag in soup.select(
                    "sup, "  # reference numbers [1] [2]
                    ".toc, "  # table of contents
                    ".navbox, "  # site navigation at bottom
                    ".mw-editsection, "  # [edit] links
                    "table, "  # affinity rewards table
                    ".spoiler"  # spoiler templates
            ):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)

            # Clean up leftover bracket artifacts and blank lines
            text = re.sub(r"\[\s*\d+\s*\]", "", text)  # [ 1 ], [ 2 ]
            text = re.sub(r"\n{3,}", "\n\n", text)  # excessive blank lines

            # Additional cleanup
            text = re.sub(r"^(Overview|Memories|Gallery|Lore|Collectibles)\n", "", text, flags=re.MULTILINE)  # nav tabs
            text = re.sub(r"Subscribe to.*?Privacy Policy\.", "", text, flags=re.DOTALL)  # Substack footer

            content.append(text)
            logger.info(f"Extracted content from {url} with length {len(text)}.")

        browser.close()

    logger.info("Scraping service completed.")
    return "\n\n".join(content)

if __name__ == "__main__":
    main()