# Portainer Deployment Guide

Deploy the MansionRadio Bot to Portainer without needing external `.env` files. This guide assumes you have Portainer running and are familiar with the UI.

---

## Prerequisites

- **Portainer:** Installed and running (version 2.0+)
- **Docker:** Available on the Portainer host
- **Network:** Host has access to IRC server and AzuraCast API

---

## Option 1: Deploy from Git Repository (Recommended)

This automatically syncs your code from GitHub.

### Step 1: In Portainer UI

**Navigate to:** Stacks → Add Stack

### Step 2: Select Repository

1. Choose **Repository** as the build method
2. Select **GitHub** (or your git provider)
3. Fill in:
   - **Repository URL:** `https://github.com/Pontuzz/mansionradio.git`
   - **Compose path:** `docker/docker-compose.example.yml`
   - **Auto-update:** ✅ (to sync new code)

### Step 3: Configure Environment Variables

Before deploying, add these environment variables in Portainer:

**Name:** `mansion-radio-bot`

Under "Environment variables" section, add:

```
IRC_SERVER=irc.example.com
IRC_PORT=6697
BOT_NICKNAME=MansionRadio
IRC_CHANNELS=#radio
SASL_USERNAME=your_account_name
SASL_PASSWORD=your_password
AZURACAST_API=https://radio.example.com/api/nowplaying/station_id
POLL_INTERVAL=60
LOG_LEVEL=INFO
TZ=UTC
```

### Step 4: Deploy

Click **Deploy the stack**

Wait for the build to complete. Expected time: 1-2 minutes.

---

## Option 2: Deploy from Web Editor (Quick Manual)

If you don't have git configured or want to deploy quickly.

### Step 1: Copy docker-compose File

Get the example docker-compose file from your workstation:

```bash
cat ~/projects/mansionradio/docker/docker-compose.example.yml
```

Or download/copy the raw file from: https://raw.githubusercontent.com/Pontuzz/mansionradio/main/docker/docker-compose.example.yml

### Step 2: In Portainer UI

**Navigate to:** Stacks → Add Stack

### Step 3: Paste Configuration

1. Choose **Web Editor**
2. Paste the entire `docker-compose.example.yml` content:

```yaml
version: '3.8'

services:
  mansion-radio-bot:
    image: mansion-radio-bot:latest
    container_name: mansion-radio-bot
    user: "1000:1000"
    restart: unless-stopped
    environment:
      # IRC Configuration
      - IRC_SERVER=irc.example.com
      - IRC_PORT=6697
      - BOT_NICKNAME=MansionRadio
      - IRC_CHANNELS=#radio
      # SASL authentication (for registered nicks)
      - SASL_USERNAME=your_sasl_username_here
      - SASL_PASSWORD=your_sasl_password_here
      # AzuraCast API
      - AZURACAST_API=https://radio.example.com/api/nowplaying/station_id
       # Polling interval (seconds)
       - POLL_INTERVAL=60
      # Logging (optional)
      - LOG_LEVEL=INFO
      # Timezone
      - TZ=UTC
    volumes:
      - ./logs:/app/logs
    networks:
      - mansion-net
    healthcheck:
      test: ["CMD", "pgrep", "-f", "src/main.py"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

networks:
  mansion-net:
    driver: bridge
```

> **⚠️ Relative volume paths on remote agents:** If deploying to a **remote** Portainer environment (agent endpoint), use an **absolute** host path for the logs volume (e.g. `/path/to/mansionradio/docker/logs:/app/logs`). Relative paths (`./logs`) resolve relative to where Portainer stores the compose file, not your project directory — a common source of confusion.

### Step 4: Edit Environment Variables

Update these values in the `environment` section to match your setup:

```yaml
environment:
  - IRC_SERVER=irc.example.com              # Your IRC server
  - IRC_PORT=6697                           # Usually 6697 (TLS) or 6667
  - BOT_NICKNAME=MansionRadio               # Bot nickname
  - IRC_CHANNELS=#radio                     # Channels (comma-separated)
  - SASL_USERNAME=your_account_name         # If using registered nick
  - SASL_PASSWORD=your_password             # SASL password
  - AZURACAST_API=https://radio.example... # Your AzuraCast API endpoint
   - POLL_INTERVAL=60                        # Seconds between checks
  - LOG_LEVEL=INFO                          # Logging level (optional)
  - TZ=UTC                                  # Timezone
```

### Step 5: Deploy

1. **Name:** `mansion-radio-bot`
2. Click **Deploy the stack**

