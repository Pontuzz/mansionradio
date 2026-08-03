# Portainer & Docker Troubleshooting Guide

This guide helps you diagnose and fix common Docker and Portainer issues when deploying the MansionRadio Bot.

---

## General Diagnostics

### Get Basic Information

Before troubleshooting, gather information about your deployment:

**In Portainer:**
1. **Stacks** → **mansion-radio-bot** → **mansion-radio-bot** container
2. Record:
   - **Status:** Running? Exited? Restarting?
   - **Port Bindings:** Any exposed ports?
   - **Environment:** What variables are set?
   - **Logs:** Any error messages?

**From host terminal:**
```bash
# See all containers
docker ps -a | grep mansion

# Check logs
docker logs mansion-radio-bot

# Check resource usage
docker stats mansion-radio-bot --no-stream

# Inspect container configuration
docker inspect mansion-radio-bot
```

---

## Issue: "Frame Too Large" Error During Build

### Symptoms

When deploying in Portainer, you see:
```
compose build operation failed: listing workers for Build: 
failed to list workers: Unavailable: connection error: 
error reading server preface: http2: failed reading the frame payload: 
http2: frame too large
```

This is a Buildkit/Docker daemon issue with large build contexts.

---

## Solution 1: Use Pre-Built Image (Fastest ⭐ Recommended)

Instead of building in Portainer, build once on the Docker host.

### Step 1: Build Image on Host

SSH to your Docker host:

```bash
cd ~/projects/mansionradio

# Build the image
docker build -f docker/Dockerfile -t mansion-radio-bot:latest .

# Verify it built successfully
docker images | grep mansion-radio-bot
```

Expected output:
```
REPOSITORY              TAG       IMAGE ID      CREATED        SIZE
mansion-radio-bot       latest    abc1234def    2 minutes ago   98MB
```

### Step 2: Use Pre-Built Image in Portainer

In the docker-compose.yml, use the pre-built image:

```yaml
version: '3.8'

services:
  mansion-radio-bot:
    image: mansion-radio-bot:latest     # Uses pre-built image
    container_name: mansion-radio-bot
    restart: unless-stopped
    environment:
      - IRC_SERVER=irc.example.com
      - IRC_PORT=6697
      - BOT_NICKNAME=MansionRadio
      - IRC_CHANNELS=#radio
      - SASL_USERNAME=your_account_name
      - SASL_PASSWORD=your_password
      - AZURACAST_API=https://radio.example.com/api/nowplaying/station_id
      - POLL_INTERVAL=15
      - TZ=UTC
    volumes:
      - ./logs:/app/logs
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

**Important:** Remove any `build:` section—just use `image:`.

### Step 3: Deploy in Portainer

1. **Stacks** → **Add Stack**
2. Paste the above docker-compose.yml
3. Click **Deploy the stack**

✅ **Instant deployment—no build step!**

### Updating the Image Later

When you have new code:

```bash
# On the Docker host
cd ~/projects/mansionradio
docker build -f docker/Dockerfile -t mansion-radio-bot:latest .

# Then redeploy in Portainer (it will pull the new image)
```

---

## Solution 2: Disable BuildKit

If you need to build in Portainer and Solution 1 isn't viable:

### Step 1: Edit Docker Daemon Config

On the Docker host:

```bash
sudo nano /etc/docker/daemon.json
```

Add or modify the `buildkit` setting:

```json
{
  "default-runtime": "runc",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "5"
  },
  "features": {
    "buildkit": false
  }
}
```

### Step 2: Restart Docker

```bash
sudo systemctl restart docker

