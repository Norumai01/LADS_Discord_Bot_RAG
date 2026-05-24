from pathlib import Path
import re

INPUT_FILE = Path("../../data/sylus_raw.txt")
CHUNK_SIZE = 300        # words per chunk
CHUNK_OVERLAP = 30      # words carried over to the next chunk
MIN_CHUNK_SIZE = 100    # characters - filters out noise

def chunk(text: str,  size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) ->  list[str]:
    """
    Splits text into overlapping chunks roughly equal in size.

    Args:
        text (str): The text to be chunked.
        size (int): The target size of each chunk in words. Defaults to 300.
        overlap (int): Number of words to carry over chunks if overlapped. Defaults to 30.

    Returns:
        list[str]: A list of chunked text.
    """
    words: list[str] = text.split()
    chunks = []
    i = 0

    while i < len(words):
        textChunk = " ".join(words[i:i + size])
        chunks.append(textChunk)
        i += size - overlap

    return chunks

def clean(text: str) -> str:
    """
    Applies basic cleanup to raw scraped text before chunking.

    Args:
        text (str): Raw text to clean.

    Returns:
        str: Cleaned text.
    """
    text = re.sub(r"\[\s*\d+\s*\]", "", text)   # leftover [1] [2] references
    text = re.sub(r"\n{3,}", "\n\n", text)       # excessive blank lines
    return text.strip()

def filterChunks(chunks: list[str], minLength: int = MIN_CHUNK_SIZE) -> list[str]:
    """
    Removes chunks that are too short to be meaningful.

    Args:
        chunks (list[str]): List of text chunks to filter.
        minLength (int): Minimum character length to keep. Defaults to 100.

    Returns:
        list[str]: Filtered list of chunks.
    """
    return [c for c in chunks if len(c.strip()) >= minLength]

def processFile(inputFile: Path) -> list[str]:
    """
    Reads, cleans, chunks, and filters a raw text file.

    Args:
        inputFile (Path): Path to the raw text file.

    Returns:
        list[str]: Final list of usable chunks.
    """
    text = inputFile.read_text(encoding="utf-8")
    text = clean(text)
    chunks = chunk(text)
    filteredChunks = filterChunks(chunks)
    return filteredChunks

