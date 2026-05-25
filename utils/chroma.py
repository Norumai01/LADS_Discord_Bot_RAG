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

        # Get or create the collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=embedding_functions.DefaultEmbeddingFunction(),
        )

        existing_count = self.collection.count()
        if existing_count > 0:
            self.logger.info(f"Collection '{self.collection_name}' already exists with {existing_count} documents.")
        else:
            self.logger.warning(f"Collection '{self.collection_name}' does not exist. Creating...")

    def add_chunks(self, chunks: list[str], character: str, source_file: str, metadata: Optional[dict] = None) -> None:
        """

        :param chunks:
        :param character:
        :param source_file:
        :param metadata:
        :return:
        """
        if not chunks or not character or not source_file:
            self.logger.error("Missing required parameters: chunks, character, or source_file")
            return
        if len(chunks) <= 0:
            self.logger.error("No chunks to add")
            return

        #print(len(chunks), character, source_file, metadata)

        added: int = 0
        skipped: int = 0

        existing_ids: list[str] = self.collection.get()["ids"]

        for i, chunk in enumerate(chunks):
            doc_id = hashlib.md5(f"{character}_{chunk}".encode("utf-8")).hexdigest()

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

            self.collection.add(
                documents=[chunk],
                ids=[doc_id],
                metadatas=[chunk_metadata],
            )
            added += 1

        self.logger.info(f"Added {added} chunks, skipped {skipped} existing chunks for {character}.")

    def search_character(self, character: str, limit: int = 10):
        self.logger.info(f"Searching query related to {character}...")
        pass

    def delete_character(self, character: str):
        pass

    def delete_all_characters(self):
        pass

    # Testing purposes
    def query_chunk(self, chunks: list[str], character: str):
        maxLength = len(chunks)
        randomNumber = random.randint(0, maxLength - 1)

        self.logger.debug(f"Querying chunk {randomNumber} for character, {character}...")
        print(self.collection.query(
            query_texts=[chunks[randomNumber]],
            n_results=1,
        ))

        print(self.collection.query(
            query_texts=["What planet are you from?"],
            n_results=1,
        ))

