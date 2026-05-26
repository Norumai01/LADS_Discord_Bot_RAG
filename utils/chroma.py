import hashlib
import logging
import random
from datetime import datetime
from typing import Optional

import chromadb
from chromadb.utils import embedding_functions

class ChromaDatabase:
    """ChromaDB wrapper with helper methods."""

    def __init__(self, path: str = "./chroma_db", collection_name: str = "documents") -> None:
        """
        Initialize the ChromaDB client and collection.

        Args:
            path (str): Path to the ChromaDB database directory.
            collection_name (str): Name of the ChromaDB collection.
        """
        # Setup logging
        self.logger = logging.getLogger(__name__)

        self.logger.info("Initializing ChromaDB...")
        self.db_path = path
        self.collection_name = collection_name

        # Initialize the ChromaDB client, also create a database folder if it doesn't exist
        self.logger.info("Initializing ChromaDB client...")
        self.client = chromadb.PersistentClient(path=self.db_path)

        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="BAAI/bge-small-en-v1.5"
        )
        # Get or create the collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
        )

        existing_count = self.collection.count()
        if existing_count > 0:
            self.logger.info(f"Collection '{self.collection_name}' already exists with {existing_count} documents.")
        else:
            self.logger.warning(f"Collection '{self.collection_name}' does not exist. Creating...")

    def add_chunks(self, chunks: list[str], character: str, source_file: str, metadata: Optional[dict] = None) -> None:
        """
        Add data (that has been chunked) to the chroma database.

        Args:
            chunks (list[str]): List of chunks to add.
            character (str): Character name for the data.
            source_file (str): Path to the original file from which the chunks were extracted.
            metadata (dict, optional): Additional metadata to associate with the chunks.

        Returns:
            None
        """
        if not chunks or not character or not source_file:
            self.logger.error("Missing required parameters: chunks, character, or source_file")
            return
        if len(chunks) <= 0:
            self.logger.error("No chunks to add")
            return

        #print(len(chunks), character, source_file, metadata) # Debugging

        added: int = 0
        skipped: int = 0

        existing_ids: list[str] = self.collection.get()["ids"]

        for i, chunk in enumerate(chunks):
            doc_id = hashlib.md5(f"{character}_{chunk}".encode("utf-8")).hexdigest()

            # Check if the chunk hash matches the existing chunks
            # If so, no need to add it again
            if doc_id in existing_ids:
                skipped += 1
                continue

            # Metadata for each chunk
            chunk_metadata = {
                "character": character.lower(),
                "source_file": source_file,
                "date_added": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            }

            # Merge any additional metadata provided
            if metadata:
                chunk_metadata.update(metadata)

            #  Add the chunk into the collection (or database)
            self.collection.add(
                documents=[chunk],
                ids=[doc_id],
                metadatas=[chunk_metadata],
            )
            added += 1

        self.logger.info(f"Added {added} chunks, skipped {skipped} existing chunks for {character}.")

    def search_character(self, query: str, character: str, limit: int = 5) -> list[str] | None:
        """
        Search for relevant contexts based on the query and character.

        Args:
            query (str): The user input query.
            character (str): The character to search for.
            limit (int): The maximum number of results to return. Defaults to 5.

        Returns:
            list[str] | None: A list of relevant contexts, or None if no results are found or errors.
        """

        self.logger.info(f"Searching query related to {character}...")
        if not query or not character:
            self.logger.error("Missing required parameters: query or character")
            return None

        user_input: str = query.lower()

        results = self.collection.query(
            query_texts=[user_input],
            n_results=limit,
            where={"character": character.lower()}
        )

        chunks = results["documents"][0]
        distances = results["distances"][0]
        # Debugging
        #self.logger.debug(f"chunks: {chunks}")
        #self.logger.debug(f"distances: {distances}")

        if len(chunks) <= 0:
            self.logger.error("No results found for the query.")
            return None

        relevant_chunks = [
            chunk for chunk, distance in zip(chunks, distances) if distance < 1.4
        ]
        relevant_distances = [
            distance for chunk, distance in zip(chunks, distances) if distance < 1.4
        ]

        chunks = [chunk.strip() for chunk in relevant_chunks]
        distances = [round(distance, 3) for distance in relevant_distances]
        # Debugging
        # self.logger.debug(f"Relevant chunks: {chunks}")
        # self.logger.debug(f"Relevant distances: {distances}")

        self.logger.info(f"Found {len(chunks)} relevant chunks for {character} based on the query.")
        return chunks

    def delete_character(self, character: str) -> None:
        """
        Reset all chunks for a specific character.

        Args:
            character (str): Character name.

        Returns:
            None
        """
        if not character:
            self.logger.error("Missing required parameter: character")
            return

        self.logger.info(f"Resetting all chunks for {character}...")
        self.collection.delete(
            where={"character": character.lower()}
        )
        self.logger.info(f"All data for {character} have been deleted.")

    def delete_all_characters(self) -> None:
        """
        Reset the entire database.

        Returns:
            None
        """
        # Need to get all existing IDs to delete them all
        existing_ids: list[str] = self.collection.get()["ids"]

        if len(existing_ids) <= 0:
            self.logger.warning("No chunks to reset.")
            return

        self.logger.info("Resetting all chunks...")
        self.collection.delete(ids=existing_ids)
        self.logger.info("Database reset.")

    # Testing purposes
    def query_chunk(self, chunks: list[str], character: str):
        maxLength = len(chunks)
        randomNumber = random.randint(0, maxLength - 1)

        self.logger.debug(f"Querying chunk {randomNumber} for character, {character}...")
        print(self.collection.query(
            query_texts=[chunks[randomNumber]],
            n_results=1,
        ))

        self.logger.debug(f"Querying random chunk for character, {character}...")
        print(self.collection.query(
            query_texts=["What planet are you from?"],
            n_results=1,
        ))