# Verify Docker is running
sudo systemctl status docker
```

### Step 3: Retry Portainer Deployment

Go back to Portainer and try deploying the stack again.

⚠️ **Note:** This may be slower but avoids the frame size issue.

---

## Solution 3: Reduce Build Context

Minimize the files Docker sends during build:

### Update .dockerignore

Create or update `docker/.dockerignore`:

```
.git
.gitignore
.github
docs/
systemd/
scripts/
*.md
.pytest_cache
__pycache__
*.pyc
.venv
venv
docker/docker-compose*.yml
```

This reduces the build context from ~1MB to <100KB.

### Rebuild in Portainer

1. **Stacks** → **mansion-radio-bot** → **Editor**
2. Make a minor change (e.g., add/remove whitespace)
3. **Update the stack**

---

## Issue: Container Won't Start

### Symptom

**Status:** "Exited" or "Restarting" repeatedly

### Diagnosis

**Check the logs:**

1. **Portainer:** Stacks → **mansion-radio-bot** → container → **Logs** tab
2. **Or from host:**
   ```bash
   docker logs mansion-radio-bot
   # Or follow logs in real-time
   docker logs -f mansion-radio-bot
   ```

### Common Causes & Fixes

#### A. "No such file or directory: /app/src/main.py"

The image was built with old code. The `Dockerfile` should copy `src/` into the image.

**Check Dockerfile:**
```bash
grep -n "COPY\|src" ~/projects/mansionradio/docker/Dockerfile
```

Should show:
```
COPY src/ ./src
```

**Fix:** Rebuild the image:
```bash
cd ~/projects/mansionradio
docker build --no-cache -f docker/Dockerfile -t mansion-radio-bot:latest .
```

Then redeploy in Portainer.

#### B. "ModuleNotFoundError: No module named 'irc'"

Dependencies aren't installed in the image.

**Check Dockerfile:**
```bash
grep -n "pip install" ~/projects/mansionradio/docker/Dockerfile
```

Should show:
```
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt
```

**Fix:** Rebuild without cache:
```bash
cd ~/projects/mansionradio
docker build --no-cache -f docker/Dockerfile -t mansion-radio-bot:latest .
```

#### C. "Cannot connect to IRC server"

The bot started but can't reach the IRC server.

**Check the logs for:** `Failed to connect` or `Connection refused`

**Diagnostics:**

From the Docker host:
```bash
# Test DNS resolution
docker run -it mansion-radio-bot:latest nslookup irc.example.com

# Test port connectivity
docker run -it mansion-radio-bot:latest nc -zv irc.example.com 6697
```

**Fixes:**
- Verify `IRC_SERVER` and `IRC_PORT` are correct in environment variables
- Check firewall on Docker host allows outbound to that server
- Verify the IRC server is actually running and accessible

#### D. "SASL authentication failed"

The bot connected but SASL credentials are wrong.

**Check logs for:** `SASL authentication failed (904)`

**Diagnostics:**
```bash
# Verify credentials
docker inspect mansion-radio-bot | grep -A 20 "Env"
# Look for SASL_USERNAME and SASL_PASSWORD
```

**Fixes:**
- Verify `SASL_USERNAME` and `SASL_PASSWORD` are correct
- The username should be the account that owns the registered nick
- Try temporarily disabling SASL (set `SASL_PASSWORD=""`) to isolate the issue
- Make sure the account is actually registered on the IRC server

#### E. "RuntimeError: address already in use"

Another container is using the same port (unlikely unless you mapped ports).

**Check if this bot has port mappings:**

In Portainer: **Stacks** → **mansion-radio-bot** → Look for **Ports**

If there are ports listed, try:
```bash
# Check what's using that port
sudo lsof -i :6697  # Replace 6697 with your port
# Kill the conflicting process if needed
sudo kill -9 <PID>
```

Or change the port mapping in docker-compose.yml.

---

## Issue: Bot Connects But Doesn't Announce Songs

### Symptoms

- Bot appears in IRC channel ✅
- No song announcements appear ❌
- Logs show no errors ❌

### Diagnosis

The bot is alive but the polling or announcement logic isn't working.

**Check logs for API calls:**

```bash
docker logs mansion-radio-bot | grep -i "api\|poll\|azura\|nowplaying"
```

### Possible Causes & Fixes

#### A. API Endpoint is Wrong

**Check the logs:**
```bash
docker logs mansion-radio-bot | head -20
# Look for "AZURACAST_API=" line
```

**Test the API from the host:**
```bash
curl https://radio.example.com/api/nowplaying/station_id | head -20
# Should return JSON with song data
```

**Fix:** Verify `AZURACAST_API` in environment variables is exact and working.

#### B. API is Down or Unreachable

**Test from inside the container:**
```bash
docker exec mansion-radio-bot curl https://radio.example.com/api/nowplaying/station_id
```

**If it fails:**
- Check the API server is running
- Check firewall allows container outbound to the API server
- Check DNS from the container can resolve the domain

#### C. Bot Joined Wrong Channel

**Check logs:**
```bash
docker logs mansion-radio-bot | grep -i "join"
```

Should show: `[INFO] Joined #radio` (or whatever your channels are)

**If it doesn't show joined:**
- Check `IRC_CHANNELS` environment variable is set correctly
- Check bot has permission to join the channel (some channels are locked)
- Check bot's nick isn't already banned

#### D. No Song Changes to Announce

The bot is working but the song hasn't changed.

**Check logs for poll activity:**
```bash
docker logs mansion-radio-bot | grep -i "poll\|checking\|song"
```

**If you see poll activity:**
- Wait for an actual song change on the radio station
- Songs may not change for 30+ minutes if it's a long song
- Manually test by changing the song in AzuraCast

