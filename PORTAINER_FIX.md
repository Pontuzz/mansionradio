# Quick Fix for Portainer Deployment

You got a "frame too large" error. Here's the fix:

---

## ⚡ Fastest Solution (5 minutes)

### Step 1: Build the image on your Docker host (not in Portainer)

```bash
cd ~/projects/mansionradio
bash build.sh
```

This creates the image: `mansion-radio-bot:latest`

### Step 2: Use this docker-compose.yml in Portainer

```yaml
version: '3.8'

services:
  mansion-radio-bot:
    image: mansion-radio-bot:latest
    container_name: mansion-radio-bot
    restart: unless-stopped
    environment:
      - IRC_SERVER=irc.inthemansion.com
      - IRC_PORT=6697
      - BOT_NICKNAME=MansionRadio
      - IRC_CHANNELS=#radio
      - AZURACAST_API=https://radio.inthemansion.com/api/nowplaying/mansionnet
      - POLL_INTERVAL=15
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

### Step 3: Deploy in Portainer

1. **Stacks** → **Add Stack**
2. **Web Editor**
3. Paste the docker-compose.yml above
4. **Deploy**

No build step = No "frame too large" error!

---

## What Changed

**Before:** Portainer tried to build the image → "frame too large" error
**Now:** Pre-built image → Just run → Works!

---

## File Changes Made

- Updated `Dockerfile` - Optimized file copying
- Updated `.dockerignore` - Exclude more unnecessary files
- Updated `docker-compose.yml` - Ready for pre-built image
- Created `build.sh` - One-command build script
- Created `TROUBLESHOOT_PORTAINER.md` - Full troubleshooting guide

---

## Which Host to Build On?

Build on whichever has Docker running:
- **Option A:** Your development machine, then copy image
- **Option B:** The Docker host (HS02 or wherever Docker runs)
- **Option C:** Pi3 or Ubuntu VM if they have Docker

The image will be available to all containers on that host.

---

## After Deployment

Once running in Portainer:

### Check Status
- **Stacks** → **mansion-radio-bot**
- All containers should be green ✓

### View Logs
- Click **mansion-radio-bot** container
- **Logs** tab

### Verify Bot is Working
- Join IRC channel `#radio`
- Wait for next song change (max 15 seconds)
- Should see: `♫ Now playing: Artist - Title (Album)`

---

## Need Different Configuration?

Once deployed, edit in Portainer:
1. **Stacks** → **mansion-radio-bot** → **Editor**
2. Change environment variables
3. **Update the stack**

Example changes:
```yaml
environment:
  - BOT_NICKNAME=MyCustomName
  - IRC_CHANNELS=#radio,#music
  - POLL_INTERVAL=30
```

---

## If You Still Have Issues

See `docs/TROUBLESHOOT_PORTAINER.md` for other solutions:
- Increase Docker frame size (system level)
- Manual build + push to registry
- Disable BuildKit

---

**Try the build.sh + pre-built image approach first - it's the most reliable!**

```bash
cd ~/projects/mansionradio
bash build.sh
```

Then deploy the compose file with `image: mansion-radio-bot:latest`
