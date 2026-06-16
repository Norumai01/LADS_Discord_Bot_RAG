import logging

from utils.chroma import ChromaDatabase

logger = logging.getLogger(__name__)

async def deleteUserMemory(doc_ids: str | list[str]) -> bool:
    """
    Deletes user memory entries from the database corresponding to the deleted messages.

    Args:
        doc_ids (str | list[str]): A single document ID or a list of document IDs to delete.
    
    Returns:
        bool: True if the deletion was successful, False if some (if not all) failed.
    """
    if not doc_ids or not isinstance(doc_ids, (str, list)):
        logger.error("Invalid document IDs provided for deletion. Must be a string or a list of strings.")
        return False
    
    if isinstance(doc_ids, str):
        doc_ids = [doc_ids]  # Convert to list for uniform processing
    
    if len(doc_ids) <= 0:
        logger.error("No valid document IDs provided for deletion.")
        return False
    
    # Initialize the user memory database
    user_memory_database: ChromaDatabase = ChromaDatabase("./chroma_db", collection_names="user_memory")

    try:
        user_memory_database.collection.delete(ids=doc_ids)
        logger.info("Successfully deleted user memory entries for document IDs.")
        return True
    except Exception as e:
        logger.error(f"Error occurred while trying to delete user memory entries: {e}")
        return False