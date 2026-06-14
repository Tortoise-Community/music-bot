import os
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from utils import pixeldrain_manager
from decouple import config


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.playlist = []
        self.current_index = 0

        self.guild_id = int(config("GUILD_ID"))
        self.channel_id = int(config("CHANNEL_ID"))
        self.api_key = config("PIXELDRAIN_API_KEY")
        self.album_id = config("PIXELDRAIN_ALBUM_ID")

    async def cog_load(self):
        self.bot.loop.create_task(self.startup_task())

    def fetch_files_blocking(self):
        print("Checking local files and synchronizing with Pixeldrain...")
        self.playlist = pixeldrain_manager.sync_music(self.api_key, self.album_id)
        if self.current_index >= len(self.playlist):
            self.current_index = 0

    def play_next(self, error=None):
        if error:
            print(f"Player error: {error}")

        guild = self.bot.get_guild(self.guild_id)
        if not guild or not guild.voice_client or not guild.voice_client.is_connected():
            return

        vc = guild.voice_client

        if not self.playlist:
            print("Playlist is empty. Add files and use /refresh.")
            return

        if self.current_index >= len(self.playlist):
            self.current_index = 0

        song = self.playlist[self.current_index]
        self.current_index += 1

        try:
            if os.path.getsize(song["path"]) == 0:
                raise ValueError("File is 0 bytes (corrupted download).")

            source = discord.FFmpegPCMAudio(song["path"])
            vc.play(source, after=self.play_next)
            print(f"▶️ Playing local file: {song['name']}")

        except Exception as e:
            print(f"⚠️ Playback error for {song['name']}: {repr(e)}")
            self.bot.loop.call_later(2.0, self.play_next)

    async def startup_task(self):
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

    @app_commands.command(name="skip", description="Skips the currently playing track.")
    @app_commands.default_permissions(kick_members=True)
    async def skip(self, interaction: discord.Interaction):
        if interaction.guild_id != self.guild_id:
            await interaction.response.send_message("This command is restricted to the main server.", ephemeral=True)
            return

        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("⏩ Track skipped.")
        else:
            await interaction.response.send_message("Nothing is playing right now.", ephemeral=True)

    @app_commands.command(name="refresh", description="Forces a sync with Pixeldrain to pick up new files.")
    @app_commands.default_permissions(kick_members=True)
    async def refresh(self, interaction: discord.Interaction):
        if interaction.guild_id != self.guild_id:
            await interaction.response.send_message("This command is restricted to the main server.", ephemeral=True)
            return

        # Defer the interaction immediately so Discord doesn't timeout the 3-second limit
        await interaction.response.defer(thinking=True)

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.fetch_files_blocking)

        # Use followup.send() because we already deferred the initial response
        await interaction.followup.send(f"✅ Sync complete! Total tracks in local rotation: **{len(self.playlist)}**")

        vc = interaction.guild.voice_client
        if vc and not vc.is_playing() and self.playlist:
            self.play_next()

    @app_commands.command(name="status", description="Displays the currently streaming song.")
    async def status(self, interaction: discord.Interaction):
        if interaction.guild_id != self.guild_id:
            await interaction.response.send_message("This command is restricted to the main server.", ephemeral=True)
            return

        vc = interaction.guild.voice_client
        if self.playlist and vc and vc.is_playing():
            current_song = self.playlist[(self.current_index - 1) % len(self.playlist)]
            await interaction.response.send_message(f"🎶 **Now Playing:** `{current_song['name']}`")
        else:
            await interaction.response.send_message("The player is currently idle.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(MusicCog(bot))