**If you see no poll activity:**
- The scheduler-based poll may not be running
- Check for errors in the logs
- Try restarting: **Stacks** → **mansion-radio-bot** → **Restart**

---

## Issue: High Memory Usage

### Symptom

Container using >200MB memory (expected: 40-100MB)

### Diagnosis

**Check resource usage:**

**In Portainer:**
1. **Containers** → **mansion-radio-bot** → **Stats** tab
2. Look at **Memory** (current and limit)

**From host:**
```bash
docker stats mansion-radio-bot --no-stream
```

### Possible Causes & Fixes

#### A. Memory Leak in Bot Code

Check if memory grows over time:

```bash
# Monitor memory every 5 seconds for 1 minute
for i in {1..12}; do docker stats mansion-radio-bot --no-stream | grep Memory; sleep 5; done
```

If memory keeps growing: There's likely a memory leak.

**Workaround:** Restart regularly with a cron job:
```bash
# Restart every 6 hours
0 */6 * * * docker restart mansion-radio-bot
```

#### B. Bloated Image

Rebuild with cache cleared:

```bash
cd ~/projects/mansionradio
docker build --no-cache -f docker/Dockerfile -t mansion-radio-bot:latest .
```

#### C. Resource Limit Set Too High

Check if you've set memory limits in docker-compose.yml:

```yaml
services:
  mansion-radio-bot:
    # ... other settings
    deploy:
      resources:
        limits:
          memory: 512m  # If this is high, lower it
```

---

## Issue: Health Check Failing

### Symptom

**Health Status:** Unhealthy (red) or Warning (yellow)

### Diagnosis

**Check what the health check is doing:**

In docker-compose.yml:
```yaml
healthcheck:
  test: ["CMD", "pgrep", "-f", "python src/main.py"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 10s
```

This checks if the Python process is still running.

**Check the status:**
```bash
docker inspect mansion-radio-bot --format='{{json .State.Health}}' | jq
```

Output shows: `Status`, `FailingStreak`, `Log`

### Possible Causes & Fixes

#### A. Bot Crashed or Exited

**Check if the container is still running:**
```bash
docker ps | grep mansion-radio-bot
# Should show the container; if not, it exited
```

**Check logs for crash:**
```bash
docker logs mansion-radio-bot | tail -50
```

**Fix:** Look at the error and fix the underlying issue (see "Container Won't Start" section above)

#### B. Health Check Timeout Too Short

The bot is fine but the check times out.

Increase the timeout in docker-compose.yml:
```yaml
healthcheck:
  timeout: 30s  # Increased from 10s
```

Then redeploy.

#### C. `pgrep` Not Available in Image

The health check command `pgrep` might not be installed.

**Test from inside the container:**
```bash
docker exec mansion-radio-bot pgrep -f "python src/main.py"
# Should return a PID number; if error, pgrep isn't available
```

**Alternate health check:**
```yaml
healthcheck:
  test: ["CMD", "ps", "aux"]  # Generic ps command
```

---

## Issue: Logs Not Appearing

### Symptom

Container is running but **Logs** tab shows nothing or old logs

### Diagnosis

**Check if bot is actually running:**
```bash
docker exec mansion-radio-bot ps aux | grep main.py
```

If it shows a process, the bot is running.

### Possible Causes & Fixes

#### A. Bot Runs but Produces No Output

The bot might not be logging anything.

**Check main.py logging configuration:**
```bash
grep -n "logging" ~/projects/mansionradio/src/main.py | head -10
```

Should show logging is configured to stdout.

**If logging is off:** Edit src/main.py and ensure logging is enabled, rebuild image.

#### B. Logs Are Being Written to a File Instead

**Check if bot writes to files:**
```bash
docker exec mansion-radio-bot ls -la /app/logs/
# If files exist here, logs aren't going to stdout
```

**Fix:** Update the bot to log to stdout, rebuild image.

#### C. Volume Mount Issues

**If using log volume:**
```yaml
volumes:
  - ./logs:/app/logs
```

Check the host has the `logs/` directory:
```bash
ls -la logs/
```

If the directory doesn't exist, Docker creates it but with different permissions.

**Fix:** Create directory first:
```bash
mkdir -p logs
chmod 777 logs
```

---

## Issue: Can't Connect to Portainer UI

### Symptom

Can't reach Portainer at `http://localhost:9000` (or your URL)

### Diagnosis

**Check if Portainer container is running:**
```bash
docker ps | grep portainer
```

Should show a running `portainer/portainer-ce` or similar container.

### Possible Causes & Fixes

