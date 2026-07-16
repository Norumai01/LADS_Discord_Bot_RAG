import logging

from paths import ROOT

prompt_file: str = f"{ROOT}/config/system_prompt.txt"
logger = logging.getLogger(__name__)

def readSystemPrompt() -> str | None:
    if prompt_file is None or prompt_file == "":
        logger.error("System prompt file not found.")
        return None

    prompt: str = ""
    with open(prompt_file, "r") as file:
        # Read lines and remove leading/trailing whitespace
        lines = file.read().splitlines()

        # Strip bullet characters (like *, -, •) and spaces from the start of each line
        cleaned_lines = [line.lstrip("*-• ").strip() for line in lines if line.strip()]

        # Join everything into one single string separated by spaces
        prompt = " ".join(cleaned_lines)

    if prompt is None or prompt == "":
        logger.error("Something went wrong. System prompt is empty.")
        return None

    return prompt