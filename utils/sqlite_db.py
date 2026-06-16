import sqlite3
import logging

logger = logging.getLogger(__name__)

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
        logger.info(f"Initializing SQLite database at path: {db_path}")
        self.db_path = db_path
        self.create_table()
        logger.info("SQLite database initialized and table created if it did not exist.")

    def get_connection(self) -> sqlite3.Connection:
        """
        Get a connection to the SQLite database.

        Returns:
            sqlite3.Connection: A connection object to the SQLite database.
        """
        logger.info("Getting SQLite database connection.")
        conn = sqlite3.connect(self.db_path)
        # Turns rows into dictionaries, so we can access columns by name instead of index
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_table(self) -> None:
        """
        Create the recent conversation history table in the SQLite database if it doesn't already exist.

        Returns:
            None
        """
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
            logger.info("Chat logs table created or already exists.")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_character ON chat_logs (character)")
            conn.commit()
        
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
        logger.info(f"Appending message for character: {character}")
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
            logger.info("Message appended to chat logs successfully.")
        
    def get_recent_messages(self, character: str, limit: int = 10) -> list[sqlite3.Row]:
        """
        Get recent messages for a specific character.

        Args:
            character (str): The roleplay character to fetch messages for.
            limit (int): The maximum number of messages to retrieve.

        Returns:
            list[sqlite3.Row]: A list of recent messages for the specified character.
        """
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
                logger.info(f"Retrieved {len(rows)} recent messages for character: {character}")
                return rows
    
    def clear_history(self, character: str) -> None:
        """
        Clear the chat history for a specific character.

        Args:
            character (str): The roleplay character to clear messages for.
        Returns:
            None
        """
        logger.info(f"Clearing chat history for character: {character}")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_logs WHERE character = ?", (character,))
            conn.commit()
        logger.info(f"Chat history cleared for character: {character}")

    async def delete_message(self, message_id: str) -> None:
        """
        Delete a specific message from the chat logs based on the message ID, if user deleted their message.

        Args:
            message_id (str): The Discord ID of the message to delete.
        Returns:
            None
        """
        logger.info("Deleting message with ID")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_logs WHERE message_id = ?", (message_id,))
            conn.commit()
        logger.info("Message with specific ID deleted from chat logs.")

    def delete_messages_by_user(self, user_id: str) -> None:
        """
        Delete all messages from the chat logs for a specific user, if user requests deletion.

        Args:
            user_id (str): The Discord ID of the user whose messages should be deleted.
        Returns:
            None
        """
        logger.info("User requested deletion of messages. Deleting messages...")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_logs WHERE user_id = ?", (user_id,))
            conn.commit()
        logger.info("All messages for user have been deleted from chat logs.")