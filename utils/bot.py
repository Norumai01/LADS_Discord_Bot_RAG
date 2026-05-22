import discord
import logging

def initiateDiscordBot(token: str) -> None:
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

        await message.channel.send(f"Hello {message.author.mention}, I am alive!")
        logging.info("Message received")

    bot.run(token)