import logging
import os
from dotenv import load_dotenv
import httpx
import Groq

load_dotenv()
logger = logging.getLogger(__name__)

def llm(user_input: str, context: str, username: str) -> str:
    """
    Sends all context, user inputs, and username to an LLM API to generate a response.

    Args:
        user_input (str): The input provided by the user.
        context (str): The retrieved context from the database, combined into a single string.
        username (str): The username of the user.

    Returns:
        str: The generated response from the LLM.
    """
    LLM_KEY = os.getenv("LLM_KEY") or ""

    if LLM_KEY is None or LLM_KEY == "":
        logger.error("LLM_KEY is not set in the environment variables.")
        return ""
    
    client = Groq.Client(api_key=LLM_KEY, timeout=30.0, max_retries=2)

    

    return ""