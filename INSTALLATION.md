# MansionRadio Bot - Release Bundle Installation Guide

## What's in This Bundle?

This release bundle (`mansion-radio-bot-0.1.0.tar.gz`) contains everything you need to deploy the MansionRadio IRC bot on bare metal (Linux/Raspberry Pi).

### Bundle Contents
```
mansion-radio-bot/
├── scripts/
│   ├── install.sh              ← Automated installer (use this!)
│   ├── setup.sh                ← Manual setup helper
│   └── build.sh                ← Docker build helper
├── src/                         ← Python source code
│   ├── main.py
│   ├── bot.py
│   └── fetchers/azuracast.py
├── config/
│   └── .env.example            ← Configuration template
├── docker/                      ← Docker files (optional)
│   ├── Dockerfile
│   └── docker-compose.example.yml
├── systemd/
│   └── mansion-radio-bot.service ← Auto-start configuration
├── docs/
│   ├── DEPLOY_BAREMETAL.md     ← Detailed manual setup
│   ├── DEPLOY_DOCKER.md        ← Docker deployment
│   ├── DEPLOY_PORTAINER.md     ← Portainer deployment
│   ├── ARCHITECTURE.md         ← Technical design
│   └── TROUBLESHOOT_*.md       ← Troubleshooting guides
├── RELEASE_NOTES.md            ← Version information
├── README.md                   ← Quick overview
└── requirements.txt            ← Python dependencies
```

## Quick Start (Recommended)

### 1. Extract the Bundle
```bash
tar -xzf mansion-radio-bot-0.1.0.tar.gz
cd mansion-radio-bot
```

### 2. Run the Automated Installer
```bash
sudo bash scripts/install.sh
```

The installer will:
- ✅ Check prerequisites (Python 3.9+)
- ✅ Create a dedicated `radiobot` user
- ✅ Copy files to `/home/radiobot/mansion-radio-bot`
- ✅ Create a Python virtual environment
- ✅ Install dependencies
- ✅ Configure systemd service for auto-start
- ✅ Create `.env` file from template

### 3. Configure the Bot
```bash
sudo nano /home/radiobot/mansion-radio-bot/.env
```

Edit these essential variables:
```bash
IRC_SERVER=irc.example.com              # Your IRC server
IRC_PORT=6697                            # Usually 6697 (TLS) or 6667 (plain)
BOT_NICKNAME=MansionRadio               # Bot nickname
IRC_CHANNELS="#radio,#music"            # Channels to join (comma-separated)
AZURACAST_API=https://radio.example.com/api/nowplaying/station_id
POLL_INTERVAL=60                        # Check for new songs every 60 seconds
SASL_USERNAME=your_account              # Optional: if nick is registered
SASL_PASSWORD=your_password             # Optional: SASL password
```

### 4. Start the Bot
```bash
sudo systemctl start mansion-radio-bot
```

### 5. Verify It's Running
```bash
sudo systemctl status mansion-radio-bot
sudo journalctl -u mansion-radio-bot -f  # Watch logs in real-time
```

You should see:
```
[INFO] Starting MansionNET Radio Bot...
[INFO] RadioBot initialized
[INFO] Connected to IRC server
[INFO] Joined #radio
[INFO] Poll interval: 60s
```

## Installer Options

The automated installer has several options:

```bash
# Standard installation (creates 'radiobot' user)
sudo bash scripts/install.sh

# Use a different username
sudo bash scripts/install.sh --user myuser

# Skip systemd setup (manual only)
sudo bash scripts/install.sh --no-systemd

# See what would be done without making changes
bash scripts/install.sh --dry-run

# Show help
bash scripts/install.sh --help
```

## Managing the Service

After installation, manage the bot with systemd:

```bash
# Start the bot
sudo systemctl start mansion-radio-bot

# Stop the bot
sudo systemctl stop mansion-radio-bot

# Restart the bot
sudo systemctl restart mansion-radio-bot

# Check status
sudo systemctl status mansion-radio-bot

# View logs (real-time)
sudo journalctl -u mansion-radio-bot -f

# View last 50 log lines
sudo journalctl -u mansion-radio-bot -n 50

# View today's logs
sudo journalctl -u mansion-radio-bot --since today

# Disable auto-start on boot
sudo systemctl disable mansion-radio-bot

# Enable auto-start on boot
sudo systemctl enable mansion-radio-bot
```

## Manual Installation (If Needed)

If the automated installer doesn't work for your setup, see `docs/DEPLOY_BAREMETAL.md` for step-by-step manual instructions.

### Quick Manual Steps
```bash
# 1. Extract and navigate
tar -xzf mansion-radio-bot-0.1.0.tar.gz
cd mansion-radio-bot

# 2. Create user
sudo useradd -m -s /bin/bash -d /home/radiobot radiobot

# 3. Install to home directory
sudo cp -r . /home/radiobot/mansion-radio-bot
sudo chown -R radiobot:radiobot /home/radiobot/mansion-radio-bot

# 4. Setup Python
cd /home/radiobot/mansion-radio-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configure
cp config/.env.example .env
nano .env  # Edit with your settings

# 6. Test manually
source venv/bin/activate
python src/main.py

# 7. Setup systemd
sudo cp systemd/mansion-radio-bot.service /etc/systemd/system/
# Edit paths in service file if needed
sudo systemctl daemon-reload
sudo systemctl enable mansion-radio-bot
sudo systemctl start mansion-radio-bot
```

## System Requirements

**Minimum:**
- Python 3.9+ (3.11 recommended)
- Linux OS: Ubuntu 20.04+, Debian 11+, Raspberry Pi OS
- 50MB disk space
- Network access to IRC server and AzuraCast API

