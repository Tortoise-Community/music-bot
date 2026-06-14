import os
import time
import discord
from discord.ext import commands
from discord import app_commands
from aiohttp import web


class HealthCheck(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = time.time()

        self.app = web.Application()
        self.app.add_routes([web.get('/', self.handle)])
        self.runner = None
        self.site = None

    async def cog_load(self):
        self.bot.loop.create_task(self._start_server())

    async def handle(self, request: web.Request) -> web.Response:
        return web.Response(text="Chilltoise Music Bot is awake and running on Render!")

    async def _start_server(self):
        await self.bot.wait_until_ready()

        self.runner = web.AppRunner(self.app)
        await self.runner.setup()

        port = int(os.environ.get("PORT", 10000))
        self.site = web.TCPSite(self.runner, '0.0.0.0', port)
        await self.site.start()

        print(f"🫀 Dummy web server running on port {port} to keep Render happy.")

    async def cog_unload(self):
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()

    @app_commands.command(name="health", description="Check if the bot is alive")
    async def health_command(self, interaction: discord.Interaction):
        uptime = int(time.time() - self.start_time)
        latency = round(self.bot.latency * 1000)

        await interaction.response.send_message(
            f"🟢 **Status:** Healthy\n📡 **Latency:** {latency}ms\n⏱️ **Uptime:** {uptime}s",
            ephemeral=False
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(HealthCheck(bot))
