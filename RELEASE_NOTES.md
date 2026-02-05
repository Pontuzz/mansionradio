# MansionRadio Bot - Release Notes

## Version 0.1.0 (2026-02-05)

### Overview
First production-ready release of MansionRadio IRC bot with full bare metal and Docker deployment support.

### Features
- **State Machine Architecture**: Explicit connection states with proper state transitions
- **SASL Authentication**: RFC 5802 PLAIN mechanism with CAP negotiation for secure identification
- **Non-blocking API Polling**: Respects bot state and only announces when fully connected
- **AzuraCast Integration**: Real-time song announcements from AzuraCast streaming platform
- **Multiple Deployment Options**:
  - Docker (Portainer ready)
  - Bare metal with systemd
  - Manual/development setup

### Documentation
- **README.md** - Quick start and overview
- **docs/ARCHITECTURE.md** - Technical design and implementation details
- **docs/DEPLOY_DOCKER.md** - Docker and Portainer deployment
- **docs/DEPLOY_BAREMETAL.md** - Linux/systemd deployment
- **docs/DEPLOY_PORTAINER.md** - Portainer UI deployment
- **docs/TROUBLESHOOT_*.md** - Issue-specific troubleshooting guides

### Installation Methods

#### Bare Metal (Linux/Raspberry Pi)
```bash
bash scripts/install.sh                    # Automated setup
bash scripts/install.sh --user myuser      # Custom user
bash scripts/install.sh --help             # Show options
```

#### Docker
```bash
docker-compose up --build
```

#### Manual
```bash
bash scripts/setup.sh
source venv/bin/activate
python src/main.py
```

### Configuration
All deployments use the same configuration format:
```bash
IRC_SERVER=irc.example.com
IRC_PORT=6697
BOT_NICKNAME=MansionRadio
IRC_CHANNELS=#radio,#music
SASL_USERNAME=account_name      # Optional
SASL_PASSWORD=password          # Optional
AZURACAST_API=https://radio.example.com/api/nowplaying/station_id
POLL_INTERVAL=60                # seconds
```

### System Requirements

**Bare Metal:**
- Python 3.9+ (3.11 recommended)
- Linux (Ubuntu 20.04+, Debian 11+, Raspberry Pi OS)
- ~50MB disk space
- Network access to IRC server and AzuraCast API

**Docker:**
- Docker 20.10+ or Docker Desktop
- ~150MB image size
- Same network requirements

### Fixed in v0.1.0
- Documentation updated to reflect 60-second production polling interval
- Systemd service hardening with security options
- Comprehensive bare metal installation documentation

### Known Limitations
- Single-station AzuraCast support (expand to multiple stations in future)
- No song history or statistics tracking (planned for v0.2)
- No automatic IRC reconnection with exponential backoff (uses systemd restart instead)

### Changelog

#### Documentation
- Updated all deployment examples to use 60-second polling interval
- Added comprehensive bare metal installation guide
- Added systemd service management documentation
- Added Portainer deployment guide
- Added troubleshooting guides for common issues

#### Installation
- Added `scripts/install.sh` for one-command bare metal setup
- Improved `scripts/setup.sh` with better error checking
- Enhanced systemd service file with security hardening

#### Code Quality
- All examples tested and verified to match production code
- Configuration templates validated against actual defaults
- Documentation paths verified to exist in repository

### Future Roadmap

**v0.2.0 (Q1 2026)**
- Multi-station AzuraCast support
- Song history tracking
- Statistics dashboard
- Configurable announcement formats

**v0.3.0 (Q2 2026)**
- Automatic IRC reconnection with exponential backoff
- Rate limiting for API calls
- Webhook support for external integrations
- Plugin system for custom announcements

**v0.4.0 (Q3 2026)**
- Web UI for management and monitoring
- Database persistence (SQLite)
- Performance optimizations for Raspberry Pi

### Installation Instructions

1. **Download the release bundle**
   ```bash
   wget https://github.com/Pontuzz/mansionradio/releases/download/v0.1.0/mansion-radio-bot-0.1.0.tar.gz
   tar -xzf mansion-radio-bot-0.1.0.tar.gz
   cd mansion-radio-bot
   ```

2. **Run installation (automated)**
   ```bash
   sudo bash scripts/install.sh
   ```

3. **Configure the bot**
   ```bash
   sudo nano /home/radiobot/mansion-radio-bot/.env
   ```

4. **Start the service**
   ```bash
   sudo systemctl start mansion-radio-bot
   sudo systemctl status mansion-radio-bot
   ```

5. **Verify it's working**
   ```bash
   sudo journalctl -u mansion-radio-bot -f
   ```

### Support & Troubleshooting

See `docs/TROUBLESHOOT_*.md` files in the release bundle for:
- Installation issues
- Configuration problems
- Network connectivity
- API errors
- Systemd service issues

### License
MIT License - See repository for full terms

### Author
Pontuzz

### Repository
https://github.com/Pontuzz/mansionradio