**Tested On:**
- Ubuntu 20.04 LTS, 22.04 LTS
- Debian 11 (Bullseye)
- Raspberry Pi OS (all versions with Python 3.9+)
- Raspberry Pi 3B+, 4B, 5 (all work well)

## Troubleshooting

### Common Issues

**"Python 3 is not installed"**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**"Permission denied" when running installer**
```bash
# Make sure to use sudo
sudo bash scripts/install.sh

# Or if script isn't executable
bash scripts/install.sh
```

**"Module not found" errors after installation**
```bash
# Reinstall dependencies
cd /home/radiobot/mansion-radio-bot
source venv/bin/activate
pip install -r requirements.txt
```

**Bot won't connect to IRC**
```bash
# Check configuration
cat /home/radiobot/mansion-radio-bot/.env | grep IRC_

# Verify IRC server is reachable
nc -zv irc.example.com 6697

# Check logs for more details
sudo journalctl -u mansion-radio-bot | grep -i error
```

**Bot connects but doesn't announce songs**
```bash
# Check AzuraCast API configuration
cat /home/radiobot/mansion-radio-bot/.env | grep AZURACAST_API

# Test API manually
curl https://radio.example.com/api/nowplaying/station_id

# Check logs
sudo journalctl -u mansion-radio-bot | grep -i "api\|song\|announce"
```

See `docs/TROUBLESHOOT_*.md` files in the bundle for more detailed troubleshooting.

## Updating the Bot

When a new release is available:

```bash
# Stop the bot
sudo systemctl stop mansion-radio-bot

# Backup current installation
sudo cp -r /home/radiobot/mansion-radio-bot /home/radiobot/mansion-radio-bot.backup

# Extract new release
tar -xzf mansion-radio-bot-0.2.0.tar.gz

# Copy source files (keeps your .env and venv)
sudo cp -r mansion-radio-bot/src /home/radiobot/mansion-radio-bot/
sudo cp mansion-radio-bot/requirements.txt /home/radiobot/mansion-radio-bot/

# Update dependencies
cd /home/radiobot/mansion-radio-bot
source venv/bin/activate
pip install -r requirements.txt

# Restart
sudo systemctl start mansion-radio-bot

# Verify
sudo journalctl -u mansion-radio-bot -f
```

## Configuration Details

### IRC Settings
- **IRC_SERVER**: Your IRC network address (e.g., irc.example.com)
- **IRC_PORT**: IRC port (6697 for TLS, 6667 for plain, others supported)
- **BOT_NICKNAME**: Name of the bot in IRC (e.g., MansionRadio)
- **IRC_CHANNELS**: Comma-separated list of channels to join (e.g., #radio,#music)

### SASL Authentication (Optional)
Only needed if your bot's nickname is registered:
- **SASL_USERNAME**: Account name (usually same as BOT_NICKNAME)
- **SASL_PASSWORD**: Account password

### AzuraCast API
- **AZURACAST_API**: Full URL to your AzuraCast nowplaying endpoint
  - Format: `https://radio.example.com/api/nowplaying/STATION_ID`
  - Find it in AzuraCast admin panel > Stations > API docs

### Performance
- **POLL_INTERVAL**: Seconds between API polls (60 recommended, 30-120 typical)
  - Lower = faster announcements but more API calls
  - Higher = fewer API calls but delayed announcements

## Uninstalling

To completely remove the bot:

```bash
# Stop the service
sudo systemctl stop mansion-radio-bot

# Disable auto-start
sudo systemctl disable mansion-radio-bot

# Remove service file
sudo rm /etc/systemd/system/mansion-radio-bot.service
sudo systemctl daemon-reload

# Remove bot files
sudo rm -rf /home/radiobot/mansion-radio-bot

# Remove user
sudo userdel -r radiobot

# Remove any backups (optional)
sudo rm -rf /home/radiobot
```

## Support & Documentation

- **Quick Start**: See README.md
- **Technical Details**: See docs/ARCHITECTURE.md
- **Manual Setup**: See docs/DEPLOY_BAREMETAL.md
- **Docker Deployment**: See docs/DEPLOY_DOCKER.md
- **Portainer Deployment**: See docs/DEPLOY_PORTAINER.md
- **Issues**: See docs/TROUBLESHOOT_*.md

## Version Information

- **Release**: 0.1.0
- **Released**: 2026-02-05
- **Python**: 3.9+ (3.11 recommended)
- **License**: MIT
- **Repository**: https://github.com/Pontuzz/mansionradio

## What's Next?

After successful installation:

1. ✅ Verify bot appears in IRC channel
2. ✅ Wait for a song change (max 60 seconds)
3. ✅ Bot should announce: `♫ Now playing: Artist - Title (Album)`
4. ✅ Monitor logs with: `sudo journalctl -u mansion-radio-bot -f`
5. ✅ Set up monitoring/alerts (optional, using your system monitoring tools)

## Getting Help

If you encounter issues:

1. **Check the logs first**
   ```bash
   sudo journalctl -u mansion-radio-bot -n 50
   ```

2. **Search troubleshooting docs**
   - docs/TROUBLESHOOT_BAREMETAL.md (if exists)
   - docs/TROUBLESHOOT_*.md

3. **Test manually to see errors**
   ```bash
   cd /home/radiobot/mansion-radio-bot
   sudo -u radiobot bash -c 'source venv/bin/activate && python src/main.py'
   ```

4. **Report issues**
   - GitHub: https://github.com/Pontuzz/mansionradio/issues
   - Include: OS version, Python version, error logs, configuration (without passwords)
