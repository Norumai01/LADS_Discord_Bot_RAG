import logging
from pathlib import Path

from utils.RAG.chunker import processFile
from utils.chroma import ChromaDatabase

# Initialize the logging system
logger = logging.getLogger(__name__)

def saveDataToChroma(inputFile: Path | str, character: str) -> None:
    """
    Chunks a scraped text file and loads the results into ChromaDB.

    Args:
        inputFile (Path | str): Path to the raw text file to load.
        character (str): Character name for the data.

    Returns:
        None
    """
    if inputFile is None:
        logger.error("Input file does not exist.")
        return

    # Convert str to Path, if necessary
    if isinstance(inputFile, str):
        inputFile = Path(inputFile)
    elif not isinstance(inputFile, Path):
        logger.error("Invalid input file type.")
        return

    chunks: list[str] = processFile(inputFile)
    database = ChromaDatabase()
    database.add_chunks(chunks, character, str(inputFile))
    logger.info(f"Saved {inputFile.name} to Chroma DB.")

    # Debugging purposes
    # database.query_chunk(chunks, character)
    # database.search_character("dragon curse kills the one he loves", "sylus") # Test 1: something definitely in your data
    # database.search_character("what is your favourite food", "sylus") # Test 2: something definitely not in your data
    # database.search_character("who do you love", "sylus") # Test 3: something similar to what you have in your data