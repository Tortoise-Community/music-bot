FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /app/music

COPY bot.py pixeldrain_sync.py keep_alive.py ./
COPY cogs/ /app/cogs

CMD ["python", "bot.py"]