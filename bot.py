import discord
from discord.ext import commands
from decouple import config

TOKEN = config("DISCORD_TOKEN")

class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.none()
        intents.voice_states = True
        intents.guilds = True

        status_activity = discord.CustomActivity(
            name="Playing lofi music",
            emoji="🎧"
        )

        super().__init__(
            command_prefix=None,
            intents=intents,
            activity=status_activity,
            status=discord.Status.dnd,
            max_messages=0,
            member_cache_flags=discord.MemberCacheFlags.none(),
            chunk_guilds_at_startup=False,
            help_command=None
        )

    async def setup_hook(self):
        try:
            await self.load_extension("cogs.music")
            await self.load_extension("cogs.health")
            await self.tree.sync()
        except Exception as e:
            print(f"Failed to load extension: {e}")

    async def on_ready(self):
        print(f"Logged in successfully as {self.user.name}")

bot = MusicBot()

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_TOKEN is missing from .env file.")
    else:
        bot.run(TOKEN)