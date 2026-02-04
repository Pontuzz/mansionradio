# Building Docker Image Locally

Since building on WSL2 is slow, here's how to build the image on your actual Docker host (Pi3, Ubuntu VM, or wherever Docker runs).

---

## Option A: Copy Files & Build on Docker Host

### Step 1: Copy project to Docker host

```bash
# From your WSL2 machine
scp -r ~/projects/mansionradio user@docker-host:~/

# Example for Pi3:
scp -r ~/projects/mansionradio user@pi3:~/
```

### Step 2: SSH into Docker host and build

```bash
# SSH into the host
ssh user@docker-host

# Navigate to project
cd ~/mansionradio

# Build the image
docker build -t mansion-radio-bot:latest .

# Verify it built
docker images | grep mansion-radio-bot
```

You should see:
```
REPOSITORY              TAG       IMAGE ID       SIZE
mansion-radio-bot       latest    <hash>         ~250MB
```

---

## Option B: Use Portainer's Built-In Builder (After Fix)

If your Portainer has access to the Docker daemon properly configured:

1. **Stacks** → **Add Stack** → **Upload**
2. Upload the entire `mansionradio` folder
3. Set compose path to `docker-compose.yml`
4. It will build the image using Docker daemon

---

## What Happens During Build

The build process:
1. Downloads Python 3.11 Alpine base image (~50MB)
2. Installs system dependencies (gcc, musl-dev, linux-headers)
3. Installs Python dependencies from requirements.txt (~20MB)
4. Copies application code (~50KB)
5. Creates non-root user for security
6. Final image size: ~250MB

**Time:** 3-5 minutes on a typical machine

---

## After Image is Built

Once built, you have two options:

### For Portainer Deployment (Recommended):

Use this docker-compose.yml:

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

Then deploy in Portainer - **no build step** since image is already built.

### For Direct Docker Compose:

```bash
docker-compose up -d
docker-compose logs -f
```

---

## Testing the Image

Before deploying to Portainer, test it:

```bash
# Run the container
docker run -it --rm \
  -e IRC_SERVER=irc.inthemansion.com \
  -e IRC_PORT=6697 \
  -e BOT_NICKNAME=MansionRadio \
  -e IRC_CHANNELS=#radio \
  -e AZURACAST_API=https://radio.inthemansion.com/api/nowplaying/mansionnet \
  -e POLL_INTERVAL=15 \
  mansion-radio-bot:latest
```

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

Press `Ctrl+C` to stop.

---

## If Build Fails

Check Docker logs:

```bash
# Check Docker daemon
docker info

# Try rebuilding with verbose output
docker build -t mansion-radio-bot:latest --progress=plain ~/mansionradio

# Check system resources
free -h
df -h
```

---

## Quick Summary

1. Copy `~/projects/mansionradio` to Docker host
2. Run: `docker build -t mansion-radio-bot:latest .`
3. Wait 3-5 minutes
4. Verify: `docker images | grep mansion-radio-bot`
5. Use pre-built image in Portainer
6. Deploy: No build errors!

---

**Which host should I build on?** (Reply with: Pi3, VM, or other)

That way I can give you exact SSH commands if needed.
