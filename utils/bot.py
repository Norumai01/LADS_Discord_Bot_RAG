import discord
import logging

from utils.rag_pipeline import ragPipeline

logger = logging.getLogger(__name__)

def initiateDiscordBot(token: str) -> None:
    """
    Initializes and runs the Discord bot.

    Args:
        token (str): The Discord bot token used for authentication.

    Returns:
        None
    """
    logger.info("Initializing Discord bot...")

    intents = discord.Intents.default()
    intents.message_content = True
    bot = discord.Client(intents=intents)

    @bot.event
    async def on_ready():
        print(f"Online as  {bot.user}")
        logger.info(f"Online as  {bot.user}")

    @bot.event
    async def on_message(message):
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
        response: str = await ragPipeline(user_input, message.author.name)
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

    bot.run(token)
    logger.info("Discord bot initialized")


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