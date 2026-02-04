# Quick Start

## One-Command Setup

```bash
cd mansion-radio-bot
bash setup.sh
```

This will:
1. Create a Python virtual environment
2. Install all dependencies
3. Create `.env` file from template

## Configuration

Edit `.env` with your settings:

```bash
nano .env
```

Default values are already set for MansionNET:
- **IRC Server**: `irc.inthemansion.com`
- **IRC Port**: `6697` (TLS)
- **Channel**: `#radio`
- **Poll Interval**: `15 seconds`
- **API**: `https://radio.inthemansion.com/api/nowplaying/mansionnet`

You only need to customize `BOT_NICKNAME` to a unique name.

## Run the Bot

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Start the bot
python main.py
```

## Expected Output

```
[INFO] Starting MansionNET Radio Bot...
[INFO] RadioBot initialized
[INFO] Server: irc.inthemansion.com:6697
[INFO] Channels: #radio
[INFO] Poll interval: 15s
[INFO] Connected to IRC server
[INFO] Joined #radio
[ANNOUNCE] #radio: ♫ Now playing: Tycho - Coastal Brake (Dive)
```

## Stop the Bot

Press `Ctrl+C` to gracefully shut down.

## Verify It's Working

In your IRC client, join `#radio` and wait for the next song change (max 15 seconds).

You should see a message like:
```
♫ Now playing: Artist Name - Song Title (Album Name)
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Bot won't connect | Check `IRC_SERVER` and `IRC_PORT` in `.env` |
| "Connection refused" | Verify port 6697 is accessible |
| Bot connects but no announcements | Check bot successfully joined channel (see logs) |
| API errors | Test API: `curl https://radio.inthemansion.com/api/nowplaying/mansionnet` |

## Next: Run as Service (Optional)

See README.md for instructions to run as systemd service or supervisor daemon.
