"""Main entry point for the radio bot."""

import os
import sys
import signal
import logging
from dotenv import load_dotenv
from bot import RadioBot

# Configure logging to stdout only
# (File logging will be handled by container logs/volume mounts if needed)
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s] %(asctime)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def main():
    """Load configuration and start the bot."""
    load_dotenv()

    config = {
        "server": os.getenv("IRC_SERVER", "irc.example.com"),
        "port": int(os.getenv("IRC_PORT", "6697")),
        "nickname": os.getenv("BOT_NICKNAME", "MansionRadio"),
        "channels": os.getenv("IRC_CHANNELS", "#radio").split(","),
        "api_url": os.getenv(
            "AZURACAST_API", "https://radio.example.com/api/nowplaying/station_id"
        ),
        "poll_interval": int(os.getenv("POLL_INTERVAL", "15")),
        "sasl_username": os.getenv("SASL_USERNAME", ""),
        "sasl_password": os.getenv("SASL_PASSWORD", ""),
    }

    # Validate config
    if not config["server"] or not config["port"]:
        logger.error("IRC_SERVER and IRC_PORT must be set")
        sys.exit(1)

    if not config["api_url"]:
        logger.error("AZURACAST_API must be set")
        sys.exit(1)

    logger.info("Starting MansionNET Radio Bot...")
    logger.info(f"Configuration: {config}")

    try:
        bot = RadioBot(config)
        logger.info("Bot instance created, entering event loop...")
    except Exception as e:
        logger.error(f"Failed to create bot: {e}", exc_info=True)
        sys.exit(1)

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        logger.info("Received interrupt signal")
        bot.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        logger.info("Calling bot.start() - entering blocking event loop...")
        bot.start()
        logger.info("bot.start() returned (should not happen)")
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt")
        bot.shutdown()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
