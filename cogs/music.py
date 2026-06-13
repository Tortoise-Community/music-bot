import os
import asyncio
import discord
from discord.ext import commands
import pixeldrain_sync


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.playlist = []
        self.current_index = 0

        self.guild_id = int(os.getenv("GUILD_ID"))
        self.channel_id = int(os.getenv("CHANNEL_ID"))
        self.api_key = os.getenv("PIXELDRAIN_API_KEY")
        self.album_id = os.getenv("PIXELDRAIN_ALBUM_ID")

    async def cog_load(self):
        self.bot.loop.create_task(self.startup_task())

    def fetch_files_blocking(self):
        print("Checking local files and synchronizing with Pixeldrain...")
        self.playlist = pixeldrain_sync.sync_music(self.api_key, self.album_id)
        if self.current_index >= len(self.playlist):
            self.current_index = 0

    def play_next(self, error=None):
        """Callback function to loop through local files continuously."""
        if error:
            print(f"Player error: {error}")

        guild = self.bot.get_guild(self.guild_id)
        if not guild or not guild.voice_client or not guild.voice_client.is_connected():
            return

        vc = guild.voice_client

        if not self.playlist:
            print("Playlist is empty. Add files and use !refresh.")
            return

        if self.current_index >= len(self.playlist):
            self.current_index = 0

        song = self.playlist[self.current_index]
        self.current_index += 1

        try:
            # Safeguard: Check if the file is completely empty before playing
            if os.path.getsize(song["path"]) == 0:
                raise ValueError("File is 0 bytes (corrupted download).")

            source = discord.FFmpegPCMAudio(song["path"])
            vc.play(source, after=self.play_next)
            print(f"▶️ Playing local file: {song['name']}")

        except Exception as e:
            # Using repr(e) forces Python to print the exact error object, preventing blank logs
            print(f"⚠️ Playback error for {song['name']}: {repr(e)}")

            # Safeguard: Wait 2 seconds before trying the next song to prevent infinite loops
            self.bot.loop.call_later(2.0, self.play_next)

    async def startup_task(self):
        """Dedicated background task to handle sync and connection safely."""
        await self.bot.wait_until_ready()

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.fetch_files_blocking)

        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            print(f"Error: Could not find Guild ID {self.guild_id}")
            return

        channel = guild.get_channel(self.channel_id)
        if not channel:
            print(f"Error: Could not find Channel ID {self.channel_id}")
            return

        try:
            vc = discord.utils.get(self.bot.voice_clients, guild=guild)
            if not vc or not vc.is_connected():
                vc = await channel.connect(timeout=60.0, reconnect=True)
                print(f"Connected to Voice Channel: {channel.name}")

            if not vc.is_playing() and self.playlist:
                self.play_next()
        except Exception as e:
            print(f"Voice connection error: {e}")

    @commands.command(name="skip")
    async def skip(self, ctx):
        if ctx.guild.id != self.guild_id: return
        vc = ctx.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await ctx.send("⏩ Track skipped.")
        else:
            await ctx.send("Nothing is playing right now.")

    @commands.command(name="refresh")
    async def refresh(self, ctx):
        if ctx.guild.id != self.guild_id: return
        await ctx.send("🔄 Checking Pixeldrain for new files... (This runs in the background)")

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.fetch_files_blocking)

        await ctx.send(f"✅ Sync complete! Total tracks in local rotation: **{len(self.playlist)}**")

        vc = ctx.guild.voice_client
        if vc and not vc.is_playing() and self.playlist:
            self.play_next()

    @commands.command(name="status")
    async def status(self, ctx):
        if ctx.guild.id != self.guild_id: return
        vc = ctx.guild.voice_client
        if self.playlist and vc and vc.is_playing():
            current_song = self.playlist[(self.current_index - 1) % len(self.playlist)]
            await ctx.send(f"🎶 **Now Playing:** `{current_song['name']}`")
        else:
            await ctx.send("The bot is idle.")


async def setup(bot):
    await bot.add_cog(MusicCog(bot))