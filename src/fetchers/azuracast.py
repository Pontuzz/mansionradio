"""AzuraCast API fetcher for radio station data."""

import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class AzuraCastFetcher:
    """Fetches current song data from AzuraCast API."""

    def __init__(self, api_url: str):
        self.api_url = api_url
        self.last_song_id = None

        # Reuse a persistent HTTPS connection across polls instead of
        # opening a fresh TCP+TLS handshake every 60s (1,440/day).
        # This avoids repeated handshake load on the hoster's server.
        # A connect-retry transparently handles stale keep-alive
        # connections (server may close idle connections between polls).
        self.session = requests.Session()
        retries = Retry(
            total=1,
            connect=1,
            read=0,
            status=0,
            allowed_methods=["GET"],
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        self.session.mount("http://", HTTPAdapter(max_retries=retries))

    def get_now_playing(self) -> Optional[Dict[str, Any]]:
        """Fetch current song from AzuraCast API.

        Returns:
            JSON response dict or None if request fails.
        """
        try:
            response = self.session.get(self.api_url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch from AzuraCast: {e}")
            return None

    def has_song_changed(self, data: Dict[str, Any]) -> bool:
        """Check if currently playing song changed.

        Args:
            data: Response from AzuraCast API

        Returns:
            True if song is different from last check, False otherwise.
        """
        if not data or "now_playing" not in data:
            return False

        try:
            current_song_id = data["now_playing"]["song"]["id"]
        except (KeyError, TypeError):
            logger.error("Invalid API response structure")
            return False

        if current_song_id != self.last_song_id:
            self.last_song_id = current_song_id
            return True

        return False

    def format_song(self, data: Dict[str, Any]) -> str:
        """Format song info as IRC message.

        Args:
            data: Response from AzuraCast API

        Returns:
            Formatted message string: "Now playing: Song [Album] by Artist"
        """
        try:
            now_playing = data["now_playing"]["song"]
            artist = now_playing.get("artist", "Unknown Artist")
            title = now_playing.get("title", "Unknown Title")
            album = now_playing.get("album", "")

            # Format: Now playing: Song [Album] by Artist
            if album:
                msg = f"♫ Now playing: {title} [{album}] by {artist}"
            else:
                msg = f"♫ Now playing: {title} by {artist}"

            return msg
        except (KeyError, TypeError) as e:
            logger.error(f"Failed to format song: {e}")
            return "♫ Error retrieving current song"
