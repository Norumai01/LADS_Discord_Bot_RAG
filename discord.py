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
        format="[%(asctime)s] [%(levelname)s] - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=logFile,
        filemode='a',
    );

def main():
    logging.info("Starting the Discord bot...");
    # Add your Discord bot code here
    logging.info("Discord bot started successfully.");

if __name__ == "__main__":
    # Initialize the logging system
    logDir: str = "logs";
    if not os.path.exists(logDir):
        os.makedirs(logDir);
    InitiateLogging(logDir);
    
    main();