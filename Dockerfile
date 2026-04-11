FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for Pillow, psycopg2, moviepy
RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc g++ libpq-dev libjpeg-dev zlib1g-dev libffi-dev \
  ffmpeg imagemagick fonts-dejavu-core \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
