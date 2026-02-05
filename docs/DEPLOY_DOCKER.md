# Docker Deployment Guide

This guide covers deploying the MansionRadio Bot using Docker and Docker Compose. This is the recommended approach for production deployments.

---

## Prerequisites

- **Docker:** 20.10+ (with Docker Compose)
- **Network:** Access to your IRC server and AzuraCast API endpoint
- **Disk:** ~200MB for the container image

---

## Quick Start (Local Testing)

Get the bot running locally in under 5 minutes:

```bash
cd ~/projects/mansionradio

# Build the image
docker build -f docker/Dockerfile -t mansion-radio-bot:latest .

# Run the bot with environment variables
docker run --rm \
  -e IRC_SERVER=irc.example.com \
  -e IRC_PORT=6697 \
  -e BOT_NICKNAME=MansionRadio \
  -e IRC_CHANNELS="#radio" \
  -e AZURACAST_API="https://radio.example.com/api/nowplaying/station_id" \
   -e POLL_INTERVAL=60 \
  mansion-radio-bot:latest
```

Expected output:
```
[INFO] Starting MansionNET Radio Bot...
[INFO] RadioBot initialized
[INFO] Server: irc.example.com:6697
[INFO] Channels: #radio
[INFO] Poll interval: 60s
[INFO] Connected to IRC server
[INFO] Joined #radio
```

Stop the bot: Press `Ctrl+C`

---

## Production Deployment (with Docker Compose)

### Step 1: Copy Project to Target Machine

```bash
# From your workstation
scp -r ~/projects/mansionradio user@pi3:~/mansion-radio-bot

# Or manually copy and extract
ssh user@pi3
mkdir -p ~/mansion-radio-bot
# ... upload files via SFTP or git clone
```

### Step 2: Configure Environment

```bash
cd ~/mansion-radio-bot

# Copy the example docker-compose file
cp docker/docker-compose.example.yml docker-compose.yml

# Edit with your settings
nano docker-compose.yml
```

Update these environment variables in the `services.mansion-radio-bot.environment` section:

```yaml
environment:
  # IRC Server Configuration
  - IRC_SERVER=irc.example.com          # Your IRC server hostname
  - IRC_PORT=6697                       # Usually 6697 (TLS) or 6667 (plain)
  - BOT_NICKNAME=MansionRadio           # The bot's nickname in IRC
  - IRC_CHANNELS="#radio,#music"        # Comma-separated channel list
  
  # SASL Authentication (optional, for registered nicks)
  - SASL_USERNAME=your_account_name     # Account that owns the registered nick
  - SASL_PASSWORD=your_password         # SASL password
  
  # AzuraCast API Configuration
  - AZURACAST_API=https://radio.example.com/api/nowplaying/station_id
  
  # Polling Configuration
  - POLL_INTERVAL=60                    # How often to check for song changes (seconds)
  - TZ=UTC                              # Timezone for logs (optional)
```

### Step 3: Build the Docker Image

```bash
# Build the image
docker build -f docker/Dockerfile -t mansion-radio-bot:latest .

# Verify the build succeeded
docker images | grep mansion-radio-bot
```

Expected output:
```
REPOSITORY              TAG       IMAGE ID      CREATED       SIZE
mansion-radio-bot       latest    abc1234def    2 minutes ago 98MB
```

### Step 4: Start the Bot

```bash
# Start in background (detached mode)
docker-compose up -d

# Check if it started
docker-compose ps
```

Expected output:
```
NAME                 COMMAND              STATUS          PORTS
mansion-radio-bot    python src/main.py   Up 5 seconds    
```

### Step 5: Verify the Bot is Working

```bash
# View real-time logs
docker-compose logs -f mansion-radio-bot

# Wait for these messages:
# [INFO] Connected to IRC server
# [INFO] Joined #radio
```

Once you see "Joined [channel]", the bot is ready to announce songs!

---

## Managing Your Deployment

### View Logs

```bash
# Real-time logs (press Ctrl+C to stop)
docker-compose logs -f mansion-radio-bot

# Last 50 lines
docker-compose logs --tail 50 mansion-radio-bot

# Logs from the last hour
docker-compose logs --since 1h mansion-radio-bot
```

### Check Container Health

```bash
# Show running containers
docker-compose ps

# Check resource usage
docker stats mansion-radio-bot
```

Expected resource usage: **<100MB memory**, **<5% CPU** (when idle)

### Restart the Bot

```bash
# Graceful restart
docker-compose restart mansion-radio-bot

# Or stop and start separately
docker-compose stop mansion-radio-bot
docker-compose start mansion-radio-bot
```

### Stop the Bot

```bash
# Stop but keep container
docker-compose stop mansion-radio-bot

# Stop and remove container
docker-compose down
```

### Update to Latest Code

