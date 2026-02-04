# Deployment to HS01 via Portainer

HS01 has both Docker and Portainer running. Here's the exact process:

---

## Step 1: Copy Project to HS01

From your WSL2 machine:

```bash
# Copy the project to HS01
scp -r ~/projects/mansionradio user@hs01:~/

# Or if using IP directly:
scp -r ~/projects/mansionradio user@192.168.1.20:~/
```

Replace `user` with your HS01 username.

---

## Step 2: SSH into HS01 and Build Image

```bash
# SSH into HS01
ssh user@hs01

# Navigate to project
cd ~/mansionradio

# Build the Docker image
docker build -t mansion-radio-bot:latest .

# Verify the image was created
docker images | grep mansion-radio-bot
```

Expected output:
```
REPOSITORY              TAG       IMAGE ID       CREATED        SIZE
mansion-radio-bot       latest    abc123def456   2 minutes ago   ~250MB
```

---

## Step 3: Deploy in Portainer on HS01

### Option A: Using docker-compose.yml (Easiest)

1. In Portainer UI (on HS01): **Stacks** → **Add Stack**
2. Choose: **Web Editor**
3. Paste this docker-compose.yml:

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

4. **Name:** `mansion-radio-bot`
5. **Deploy the stack**

### Option B: Upload Files (Alternative)

1. **Stacks** → **Add Stack** → **Upload**
2. Upload the `mansionradio` folder
3. It will use the local docker-compose.yml
4. Deploy

---

## Step 4: Verify Deployment

In Portainer on HS01:

1. Go to **Stacks** → **mansion-radio-bot**
2. All containers should be **green** (running)
3. Click **mansion-radio-bot** container
4. Check **Logs** tab

Expected logs:
```
[INFO] Starting MansionNET Radio Bot...
[INFO] RadioBot initialized
[INFO] Server: irc.inthemansion.com:6697
[INFO] Channels: #radio
[INFO] Poll interval: 15s
[INFO] Connected to IRC server
[INFO] Joined #radio
[ANNOUNCE] #radio: ♫ Now playing: Artist - Title (Album)
```

---

## Step 5: Test in IRC

1. Join IRC channel `#radio` on `irc.inthemansion.com:6697`
2. Wait for next song change (max 15 seconds)
3. Bot should announce: `♫ Now playing: Artist - Title (Album)`

---

## Customizing Configuration (Optional)

If you need to change settings later:

1. In Portainer: **Stacks** → **mansion-radio-bot** → **Editor**
2. Modify environment variables:
   ```yaml
   - BOT_NICKNAME=CustomName
   - IRC_CHANNELS=#radio,#music
   - POLL_INTERVAL=30
   ```
3. **Update the stack**

---

## Management Commands (SSH on HS01)

```bash
# Check if image exists
docker images | grep mansion-radio-bot

# List running containers
docker ps

# View container logs
docker logs -f mansion-radio-bot

# Stop container
docker stop mansion-radio-bot

# Start container
docker start mansion-radio-bot

# Remove container (if deployed outside Portainer)
docker rm mansion-radio-bot

# Remove image (if no longer needed)
docker rmi mansion-radio-bot:latest
```

---

## Troubleshooting

### Image not found when deploying
```bash
# SSH into HS01 and verify image exists
docker images | grep mansion-radio-bot

# If missing, rebuild:
cd ~/mansionradio
docker build -t mansion-radio-bot:latest .
```

### Container won't start
```bash
# Check container logs
docker logs mansion-radio-bot

# View detailed logs
docker inspect mansion-radio-bot
```

### IRC connection fails
- Verify `IRC_SERVER` and `IRC_PORT` in environment variables
- Test from HS01: `nc -zv irc.inthemansion.com 6697`

### API connection fails
```bash
# Test API from HS01
curl https://radio.inthemansion.com/api/nowplaying/mansionnet | head -20
```

---

## Quick Command Summary

```bash
# Copy to HS01
scp -r ~/projects/mansionradio user@hs01:~/

# Build on HS01
ssh user@hs01
cd ~/mansionradio
docker build -t mansion-radio-bot:latest .

# Deploy in Portainer UI
# Stacks → Add Stack → Web Editor → Paste docker-compose.yml → Deploy
```

---

## Complete Flow Checklist

- [ ] Copy project to HS01: `scp -r ~/projects/mansionradio user@hs01:~/`
- [ ] SSH to HS01: `ssh user@hs01`
- [ ] Build image: `docker build -t mansion-radio-bot:latest ~/mansionradio`
- [ ] Verify: `docker images | grep mansion-radio-bot`
- [ ] Open Portainer on HS01
- [ ] Create stack: **Stacks** → **Add Stack**
- [ ] Paste docker-compose.yml with `image: mansion-radio-bot:latest`
- [ ] Deploy stack
- [ ] Check logs in Portainer
- [ ] Test in IRC: Join `#radio` on `irc.inthemansion.com:6697`
- [ ] ✅ Done!

---

**Ready? Run these commands and report back!**
