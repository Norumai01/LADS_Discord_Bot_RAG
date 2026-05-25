import argparse
import logging
from pathlib import Path

from utils.Data_Gathering.loader import saveDataToChroma
from utils.Data_Gathering.scrape import scrape
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
CHROMA_PATH = "./chroma_db"

# Initialize the logging system
logDir: str = "logs"
initiateLogging(logDir, "scraper")
logger = logging.getLogger(__name__)

def runScraper(links: dict[str, list[str]]) -> None:
   # Ensure the data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Scrape each character's data'
    for character, urls in links.items():
        if not urls:
            logger.info(f"No URLs for {character.capitalize()}, skipping.")
            continue

        logger.info(f"Starting scrape for: {character.capitalize()}...")
        content = scrape(urls)
        if content == "" or content is None:
            logger.error(f"No content found for {character.capitalize()}, skipping.")
            continue

        outputFile = DATA_DIR / f"{character}_raw.txt"
        with open(outputFile, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Saved {character.capitalize()} data to {outputFile}")

def runLoader(inputFile: Path) -> None:
    # Check if the data directory is empty
    if not inputFile.exists() or not any(inputFile.iterdir()):
        logger.error("No data files found in the data directory.")
        exit(1)

    # Save all character's data to Chroma DB
    for character in URLS.keys():
        if not (DATA_DIR / f"{character}_raw.txt").exists():
            logger.warning(f"No data file found for {character.capitalize()}, skipping.")
            continue

        saveDataToChroma(inputFile / f"{character}_raw.txt", character)

def main():
    """
    Command-lines interface:

    * python scraper.py --scrape
    * python scraper.py --save
    * python scraper.py --all
    * python scraper.py --character {character_name} --scrape
    * python scraper.py --character {character_name} --save
    * python scraper.py --character {character_name} --all
    """
    parser = argparse.ArgumentParser(description="Scrape and save character data.")
    parser.add_argument("--scrape", action="store_true", help="Scrape character data.")
    parser.add_argument("--save", action="store_true", help="Save character data to Chroma DB.")
    parser.add_argument("--all", action="store_true", help="Scrape and save all character data.")
    parser.add_argument("--character", type=str, help="Scrape and save a specific character's data.")
    args = parser.parse_args()

    if args.scrape:
        runScraper(URLS)
        exit(0)
    if args.save:
        runLoader(DATA_DIR)
        exit(0)
    if args.all:
        runScraper(URLS)
        runLoader(DATA_DIR)
        exit(0)

if __name__ == "__main__":
    main()