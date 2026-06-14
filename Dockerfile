FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

WORKDIR /app

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-interaction --no-root --no-ansi

COPY . .

RUN mkdir -p /app/music

CMD ["python", "bot.py"]
