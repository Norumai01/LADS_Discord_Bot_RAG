import discord
import logging
from discord.ext import commands, tasks
from discord.ext.commands import Bot

from utils.RAG.Data_Cleaning.deleteUserConversation import deleteUserConversation
from utils.RAG.Data_Cleaning.deleteUserMemory import deleteUserMemory
from utils.rag_pipeline import ragPipeline
from utils.Discord.birthday import runImmediateTest, pingBirthdayMessage, saveUserBirthday, checkScheduleBirthdays

logger = logging.getLogger(__name__)

def initiateDiscordBot(token: str, character: str) -> None:
    """
    Initializes and runs the Discord bot.

    Args:
        token (str): The Discord bot token used for authentication.
        character (str): The roleplay character that the bot will respond as.

    Returns:
        None
    """
    logger.info("Initializing Discord bot...")

    if not token or token.strip() == "":
        logger.error("Discord token is empty. Cannot initialize bot.")
        return
    if not character or character.strip() == "":
        logger.error("No character presented. Cannot initialize bot.")
        return

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    # Birthday Events Listener
    setupBirthdayEvents(bot)

    @bot.event
    async def on_ready():
        logger.info(f"Online as {bot.user}, roleplaying as {character.capitalize()}")

    @bot.event
    async def on_message(message: discord.Message):
        if message.author == bot.user:
            return
        if bot.user not in message.mentions:
            return

        # Separate the user's name from the message content
        botMentionString: str = bot.user.mention
        # logger.debug(f"Bot mentioned in message: {botMentionString}")
        user_input: str = message.content.replace(botMentionString, "").strip()
        # logger.debug(f"User input: {user_input}")
        if not user_input:
            logger.warning("No user input provided after removing bot mention. Returning generic response.")
            # Return a generic response of that specific character. Awaiting the user message.
            # await message.channel.send("...")
            return

        # Execute the RAG pipeline
        response: str = await ragPipeline(message, character, user_input)
        if response is None or response.strip() == "":
            logger.error("Unable to process pipeline or generate response.")
            # Return a generic response of that specific character. Saying try again later or something.
            # await message.channel.send("...")
            return

        # Split the response into chunks to be send back through Discord, if the response is too long.
        chunks = splitMessage(response)
        for chunk in chunks:
            await message.channel.send(chunk)

        logger.info("Message received")
    
    @bot.event
    async def on_message_delete(message: discord.Message):
        logger.info("Deleting a message from user memory database...")

        if message.author.bot:
            return
        
        doc_id = str(message.id)
        if not doc_id or doc_id.strip() == "":
            logger.error("Cannot find document ID for deleted message. Skipping...")
            return
        
        statusChromaDB: bool = await deleteUserMemory(doc_id)
        if statusChromaDB is None:
            logger.error("Error occurred while trying to delete user memory entry for deleted message.")
            return
        
        statusSQLiteDB: bool = await deleteUserConversation(doc_id)
        if statusSQLiteDB is None:
            logger.error("Error occurred while trying to delete user conversation entry for deleted message.")
            return

        logger.info(f"Deleted user message by {message.author.name}." if statusChromaDB and statusSQLiteDB else f"Failed to delete user message by {message.author.name}.")
        
    @bot.event
    async def on_bulk_message_delete(messages: list[discord.Message]):
        logger.info("Deleting messages from user memory database...")
        deleted_ids: list[str] = []

        for message in messages:
            if message.author.bot:
                continue

            doc_id = str(message.id)
            deleted_ids.append(doc_id)
        
        if not deleted_ids or len(deleted_ids) == 0:
            logger.error("No valid document IDs found for bulk deleted messages. Skipping...")
            return
        
        statusChromaDB: bool = await deleteUserMemory(deleted_ids)
        if statusChromaDB is None:
            logger.error("Error occurred while trying to delete user memory entries for bulk deleted messages.")
            return

        statusSQLiteDB: bool = await deleteUserConversation(deleted_ids)
        if statusSQLiteDB is None:
            logger.error("Error occurred while trying to delete user conversation entries for bulk deleted messages.")
            return

        logger.info("Messages deleted from user memory database." if statusChromaDB and statusSQLiteDB else "Failed to delete some messages, if not all.")

    bot.run(token)
    logger.info("Discord bot initialized")

