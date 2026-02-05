# Bare Metal Deployment Guide

Deploy the MansionRadio Bot directly on a machine (Pi3, Ubuntu VM, etc.) without Docker, using systemd for management—similar to eggdrop deployment.

---

## Prerequisites

- **OS:** Ubuntu 20.04+, Debian 11+, or Raspberry Pi OS
- **Python:** 3.9 or higher
- **Privileges:** Sudo access (for systemd setup)
- **User:** Dedicated `radiobot` user (recommended)
- **Network:** Access to your IRC server and AzuraCast API

### Verify Python Version

```bash
python3 --version
# Should be 3.9+; if not, install Python 3.11
```

**If you need Python 3.11 on Ubuntu:**
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip
```

**If you need Python 3.11 on Raspberry Pi OS:**
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv
```

---

## Installation Steps

### Step 1: Create Dedicated User (Recommended)

```bash
# Create radiobot user with home directory
sudo useradd -m -s /bin/bash -d /home/radiobot radiobot

# Switch to the new user
sudo su - radiobot
```

From this point on, run commands as the `radiobot` user.

### Step 2: Copy Project to Target Machine

**From your workstation:**
```bash
scp -r ~/projects/mansionradio user@pi3:~/mansion-radio-bot
```

**Or SSH and clone:**
```bash
ssh radiobot@pi3
git clone https://github.com/Pontuzz/mansionradio.git ~/mansion-radio-bot
```

**Or manually:**
```bash
ssh radiobot@pi3
mkdir -p ~/mansion-radio-bot
# Upload files via SFTP or other means
```

### Step 3: Navigate to Project and Verify

```bash
cd ~/mansion-radio-bot

# Verify project structure
ls -la
# Should show: src/, docker/, scripts/, config/, docs/, systemd/, requirements.txt, etc.
```

### Step 4: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Verify activation (prompt should show (venv))
which python
# Should show: /home/radiobot/mansion-radio-bot/venv/bin/python
```

### Step 5: Install Dependencies

```bash
# Ensure pip is up to date
pip install --upgrade pip

# Install required packages from requirements.txt
pip install -r requirements.txt

# Verify installation
python -c "import irc.bot; print('irc library OK')"
```

### Step 6: Configure Environment Variables

```bash
# Copy the example config
cp config/.env.example .env

# Edit with your settings
nano .env
```

Set these variables in `.env`:

```bash
# IRC Server Configuration
IRC_SERVER=irc.example.com              # Your IRC server
IRC_PORT=6697                           # Usually 6697 (TLS) or 6667 (plain)
BOT_NICKNAME=MansionRadio               # Bot's nickname
IRC_CHANNELS="#radio,#music"            # Channels to join (comma-separated)

# SASL Authentication (optional)
SASL_USERNAME=your_account_name         # If using account-based auth
SASL_PASSWORD=your_sasl_password        # Account password

# AzuraCast API
AZURACAST_API=https://radio.example.com/api/nowplaying/station_id

# Polling
POLL_INTERVAL=60                        # Check for songs every 60 seconds
```

**How to find these values:**
- **IRC_SERVER/IRC_PORT:** From your IRC network documentation
- **BOT_NICKNAME:** Choose any name; it can be anything
- **IRC_CHANNELS:** Channels you want the bot to announce songs in
- **SASL_USERNAME/PASSWORD:** Only needed if your nick is registered
- **AZURACAST_API:** From your AzuraCast instance admin panel
- **POLL_INTERVAL:** 30-120 seconds is typical (production uses 60 seconds)

---

## Test Manual Run

Before setting up systemd, test that the bot works:

```bash
# Activate venv if not already active
source venv/bin/activate

# Run the bot
python src/main.py
```

You should see output like:
```
[INFO] Starting MansionNET Radio Bot...
[INFO] RadioBot initialized
[INFO] Server: irc.example.com:6697
[INFO] Channels: #radio
[INFO] Poll interval: 60s
[INFO] Connected to IRC server
[INFO] Joined #radio
```

**To verify it's working:**
1. Check your IRC channel—the bot should appear
2. Wait for a song change (max 60 seconds with production settings)
3. Bot should announce: `♫ Now playing: Artist - Title (Album)`

**To stop:** Press `Ctrl+C`

---

## Setup as Systemd Service (Auto-Start & Management)

This makes the bot run automatically on boot and managed by systemd, just like your eggdrops.

### Step 1: Configure Systemd Service File

The template is at `systemd/mansion-radio-bot.service`. You need to customize it for your installation:

```bash
# Copy template to systemd directory
sudo cp systemd/mansion-radio-bot.service /etc/systemd/system/

