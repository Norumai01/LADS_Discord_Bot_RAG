import datetime
import json
import os
import re
import discord
import logging

from paths import ROOT

JSON_FILE = str(ROOT / "data" / "birthday.json")

logger = logging.getLogger(__name__)

def loadBirthdayData():
    if not os.path.exists(JSON_FILE):
        logger.warning("Birthday data file not found.")
        return {}
    with open(JSON_FILE, "r") as f:
        try:
            logger.info("Loaded birthday data file.")
            return json.load(f)
        except json.JSONDecodeError:
            logger.error("Error decoding birthday data file.")
            return {}

def saveBirthdayData(data) -> None:
    with open(JSON_FILE, "w") as f:
        logger.info("Saving birthday to data file...")
        json.dump(data, f, indent=4)

async def runImmediateTest(bot, targetID: str | None = None):
    logger.info("Bypassing birthday schedule. Attempting to send test right now...")

    birthday: dict = loadBirthdayData()
    if not birthday:
        logger.error("Birthday data file is empty or does not exist.")
        return

    if targetID:
        if targetID not in birthday:
            logger.error(f"User with ID {targetID} not found in birthday data.")
            return

    for user_id, birthday_data in birthday.items():
        try:
            if user_id != targetID:
                continue

            user: discord.User = await bot.fetch_user(int(user_id))

            # Send them a test message
            await user.send(f"Test message from bot!")
        except discord.Forbidden:
            logger.error(f"Failed to send test message to user {user_id}. Private message blocked.")
        except Exception as e:
            logger.error(f"Failed to send test message to user {user_id}. Error: {e}")

    logger.info("Test message sent.")