import rag_pipeline
import discord
import asyncio
import logging
from utils.logger_config import initiateLogging


def main():
    logger = logging.getLogger(__name__)
    logger.info("Starting the Discord bot...")
    # Add discord code here
    logger.info("Discord bot successfully started.")
    rag_pipeline.save_response("Discord bot is running and ready to handle messages.")
    

if __name__ == "__main__":
    # Initialize the logging system
    logDir: str = "logs"
    initiateLogging(logDir)

    main()