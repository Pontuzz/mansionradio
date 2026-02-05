# Docker Deployment Guide

## Quick Start (Local Testing)

```bash
cd ~/projects/mansionradio

# Build and run (no .env needed - config is in docker-compose.yml)
docker-compose up --build
```

The bot will start and connect to IRC. Check logs:
```bash
docker-compose logs -f mansion-radio-bot
```

Stop the bot:
```bash
docker-compose down
```

---

## Production Deployment (Pi3 or Ubuntu VM with Docker)

### Prerequisites
- Docker and Docker Compose installed

### Deploy

```bash
# Copy project to target machine
scp -r ~/projects/mansionradio user@pi3:~/

# SSH into machine
ssh user@pi3

# Navigate to project
cd ~/mansion-radio-bot

# Build image (first time only)
docker-compose build

# Start bot (runs in background)
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f mansion-radio-bot
```

### Manage

```bash
# View logs
docker-compose logs -f

# Stop bot
docker-compose down

# Restart bot
docker-compose restart

# View resource usage
docker stats mansion-radio-bot
```

---

## Image Details

- **Base:** Alpine Linux 3.11 (lightweight ~50MB)
- **Python:** 3.11
- **User:** Non-root `radiobot` user (security)
- **Health Check:** Every 30 seconds
- **Restart Policy:** Auto-restart on failure

---

## Customizing Environment Variables (Optional)

The default configuration in `docker-compose.yml` is ready to use:
```yaml
environment:
  - IRC_SERVER=irc.example.com
  - IRC_PORT=6697
  - BOT_NICKNAME=MansionRadio
  - IRC_CHANNELS=#radio
  - AZURACAST_API=https://radio.example.com/api/nowplaying/station_id
  - POLL_INTERVAL=15
  - TZ=Europe/Belgrade
```

To customize (e.g., different bot nickname or channels):

**Option A: Edit docker-compose.yml directly**
```bash
nano docker-compose.yml
# Change environment variables as needed
docker-compose up -d
```

**Option B: Use Portainer UI**
1. Go to Stacks → Your Stack
2. Edit the Stack
3. Modify environment variables
4. Update the stack

---

## Troubleshooting Docker

### Bot won't start
```bash
docker-compose logs mansion-radio-bot
# Check for errors in output
```

### High memory usage
```bash
docker stats mansion-radio-bot
# Alpine + Python should use <100MB
```

### Rebuild image
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Completely clean up
```bash
docker-compose down -v
docker image rm mansion-radio-bot:latest
docker-compose build
```

---

## Kubernetes/Advanced Deployment

If deploying to Kubernetes or Docker Swarm, the Dockerfile is ready. Contact for additional deployment manifests.