# Edit for your installation
sudo nano /etc/systemd/system/mansion-radio-bot.service
```

Update these lines to match your setup:

```ini
[Service]
# Change to your username if not using 'radiobot'
User=radiobot
Group=radiobot

# Change to your project path
WorkingDirectory=/home/radiobot/mansion-radio-bot

# Update with your venv path
Environment="PATH=/home/radiobot/mansion-radio-bot/venv/bin"
ExecStart=/home/radiobot/mansion-radio-bot/venv/bin/python src/main.py
```

### Step 2: Enable and Start Service

```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable mansion-radio-bot

# Start the service immediately
sudo systemctl start mansion-radio-bot

# Check status
sudo systemctl status mansion-radio-bot
```

Expected output:
```
● mansion-radio-bot.service - MansionNET Radio IRC Bot
     Loaded: loaded (/etc/systemd/system/mansion-radio-bot.service; enabled)
     Active: active (running) since Mon 2026-02-05 10:15:23 UTC
   Process: 1234 ExecStart=...
  Main PID: 1235 (python)
     Tasks: 2
     Memory: 45.2M
```

The bot is now running and will auto-restart on crashes or system reboot.

---

## Managing the Service

### Check Status

```bash
systemctl status mansion-radio-bot

# Quick check (one-liner)
systemctl is-active mansion-radio-bot
# Output: active or inactive
```

### View Logs

```bash
# Real-time logs (like 'tail -f')
sudo journalctl -u mansion-radio-bot -f

# Last 50 lines
sudo journalctl -u mansion-radio-bot -n 50

# Today's logs
sudo journalctl -u mansion-radio-bot --since today

# Last 2 hours
sudo journalctl -u mansion-radio-bot --since "2 hours ago"

# Show logs with full details
sudo journalctl -u mansion-radio-bot --no-pager
```

### Control the Service

```bash
# Stop the bot
sudo systemctl stop mansion-radio-bot

# Start the bot
sudo systemctl start mansion-radio-bot

# Restart the bot
sudo systemctl restart mansion-radio-bot

# Disable auto-start on boot
sudo systemctl disable mansion-radio-bot

# Re-enable auto-start on boot
sudo systemctl enable mansion-radio-bot
```

### Check Resource Usage

```bash
# While service is running
ps aux | grep "python src/main.py"

# Expected: ~2-5% CPU, 40-100MB memory
```

---

## Updating the Bot

When you pull new code or update dependencies:

```bash
# Stop the bot
sudo systemctl stop mansion-radio-bot

# Update code (if using git)
cd ~/mansion-radio-bot
git pull origin main

# Activate venv and update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart the service
sudo systemctl start mansion-radio-bot

# Verify it's running
sudo journalctl -u mansion-radio-bot -n 20 -f
```

---

## Troubleshooting

### Bot won't start

**Check service status:**
```bash
sudo systemctl status mansion-radio-bot
# Shows the error (if any)
```

**Check logs for errors:**
```bash
sudo journalctl -u mansion-radio-bot -n 50
# Look for [ERROR] or [CRITICAL] messages
```

**Try running manually to see errors:**
```bash
cd ~/mansion-radio-bot
source venv/bin/activate
python src/main.py
# Shows errors directly
```

### "python: command not found"

```bash
# Verify Python is installed
python3 --version
which python3

# If not installed:
sudo apt install python3.11 python3.11-venv

# Make sure ExecStart in service file uses full path:
# /home/radiobot/mansion-radio-bot/venv/bin/python src/main.py
```

### "Permission denied"

If running as `radiobot` user, ensure it owns the files:

```bash
sudo chown -R radiobot:radiobot /home/radiobot/mansion-radio-bot
ls -ld ~/mansion-radio-bot
# Should show: drwxr-xr-x radiobot radiobot
```

### ".env file not found"

```bash
# Make sure .env exists
ls -la ~/mansion-radio-bot/.env

# If missing, create it:
cd ~/mansion-radio-bot
cp config/.env.example .env
nano .env
```

### "Cannot connect to IRC server"

**Check your settings:**
```bash
cat ~/mansion-radio-bot/.env | grep IRC_
```

**Test connectivity:**
```bash
# Install netcat if needed
sudo apt install netcat-openbsd

