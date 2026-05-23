"""IRC bot for announcing radio station songs.

Architecture inspired by eggdrop's battle-tested design patterns:
- Explicit state machine for connection phases
- Raw message parsing for SASL (irc.bot event system can't handle AUTHENTICATE +)
- Rate limiting awareness (respects server penalty system)
- Clean separation of concerns (connection, auth, polling, announcing)
"""

import irc.bot
import irc.connection
import ssl
import time
import threading
import logging
import base64
from enum import Enum
from fetchers.azuracast import AzuraCastFetcher

logger = logging.getLogger(__name__)


class BotState(Enum):
    """Explicit connection states following eggdrop's lifecycle model."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"  # CAP LS sent, awaiting response
    AUTHENTICATING = "authenticating"  # SASL in progress
    REGISTERED = "registered"  # 001 WELCOME received
    ACTIVE = "active"  # Channels joined, ready to announce


def ssl_wrapper(sock):
    """Wrap a socket with TLS/SSL for IRC connection."""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    return ssl_context.wrap_socket(sock, server_hostname=None)


class RadioBot(irc.bot.SingleServerIRCBot):
    """IRC bot that announces currently playing songs from a radio station.

    Design principles from eggdrop:
    - Never assume connection state; track it explicitly
    - Parse raw IRC for SASL (event system insufficient)
    - Respect server penalties (don't fight rate limiting)
    - Clean state cleanup on errors
    """

    def __init__(self, config):
        """Initialize the bot with configuration.

        Args:
            config: Dictionary with keys:
                - server: IRC server address
                - port: IRC server port
                - nickname: Bot's IRC nickname
                - sasl_username: SASL username (optional)
                - sasl_password: SASL password (optional)
                - channels: List of channels to join
                - api_url: AzuraCast API endpoint
                - poll_interval: Seconds between API polls
        """
        self.config = config

        # Setup TLS connection factory
        factory = irc.connection.Factory(wrapper=ssl_wrapper)

        # Initialize parent class
        irc.bot.SingleServerIRCBot.__init__(
            self,
            server_list=[(config["server"], config["port"])],
            nickname=config["nickname"],
            realname=config["nickname"],
            connect_factory=factory,
        )

        # State machine
        self.state = BotState.DISCONNECTED
        self.last_state = BotState.DISCONNECTED

        # Connection tracking
        self.sasl_enabled = bool(config.get("sasl_password"))
        self.sasl_authenticated = False
        self.cap_ack_received = False
        self.cap_multiline_in_progress = False  # Track multiline CAP LS messages

        # Song data
        self.fetcher = AzuraCastFetcher(config["api_url"])
        self.last_song_data = None
        self.last_announcement_time = 0  # Track for rate limiting

        # Lifecycle control
        self.running = True
        self.poller_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.poller_thread.start()

        logger.info("=" * 60)
        logger.info("RadioBot initialized")
        logger.info(f"Server: {config['server']}:{config['port']}")
        logger.info(f"Channels: {', '.join(config['channels'])}")
        logger.info(f"SASL: {'enabled' if self.sasl_enabled else 'disabled'}")
        logger.info(f"Poll interval: {config['poll_interval']}s")
        logger.info("=" * 60)

    def _set_state(self, new_state: BotState):
        """Set state and log transition."""
        if self.state != new_state:
            self.last_state = self.state
            self.state = new_state
            logger.info(
                f"State transition: {self.last_state.value} → {new_state.value}"
            )

    def _connect(self):
        """Override parent's _connect to send CAP LS at the right moment.

        Following eggdrop's pattern (servmsg.c:2083), CAP LS must be sent
        immediately after socket connection, before NICK/USER complete.
        """
        logger.debug("_connect() called")
        self._set_state(BotState.CONNECTING)

        # Call parent to establish connection and send NICK/USER
        irc.bot.SingleServerIRCBot._connect(self)

        # Send CAP LS to negotiate capabilities (including SASL if enabled)
        # This must happen early, while registration is in progress
        if self.connection:
            try:
                # Small delay to ensure socket is ready
                time.sleep(0.05)
                self.connection.send_raw("CAP LS 302")
                logger.debug("Sent: CAP LS 302")
            except Exception as e:
                logger.error(f"Failed to send CAP LS: {e}", exc_info=True)

    def on_connect(self, connection, event):
        """Called when socket connection is established (not IRC registration).

        At this point, NICK/USER may not have been sent yet by parent.
        We rely on _connect() override to send CAP LS.
        """
        logger.debug("Socket connected (on_connect event)")

    def on_cap(self, connection, event):
        """Called when server sends CAP message (capability negotiation).

        Event arguments contain the parsed CAP response:
        - For CAP LS: ["LS", "*", "capabilities..."] or ["LS", "capabilities..."]
        - For CAP ACK: ["ACK", "capabilities..."]
        """
        try:
            args = event.arguments if hasattr(event, "arguments") else []
            if len(args) < 1:
                return

            subcommand = args[0]
            logger.debug(f"CAP {subcommand}: {args[1:] if len(args) > 1 else ''}")

            if subcommand == "LS":
                # CAP LS [*] :capabilities
                # Check if multiline: if args has "*" it means more coming
                is_multiline = len(args) >= 2 and args[1] == "*"
                logger.debug(
                    f"CAP LS - multiline: {is_multiline}, "
                    f"was_in_progress: {self.cap_multiline_in_progress}"
                )

                if is_multiline:
                    # Multiline message, wait for rest
                    self.cap_multiline_in_progress = True
                    return
                elif self.cap_multiline_in_progress:
                    # Final message of multiline sequence
                    self.cap_multiline_in_progress = False
                    logger.info("CAP LS multiline complete")

                # Now send CAP REQ if SASL enabled
                if self.sasl_enabled:
                    logger.info("Requesting SASL capability")
                    connection.send_raw("CAP REQ :sasl")
                    logger.debug("Sent: CAP REQ :sasl")

            elif subcommand == "ACK":
                # CAP ACK :capabilities
                caps_str = " ".join(str(a) for a in args[1:])
                if "sasl" in caps_str:
                    logger.info("Server acknowledged SASL capability")
                    self.cap_ack_received = True
                    self._set_state(BotState.AUTHENTICATING)

                    # Begin SASL authentication
                    sasl_username = self.config.get(
                        "sasl_username", self.config["nickname"]
                    )
                    logger.info(f"Starting SASL PLAIN as '{sasl_username}'")
                    connection.send_raw("AUTHENTICATE PLAIN")
                    logger.debug("Sent: AUTHENTICATE PLAIN")

        except Exception as e:
            logger.error(f"Error in on_cap: {e}", exc_info=True)

    def on_authenticate(self, connection, event):
        """Called when server sends AUTHENTICATE response during SASL.

        The + is in event.target, not event.arguments.
        """
        try:
            # AUTHENTICATE + comes with + in the target field
            target = event.target if hasattr(event, "target") else ""
            logger.debug(f"AUTHENTICATE: target='{target}'")

            if target == "+":
                # Server ready for credentials
                logger.info("Server sent AUTHENTICATE +")
                self._send_sasl_credentials(connection)

        except Exception as e:
            logger.error(f"Error in on_authenticate: {e}", exc_info=True)

    def on_saslsuccess(self, connection, event):
        """Called when SASL authentication succeeds (numeric 903)."""
        try:
            logger.info("SASL authentication successful (903)")
            self.sasl_authenticated = True
            connection.send_raw("CAP END")
            logger.debug("Sent: CAP END")
        except Exception as e:
            logger.error(f"Error in on_saslsuccess: {e}", exc_info=True)

    def on_saslfail(self, connection, event):
        """Called when SASL authentication fails (numeric 904, 905, 906)."""
        try:
            # Event type contains the numeric code (904, 905, or 906)
            numeric = event.type if hasattr(event, "type") else "unknown"
            msg = " ".join(event.arguments) if event.arguments else "unknown error"
            logger.error(f"SASL authentication failed: numeric={numeric}, msg={msg}")
            self.sasl_authenticated = False
            connection.send_raw("CAP END")
            logger.debug("Sent: CAP END")
        except Exception as e:
            logger.error(f"Error in on_saslfail: {e}", exc_info=True)

    def _poll_loop(self):
        """Poll API continuously, respecting connection state.

        Only announces when in ACTIVE state.
        Follows eggdrop's principle: don't act until ready.
        """
        logger.info("Poll loop started")
        while self.running:
            try:
                # Wait until bot is active and connected
                if self.state != BotState.ACTIVE:
                    time.sleep(self.config["poll_interval"])
                    continue

                logger.debug("Polling API for current song...")
                data = self.fetcher.get_now_playing()

                if not data:
                    logger.warning("API returned no data")
                    time.sleep(self.config["poll_interval"])
                    continue

                # Store latest song data for !playing command
                self.last_song_data = data

                # Announce if song changed
                if self.fetcher.has_song_changed(data):
                    message = self.fetcher.format_song(data)
                    logger.info(f"Song changed: {message}")
                    self._announce(message)

            except Exception as e:
                logger.error(f"Poll loop error: {e}", exc_info=True)

            time.sleep(self.config["poll_interval"])

    def _announce(self, message: str):
        """Send message to IRC channels.

        Respects rate limiting:
        - Never announce faster than poll interval
        - Space out messages to respect server penalties
        """
        now = time.time()
        time_since_last = now - self.last_announcement_time

        if time_since_last < self.config["poll_interval"]:
            logger.debug(
                f"Rate limiting: {time_since_last:.1f}s < {self.config['poll_interval']}s, "
                "skipping announcement"
            )
            return

        self.last_announcement_time = now

        for channel in self.config["channels"]:
            try:
                self.connection.privmsg(channel, message)
                logger.info(f"[ANNOUNCE] {channel}: {message}")
            except Exception as e:
                logger.error(f"Failed to announce to {channel}: {e}")

    def _send_sasl_credentials(self, connection):
        """Send SASL PLAIN credentials to server.

        SASL PLAIN format (RFC 4616): [authzid] UTF8NUL authcid UTF8NUL passwd
        For our use: "" NUL username NUL password
        Eggdrop implementation: sasl.c:156-172
        """
        sasl_username = self.config.get("sasl_username", self.config["nickname"])
        sasl_password = self.config.get("sasl_password", "")

        # Build auth string: \0username\0password
        # Using empty authzid (first field) is standard
        auth_string = f"\0{sasl_username}\0{sasl_password}"
        auth_bytes = auth_string.encode("utf-8")
        auth_b64 = base64.b64encode(auth_bytes).decode("ascii")

        logger.info(f"Sending SASL credentials for {sasl_username}")
        connection.send_raw(f"AUTHENTICATE {auth_b64}")
        logger.debug(f"Sent: AUTHENTICATE {auth_b64[:20]}...")

    def on_welcome(self, connection, event):
        """Called when server sends 001 WELCOME (registration complete).

        At this point:
        - Socket is connected
        - NICK/USER accepted by server
        - SASL authentication is complete (if enabled)

        Eggdrop pattern (servmsg.c:353-388): update server info, then join channels.
        """
        logger.info("Received 001 WELCOME - registration complete")
        self._set_state(BotState.REGISTERED)

        # Verify SASL completed if enabled
        if self.sasl_enabled:
            if not self.sasl_authenticated:
                logger.warning(
                    "SASL enabled but authentication was not completed. "
                    "May fail to join registered-only channels."
                )
            else:
                logger.info("SASL authentication verified")

        # Set +b flag to indicate this is a bot
        connection.send_raw(f"MODE {self.connection.get_nickname()} +b")
        logger.info("Set +b (bot) flag")
        connection.send_raw(f"MODE {self.connection.get_nickname()} +b")
        logger.info("Set +b (bot) flag")

        # Now ready to join channels
        self._join_channels(connection)

    def _join_channels(self, connection):
        """Join all configured channels.

        Called only after 001 WELCOME received.
        Eggdrop pattern (servmsg.c:393-402): join with keys if specified.
        """
        logger.info(f"Joining {len(self.config['channels'])} channel(s)")

        for channel in self.config["channels"]:
            try:
                connection.join(channel)
                logger.info(f"Joined: {channel}")
            except Exception as e:
                logger.error(f"Failed to join {channel}: {e}")

        self._set_state(BotState.ACTIVE)
        logger.info("All channels joined - bot is now active")

    def on_disconnect(self, connection, event):
        """Called when bot disconnects from server.

        Eggdrop pattern: clear state and prepare for reconnect.
        """
        logger.warning("Disconnected from IRC server")
        self._set_state(BotState.DISCONNECTED)

        # Reset authentication state
        self.sasl_authenticated = False
        self.cap_ack_received = False

        # irc.bot will automatically reconnect, but wait a bit
        if self.running:
            logger.info("Reconnecting in 10 seconds...")
            time.sleep(10)

    def on_join(self, connection, event):
        """Called when bot successfully joins a channel."""
        channel = event.target
        logger.debug(f"Successfully joined {channel}")

    def on_part(self, connection, event):
        """Called when bot leaves a channel."""
        channel = event.target
        logger.debug(f"Left {channel}")

    def on_kick(self, connection, event):
        """Called when bot is kicked from a channel."""
        channel = event.target
        kicker = event.source.nick if event.source else "unknown"
        reason = event.arguments[0] if event.arguments else "no reason"
        logger.warning(f"KICKED from {channel} by {kicker}: {reason}")
        # Try to rejoin
        logger.info("Attempting to rejoin after kick...")
        connection.join(channel)

    def on_error(self, connection, event):
        """Called when IRC server sends an error."""
        logger.error(f"IRC server error: {event}")

    def on_pubmsg(self, connection, event):
        """Called when a public message is posted in a channel."""
        try:
            message = event.arguments[0]
            nick = event.source.nick
            channel = event.target

            # Handle !playing command
            if message.lower().startswith("!playing"):
                self._handle_playing_command(connection, channel, nick)
        except Exception as e:
            logger.error(f"Error in on_pubmsg: {e}", exc_info=True)

    def _handle_playing_command(self, connection, channel, nick):
        """Handle the !playing command.

        Respects rate limiting: don't query API more than poll interval.
        """
        if not self.last_song_data:
            connection.privmsg(
                channel, f"{nick}: No song data available yet, try again shortly"
            )
            return

        try:
            message = self.fetcher.format_song(self.last_song_data)
            connection.privmsg(channel, f"{nick}: {message}")
            logger.debug(f"!playing from {nick} in {channel}")
        except Exception as e:
            logger.error(f"Error handling !playing: {e}")
            connection.privmsg(channel, f"{nick}: Error retrieving song info")

    def shutdown(self):
        """Gracefully shutdown the bot.

        Eggdrop pattern: nuke_server() sends QUIT, clears state.
        """
        logger.info("Shutting down bot")
        self.running = False

        try:
            if self.connection:
                self.connection.disconnect("Bot shutting down")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")

        logger.info("Bot shutdown complete")