```bash
# Stop the bot
docker-compose down

# Pull latest changes (if using git)
git pull origin main

# Rebuild the image
docker build -f docker/Dockerfile -t mansion-radio-bot:latest .

# Start with new image
docker-compose up -d
```

---

## Image Details

| Property | Details |
|----------|---------|
| **Base Image** | Alpine Linux 3.11 (~25MB) |
| **Python Version** | 3.11 (minimal footprint) |
| **Security User** | Non-root `radiobot` (uid 1000) |
| **Working Directory** | `/app` |
| **Entrypoint** | `python src/main.py` |
| **Health Check** | Runs every 30 seconds |
| **Restart Policy** | `unless-stopped` (auto-restart on crash) |

---

## Customizing Configuration

### Option A: Edit docker-compose.yml

Edit the file before starting:

```bash
nano docker-compose.yml
# Change environment variables
docker-compose up -d
```

### Option B: Runtime Environment Overrides

Override variables at runtime:

```bash
docker-compose run --rm \
  -e BOT_NICKNAME=MyBot \
  -e POLL_INTERVAL=30 \
  mansion-radio-bot
```

### Option C: Use Portainer (if available)

See [DEPLOY_PORTAINER.md](DEPLOY_PORTAINER.md) for Portainer UI steps.

---

## Troubleshooting

### Container won't start

```bash
# Check the logs
docker-compose logs mansion-radio-bot

# Common issues:
# - "Cannot connect to IRC server" → Check IRC_SERVER and IRC_PORT
# - "API connection failed" → Check AZURACAST_API URL is reachable
# - "SASL authentication failed" → Verify SASL_USERNAME and SASL_PASSWORD
```

### Bot connects but doesn't announce songs

```bash
# Check logs for API errors
docker-compose logs mansion-radio-bot | grep -i "error\|exception\|api"

# Verify the AzuraCast API is responding
curl https://radio.example.com/api/nowplaying/station_id | head -20
```

### High memory usage

```bash
# Check stats
docker stats mansion-radio-bot

# Alpine + Python should use <100MB
# If higher, there may be a memory leak
# Try rebuilding the image:
docker-compose down
docker build --no-cache -f docker/Dockerfile -t mansion-radio-bot:latest .
docker-compose up -d
```

### Networking issues

```bash
# Verify DNS resolution
docker-compose exec mansion-radio-bot nslookup irc.example.com

# Test IRC server connectivity
docker-compose exec mansion-radio-bot nc -zv irc.example.com 6697

# Test API endpoint
docker-compose exec mansion-radio-bot curl -s https://radio.example.com/api/nowplaying/station_id
```

---

## Docker Compose Reference

### File Structure

The `docker-compose.yml` is configured in `docker/docker-compose.example.yml`:

```yaml
version: '3.8'

services:
  mansion-radio-bot:
    image: mansion-radio-bot:latest        # Built from docker/Dockerfile
    container_name: mansion-radio-bot
    user: "1000:1000"                       # Non-root security
    restart: unless-stopped                 # Auto-restart policy
    environment:
      # ... configuration variables
    volumes:
      - ./logs:/app/logs                    # Optional: persist logs
    networks:
      - mansion-net
    healthcheck:
      test: ["CMD", "pgrep", "-f", "python src/main.py"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

networks:
  mansion-net:
    driver: bridge
```

---

## Advanced Deployment

### Multiple IRC Networks

Create separate docker-compose entries for each network:

```yaml
services:
  mansion-radio-bot-libera:
    image: mansion-radio-bot:latest
    environment:
      - IRC_SERVER=irc.libera.chat
      - BOT_NICKNAME=MansionRadio1
      # ... other settings
    
  mansion-radio-bot-undernet:
    image: mansion-radio-bot:latest
    environment:
      - IRC_SERVER=irc.undernet.org
      - BOT_NICKNAME=MansionRadio2
      # ... other settings
```

Then manage them together:
```bash
docker-compose up -d
docker-compose ps
```

### Persisting Logs

By default, logs are printed to stdout. To persist them in the container:

1. Uncomment the `volumes` section in docker-compose.yml:
   ```yaml
   volumes:
     - ./logs:/app/logs
   ```

2. Update the bot to write logs to file (requires code modification)

3. Access logs:
   ```bash
   cat logs/mansion-radio-bot.log
   ```

---

## Next Steps

1. ✅ Configure docker-compose.yml with your settings
2. ✅ Build and start the container
3. ✅ Verify bot joins IRC channel
4. ✅ Wait for first song announcement (max 60 seconds)
5. ✅ Monitor logs with `docker-compose logs -f`

**Need Docker Compose reference?** See [docker-compose official docs](https://docs.docker.com/compose/)

**Having issues?** Check [TROUBLESHOOT_PORTAINER.md](TROUBLESHOOT_PORTAINER.md) for Docker-specific troubleshooting.