def setupBirthdayEvents(bot: Bot) -> None:
    """
        Sets up birthday listener and commands events for the Discord bot

        Args:
            bot (discord.Bot): The Discord bot instance.
    """
    logger.info("Setting up birthday events...")

    async def pingBirthdayMessageListener(message: discord.Message) -> None:
        """
        Listener helper to process ping birthday message command.
        Format: !birthday @username

        Args:
            message: The Discord message object.

        Returns:
            None
        """
        messagesPart = message.content.strip().split(maxsplit=10)
        commandWord = messagesPart[0].lower()
        targetUser = messagesPart[1] if len(messagesPart) > 1 else None

        if message.author.bot:
            return
        if commandWord != "!birthday":
            return
        if targetUser is None:
            return
        if len(messagesPart) != 2:
            return

        await pingBirthdayMessage(message ,targetUser)

    @tasks.loop(seconds=60.0)
    async def birthdayCheckLoop() -> None:
        """
        Birthday check schedule loop to run parallel with system.

        Returns:
            None
        """
        await checkScheduleBirthdays(bot)

    async def birthdayReadyListener() -> None:
        """
        Discord event listener to start birthday check schedule loop.

        Returns:
            None
        """
        if not birthdayCheckLoop.is_running():
            birthdayCheckLoop.start()
            logger.info("Started birthday check schedule.")

    async def saveUserBirthdayListener(message: discord.Message) -> None:
        """
        Listener helper to process save user birthday command.
        Format: !savebirthday MM-DD

        Args:
            message: The Discord message object.

        Returns:
            None
        """
        messageParts = message.content.strip().split(maxsplit=10)
        commandWord = messageParts[0].lower()
        birthdate: str | None = messageParts[1] if len(messageParts) > 1 else None

        if message.author.bot:
            return
        if commandWord != "!savebirthday":
            return
        if birthdate is None:
            logger.error("Invalid birthday format.")
            await message.channel.send("Invalid birthday format. Please use MM-DD (e.g., `10-15` or `05-21`).")
            return
        if len(messageParts) != 2:
            logger.error("Invalid birthday format.")
            await message.channel.send("Invalid birthday format. Please use MM-DD (e.g., `10-15` or `05-21`).")
            return

        await saveUserBirthday(message, birthdate)

    async def birthdayTestCommandListener(message: discord.Message) -> None:
        """
        Listener helper to process test command only usable by bot owner.
        Format: !test <user_id>

        Args:
            message: The Discord message object.

        Returns:
            None
        """
        OWNER_ID: int = 271839706109575168  # Discord owner ID. Replace with your own ID

        messageParts = message.content.strip().split(maxsplit=10)
        commandWord = messageParts[0].lower()
        targetUserID: str | None = messageParts[1] if len(messageParts) > 1 else None

        if message.author.bot: # Do not process messages from bots
            return
        if commandWord != "!test": # Do not process if command is not "!test"
            return
        if len(messageParts) != 2: # Do not process if there are not exactly two parts in the message
            return
        if message.author.id != OWNER_ID: # Do not process if the author is not the owner
            return

        await runImmediateTest(bot, targetUserID)

    bot.add_listener(pingBirthdayMessageListener, "on_message")
    bot.add_listener(saveUserBirthdayListener, "on_message")
    bot.add_listener(birthdayTestCommandListener, "on_message")
    bot.add_listener(birthdayReadyListener, "on_ready")
    logger.info("Birthday events setup complete.")

def splitMessage(text: str, limit: int = 1900) -> list[str]:
    """
        Splits a message into chunks that fit within Discord's character limit.

        Args:
            text (str): The message content to be split.
            limit (int): Maximum character length per chunk. Defaults to 1900.

        Returns:
            list[str]: A list of message chunks, each within the character limit.
    """
    if text is None:
        return []

    if len(text) <= limit:
        return [text]

    chunks = []
    while len(text) > limit:
        # Split at newline, sentence boundary, then word.
        cut = text.rfind("\n", 0, limit)
        if cut == -1:
            cut = text.rfind(". ", 0, limit)
        if cut == -1:
            cut = text.rfind(" ", 0, limit)
        if cut == -1:
            cut = limit

        chunks.append(text[:cut].strip())
        text = text[cut:].strip()

    if text:
        chunks.append(text)

    return chunks