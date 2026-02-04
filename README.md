# MansionNET Radio Bot

IRC bot that automatically announces songs from MansionNET Radio to your IRC channel.

## Quick Start

Choose your deployment method:

### Docker (Testing & Multi-Host)
```bash
docker-compose up --build
```
Environment variables are built into `docker-compose.yml`. See **[DEPLOY_DOCKER.md](docs/DEPLOY_DOCKER.md)** for details.

### Bare Metal (Production, Like Eggdrops)
```bash
bash setup.sh
source venv/bin/activate
python main.py
```
Then setup systemd: See **[DEPLOY_BAREMETAL.md](docs/DEPLOY_BAREMETAL.md)** for details.

---

## Configuration

**For Docker:** Environment variables are embedded in `docker-compose.yml`:
```yaml
environment:
  - IRC_SERVER=irc.inthemansion.com
  - IRC_PORT=6697
  - BOT_NICKNAME=MansionRadio
  - IRC_CHANNELS=#radio
  - AZURACAST_API=https://radio.inthemansion.com/api/nowplaying/mansionnet
  - POLL_INTERVAL=15
```

To customize, edit `docker-compose.yml` directly or use Portainer UI.

**For Bare Metal:** Create a `.env` file (copy from `.env.example`):

```bash
# IRC Configuration
IRC_SERVER=irc.inthemansion.com
IRC_PORT=6697
BOT_NICKNAME=MansionRadio
IRC_CHANNELS=#radio

# AzuraCast API
AZURACAST_API=https://radio.inthemansion.com/api/nowplaying/mansionnet

# Polling interval (seconds)
POLL_INTERVAL=15
```

## How It Works

1. **Connects** to IRC server with TLS encryption
2. **Polls** AzuraCast API every 15 seconds
3. **Detects** when a new song starts playing
4. **Announces** the song to IRC channel(s)

### Example Output

```
♫ Now playing: Tycho - Coastal Brake (Dive)
```

## Project Structure

```
mansionradio/
├── main.py                          # Entry point
├── bot.py                           # IRC bot implementation
├── fetchers/
│   ├── __init__.py
│   └── azuracast.py                 # AzuraCast API client
├── Dockerfile                       # Docker image definition
├── docker-compose.yml               # Docker Compose (testing)
├── systemd/
│   └── mansion-radio-bot.service    # Systemd service file
├── docs/
│   ├── DEPLOY_DOCKER.md             # Docker deployment guide
│   └── DEPLOY_BAREMETAL.md          # Bare metal deployment guide
├── requirements.txt                 # Python dependencies
├── .env.example                     # Configuration template
├── .gitignore
├── .dockerignore
├── QUICKSTART.md
└── README.md
```

## Error Handling

- **API failures**: Bot continues operating; logs errors
- **Disconnection**: Bot automatically attempts to reconnect
- **Graceful shutdown**: Ctrl+C cleanly disconnects from IRC

## Troubleshooting

### Bot won't connect to IRC
- Check `IRC_SERVER` and `IRC_PORT` are correct
- Verify port 6697 is accessible (TLS)
- Check bot nickname isn't already in use

### Bot connects but doesn't announce
- Verify bot successfully joined the channel (check logs)
- Check `IRC_CHANNELS` in `.env`
- Verify `AZURACAST_API` URL is correct
- Check AzuraCast API is responding: `curl <API_URL>`

### API connection fails
- Test API directly: `curl https://radio.inthemansion.com/api/nowplaying/mansionnet`
- Check internet connectivity
- Verify `AZURACAST_API` URL in `.env`

## Deployment Methods

### Docker (Testing & Flexible Deployment)

For local testing or deployment with Docker:

```bash
docker-compose up --build
docker-compose logs -f
```

See **[DEPLOY_DOCKER.md](docs/DEPLOY_DOCKER.md)** for full instructions.

**Advantages:**
- Isolated environment
- Same setup across machines
- Easy to test before production
- Portable to any Docker-enabled system

### Bare Metal (Production, Like Eggdrops)

For direct deployment on Pi3 or Ubuntu VM:

```bash
bash setup.sh
systemctl start mansion-radio-bot
systemctl status mansion-radio-bot
```

See **[DEPLOY_BAREMETAL.md](docs/DEPLOY_BAREMETAL.md)** for full instructions.

**Advantages:**
- Minimal overhead
- Familiar systemd management
- Like your eggdrop setup
- Direct system integration

---

## Error Handling

- **API failures**: Bot continues operating; logs errors
- **Disconnection**: Bot automatically attempts to reconnect
- **Graceful shutdown**: Ctrl+C cleanly disconnects from IRC

## Troubleshooting

### Bot won't connect to IRC
- Check `IRC_SERVER` and `IRC_PORT` are correct
- Verify port 6697 is accessible (TLS)
- Check bot nickname isn't already in use

### Bot connects but doesn't announce
- Verify bot successfully joined the channel (check logs)
- Check `IRC_CHANNELS` in `.env`
- Verify `AZURACAST_API` URL is correct
- Check AzuraCast API is responding: `curl <API_URL>`

### API connection fails
- Test API directly: `curl https://radio.inthemansion.com/api/nowplaying/mansionnet`
- Check internet connectivity
- Verify `AZURACAST_API` URL in `.env`

---

## Further Development

The bot is ready for enhancements:
- Add listener count to announcements
- Show next song in queue
- Add `!np` command for on-demand requests
- Store song history
- Display genre/mood information
- Multi-station support

See AzuraCast API docs for available data fields.

---

## License

MIT
