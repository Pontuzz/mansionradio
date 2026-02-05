# Portainer Deployment Troubleshooting

## "Frame Too Large" Error

If you get this error when deploying:
```
compose build operation failed: listing workers for Build: 
failed to list workers: Unavailable: connection error: 
error reading server preface: http2: failed reading the frame payload: 
http2: frame too large
```

This is a Buildkit/Docker daemon issue. Here are the solutions:

---

## Solution 1: Use Pre-Built Image (Fastest)

Instead of building the image in Portainer, use a pre-built image from Docker Hub.

**Updated docker-compose.yml:**

```yaml
version: '3.8'

services:
  mansion-radio-bot:
    image: mansion-radio-bot:latest  # Use pre-built image
    container_name: mansion-radio-bot
    restart: unless-stopped
    environment:
      - IRC_SERVER=irc.example.com
      - IRC_PORT=6697
      - BOT_NICKNAME=MansionRadio
      - IRC_CHANNELS=#radio
      - AZURACAST_API=https://radio.example.com/api/nowplaying/station_id
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

**Then build the image once on the host:**

```bash
# On the Docker host (not in Portainer)
cd ~/projects/mansionradio
docker build -t mansion-radio-bot:latest .

# Verify
docker images | grep mansion-radio-bot
```

**Then deploy in Portainer** - it will use the pre-built image (no build step).

---

## Solution 2: Increase Docker Daemon Frame Size (System Level)

If you want to keep building in Portainer, increase the Docker daemon's frame size.

**On the host running Docker:**

1. **Edit Docker daemon config:**
   ```bash
   sudo nano /etc/docker/daemon.json
   ```

2. **Add or modify:**
   ```json
   {
     "default-runtime": "runc",
     "log-driver": "json-file",
     "log-opts": {
       "max-size": "10m",
       "max-file": "5"
     },
     "experimental": true,
     "features": {
       "buildkit": false
     }
   }
   ```

3. **Restart Docker:**
   ```bash
   sudo systemctl restart docker
   ```

4. **Try deploying in Portainer again**

---

## Solution 3: Manual Build & Push to Registry

**Step 1: Build locally**
```bash
cd ~/projects/mansionradio
docker build -t mansion-radio-bot:latest .
```

**Step 2: Push to registry** (if you have one)
```bash
docker tag mansion-radio-bot:latest your-registry/mansion-radio-bot:latest
docker push your-registry/mansion-radio-bot:latest
```

**Step 3: Update docker-compose to use pushed image**
```yaml
services:
  mansion-radio-bot:
    image: your-registry/mansion-radio-bot:latest
    # ... rest of config
```

**Step 4: Deploy in Portainer** (no build, just run)

---

## Solution 4: Use Stack Deploy Mode Instead of Compose

Some Portainer versions have issues with `docker-compose build`. Try using **Stack Mode** instead:

1. In Portainer: **Stacks** → **Add Stack**
2. Choose: **Stack mode** (not Compose)
3. Use the standard docker-compose.yml
4. It may bypass the build issue

---

## Recommended: Solution 1 (Pre-Built Image)

This is the cleanest approach:

**Step 1: Build image once on the host**
```bash
ssh user@docker-host
cd ~/projects/mansionradio
docker build -t mansion-radio-bot:latest .
```

**Step 2: Use this docker-compose.yml in Portainer**
```yaml
version: '3.8'

services:
  mansion-radio-bot:
    image: mansion-radio-bot:latest
    container_name: mansion-radio-bot
    restart: unless-stopped
    environment:
      - IRC_SERVER=irc.example.com
      - IRC_PORT=6697
      - BOT_NICKNAME=MansionRadio
      - IRC_CHANNELS=#radio
      - AZURACAST_API=https://radio.example.com/api/nowplaying/station_id
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

**Step 3: Deploy in Portainer**
- No build errors
- Instant deployment
- Same functionality

---

## Quick Summary

| Solution | Effort | Reliability | Recommendation |
|----------|--------|-------------|---|
| Pre-built image | 5 min | ★★★★★ | ⭐ Best |
| Increase frame size | 10 min | ★★★☆☆ | Okay |
| Manual build+push | 15 min | ★★★★☆ | Good |
| Disable BuildKit | 5 min | ★★☆☆☆ | Risky |

**Use Solution 1 (Pre-built Image)** - it's the most reliable.
