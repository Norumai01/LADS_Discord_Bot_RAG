import logging

from utils.RAG.llm import llm

logger = logging.getLogger(__name__)

def llmResponse(user_input: str, context: list[str] | None, username: str) -> str:
    """
    This function is responsible for generating a response from the language model (LLM) based on the user's input and the retrieved context from the database. 
    It uses the RAG (Retrieval-Augmented Generation) pipeline to combine the retrieved context with the LLM's capabilities to produce a coherent and relevant response.

    Args:
        user_input (str): The input provided by the user.
        context (list[str]): The retrieved context from the database.
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
    if context is None or len(context) <= 0:
        logger.warning("No relevant context found for the user input. Proceeding with empty context.")
        context = []

    # Combine the retrieved context into a single string
    contextLLM: str = "\n".join(context)

    # Generate response using the LLM with the retrieved context
    response: str = llm(user_input, contextLLM, username) 
    if response is None or response.strip() == "":
        logger.error("Something went wrong. LLM did not return a valid response.")
        return ""

    logger.info("LLM response generated.")
    return response