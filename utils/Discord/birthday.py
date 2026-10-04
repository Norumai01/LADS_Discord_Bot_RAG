import datetime
import json
import os
import re
import discord
import logging

from paths import ROOT

JSON_FILE = str(ROOT / "data" / "birthday.json")

logger = logging.getLogger(__name__)

def loadBirthdayData() -> dict:
    """
    Load birthday data from the file.

    Return:
        Birthday data or empty dictionary
    """
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
    """
    Save birthday data to the file.

    Args:
        data: Birthday data to save

    Returns:
        None
    """
    with open(JSON_FILE, "w") as f:
        logger.info("Saving birthday to data file...")
        json.dump(data, f, indent=4)

def extractUserIDFromMention(mentionUser: str) -> int | None:
    """
    Extract user ID from mention string.

    Args:
        mentionUser: Mention string
    Return:
        User ID or None if invalid mention
    """
    match = re.search(r"<@!?(\d+)>", mentionUser)
    if match:
        return int(match.group(1))
    return None

async def pingBirthdayMessage(bot, message: discord.Message, targetUser: str | None = None) -> None:
    """
    Announce a birthday message to a user on server.

    Args:
        bot: Discord bot instance
        message: Discord message object
        targetUser: Mention string of the user to ping

    Return:
        None
    """
    logger.info("Skipping birthday schedule search. Sending birthday message to user...")

    targetID: int | None = extractUserIDFromMention(targetUser) if targetUser else None
    if not targetID:
        logger.error("Invalid user mention provided.")
        return

    if not message.guild:
        logger.error("Message is not send on the server.")
        return

    targetMember: discord.Member | None = message.guild.get_member(targetID)
    if not targetMember:
        logger.error(f"User with ID {targetID} not found in the server.")
        await message.channel.send("User not found.")
        return

    # TODO: Implement actual birthday message
    logger.info("Message announced to user.")

async def runImmediateTest(bot, targetID: str | None = None) -> None:
    """
    Run an immediate test to send a test private message to user for testing purposes.

    Args:
        bot: Discord bot instance
        targetID: User ID to send the test message to

    Return:
        None
    """
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