import asyncio
import logging
import discord

from utils.RAG.llm_response import llmResponse
from utils.RAG.recentConversation import saveRecentConversation, getRecentConversation
from utils.RAG.user_memory import saveToUserMemory
from utils.chroma import ChromaDatabase
from utils.RAG.Data_Cleaning.filterUserInput import filterUserInput

logger = logging.getLogger(__name__)

async def ragPipeline(message: discord.Message, character: str, user_input: str) -> str:
    """
    Executes the Retrieval-Augmented Generation (RAG) pipeline.

    Args:
        message (discord.Message): The Discord message object.
        character (str): The roleplay character that the bot will respond as.
        user_input (str): The user's input message without the bot mention.

    Returns:
        str: The generated response based on the user input and context.
    """
    logger.info("Executing RAG pipeline...")

    # ---------------- Validation Checks ----------------
    if not character or character.strip() == "":
        logger.warning("Character is empty. Cannot execute RAG pipeline.")
        return ""
    if not user_input or user_input.strip() == "":
        logger.warning("User input is empty. Cannot execute RAG pipeline.")
        return ""
    if not message or not isinstance(message, discord.Message):
        logger.warning("Invalid message object. Cannot execute RAG pipeline.")
        return ""

    # ---------------- Initialize Databases ----------------

    # Initialize the character database connection   
    character_database: ChromaDatabase = ChromaDatabase("./chroma_db", collection_names="characters_lore")
    user_memory_database: ChromaDatabase = ChromaDatabase("./chroma_db", collection_names="user_memory")

    # ---------------- Retrieve Context from Databases ----------------

    # Retrieve relevant context from the database based on user input
    characterContext: list[str] | None = await character_database.search_character(user_input, character)
    # logger.debug(f"Context: {context}") # Debugging
    if characterContext is None or len(characterContext) <= 0:
        logger.warning("No relevant context found for the user input. Proceeding with empty context.")
        characterContext = []

    userMemoryContext: list[str] | None = await user_memory_database.query_database(
        user_input,
        limit=5,
        user_id=str(message.author.id),
        character=character
    )
    # logger.debug(f"User memory context: {userMemoryContext}") # Debugging
    if userMemoryContext is None or len(userMemoryContext) <= 0:
        logger.warning("No relevant user memory context found for the user input. Proceeding with empty context.")
        userMemoryContext = []

    recentConversationContext: list[dict] | None = await getRecentConversation(character, str(message.author.id), limit=5)
    # logger.debug(f"Recent conversation context: {recentConversationContext}") # Debugging
    if recentConversationContext is None or len(recentConversationContext) <= 0:
        logger.warning("No relevant recent conversation context found for the user input. Proceeding with empty context.")
        recentConversationContext = []

    # ---------------- Generate LLM Response ----------------

    llm_response: str = llmResponse(user_input, characterContext, userMemoryContext, recentConversationContext, message.author.name)
    # logger.debug(f"LLM Response: {llm_response}") # Debugging

    if llm_response is None or llm_response.strip() == "":
        logger.error("LLM response is empty. Returning empty response.")
        return ""

    # ---------------- Save Conversation Into Databases ----------------

    # If user input has meaningful content, save the user input and LLM response to the user memory database.
    if filterUserInput(user_input):
        logger.info("User input passed the filter. Saving to user memory database.")
        await saveToUserMemory(llm_response, message, character, user_input) # Asynchronously, not bogging down the main pipeline execution
    else:
        logger.info("User input did not pass the filter. Not saving to user memory database.")
    
    # Debugging: Query the user memory database to verify that the data was saved correctly. May need to adjust parameter.
    # user_memory_database: ChromaDatabase = ChromaDatabase("./chroma_db", collection_names="user_memory")
    # logger.debug(f"User memory database contents: {user_memory_database.collection.query(
    #     query_texts=["hello world"],
    #     n_results=5,
    # )}")

    # Save recent conversation to SQLite DB
    save_recent_convo: bool = await saveRecentConversation(llm_response, message, character, user_input)
    logger.info("Recent conversation saved" if save_recent_convo else "Failed to save recent conversation.")

    logger.info("RAG pipeline execution completed.")
    return llm_response