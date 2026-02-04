# Portainer Deployment Guide

Deploy the MansionNET Radio Bot to Portainer without needing external `.env` files.

---

## Prerequisites

- Portainer installed and running
- Docker and Docker Compose available
- Access to Portainer UI

---

## Step-by-Step Deployment

### 1. Copy docker-compose.yml to Portainer Host

Get the contents of `docker-compose.yml`:

```bash
cat ~/projects/mansionradio/docker-compose.yml
```

Or copy the entire project:
```bash
scp -r ~/projects/mansionradio user@portainer-host:~/
```

---

### 2. In Portainer UI

**Navigate to:** Stacks → Add Stack

**Option A: Paste Compose File**

1. Choose **Web Editor**
2. Paste the entire contents of `docker-compose.yml`:

```yaml
version: '3.8'

services:
  mansion-radio-bot:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: mansion-radio-bot
    restart: unless-stopped
    environment:
      # IRC Configuration
      - IRC_SERVER=irc.inthemansion.com
      - IRC_PORT=6697
      - BOT_NICKNAME=MansionRadio
      - IRC_CHANNELS=#radio
      # AzuraCast API
      - AZURACAST_API=https://radio.inthemansion.com/api/nowplaying/mansionnet
      # Polling interval (seconds)
      - POLL_INTERVAL=15
      # Timezone
      - TZ=Europe/Belgrade
    volumes:
      - ./logs:/app/logs
    networks:
      - mansion-net
    healthcheck:
      test: ["CMD", "pgrep", "-f", "python main.py"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

networks:
  mansion-net:
    driver: bridge
```

3. **Name:** `mansion-radio-bot`
4. **Deploy the stack**

**Option B: Upload Files**

1. Choose **Repository**
2. Select **Git** and provide your repo URL (if using git)
   - Or use **Upload** to upload the `docker-compose.yml` and `Dockerfile`

3. Configure:
   - **Compose path:** `docker-compose.yml`
   - **Deploy the stack**

---

## 3. Verify Deployment

### Check Stack Status
1. Go to **Stacks** → **mansion-radio-bot**
2. Verify all containers are running (green status)

### View Logs
1. Click the stack
2. Click **mansion-radio-bot** container
3. View **Logs** tab

Expected output:
```
[INFO] Starting MansionNET Radio Bot...
[INFO] RadioBot initialized
[INFO] Server: irc.inthemansion.com:6697
[INFO] Channels: #radio
[INFO] Poll interval: 15s
[INFO] Connected to IRC server
[INFO] Joined #radio
```

---

## Customizing Configuration

### Method 1: Edit Stack in Portainer

1. **Stacks** → **mansion-radio-bot** → **Editor**
2. Find the `environment:` section
3. Change values (e.g., `BOT_NICKNAME`, `IRC_CHANNELS`)
4. **Update the stack**

Example changes:
```yaml
environment:
  - BOT_NICKNAME=MyCustomBotName
  - IRC_CHANNELS=#radio,#music,#lounge
  - POLL_INTERVAL=30
```

### Method 2: Update docker-compose.yml Before Deployment

Edit the file on your machine, then upload/deploy again.

---

## Management

### Stop Stack
**Stacks** → **mansion-radio-bot** → **Stop**

### Start Stack
**Stacks** → **mansion-radio-bot** → **Start**

### Restart Stack
**Stacks** → **mansion-radio-bot** → **Restart**

### Delete Stack
**Stacks** → **mansion-radio-bot** → **Remove** (choose "Remove volume" if desired)

### View Real-Time Logs
Click the stack → Click **mansion-radio-bot** → **Logs** (check "Auto-scroll")

### Rebuild Image
**Stacks** → **mansion-radio-bot** → **Editor** → **Update the stack**
(This will rebuild the image if `Dockerfile` changed)

---

## Troubleshooting

### Container won't start
1. Check **Logs** tab for errors
2. Verify IRC server is accessible (port 6697)
3. Check AzuraCast API is responding

### Bot connects but doesn't announce
1. Verify `IRC_CHANNELS` is correct
2. Check bot successfully joined channel (see logs)
3. Verify AzuraCast API is working

### High memory usage
1. Check **Stats** for the container
2. Alpine + Python should use <100MB
3. If higher, check for memory leaks

### Need to rebuild image
If you updated `Dockerfile` or dependencies:
1. Edit stack
2. Change something minor (add/remove space) to force update
3. Or delete and redeploy stack with new code

---

## Important Notes

- **No .env file needed** - Configuration is in `docker-compose.yml`
- **Environment variables** can be edited directly in Portainer UI
- **Restart policy** is set to `unless-stopped` - will auto-restart on failure
- **Health check** runs every 30 seconds to monitor bot status
- **Logs volume** is optional - remove if you don't need persistent logs

---

## Next Steps

1. Verify bot joins IRC channel `#radio`
2. Wait for first song change (max 15 seconds)
3. Bot should announce: `♫ Now playing: Artist - Title (Album)`

That's it! Your bot is running in Portainer.
