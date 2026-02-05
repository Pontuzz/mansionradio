# MansionRadio Bot - Manual Deployment Guide

**Bot Configuration (Current):**
- Channel: `#bots` (temporary for testing)
- Bot Nickname: `MansionRadio`
- IRC Server: `irc.inthemansion.com:6697` (TLS)
- Polling: 10 seconds
- Features: Auto-announce on song change + `!playing` command

---

## Step 1: Prepare Files on Your Local Machine

The project is ready at: `~/projects/mansionradio/`

**Option A: Copy entire directory via SCP**
```bash
# This will fail due to SSH setup, so use Option B instead
```

**Option B: Use the pre-made tarball (RECOMMENDED)**
```bash
# The tarball is already created at:
ls -lh ~/projects/mansionradio/mansionradio.tar.gz

# Copy it to your Docker host:
scp ~/projects/mansionradio/mansionradio.tar.gz [username]@[your-docker-host]:~/
# Password: (enter your host password)
```

---

## Step 2: Extract and Prepare on Your Docker Host

**SSH into your Docker host:**
```bash
ssh [username]@[your-docker-host]
# Password: (your host password)
```

**Extract the project:**
```bash
cd ~
tar -xzf mansionradio.tar.gz
mv mansionradio mansion-radio-bot  # (optional, for cleaner naming)
cd mansion-radio-bot
ls -la
```

**Verify files exist:**
```bash
# You should see:
# - bot.py
# - main.py
# - Dockerfile
# - docker-compose.yml
# - fetchers/ (directory)
# - requirements.txt
# - And documentation files
```

---

## Step 3: Build Docker Image on HS01

**Still SSH'd into HS01:**

```bash
cd ~/mansion-radio-bot

# Build the image (takes 3-5 minutes)
docker build -t mansion-radio-bot:latest .

# Watch the build progress:
# [1/5] FROM python:3.11-alpine
# [2/5] WORKDIR /app
# [3/5] COPY requirements.txt
# [4/5] RUN pip install
# [5/5] COPY . /app

# When done, you should see:
# => exporting to image
# => naming to docker.io/library/mansion-radio-bot:latest
# => SUCCESS
```

**Verify image was built:**
```bash
docker images | grep mansion-radio-bot

# Should show something like:
# REPOSITORY              TAG       IMAGE ID       CREATED        SIZE
# mansion-radio-bot       latest    abc123def...   2 minutes ago   ~250MB
```

---

## Step 4: Deploy via Portainer

**In your browser:**

1. **Open Portainer:**
   - URL: `[your-portainer-url]`
   - Navigate to Stacks section for your Docker host

2. **Create New Stack:**
   - Click: **Add Stack** (top right)
   - Name: `mansion-radio-bot`
   - Mode: **Web Editor**

3. **Paste Docker Compose Configuration:**

```yaml
version: '3.8'

services:
  mansion-radio-bot:
    image: mansion-radio-bot:latest
    container_name: mansion-radio-bot
    restart: unless-stopped
    environment:
      # IRC Configuration
      - IRC_SERVER=irc.inthemansion.com
      - IRC_PORT=6697
      - BOT_NICKNAME=MansionRadio
      - IRC_CHANNELS=#bots
      # AzuraCast API
      - AZURACAST_API=https://radio.inthemansion.com/api/nowplaying/mansionnet
      # Polling interval (seconds)
      - POLL_INTERVAL=10
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

4. **Deploy:**
   - Click: **Deploy the stack**
   - Wait for green status indicator ✓

---

## Step 5: Verify Deployment

**In Portainer:**

1. **Check Container Status:**
   - Navigate to: **Stacks** → **mansion-radio-bot**
   - Container should show: **GREEN** ✓
   - Status: **Running**

2. **View Logs:**
   - Click container: **mansion-radio-bot**
   - Go to: **Logs** tab
   - Should see startup messages:
     ```
     [INFO] RadioBot initialized
     [INFO] Server: irc.inthemansion.com:6697
     [INFO] Channels: #bots
     [INFO] Poll interval: 10s
     [INFO] Connected to IRC server
     [INFO] Joined #bots
     ```

3. **Monitor for Song Announcements:**
   - Keep logs open
   - Wait for first announcement (will happen when a song change is detected)
   - Expected format: `[ANNOUNCE] #bots: ♫ Now playing: Artist - Title (Album)`

---

## Step 6: Test in IRC

**Connect to IRC:**
- Server: `irc.inthemansion.com`
- Port: `6697` (TLS)
- Your nickname: (your choice)

**Join #bots:**
```
/join #bots
```

**Verify bot is there:**
- You should see: `MansionRadio` in the channel

**Test automatic announcement:**
- Wait up to 10 seconds
- When a song changes, bot announces:
  ```
  <MansionRadio> ♫ Now playing: Artist - Title (Album)
  ```

**Test !playing command:**
- Type: `!playing`
- Bot responds:
  ```
  <MansionRadio> @YourNick: ♫ Now playing: Artist - Title (Album)
  ```

---

## Troubleshooting

### Container won't start
```bash
# On your Docker host, check logs:
docker logs mansion-radio-bot

# Verify image exists:
docker images | grep mansion-radio-bot

# Try rebuilding:
cd ~/mansion-radio-bot
docker build -t mansion-radio-bot:latest .
```

### Bot doesn't join channel
- Verify IRC_CHANNELS is set to: `#bots`
- Check container logs for connection errors
- Test IRC server: `nc -zv irc.inthemansion.com 6697`

### Bot connects but no announcements
```bash
# Check if API is reachable:
curl -v https://radio.inthemansion.com/api/nowplaying/mansionnet

# Should return JSON with current song info
```

### !playing command not working
- Verify bot nickname is: `MansionRadio`
- Type exact command: `!playing` (case-insensitive in IRC)
- Check logs for: `[COMMAND] !playing`

---

## Post-Deployment Notes

**When ready to switch back to #radio:**
1. In Portainer: **Stacks** → **mansion-radio-bot** → **Editor**
2. Change: `IRC_CHANNELS=#bots` to `IRC_CHANNELS=#radio`
3. Click: **Update the stack**
4. Container restarts automatically

**To rollback if needed:**
1. In Portainer: **Stacks** → **mansion-radio-bot** → **Remove**
2. Image remains: `docker images | grep mansion-radio-bot`
3. Can redeploy with same image anytime

---

## Quick Reference

| Item | Value |
|------|-------|
| Image Name | `mansion-radio-bot:latest` |
| Container | `mansion-radio-bot` |
| Stack Name | `mansion-radio-bot` |
| Bot Nickname | `MansionRadio` |
| Channel | `#bots` (temporary) |
| IRC Server | `irc.inthemansion.com:6697` |
| Poll Interval | 10 seconds |
| Portainer URL | `[your-portainer-url]` |

---

**Ready to deploy? Follow the steps above in order!**
