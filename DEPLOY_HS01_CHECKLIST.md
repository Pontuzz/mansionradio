# Docker Host Deployment - Complete Checklist

**Current Configuration:**
- Polling interval: **10 seconds**
- Bot nickname: **MansionRadio**
- IRC server: **irc.inthemansion.com:6697** (TLS)
- Channel: **#bots** (temporary for testing, use #radio for production)
- Features: Auto-announce on song change + !playing command

---

## Pre-Deployment Checklist

- [ ] Verify all code is committed (if using git)
- [ ] Docker daemon running on your Docker host
- [ ] Portainer accessible on your Docker host
- [ ] SSH access to Docker host confirmed
- [ ] Sufficient disk space (~500MB for image)

---

## Deployment Steps

### Step 1: Copy Project to Your Docker Host

**Using Git (Recommended):**
```bash
# Clone from GitHub to your Docker host
ssh [username]@[your-docker-host]
cd ~
git clone https://github.com/pontuzz/mansionradio.git
cd mansionradio
```

**Or using SCP:**
```bash
# From your local machine
scp -r ~/projects/mansionradio [username]@[your-docker-host]:~/
```

**Verify copy was successful:**
```bash
ssh [username]@[your-docker-host] "ls -la ~/mansionradio"
```

Should show:
```
bot.py
main.py
Dockerfile
docker-compose.yml
fetchers/
docs/
etc.
```

---

### Step 2: Build Docker Image on Your Docker Host

**SSH to your Docker host:**
```bash
ssh [username]@[your-docker-host]
cd ~/mansionradio

# Build the image (takes 3-5 minutes)
docker build -t mansion-radio-bot:latest .

# Wait for it to complete, you'll see:
# [1/5] FROM python:3.11-alpine
# [2/5] WORKDIR /app
# ...
# => SUCCESS
```

**Verify image was built:**
```bash
docker images | grep mansion-radio-bot
```

Should show:
```
REPOSITORY              TAG       IMAGE ID       CREATED        SIZE
mansion-radio-bot       latest    abc123def...   2 minutes ago   ~250MB
```

---

### Step 3: Deploy in Portainer on Your Docker Host

1. **Open Portainer UI** - Access via browser on your Docker host
   - URL: Usually `[your-portainer-url]`

2. **Navigate to Stacks**
   - Click: **Stacks** (left sidebar)
   - Click: **Add Stack** (top right)

3. **Create Stack**
   - **Name:** `mansion-radio-bot`
   - **Mode:** Web Editor

4. **Paste docker-compose.yml**
   
   Copy entire content of `docker-compose.yml` and paste:

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
      # Timezone (adjust to your location or use UTC)
      - TZ=UTC
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

5. **Deploy**
   - Click: **Deploy the stack**
   - Wait for green status indicator

---

## Step 4: Verify Deployment

### In Portainer UI:

1. **Check Stack Status**
   - Go to: **Stacks** → **mansion-radio-bot**
   - Container should be **GREEN** ✓
   - Status: **Running**

2. **View Container Logs**
   - Click: **mansion-radio-bot** (the container)
   - Click: **Logs** tab
   - Should see:
     ```
     [INFO] RadioBot initialized
     [INFO] Server: irc.inthemansion.com:6697
     [INFO] Channels: #radio
     [INFO] Poll interval: 10s
     [INFO] Commands: !playing
     [INFO] Connected to IRC server
     [INFO] Joined #radio
     ```

3. **Monitor Logs**
   - Check "Auto-scroll" in Portainer
   - Wait for first announcement:
     ```
     [ANNOUNCE] #bots: ♫ Now playing: Artist - Title (Album)
     ```

### Via SSH (Optional):

```bash
# Check if container is running
docker ps | grep mansion-radio-bot

# View live logs
docker logs -f mansion-radio-bot

# Check container health
docker ps --all | grep mansion-radio-bot
```

---

## Step 5: Test in IRC

1. **Connect to IRC**
   - Server: `irc.inthemansion.com`
   - Port: `6697` (TLS)
   - Your nickname: (your choice)

2. **Join #bots** (or your configured channel)
   - You should see: **MansionRadio** already in channel

3. **Test Automatic Announcement**
   - Wait up to 10 seconds
   - Next song change → Bot announces
   - Expected: `<MansionRadio> ♫ Now playing: Artist - Title (Album)`

4. **Test !playing Command**
   - Type: `!playing`
   - Bot responds: `@YourNick: ♫ Now playing: Artist - Title (Album)`

---

## Configuration Changes (After Deployment)

If you need to adjust settings later:

1. In Portainer: **Stacks** → **mansion-radio-bot** → **Editor**
2. Modify environment variables:
   ```yaml
   - BOT_NICKNAME=DifferentName
   - POLL_INTERVAL=20
   - IRC_CHANNELS=#radio,#music
   ```
3. **Update the stack**
4. Restart takes effect automatically

---

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs mansion-radio-bot

# Check if image exists
docker images | grep mansion-radio-bot

# Try rebuilding
cd ~/mansionradio
docker build -t mansion-radio-bot:latest .
```

### Bot doesn't join channel

- Verify `IRC_CHANNELS=#bots` is set (or your configured channel)
- Check logs: `docker logs mansion-radio-bot`
- Test IRC server: `nc -zv irc.inthemansion.com 6697`

### Bot connects but no announcements

- Check API is working: `curl https://radio.inthemansion.com/api/nowplaying/mansionnet`
- Check logs for API errors
- Wait for next song change (may take minutes)

### !playing command not working

- Verify bot nickname appears correctly in IRC
- Type exact command: `!playing` (case-insensitive)
- Check logs for command execution: `[COMMAND] !playing`

---

## Rollback (If Needed)

If something goes wrong:

1. In Portainer: **Stacks** → **mansion-radio-bot** → **Remove**
2. Remove container: `docker rm mansion-radio-bot`
3. Keep image: `docker images` (can redeploy with same image)
4. Or remove image: `docker rmi mansion-radio-bot:latest`

---

## Post-Deployment

### Monitor
- Check Portainer logs regularly first 24 hours
- Watch for errors or disconnections
- Test commands periodically

### Backup
- Save your `docker-compose.yml` configuration
- Keep `.env` file if you added one

### Documentation
- Record:
  - Deployment date
  - Any custom configuration
  - IRC server details
  - Contact info for maintainer

---

## Quick Reference

| Item | Value |
|------|-------|
| **Image** | `mansion-radio-bot:latest` |
| **Container** | `mansion-radio-bot` |
| **Stack Name** | `mansion-radio-bot` |
| **Bot Nickname** | `MansionRadio` |
| **IRC Server** | `irc.inthemansion.com:6697` |
| **Channel** | `#radio` |
| **Polling** | 10 seconds |
| **Commands** | `!playing` |

---

## Success Indicators

✓ Docker image built without errors  
✓ Container running in Portainer (green status)  
✓ Bot appears in #radio as "MansionRadio"  
✓ Bot announces when song changes  
✓ !playing command responds correctly  
✓ No errors in logs  

---

**Ready to deploy? Follow the steps above!**

Let me know if you hit any issues during deployment.
