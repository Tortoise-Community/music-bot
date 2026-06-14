# Music-Bot: 24/7 Discord Music Bot

A lightweight discord music bot designed to play 24/7 lo-fi music in your server's voice channel. 
Built with `discord.py` this bot caches MP3 files locally and synchronizes seamlessly with Pixeldrain in the background.

> **Note:** This bot **does not** play music from Youtube or other music streaming platforms. The user will have to supply their own music via pixeldrain.


It is specifically optimized to run on the **Render Free Tier** with a built-in lightweight web server to prevent sleep mode.

---

## Features
* **24/7 Continuous Playback:** Automatically loops through the local music directory.
* **Pixeldrain Integration:** Syncs your music library directly from a Pixeldrain list.
* **Local Caching:** Downloads files locally to save bandwidth and prevent buffering.
* **Dockerized:** Ready to deploy anywhere with a clean, optimized Dockerfile.

---

## Deploying to Render (Free Tier)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Tortoise-Community/music-bot)

> **Note:** To keep the bot running 24/7 on the free tier, use a service like [UptimeRobot](https://uptimerobot.com/) to ping your Render web service URL every 10 minutes.

---

## Prerequisites
If you are running this locally (not in Docker), you will need:
* **Python 3.11+**
* **Poetry** for dependency management.
* **ffmpeg** installed on your system.
* **opus** (If on macOS: `brew install opus`).

---

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Tortoise-Community/music-bot.git
```
```bash
cd music-bot
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory and add the following credentials:

```env
DISCORD_TOKEN=your_discord_bot_token
GUILD_ID=your_server_id
CHANNEL_ID=your_voice_channel_id
PIXELDRAIN_API_KEY=your_pixeldrain_api_key
PIXELDRAIN_ALBUM_ID=your_pixeldrain_list_id
```

### 3. Run Locally (Using Poetry)

```bash
# Install dependencies
poetry install
```
```bash
# Run the bot
poetry run python bot.py
```

### 4. Run via Docker

```bash
# Build the image
docker build -t music-bot .
```
```bash
# Run the container
docker run -d \
  --name music-bot \
  --restart unless-stopped \
  --env-file .env \
  -p 10000:10000 \
  music-bot

```

---

## Slash Commands

| Command | Description | Permissions |
| --- | --- | --- |
| `/status` | Shows the currently playing track. | Everyone |
| `/skip` | Skips the current track and plays the next one. | `Kick Members` |
| `/refresh` | Syncs the local library with your Pixeldrain list in the background. | `Kick Members` |

---

## License

This project is open-source and available under the [MIT License](https://www.google.com/search?q=LICENSE).
