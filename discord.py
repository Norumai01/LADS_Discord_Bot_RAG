import rag_pipeline
import discord
import asyncio
import logging
import os
from datetime import datetime

def InitiateLogging(directory: str):
    timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S");
    logFile = os.path.join(directory, f"log_{timestamp}.log");

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=logFile,
        filemode='a',
    );

def main():
    logger = logging.getLogger(__name__)
    logger.info("Starting the Discord bot...");
    # Add discord code here
    logger.info("Discord bot successfully started.");
    rag_pipeline.save_response("Discord bot is running and ready to handle messages.");
    

if __name__ == "__main__":
    # Initialize the logging system
    logDir: str = "logs";
    if not os.path.exists(logDir):
        os.makedirs(logDir);
    InitiateLogging(logDir);
    
    main();