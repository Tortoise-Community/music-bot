from aiohttp import web
import os


async def handle(request):
    return web.Response(text="Discord Music Bot is awake and running on Render!")


async def run_dummy_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 10000))

    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Dummy web server running on port {port} to keep Render happy.")