import logging

from utils.sqlite_db import SQLiteDB

logger = logging.getLogger(__name__)

async def deleteUserConversation(message_ids: str | list[str]) -> bool:
    """
    Deletes user conversation entries from the database corresponding to the deleted messages.

    Args:
        message_ids (str | list[str]): A single message ID or a list of message IDs to delete.
    
    Returns:
        bool: True if the deletion was successful, False if some (if not all) failed.
    """
    if not message_ids or not isinstance(message_ids, (str, list)):
        logger.error("Invalid message IDs provided for deletion. Must be a string or a list of strings.")
        return False
    
    if isinstance(message_ids, str):
        message_ids = [message_ids]  # Convert to list for uniform processing
    
    if len(message_ids) <= 0:
        logger.error("No valid message IDs provided for deletion.")
        return False

    # Initialize the SQLite database
    sqlite_database: SQLiteDB = SQLiteDB()

    try:
        await sqlite_database.delete_messages(message_ids)
        logger.info("Successfully deleted user conversation entries for message IDs.")
        return True
    except Exception as e:
        logger.error(f"Error occurred while trying to delete user conversation entries: {e}")
        return False