from bs4 import BeautifulSoup
import re
import logging
from playwright.sync_api import sync_playwright

def scrape(urls: list[str]) -> str:
    """
    Scrapes text content from a list of URLs using a headless browser.
    Handles wiki pages and article-based sites with fallback selectors.

    Args:
        urls (list[str]): List of URLs to scrape.

    Returns:
        str: Cleaned and concatenated text content from all successfully scraped URLs.
    """
    logger = logging.getLogger(__name__)
    logger.info("Scraping service started...")

    if urls is None or not urls:
        logger.error("No URLs provided for scraping.")
        return ""

    content: list[str] = []

    with sync_playwright() as p:
        # Launch headless browser with a realistic user agent to avoid bot detection
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