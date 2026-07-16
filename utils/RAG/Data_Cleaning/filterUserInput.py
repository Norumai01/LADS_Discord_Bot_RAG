import string
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

# TODO: Figure out a better way to handle nltk downloads 
# nltk.download('punkt', quiet=True)
# nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('stopwords', quiet=True)

def fastFilterUserInput(user_input) -> tuple[bool, str]:
    """
    Handles obvious filters for user input before sending it to the LLM for further processing.

    Args:
        user_input (str): The input message from the user.

    Returns:
        tuple[bool, str]: A tuple containing a boolean indicating if the input is resolved and a string indicating the decision to store into long-term memory.
    """
    if not user_input or user_input.strip() == "":
        return True, "False"

    # First check: Ignore user inputs less than 3 words.
    tokenizer = RegexpTokenizer(r"\w+(?:[-']\w+)*")
    wordCounts = len(tokenizer.tokenize(user_input))
    if wordCounts < 3:
        return True, "False"

    # Second check: Fast-pass for normal roleplay conversations.
    rp_markers = ['*', '"', '_', '(', ')', '[', ']']
    if any(marker in user_input for marker in rp_markers):
        return True, "True"

    # Third Check: Spam filter
    stop_words = set(stopwords.words('english'))
    words = tokenizer.tokenize(user_input.lower())
    meaningful_words = [word for word in words if word not in stop_words and word not in string.punctuation]
    if not meaningful_words:
        return True, "False"

    # Fourth Check: Don't store basic greetings, phrases, or pleasentries.
    clean_input = user_input.lower().translate(str.maketrans('', '', string.punctuation)).strip()
    static_blocks = {"how are you", "how have you been", "whats up", "hello there", "good morning", "good night"}
    if clean_input in static_blocks:
        return True, "False"

    return False, "PENDING"