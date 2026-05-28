import asyncio
import logging

from utils.RAG.llm_response import llmResponse
from utils.RAG.user_memory import saveToUserMemory
from utils.chroma import ChromaDatabase

logger = logging.getLogger(__name__)

async def ragPipeline(user_input: str, username: str, character: str) -> str:
    """
    Executes the Retrieval-Augmented Generation (RAG) pipeline.

    Args:
        user_input (str): The input message from the user.
        context (str): The retrieved context from the database.
        username (str): The name of the user who sent the message.
        character (str): The roleplay character that the bot will respond as.    

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

    # Initialize the character database    
    character_database: ChromaDatabase = ChromaDatabase("./chroma_db", collection_names="characters_lore")

    # Retrieve relevant context from the database based on user input
    loop = asyncio.get_event_loop()
    context: list[str] = await loop.run_in_executor(
        None, character_database.search_character, user_input, "sylus"
    )
    # logger.debug(f"Context: {context}") # Debugging

    if context is None or len(context) == 0:
        logger.warning("No relevant context found for the user input. Proceeding with empty context.")
        context = []

    llm_response: str = llmResponse(user_input, context, username)
    # logger.debug(f"LLM Response: {llm_response}") # Debugging

    if llm_response is None or llm_response.strip() == "":
        logger.error("LLM response is empty. Returning empty response.")
        return ""

    # Save LLM response and user input to the user memory database asynchronously, not bogging down the main pipeline execution
    asyncio.create_task(saveToUserMemory(user_input, llm_response, username, character))
    
    # Debugging: Query the user memory database to verify that the data was saved correctly. May need to adjust parameter.
    # user_memory_database: ChromaDatabase = ChromaDatabase("./chroma_db", collection_names="user_memory")
    # logger.debug(f"User memory database contents: {user_memory_database.collection.query(
    #     query_texts=["hello world"],
    #     n_results=5,
    # )}")

    logger.info("RAG pipeline execution completed.")
    return llm_response