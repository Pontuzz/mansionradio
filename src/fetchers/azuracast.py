"""AzuraCast API fetcher for radio station data."""

import requests
from typing import Optional, Dict, Any


class AzuraCastFetcher:
    """Fetches current song data from AzuraCast API."""

    def __init__(self, api_url: str):
        self.api_url = api_url
        self.last_song_id = None

    def get_now_playing(self) -> Optional[Dict[str, Any]]:
        """Fetch current song from AzuraCast API.

        Returns:
            JSON response dict or None if request fails.
        """
        try:
            response = requests.get(self.api_url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[ERROR] Failed to fetch from AzuraCast: {e}")
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
            print("[ERROR] Invalid API response structure")
            return False

        if current_song_id != self.last_song_id:
            self.last_song_id = current_song_id
            return True

        return False

    def format_song(self, data: Dict[str, Any]) -> str:
        """Format song info as IRC message with clear delimiters.

        Args:
            data: Response from AzuraCast API

        Returns:
            Formatted message string with clear artist | song | album separation.
        """
        try:
            now_playing = data["now_playing"]["song"]
            artist = now_playing.get("artist", "Unknown Artist")
            title = now_playing.get("title", "Unknown Title")
            album = now_playing.get("album", "")

            # Format with clear visual separation between fields
            # Artist | Song Title | Album (if available)
            parts = [f"Artist: {artist}", f"Song: {title}"]
            if album:
                parts.append(f"Album: {album}")

            msg = f"♫ {' | '.join(parts)}"

            return msg
        except (KeyError, TypeError) as e:
            print(f"[ERROR] Failed to format song: {e}")
            return "♫ Error retrieving current song"
