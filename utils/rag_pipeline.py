import asyncio
import logging

from utils.RAG.llm_response import llmResponse
from utils.chroma import ChromaDatabase

logger = logging.getLogger(__name__)

async def ragPipeline(user_input: str, username: str) -> str:
    """
    Executes the Retrieval-Augmented Generation (RAG) pipeline.

    Args:
        user_input (str): The input message from the user.
        context (str): The retrieved context from the database.
        username (str): The name of the user who sent the message.

    Returns:
        str: The generated response based on the user input and context.
    """
    logger.info("Executing RAG pipeline...")

    if not user_input or user_input.strip() == "":
        logger.warning("User input is empty. Cannot execute RAG pipeline.")
        return ""
    if not username or username.strip() == "":
        logger.warning("Username is empty. Cannot execute RAG pipeline.")
        return ""

    # Initialize the database    
    database: ChromaDatabase = ChromaDatabase()

    # Retrieve relevant context from the database based on user input
    loop = asyncio.get_event_loop()
    context: list[str] = await loop.run_in_executor(
        None, database.search_character, user_input, "sylus"
    )
    # logger.debug(f"Context: {context}") # Debugging

    llm_response: str = llmResponse(user_input, context, username)
    # logger.debug(f"LLM Response: {response}") # Debugging

    logger.info("RAG pipeline execution completed.")
    return llm_response