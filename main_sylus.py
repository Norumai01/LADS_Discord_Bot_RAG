# Standard library
import os
from dotenv import load_dotenv
import logging

# Custom modules
from utils.logger_config import initiateLogging
from utils.bot import initiateDiscordBot

load_dotenv()

def main() -> None:
    # Initialize the logging system
    logDir: str = "logs"
    initiateLogging(logDir, "discord_bot")

    # Configure the logger
    logger = logging.getLogger(__name__)
    logger.info("Starting the Discord bot...")

    # Initialize the Discord bot
    token: str = os.getenv("DISCORD_TOKEN") or ""
    if token is None or token == "":
        logger.error("DISCORD_TOKEN is not set in the environment variables.")
        exit(1)
    initiateDiscordBot(token, "sylus")

    logger.info("Discord bot successfully started.")
    

if __name__ == "__main__":
    main()