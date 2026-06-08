import string
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

# TODO: Figure out a better way to handle nltk downloads 
# nltk.download('punkt', quiet=True)
# nltk.download('averaged_perceptron_tagger', quiet=True)
# nltk.download('stopwords', quiet=True)

def filterUserInput(user_input) -> bool:
    """
    Basic validation conditions if we should store user input into the Chroma database.

    Args:
        user_input (str): The input message from the user.

    Returns:
        bool: True if we want the user input stored. Otherwise, False.
    """
    if not user_input or user_input.strip() == "":
        return False
    
    # First check: Ignore user inputs less than 3 words.
    tokenizer = RegexpTokenizer(r"\w+(?:[-']\w+)*")
    wordCounts = len(tokenizer.tokenize(user_input))
    if wordCounts < 3:
        return False
    
    # Second check: Fast-pass for normal roleplay conversations.
    rp_markers = ['*', '"', '_', '(', ')', '[', ']']
    if any(marker in user_input for marker in rp_markers):
        return True

    # Third Check: Spam filter
    stop_words = set(stopwords.words('english'))
    words = tokenizer.tokenize(user_input.lower())
    meaningful_words = [word for word in words if word not in stop_words and word not in string.punctuation]
    if not meaningful_words:
        return False

    # Maybe part of speech check?
    # pos_tags = nltk.pos_tag(words)
    # if not any(tag.startswith('NN') or tag.startswith('VB') for word, tag in pos_tags):
    #     return False

    return True