#### A. Portainer Container Exited

**Check status:**
```bash
docker ps -a | grep portainer
```

**Restart it:**
```bash
docker start portainer  # Or whatever the container is named
```

#### B. Port Not Mapped

**Check port mapping:**
```bash
docker inspect portainer | grep -A 5 PortBindings
```

Should show something like `9000/tcp` → `0.0.0.0:9000`

#### C. Firewall Blocking

**Check if the port is open:**
```bash
sudo ufw status | grep 9000
# Or check iptables, depending on your firewall
```

**If blocked:** Open the port:
```bash
sudo ufw allow 9000
```

---

## Issue: Container Keeps Restarting

### Symptom

Container shows **Restarting** in Portainer and in `docker ps`

### Diagnosis

**Check restart policy:**
```bash
docker inspect mansion-radio-bot --format='{{.HostConfig.RestartPolicy}}'
```

Should show `RestartPolicy:{Name:unless-stopped MaximumRetryCount:0}` or similar.

**Check why it keeps exiting:**
```bash
docker logs mansion-radio-bot | tail -30
```

### Possible Causes & Fixes

Refer to the "Container Won't Start" section above—the bot is exiting immediately, then Docker restarts it.

Most likely causes:
- Missing dependencies (rebuild image)
- Missing .env file or bad configuration (set environment variables)
- API unreachable (check network access)
- IRC server unreachable (check network access)

**Quick test:**
```bash
# Run with better error visibility
docker run --rm -it \
  -e IRC_SERVER=irc.example.com \
  -e IRC_PORT=6697 \
  -e BOT_NICKNAME=TestBot \
  -e IRC_CHANNELS="#test" \
  -e AZURACAST_API="https://radio.example.com/api/nowplaying/station_id" \
  -e POLL_INTERVAL=15 \
  mansion-radio-bot:latest
```

Any error messages will be shown directly.

---

## Debugging from Container Shell

Sometimes you need to run commands inside the container:

```bash
# Interactive shell inside the running container
docker exec -it mansion-radio-bot /bin/sh

# Once inside:
ps aux              # Check running processes
env                 # Check environment variables
ls -la /app         # Check what files are there
curl https://...    # Test API connectivity
nc -zv host port    # Test network connectivity
```

---

## Checking Docker and System Resources

### Disk Space

```bash
df -h
# Ensure Docker has enough space for images
```

### Docker System Info

```bash
docker system df
# Shows disk usage by images, containers, volumes
```

### Clean Up Old Images/Containers

```bash
# Remove unused images
docker image prune

# Remove stopped containers
docker container prune

# Remove unused volumes
docker volume prune

# Complete cleanup (careful!)
docker system prune -a
```

---

## Getting Help

If you're stuck, gather diagnostic information:

```bash
# Save diagnostic info to a file
{
  echo "=== Docker Version ==="
  docker --version
  
  echo "=== Container Info ==="
  docker ps -a | grep mansion
  docker inspect mansion-radio-bot
  
  echo "=== Logs ==="
  docker logs mansion-radio-bot | tail -100
  
  echo "=== System Info ==="
  uname -a
  docker system df
  
} > mansion-radio-bot-diagnostics.txt

cat mansion-radio-bot-diagnostics.txt
```

Then check:
1. **Logs** for actual error messages
2. **Network** (can the host reach IRC/API servers?)
3. **Configuration** (are environment variables set correctly?)
4. **Image** (was it built recently with current code?)

---

## Reference: Useful Docker Commands

```bash
# View logs
docker logs mansion-radio-bot
docker logs -f mansion-radio-bot              # Follow (real-time)
docker logs --tail 50 mansion-radio-bot       # Last 50 lines

# Container info
docker ps                                      # Running containers
docker ps -a                                   # All containers
docker inspect mansion-radio-bot               # Detailed info
docker stats mansion-radio-bot                 # Resource usage

# Control container
docker start mansion-radio-bot
docker stop mansion-radio-bot
docker restart mansion-radio-bot
docker rm mansion-radio-bot                    # Delete stopped container

# Execute commands inside
docker exec -it mansion-radio-bot /bin/sh     # Interactive shell
docker exec mansion-radio-bot env             # Show environment variables

# Image management
docker images | grep mansion                   # List images
docker build -f docker/Dockerfile -t mansion-radio-bot:latest .  # Build
docker image rm mansion-radio-bot:latest      # Delete image
```

---

**Still stuck?** Check [DEPLOY_DOCKER.md](DEPLOY_DOCKER.md) for Docker fundamentals or [DEPLOY_PORTAINER.md](DEPLOY_PORTAINER.md) for Portainer basics.
