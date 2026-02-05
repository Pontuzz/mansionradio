# Bare Metal Deployment Guide (Like Eggdrops)

This guide covers deploying the radio bot directly on a machine (Pi3, Ubuntu VM, etc.) without Docker, just like you do with eggdrops.

---

## Prerequisites

- **OS:** Ubuntu 20.04+ or Raspberry Pi OS
- **Python:** 3.9 or higher
- **User:** Dedicated `radiobot` user (recommended)
- **Network:** Access to irc.example.com:6697

### Check Python Version

```bash
python3 --version
# Should be 3.9+
```

If you need Python 3.11:
```bash
# Ubuntu
sudo apt update
sudo apt install python3.11 python3.11-venv

# Raspberry Pi OS
sudo apt update
sudo apt install python3.11 python3.11-venv
```

---

## Installation

### 1. Create Dedicated User (Optional but Recommended)

```bash
sudo useradd -m -s /bin/bash -d /home/radiobot radiobot
sudo su - radiobot
```

### 2. Copy Project to Target Machine

From your workstation:
```bash
scp -r ~/projects/mansionradio user@pi3:~/mansion-radio-bot
```

Or manually:
```bash
# SSH to target
ssh user@pi3

# Create directory
mkdir -p ~/mansion-radio-bot

# Copy files (upload them)
cd ~/mansion-radio-bot
```

### 3. Setup Virtual Environment and Install Dependencies

```bash
cd ~/mansion-radio-bot

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify
python main.py --help  # Should start (Ctrl+C to stop)
```

### 4. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env
```

Set your values:
```bash
IRC_SERVER=irc.example.com
IRC_PORT=6697
BOT_NICKNAME=MansionRadio
IRC_CHANNELS=#radio
AZURACAST_API=https://radio.example.com/api/nowplaying/station_id
POLL_INTERVAL=15
```

---

## Run Manually (Testing)

```bash
source venv/bin/activate
python main.py
```

Should output:
```
[INFO] Starting MansionNET Radio Bot...
[INFO] RadioBot initialized
[INFO] Server: irc.example.com:6697
[INFO] Channels: #radio
[INFO] Poll interval: 15s
[INFO] Connected to IRC server
[INFO] Joined #radio
```

Press `Ctrl+C` to stop.

---

## Setup as Systemd Service (Auto-Start)

This makes it run like your eggdrops - automatically on boot, managed by systemd.

### 1. Copy Systemd Service File

```bash
# From project directory
sudo cp systemd/mansion-radio-bot.service /etc/systemd/system/

# If using radiobot user, edit path:
sudo nano /etc/systemd/system/mansion-radio-bot.service
# Change WorkingDirectory and paths to match your installation
```

### 2. Set Correct Paths

Edit the service file to match your setup:

```bash
sudo nano /etc/systemd/system/mansion-radio-bot.service
```

Change these paths if needed:
- `User=radiobot` → your username
- `WorkingDirectory=/home/radiobot/mansion-radio-bot` → your path
- `ExecStart=/home/radiobot/mansion-radio-bot/venv/bin/python main.py` → your venv path

### 3. Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable mansion-radio-bot

# Start the service
sudo systemctl start mansion-radio-bot

# Check status
sudo systemctl status mansion-radio-bot
```

### 4. View Logs

```bash
# Real-time logs
sudo journalctl -u mansion-radio-bot -f

# Last 50 lines
sudo journalctl -u mansion-radio-bot -n 50

# Today's logs
sudo journalctl -u mansion-radio-bot --since today
```

---

## Management Commands

### Check if Bot is Running

```bash
systemctl status mansion-radio-bot
```

### Stop Bot

```bash
sudo systemctl stop mansion-radio-bot
```

### Restart Bot

```bash
sudo systemctl restart mansion-radio-bot
```

### Check Bot Logs

```bash
sudo journalctl -u mansion-radio-bot -f
```

### Auto-Start on Boot

```bash
sudo systemctl enable mansion-radio-bot
```

### Disable Auto-Start

```bash
sudo systemctl disable mansion-radio-bot
```

---

## Updates

When you update the bot code:

```bash
cd ~/mansion-radio-bot

# Stop the bot
sudo systemctl stop mansion-radio-bot

# Pull latest code (if using git)
git pull origin main

# Install any new dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart
sudo systemctl start mansion-radio-bot
```

---

## Troubleshooting

### Bot won't start

```bash
# Check service status
systemctl status mansion-radio-bot

# View errors
journalctl -u mansion-radio-bot -n 50

# Try running manually to see errors
source venv/bin/activate
python main.py
```

### Python not found

Make sure Python 3.9+ is installed:
```bash
python3 --version
which python3
```

### Permission denied

If running as `radiobot` user, make sure it owns the files:
```bash
sudo chown -R radiobot:radiobot /home/radiobot/mansion-radio-bot
```

### IRC connection fails

Check your `.env` file:
```bash
cat .env
```

Verify IRC server is reachable:
```bash
nc -zv irc.example.com 6697
```

### API connection fails

Test the API endpoint:
```bash
curl -s https://radio.example.com/api/nowplaying/station_id | head -20
```

---

## Comparison: Manual vs Systemd

| Task | Manual | Systemd |
|------|--------|---------|
| Start bot | `python main.py` | `systemctl start mansion-radio-bot` |
| Stop bot | Ctrl+C | `systemctl stop mansion-radio-bot` |
| View logs | stdout | `journalctl -u mansion-radio-bot -f` |
| Auto-start on boot | ❌ Manual script | ✅ Automatic |
| Restart on crash | ❌ Manual | ✅ Automatic |
| Resource limits | ❌ None | ✅ Configurable |

**Recommendation:** Use systemd for production. It's like your eggdrops setup.

---

## Directory Structure After Installation

```
/home/radiobot/mansion-radio-bot/
├── venv/                 # Virtual environment
├── .env                  # Configuration (local, not committed)
├── main.py
├── bot.py
├── requirements.txt
├── fetchers/
│   ├── __init__.py
│   └── azuracast.py
├── docs/
│   ├── DEPLOY_DOCKER.md
│   └── DEPLOY_BAREMETAL.md
├── systemd/
│   └── mansion-radio-bot.service
├── README.md
└── ...
```

And systemd will have:
```
/etc/systemd/system/mansion-radio-bot.service  # Symlink or copy
```

---

## Like Your Eggdrops?

This setup mirrors how eggdrops work:
- ✅ Dedicated user (`radiobot`)
- ✅ Virtual environment (isolated dependencies)
- ✅ Systemd service (auto-start, managed restarts)
- ✅ Logs via journalctl (like `/var/log/eggdrop`)
- ✅ Config file (`.env` like config scripts)
- ✅ Manual control (`systemctl` like eggdrop scripts)

---

## Next Steps

1. Choose target machine (Pi3 or Ubuntu VM)
2. Copy project to target
3. Run setup.sh or manual setup
4. Test with `python main.py`
5. Configure systemd service
6. Enable and start

Questions? See README.md or DEPLOY_DOCKER.md for Docker alternative.
