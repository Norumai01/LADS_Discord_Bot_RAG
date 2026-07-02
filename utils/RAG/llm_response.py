import logging
import json

from utils.RAG.llm import llm

logger = logging.getLogger(__name__)

def llmResponse(user_input: str, characterContext: list[str] | None, userLongTermMemory: list[str] | None, recentConversations: list[dict] | None,  username: str) -> str:
    """
    This function is responsible for generating a response from the language model (LLM) based on the user's input and the retrieved context from the database.
    It uses the RAG (Retrieval-Augmented Generation) pipeline to combine the retrieved context with the LLM's capabilities to produce a coherent and relevant response.

    Args:
        user_input (str): The input provided by the user.
        characterContext (list[str]): The retrieved context about the character from the database.
        userLongTermMemory (list[str]): Long-term memory meaningful conversations between the user and the character.
        recentConversations (list[dict]): The recent conversations between the user and the character.
        username (str): The username of the user.

    Returns:
        str: The generated response from the LLM.
    """
    logger.info("Generating LLM response...")

    if not user_input or user_input.strip() == "":
        logger.warning("User input is empty. Cannot generate LLM response.")
        return ""
    if not username or username.strip() == "":
        logger.warning("Username is empty. Cannot generate LLM response.")
        return ""
    if characterContext is None or len(characterContext) <= 0:
        logger.warning("No relevant context found for the user input. Proceeding with empty context.")
        characterContext = []
    if userLongTermMemory is None or len(userLongTermMemory) <= 0:
        logger.warning("No long-term memory context found for the user.")
        userLongTermMemory = []
    if recentConversations is None or len(recentConversations) <= 0:
        logger.warning("No recent conversations found for the user.")
        recentConversations = []

    # Combine the retrieved context into a single string
    characterContextLLM: str = "\n".join(characterContext)
    userLongTermMemoryLLM: str = "\n".join(
        json.loads(conv)["conversation"] for conv in userLongTermMemory
    )
    recentConversationsLLM: str = "\n".join(
        f"{conv['username']}: {conv['user_input']} | {conv['character']}: {conv['llm_response']}" for conv in recentConversations
    )

    # Generate response using the LLM with the retrieved context
    response: str = llm(user_input, characterContextLLM, userLongTermMemoryLLM, recentConversationsLLM, username)
    if response is None or response.strip() == "":
        logger.error("Something went wrong. LLM did not return a valid response.")
        return ""

    logger.info("LLM response generated.")
    return response