import sqlite3
import logging
from pathlib import Path

class SQLiteDB:
    "Simple wrapper for SQLite database operations."

    def __init__(self, db_path: str = "short_term_chat_logs.db") -> None:
        """
        Initialize the SQLite database connection and create the table.

        Args:
            db_path (str): Path to the SQLite database file.
        Returns:
            None
        """
        # Setup logging
        self.logger = logging.getLogger(__name__)

        self.logger.info(f"Initializing SQLite database...")
        
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)  # Ensure the directory or subdirectories exist

        self.create_table()
        self.logger.info("SQLite database initialized and table created if it did not exist.")

    def get_connection(self) -> sqlite3.Connection:
        """
        Get a connection to the SQLite database.

        Returns:
            sqlite3.Connection: A connection object to the SQLite database.
        """
        self.logger.info("Getting SQLite database connection...")
        try:
            conn = sqlite3.connect(self.db_path, timeout=5)  # Set a timeout to avoid database lock issues
            # Turns rows into dictionaries, so we can access columns by name instead of index
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            self.logger.error(f"Error occurred while connecting to SQLite database: {e}")
            raise

    def create_table(self) -> None:
        """
        Create the recent conversation history table in the SQLite database if it doesn't already exist.

        Returns:
            None
        """        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS chat_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT NOT NULL,
                    character TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    user_input TEXT NOT NULL,
                    llm_response TEXT NOT NULL,
                    timestamp INTEGER NOT NULL
                )
                """
            )
            self.logger.info("Chat logs table created or already exists.")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_character ON chat_logs (character)")
            conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Error occurred while creating chat logs table: {e}")
            raise

    def append_message(self, message_id: str, character: str, user_id: str, username: str, user_input: str, llm_response: str, timestamp: int) -> None:
        """
        Append a new message to the chat logs table in the SQLite database.
        Args:
            message_id (str): The Discord ID of the message.
            character (str): The roleplay character that the bot is responding as.
            user_id (str): The Discord ID of the user who sent the message.
            username (str): The username of the user who sent the message.
            user_input (str): The user's input message.
            llm_response (str): The LLM's response message.
            timestamp (int): The timestamp of when the message was logged.
        Returns:
            None
        """
        self.logger.info(f"Appending message for character: {character}...")
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO chat_logs (message_id, character, user_id, username, user_input, llm_response, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (message_id, character, user_id, username, user_input, llm_response, timestamp),
                )
                conn.commit()
            self.logger.info(f"Message appended to chat logs for character: {character}.")
        except sqlite3.Error as e:
            self.logger.error(f"Error occurred while appending message to chat logs: {e}")
            raise
        
    def get_recent_messages(self, character: str, limit: int = 10) -> list[sqlite3.Row]:
        """
        Get recent messages for a specific character.

        Args:
            character (str): The roleplay character to fetch messages for.
            limit (int): The maximum number of messages to retrieve.

        Returns:
            list[sqlite3.Row]: A list of recent messages for the specified character.
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT * FROM chat_logs
                    WHERE character = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (character, limit),
                )
                rows = cursor.fetchall()
                self.logger.info(f"Retrieved {len(rows)} recent messages for character: {character}")
                return rows
        except sqlite3.Error as e:
            self.logger.error(f"Error occurred while fetching recent messages: {e}")
            raise

    def clear_history(self, character: str) -> None:
        """
        Clear the chat history for a specific character.

        Args:
            character (str): The roleplay character to clear messages for.
        Returns:
            None
        """
        self.logger.info(f"Clearing chat history for character: {character}")
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM chat_logs WHERE character = ?", (character,))
                conn.commit()
            self.logger.info(f"Chat history cleared for character: {character}")
        except sqlite3.Error as e:
            self.logger.error(f"Error occurred while clearing chat history: {e}")
            raise

    async def delete_message(self, message_id: str) -> None:
        """
        Delete a specific message from the chat logs based on the message ID, if user deleted their message.

        Args:
            message_id (str): The Discord ID of the message to delete.
        Returns:
            None
        """
        self.logger.info(f"Deleting message with ID: {message_id}")
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM chat_logs WHERE message_id = ?", (message_id,))
                conn.commit()
            self.logger.info(f"Message with ID: {message_id} deleted from chat logs.")
        except sqlite3.Error as e:
            self.logger.error(f"Error occurred while deleting message: {e}")
            raise

    def delete_messages_by_user(self, user_id: str) -> None:
        """
        Delete all messages from the chat logs for a specific user, if user requests deletion.

        Args:
            user_id (str): The Discord ID of the user whose messages should be deleted.
        Returns:
            None
        """
        self.logger.info(f"User requested deletion of messages. Deleting messages for user: {user_id}")
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM chat_logs WHERE user_id = ?", (user_id,))
                conn.commit()
            self.logger.info(f"All messages for user: {user_id} have been deleted from chat logs.")
        except sqlite3.Error as e:
            self.logger.error(f"Error occurred while deleting messages for user: {e}")
            raise