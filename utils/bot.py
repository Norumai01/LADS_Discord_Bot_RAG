import discord
import logging

def initiateDiscordBot(token: str) -> None:
    logging.info("Initializing Discord bot...")
    intents = discord.Intents.default()
    intents.message_content = True

    bot = discord.Client(intents=intents)

    @bot.event
    async def on_ready():
        print(f"Online as  {bot.user}")
        logging.info(f"Online as  {bot.user}")

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        if bot.user not in message.mentions:
            return

        # Separate the user's name from the message content
        botMentionString = bot.user.mention
        # logging.debug(f"Bot mentioned in message: {botMentionString}")
        user_input = message.content.replace(botMentionString, "").strip()
        # logging.debug(f"User input: {user_input}")

        if user_input is not None and user_input != "":
            # logging.debug(f"Chunks of Message: {chunks}")"
            # Split the message into chunks if it exceeds the character limit
            chunks = splitMessage(user_input)
            # TODO: Query the chunks into RAG Pipeline
        else:
            # logging.debug(f"Verify no message (should be empty): {user_input}")
            # TODO: Replace this with in-game character default response
            return

        logging.info("Message received")

    bot.run(token)
    logging.info("Discord bot initialized")


def splitMessage(text: str, limit: int = 1900) -> list[str]:
    """
        Splits a message into chunks that fit within Discord's character limit.

        Args:
            text (str): The message content to be split.
            limit (int): Maximum character length per chunk. Defaults to 1900.

        Returns:
            list[str]: A list of message chunks, each within the character limit.
    """
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