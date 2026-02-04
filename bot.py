"""IRC bot for announcing radio station songs."""

import irc.bot
import irc.connection
import time
import threading
from fetchers.azuracast import AzuraCastFetcher


class RadioBot(irc.bot.SingleServerIRCBot):
    """IRC bot that announces currently playing songs from a radio station."""

    def __init__(self, config):
        """Initialize the bot with configuration.

        Args:
            config: Dictionary with keys:
                - server: IRC server address
                - port: IRC server port
                - nickname: Bot's IRC nickname
                - channels: List of channels to join
                - api_url: AzuraCast API endpoint
                - poll_interval: Seconds between API polls
        """
        self.config = config

        # Setup TLS connection
        factory = irc.connection.Factory(wrapper=irc.connection.Factory.open)

        irc.bot.SingleServerIRCBot.__init__(
            self,
            [(config["server"], config["port"])],
            config["nickname"],
            config["nickname"],
            realname=config["nickname"],
            connect_factory=factory,
        )

        self.fetcher = AzuraCastFetcher(config["api_url"])
        self.running = True
        self.connected = False
        self.last_song_data = None

        # Start polling thread
        self.poller_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.poller_thread.start()

        print(f"[INFO] RadioBot initialized")
        print(f"[INFO] Server: {config['server']}:{config['port']}")
        print(f"[INFO] Channels: {', '.join(config['channels'])}")
        print(f"[INFO] Poll interval: {config['poll_interval']}s")
        print(f"[INFO] Commands: !playing - Show currently playing song")

    def _poll_loop(self):
        """Continuously poll for song changes."""
        while self.running:
            try:
                # Only poll if connected
                if not self.connected:
                    time.sleep(self.config["poll_interval"])
                    continue

                data = self.fetcher.get_now_playing()

                if data:
                    # Store latest song data for !playing command
                    self.last_song_data = data

                    # Announce if song changed
                    if self.fetcher.has_song_changed(data):
                        message = self.fetcher.format_song(data)
                        self._announce(message)

            except Exception as e:
                print(f"[ERROR] Poll loop error: {e}")

            time.sleep(self.config["poll_interval"])

    def _announce(self, message: str):
        """Send message to IRC channel(s).

        Args:
            message: Message to send.
        """
        for channel in self.config["channels"]:
            try:
                self.connection.privmsg(channel, message)
                print(f"[ANNOUNCE] {channel}: {message}")
            except Exception as e:
                print(f"[ERROR] Failed to announce to {channel}: {e}")

    def on_welcome(self, connection, event):
        """Called when bot successfully connects to IRC server."""
        self.connected = True
        print(f"[INFO] Connected to IRC server")

        for channel in self.config["channels"]:
            connection.join(channel)
            print(f"[INFO] Joined {channel}")

    def on_disconnect(self, connection, event):
        """Called when bot disconnects from IRC server."""
        self.connected = False
        print(f"[WARNING] Disconnected from IRC server")

        # Attempt to reconnect
        if self.running:
            print(f"[INFO] Attempting to reconnect in 10 seconds...")
            time.sleep(10)

    def on_join(self, connection, event):
        """Called when bot joins a channel."""
        channel = event.target
        print(f"[INFO] Successfully joined {channel}")

    def on_part(self, connection, event):
        """Called when bot parts a channel."""
        channel = event.target
        print(f"[INFO] Left {channel}")

    def on_error(self, connection, event):
        """Called when IRC server sends an error."""
        print(f"[ERROR] IRC Error: {event}")

    def on_pubmsg(self, connection, event):
        """Called when a public message is posted in a channel."""
        message = event.arguments[0]
        nick = event.source.nick
        channel = event.target

        # Handle !playing command
        if message.lower().startswith("!playing"):
            self._handle_playing_command(connection, channel, nick)

    def _handle_playing_command(self, connection, channel, nick):
        """Handle the !playing command.

        Args:
            connection: IRC connection
            channel: Channel where command was issued
            nick: Nickname of user who issued command
        """
        if not self.last_song_data:
            connection.privmsg(
                channel, f"{nick}: No song data available yet, try again shortly"
            )
            return

        try:
            message = self.fetcher.format_song(self.last_song_data)
            connection.privmsg(channel, f"{nick}: {message}")
            print(f"[COMMAND] !playing from {nick} in {channel}")
        except Exception as e:
            print(f"[ERROR] Failed to handle !playing command: {e}")
            connection.privmsg(channel, f"{nick}: Error retrieving song info")

    def shutdown(self):
        """Gracefully shutdown the bot."""
        print(f"[INFO] Shutting down...")
        self.running = False
        self.connection.disconnect("Bot shutting down")
