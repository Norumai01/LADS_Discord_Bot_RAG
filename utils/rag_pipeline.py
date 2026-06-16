import asyncio
import logging
import discord

from utils.RAG.llm_response import llmResponse
from utils.RAG.user_memory import saveToUserMemory
from utils.chroma import ChromaDatabase
from utils.RAG.Data_Cleaning.filterUserInput import filterUserInput

logger = logging.getLogger(__name__)

async def ragPipeline(message: discord.Message, character: str) -> str:
    """
    Executes the Retrieval-Augmented Generation (RAG) pipeline.

    Args:
        message (discord.Message): The Discord message object.
        character (str): The roleplay character that the bot will respond as.    

    Returns:
        str: The generated response based on the user input and context.
    """
    logger.info("Executing RAG pipeline...")

    # Extract user input from the Discord message
    user_input: str = message.clean_content.strip()

    if not user_input or user_input.strip() == "":
        logger.warning("User input is empty. Cannot execute RAG pipeline.")
        return ""
    if not message or not isinstance(message, discord.Message):
        logger.warning("Invalid message object. Cannot execute RAG pipeline.")
        return ""

    # Initialize the character database connection   
    character_database: ChromaDatabase = ChromaDatabase("./chroma_db", collection_names="characters_lore")

    # Retrieve relevant context from the database based on user input
    loop = asyncio.get_event_loop()
    context: list[str] = await loop.run_in_executor(
        None, character_database.search_character, user_input, character
    )
    # logger.debug(f"Context: {context}") # Debugging

    if context is None or len(context) == 0:
        logger.warning("No relevant context found for the user input. Proceeding with empty context.")
        context = []

    llm_response: str = llmResponse(user_input, context, message.author.name)
    # logger.debug(f"LLM Response: {llm_response}") # Debugging

    if llm_response is None or llm_response.strip() == "":
        logger.error("LLM response is empty. Returning empty response.")
        return ""

    # If user input has meaningful content, save the user input and LLM response to the user memory database.
    if filterUserInput(user_input):
        logger.info("User input passed the filter. Saving to user memory database.")
        asyncio.create_task(saveToUserMemory(llm_response, message, character)) # Asynchronously, not bogging down the main pipeline execution
    else:
        logger.info("User input did not pass the filter. Not saving to user memory database.")
    
    # Debugging: Query the user memory database to verify that the data was saved correctly. May need to adjust parameter.
    # user_memory_database: ChromaDatabase = ChromaDatabase("./chroma_db", collection_names="user_memory")
    # logger.debug(f"User memory database contents: {user_memory_database.collection.query(
    #     query_texts=["hello world"],
    #     n_results=5,
    # )}")

    logger.info("RAG pipeline execution completed.")
    return llm_response