---

## Option 3: Pre-Built Image (Fastest, No Build)

If you prefer to pre-build the image on your Docker host first.

### Step 1: Build Image on Host

SSH to your Docker host and build the image:

```bash
cd ~/projects/mansionradio
docker build -f docker/Dockerfile -t mansion-radio-bot:latest .

# Verify it was built
docker images | grep mansion-radio-bot
```

### Step 2: Update docker-compose.yml

In Portainer, use this simpler docker-compose.yml (it won't build, just uses the pre-built image):

```yaml
version: '3.8'

services:
  mansion-radio-bot:
    image: mansion-radio-bot:latest        # Uses pre-built image
    container_name: mansion-radio-bot
    user: "1000:1000"
    restart: unless-stopped
    environment:
      - IRC_SERVER=irc.example.com
      - IRC_PORT=6697
      - BOT_NICKNAME=MansionRadio
      - IRC_CHANNELS=#radio
      - SASL_USERNAME=your_account_name
      - SASL_PASSWORD=your_password
       - AZURACAST_API=https://radio.example.com/api/nowplaying/station_id
       - POLL_INTERVAL=60
       - LOG_LEVEL=INFO
       - TZ=UTC
    volumes:
      - ./logs:/app/logs
    networks:
      - mansion-net
    healthcheck:
      test: ["CMD", "pgrep", "-f", "src/main.py"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

networks:
  mansion-net:
    driver: bridge
```

### Step 3: Deploy

**Stacks** → **Add Stack** → Paste above → **Deploy the stack**

Deployment is instant (no build step needed).

---

## Verify Deployment

### Check Stack Status

1. **Portainer:** Stacks → **mansion-radio-bot**
2. Verify the container shows as **Running** (green status)

Expected:
```
Status: Running
Container: mansion-radio-bot (1)
```

### View Logs

1. Click the stack name → **mansion-radio-bot** container
2. Click **Logs** tab
3. Check "Auto-scroll" for real-time updates

Expected output:
```
[INFO] Starting MansionNET Radio Bot...
[INFO] RadioBot initialized
[INFO] Server: irc.example.com:6697
[INFO] Channels: #radio
[INFO] Poll interval: 15s
[INFO] Connected to IRC server
[INFO] Joined #radio
```

**Success indicator:** You should see "Joined #radio" (or whatever your channels are).

### Monitor Health

1. **Stacks** → **mansion-radio-bot**
2. Look for **Health Status: Healthy** (green checkmark)

The health check runs every 30 seconds to verify the bot is still running.

---

## Customizing Configuration

### Method 1: Edit Stack in Portainer (Recommended)

1. **Stacks** → **mansion-radio-bot** → **Editor**
2. Find the `environment:` section
3. Change values as needed
4. Click **Update the stack**

Example changes:
```yaml
environment:
  - BOT_NICKNAME=MyCustomName
  - IRC_CHANNELS=#radio,#music,#lounge
  - POLL_INTERVAL=30
```

The stack will restart with new settings immediately.

### Method 2: Edit docker-compose.yml Before Deployment

If the stack isn't running yet, just edit the compose file before clicking Deploy.

### Method 3: Use Portainer Environment Variables

Some Portainer setups support:
1. **Stacks** → **mansion-radio-bot** → **Settings**
2. Define custom variables
3. Reference with `${VARIABLE_NAME}` in compose file

---

## Stack Management

### Start Stack

**Stacks** → **mansion-radio-bot** → **Start**

Starts all containers in the stack.

### Stop Stack

**Stacks** → **mansion-radio-bot** → **Stop**

Gracefully stops the bot container.

### Restart Stack

**Stacks** → **mansion-radio-bot** → **Restart**

Restarts all containers (useful if bot gets stuck).

### Update Stack

**Stacks** → **mansion-radio-bot** → **Editor** → **Update the stack**

- If code changed (git repo): Rebuilds the image
- If only environment variables changed: Restarts with new config

### Delete Stack

**Stacks** → **mansion-radio-bot** → **Remove**

Choose:
- ✅ **Remove volume** - Deletes logs (if using volume mount)
- ❌ **Keep volume** - Preserves logs

### View Real-Time Logs

1. **Stacks** → **mansion-radio-bot** → container **mansion-radio-bot**
2. **Logs** tab
3. ✅ Check "Auto-scroll" for live updates

Press `Ctrl+C` or close to stop following logs.

---

## Monitoring & Maintenance

### Check Container Stats

1. **Containers** → Find **mansion-radio-bot**
2. Click it, then **Stats** tab

Expected resource usage:
- **Memory:** 40-100 MB
- **CPU:** 0-5% (idle most of the time)
- **Network:** Minimal (one announcement per song change)

### View Event History

1. **Stacks** → **mansion-radio-bot**
2. Click **Events** tab

Shows when containers started, stopped, restarted, etc.

### Update Image

If you've pushed a new image to Docker Hub:

1. **Images** → **Pull image**
2. Enter `mansion-radio-bot:latest`
3. Then update the stack (will use new image)

---

## Troubleshooting

### Container won't start / stays in "Not running" state

**Check the logs:**
1. **Stacks** → **mansion-radio-bot** → container
2. **Logs** tab
3. Look for error messages

**Common issues:**

- **"IRC server not reachable"**
  - Verify `IRC_SERVER` and `IRC_PORT` are correct
  - Test from host: `nc -zv irc.example.com 6697`

- **"SASL authentication failed"**
  - Verify `SASL_USERNAME` and `SASL_PASSWORD`
  - Try disabling SASL temporarily (set `SASL_PASSWORD=""`)

- **"API connection failed"**
  - Check `AZURACAST_API` URL is correct
  - Test: `curl https://radio.example.com/api/nowplaying/station_id`

### Bot connects but doesn't announce songs

**Check API connectivity:**
```bash
# From Portainer host
curl https://radio.example.com/api/nowplaying/station_id | head -20
```

**Check logs for API errors:**
1. **Stacks** → **mansion-radio-bot** → **Logs**
2. Search for "error" or "exception"

**Verify bot joined the channel:**
- Join the IRC channel manually
- You should see the bot in the user list

### Health check failing

If Health Status shows "Unhealthy":

1. **Stacks** → **mansion-radio-bot** → **Restart** to try recovering
2. Check logs for crash indicators
3. Increase `start_period` in docker-compose if bot needs more time to start:
   ```yaml
   healthcheck:
     start_period: 30s  # Increased from 10s
   ```

### High memory usage

**Check stats:**
1. **Containers** → **mansion-radio-bot** → **Stats**

If >200MB:
- Restart the container (**Restart** button)
- Check for memory leaks in logs
- Rebuild image: delete stack and redeploy with fresh image

### Need to rebuild image

If you've updated code (from git):

1. **Stacks** → **mansion-radio-bot** → **Editor**
2. Make any trivial change (e.g., add/remove whitespace)
3. **Update the stack**
4. Portainer will rebuild the image from git

Or delete and redeploy:
1. **Remove** the stack (keeping or removing volume as needed)
2. **Add Stack** again with updated configuration

---

## Advanced Configuration

### Multiple Instances for Different Networks

Create separate stacks for different IRC networks:

**Stack 1: LibreChat**
```yaml
services:
  mansion-radio-bot-libera:
    image: mansion-radio-bot:latest
    environment:
      - IRC_SERVER=irc.libera.chat
      - BOT_NICKNAME=RadioBot1
      # ... other settings
```

**Stack 2: Undernet**
```yaml
services:
  mansion-radio-bot-undernet:
    image: mansion-radio-bot:latest
    environment:
      - IRC_SERVER=irc.undernet.org
      - BOT_NICKNAME=RadioBot2
      # ... other settings
```

Manage each separately in Portainer.

### Persistent Logs

The compose file includes volume mount for logs:
```yaml
volumes:
  - ./logs:/app/logs
```

Logs are stored on the host in `./logs/` directory (relative to docker-compose location).

### Network Troubleshooting

To debug network issues from within the container:

1. **Containers** → **mansion-radio-bot**
2. **Exec Console** tab
3. Run commands in container:
   ```bash
   nslookup irc.example.com
   nc -zv irc.example.com 6697
   curl https://radio.example.com/api/nowplaying/station_id
   ```

---

## Next Steps

1. ✅ Deploy stack (via git or web editor)
2. ✅ Configure environment variables
3. ✅ Verify bot connects to IRC
4. ✅ Wait for first song announcement (max 60 seconds with production settings)
5. ✅ Monitor logs regularly

**Need Docker build troubleshooting?** See [TROUBLESHOOT_PORTAINER.md](TROUBLESHOOT_PORTAINER.md)

**Need general Docker help?** See [DEPLOY_DOCKER.md](DEPLOY_DOCKER.md)

**Need bare metal deployment?** See [DEPLOY_BAREMETAL.md](DEPLOY_BAREMETAL.md)
