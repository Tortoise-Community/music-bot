import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import keep_alive


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        status_activity = discord.CustomActivity(
            name="Playing lofi music",
            emoji="🎧"
        )

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=status_activity
        )

    async def setup_hook(self):
        try:
            await self.load_extension("cogs.music")
            print("Loaded extension: cogs.music")
        except Exception as e:
            print(f"Failed to load extension 'cogs.music': {e}")

    async def on_ready(self):
        await keep_alive.run_dummy_server()
        print(f"Logged in successfully as {self.user.name}")

bot = MusicBot()

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_TOKEN is missing from .env file.")
    else:
        bot.run(TOKEN)