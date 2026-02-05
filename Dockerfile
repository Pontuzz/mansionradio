FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers

# Copy only requirements first (minimal context)
COPY requirements.txt .

# Install Python dependencies with increased timeout
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# Copy application code
COPY main.py bot.py ./
COPY fetchers ./fetchers

# Create non-root user for security (uid/gid 1000)
RUN addgroup -g 1000 radiobot && \
    adduser -D -u 1000 -G radiobot radiobot && \
    chown -R radiobot:radiobot /app

USER radiobot

# Run the bot
CMD ["python", "main.py"]
