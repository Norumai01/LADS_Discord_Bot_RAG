import logging
import os
import groq
from dotenv import load_dotenv

from utils.RAG.sys_prompt import readSystemPrompt

load_dotenv()
logger = logging.getLogger(__name__)

def llm(user_input: str, characterContext: str, userLongTermMemory: str, recentConversations: str, username: str) -> str:
    """
    Sends all context, user inputs, and username to an LLM API to generate a response.

    Args:
        user_input (str): The input provided by the user.
        characterContext (list[str]): The retrieved context about the character from the database.
        userLongTermMemory (list[str]): Long-term memory meaningful conversations between the user and the character.
        recentConversations (list[dict]): The recent conversations between the user and the character.
        username (str): The username of the user.

    Returns:
        str: The generated response from the LLM.
    """
    LLM_KEY = os.getenv("LLM_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL") or "meta-llama/llama-4-scout-17b-16e-instruct"
    MAX_TOKENS: int = 400

    if LLM_KEY is None or LLM_KEY == "":
        logger.error("LLM_KEY is not set in the environment variables.")
        return ""
    if GROQ_MODEL is None or GROQ_MODEL == "":
        logger.error("GROQ_MODEL is not set in the environment variables.")
        return ""
    if MAX_TOKENS is None or MAX_TOKENS <= 0:
        logger.error("MAX_TOKENS is not set in the environment variables or is not a valid positive integer.")
        return ""

    # System prompt
    prompt: str | None = readSystemPrompt()
    if prompt is None:
        logger.error("System prompt is empty.")
        return ""  # Cannot proceed without it.
    #logger.debug(f"System prompt: {prompt}") # Debugging
    if username is None or username.strip() == "":
        logger.error("No user to respond to. Cannot generate LLM response.")
        return ""
    prompt += f"\n\nYou are speaking with: {username}."

    # Add relevant context and username to the prompt
    if characterContext and len(characterContext) > 0:
        prompt += f"\n\nHere is relevant in-game context and in-game dialogues about you:\n{characterContext}"
    if userLongTermMemory and len(userLongTermMemory) > 0:
        prompt += f"\n\nConversations long ago between the character and the user (apply if applicable in conversation):\n{userLongTermMemory}"
    if recentConversations and len(recentConversations) > 0:
        prompt += f"\n\nRecent conversations between the character and the user (apply if applicable in conversation):\n{recentConversations}"

    # logger.debug("Prompt for LLM:\n" + prompt)  # Debugging

    client = groq.Client(api_key=LLM_KEY, timeout=30.0, max_retries=3)

    # Generate response
    try:
        # return "" # Debugging: Uncomment this line to test the RAG pipeline without generating a response from the LLM.
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": user_input
            }],
            max_tokens=MAX_TOKENS,
            temperature=0.85,
        )
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return ""