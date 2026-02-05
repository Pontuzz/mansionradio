---
title: MansionRadio Bot
description: IRC bot that polls AzuraCast and announces songs to IRC channels
audience: beginner
completeness: 100%
last_updated: 2026-02-05
maintainer: Pontuzz
---

# MansionRadio Bot

IRC bot that polls an AzuraCast instance and announces currently playing songs to IRC channels.

## Architecture

**State machine:** Explicit connection states (disconnected → connecting → authenticating → registered → active)

**SASL authentication:** Implements RFC 5802 PLAIN mechanism with proper CAP negotiation and multiline message handling.

**Polling:** Non-blocking async polling of AzuraCast API respects bot state (only announces when ACTIVE).

See `docs/ARCHITECTURE.md` for detailed design and rationale.

## Quick Start

### Docker
```bash
docker-compose up --build
```

### Bare Metal
```bash
bash setup.sh
source venv/bin/activate
python main.py
```

## Configuration

Copy `.env.example` to `.env`:
```bash
IRC_SERVER=irc.example.com
IRC_PORT=6697
BOT_NICKNAME=MansionRadio
IRC_CHANNELS=#radio,#music
SASL_USERNAME=account_name      # Optional - for registered nicks
SASL_PASSWORD=password          # Optional - for registered nicks
AZURACAST_API=https://radio.example.com/api/nowplaying/station_id
POLL_INTERVAL=15
```

For Docker: Edit `docker-compose.yml` environment variables instead.

## Project Structure

```
├── main.py                      # Entry point, config loading
├── bot.py                       # IRC bot (state machine, SASL, polling)
├── fetchers/
│   └── azuracast.py            # AzuraCast API client
├── Dockerfile
├── docker-compose.example.yml
├── setup.sh                     # Bare metal setup
├── systemd/
│   └── mansion-radio-bot.service
├── docs/
│   ├── ARCHITECTURE.md          # Design & technical details
│   ├── DEPLOY_DOCKER.md
│   ├── DEPLOY_BAREMETAL.md
│   ├── DEPLOY_PORTAINER.md
│   └── TROUBLESHOOT_PORTAINER.md
├── requirements.txt
├── .env.example
└── README.md
```

## Dependencies

- `python-irc` - IRC protocol handling
- `python-dotenv` - Environment config
- `requests` - HTTP client for AzuraCast API

## IRC Features

- **TLS/SSL** connection
- **SASL PLAIN** authentication with CAP negotiation
- **Song announcements** with change detection
- **`!playing` command** for on-demand song status
- **Auto-reconnect** on disconnection
- **Graceful shutdown** on Ctrl+C

## Technical Details

### SASL Flow
```
CAP LS 302
← CAP LS * :...caps...
← CAP LS :final_caps
CAP REQ :sasl
← CAP ACK :sasl
AUTHENTICATE PLAIN
← AUTHENTICATE +
AUTHENTICATE [base64_credentials]
← 903 SASL success
CAP END
← 001 WELCOME
```

Properly handles multiline CAP LS responses (indicated by `*` marker).

### API Polling
- Polls every N seconds (configurable)
- Tracks song hash to detect changes
- Only announces when bot is ACTIVE (joined channels)
- Silently skips API errors, continues polling

## Deployment

### Docker
```bash
docker-compose up --build
docker-compose logs -f
```
See `docs/DEPLOY_DOCKER.md` and `docs/DEPLOY_PORTAINER.md`.

### Bare Metal
```bash
bash setup.sh
systemctl start mansion-radio-bot
systemctl status mansion-radio-bot
```
See `docs/DEPLOY_BAREMETAL.md`.

## Troubleshooting

**Won't connect:** Check IRC_SERVER:IRC_PORT accessibility and bot nickname availability.

**Connects but no announcements:** Verify bot joined channel (check logs), AZURACAST_API is correct, API is responding.

**API connection fails:** Test with `curl <AZURACAST_API>`, verify URL syntax, check network connectivity.

See `docs/TROUBLESHOOT_PORTAINER.md` for Portainer-specific issues.

## License

MIT
