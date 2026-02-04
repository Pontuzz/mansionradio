"""Main entry point for the radio bot."""

import os
import sys
import signal
from dotenv import load_dotenv
from bot import RadioBot


def main():
    """Load configuration and start the bot."""
    load_dotenv()

    config = {
        "server": os.getenv("IRC_SERVER", "irc.inthemansion.com"),
        "port": int(os.getenv("IRC_PORT", "6697")),
        "nickname": os.getenv("BOT_NICKNAME", "MansionRadio"),
        "channels": os.getenv("IRC_CHANNELS", "#radio").split(","),
        "api_url": os.getenv(
            "AZURACAST_API", "https://radio.inthemansion.com/api/nowplaying/mansionnet"
        ),
        "poll_interval": int(os.getenv("POLL_INTERVAL", "15")),
    }

    # Validate config
    if not config["server"] or not config["port"]:
        print("[ERROR] IRC_SERVER and IRC_PORT must be set")
        sys.exit(1)

    if not config["api_url"]:
        print("[ERROR] AZURACAST_API must be set")
        sys.exit(1)

    print("[INFO] Starting MansionNET Radio Bot...")

    bot = RadioBot(config)

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n[INFO] Received interrupt signal")
        bot.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        bot.start()
    except KeyboardInterrupt:
        print("\n[INFO] Keyboard interrupt")
        bot.shutdown()
    except Exception as e:
        print(f"[ERROR] Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