# Test connection to IRC server
nc -zv irc.example.com 6697
# Should print: succeeded (or Connection refused = firewall issue)
```

### "SASL authentication failed"

```bash
# Verify credentials in .env
cat ~/mansion-radio-bot/.env | grep SASL

# Test with different password or disable SASL temporarily:
# Edit .env and comment out SASL_PASSWORD
source venv/bin/activate
python src/main.py
```

### "API connection failed" or No song announcements

```bash
# Check the API endpoint is correct
cat ~/mansion-radio-bot/.env | grep AZURACAST_API

# Test if API is reachable
curl https://radio.example.com/api/nowplaying/station_id | head -20

# Check for errors in bot logs
sudo journalctl -u mansion-radio-bot | grep -i "error\|api\|exception"
```

### "Not joining channels"

```bash
# Check which channels are configured
cat ~/mansion-radio-bot/.env | grep IRC_CHANNELS

# Verify you have permission to join
# (Some channels require registered nick + SASL)

# Check logs for join attempts
sudo journalctl -u mansion-radio-bot | grep -i "join\|channel"
```

---

## Service File Reference

The systemd service file (`systemd/mansion-radio-bot.service`) includes:

| Setting | Purpose |
|---------|---------|
| `Type=simple` | Bot runs in foreground |
| `User=radiobot` | Run as dedicated user |
| `WorkingDirectory=...` | Directory where bot looks for `.env` |
| `Environment=PATH=...` | Use venv Python |
| `ExecStart=...` | Command to start bot |
| `Restart=always` | Auto-restart on crash |
| `RestartSec=10` | Wait 10 seconds before restart |
| `StandardOutput=journal` | Log to systemd journal (journalctl) |
| `StandardError=journal` | Errors also to journal |
| `NoNewPrivileges=true` | Security hardening |
| `ProtectSystem=strict` | Read-only filesystem (except working dir) |

---

## Comparison: Manual vs Systemd

| Task | Manual | Systemd |
|------|--------|---------|
| Start bot | `python src/main.py` | `systemctl start mansion-radio-bot` |
| Stop bot | `Ctrl+C` | `systemctl stop mansion-radio-bot` |
| View logs | stdout on terminal | `journalctl -u mansion-radio-bot -f` |
| Auto-start on boot | ❌ Manual script | ✅ Automatic |
| Auto-restart on crash | ❌ Manual | ✅ Automatic (10 sec delay) |
| Resource limits | ❌ None | ✅ Configurable |
| Status monitoring | ❌ Manual | ✅ `systemctl status` |

**Recommendation:** Use systemd for production (like your eggdrops setup).

---

## Directory Structure After Installation

```
/home/radiobot/mansion-radio-bot/
├── venv/                               # Python virtual environment
├── .env                                # Configuration (local, not in git)
├── src/
│   ├── main.py                         # Entry point
│   ├── bot.py                          # IRC bot implementation
│   └── fetchers/
│       ├── __init__.py
│       └── azuracast.py                # AzuraCast API client
├── config/
│   └── .env.example                    # Configuration template
├── docker/
│   ├── Dockerfile
│   └── docker-compose.example.yml
├── scripts/
│   ├── setup.sh                        # Automated setup
│   └── build.sh
├── systemd/
│   └── mansion-radio-bot.service       # Systemd service template
├── docs/
│   ├── DEPLOY_DOCKER.md
│   ├── DEPLOY_BAREMETAL.md
│   ├── DEPLOY_PORTAINER.md
│   ├── TROUBLESHOOT_PORTAINER.md
│   └── ARCHITECTURE.md
├── README.md
├── requirements.txt
└── .git/
```

And systemd will have:
```
/etc/systemd/system/mansion-radio-bot.service     # Copied from systemd/
```

---

## Next Steps

1. ✅ Create dedicated `radiobot` user
2. ✅ Copy project to `/home/radiobot/mansion-radio-bot`
3. ✅ Create virtual environment and install dependencies
4. ✅ Configure `.env` file
5. ✅ Test manual run with `python src/main.py`
6. ✅ Configure systemd service file
7. ✅ Enable and start service
8. ✅ Monitor logs with `journalctl`

**Need more help?** See:
- [README.md](../README.md) for quick overview
- [ARCHITECTURE.md](ARCHITECTURE.md) for technical design
- [DEPLOY_DOCKER.md](DEPLOY_DOCKER.md) for Docker alternative
