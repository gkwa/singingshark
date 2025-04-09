import hashlib
import json
import logging
import os
import time
import typing

# Define the cache storage location
CACHE_DIR = os.path.expanduser("~/.singingshark/cache")
# Default cache expiration in seconds (24 hours)
DEFAULT_CACHE_EXPIRY = 86400


class TranscriptCache:
    """
    Cache for transcript data to avoid redundant network requests.
    """

    def __init__(
        self, cache_dir: typing.Optional[str] = None, expiry: int = DEFAULT_CACHE_EXPIRY
    ):
        self.cache_dir = cache_dir or CACHE_DIR
        self.expiry = expiry
        self.logger = logging.getLogger("singingshark")
        self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        """Ensure the cache directory exists."""
        if not os.path.exists(self.cache_dir):
            self.logger.debug(f"Creating cache directory: {self.cache_dir}")
            os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_key(self, url: str) -> str:
        """Generate a unique cache key for the URL."""
        cache_key = hashlib.md5(url.encode()).hexdigest()
        self.logger.debug(f"Cache key for {url}: {cache_key}")
        return cache_key

    def _get_cache_path(self, key: str) -> str:
        """Get the file path for a cache key."""
        cache_path = os.path.join(self.cache_dir, f"{key}.json")
        self.logger.debug(f"Cache path: {cache_path}")
        return cache_path

    def get(
        self, url: str
    ) -> typing.Optional[typing.List[typing.Tuple[str, str, str]]]:
        """
        Retrieve transcript data from cache if available and not expired.

        Args:
            url: The URL of the transcript source

        Returns:
            The cached transcript data or None if not found or expired
        """
        key = self._get_cache_key(url)
        cache_path = self._get_cache_path(key)

        if not os.path.exists(cache_path):
            self.logger.debug(f"Cache file not found: {cache_path}")
            return None

        try:
            self.logger.debug(f"Reading cache file: {cache_path}")
            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            # Check if cache has expired
            cached_time = cache_data.get("timestamp", 0)
            cache_age = time.time() - cached_time
            self.logger.debug(
                f"Cache age: {cache_age:.2f} seconds (expires after {self.expiry} seconds)"
            )

            if cache_age > self.expiry:
                self.logger.debug("Cache expired")
                return None

            # Return the cached transcript lines
            lines = [tuple(line) for line in cache_data.get("lines", [])]
            self.logger.debug(f"Retrieved {len(lines)} lines from cache")
            return lines
        except (json.JSONDecodeError, KeyError, IOError) as e:
            self.logger.debug(f"Error reading cache: {e}")
            # If there's any error reading the cache, return None
            return None

    def set(self, url: str, lines: typing.List[typing.Tuple[str, str, str]]) -> None:
        """
        Store transcript data in the cache.

        Args:
            url: The URL of the transcript source
            lines: The transcript data to cache
        """
        key = self._get_cache_key(url)
        cache_path = self._get_cache_path(key)

        cache_data = {"url": url, "timestamp": time.time(), "lines": lines}

        try:
            self.logger.debug(f"Writing {len(lines)} lines to cache: {cache_path}")
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            self.logger.debug("Cache updated successfully")
        except IOError as e:
            self.logger.warning(f"Error writing to cache: {e}")
            # If we can't write to the cache, just continue without caching
            pass

    def clear(self, url: typing.Optional[str] = None) -> None:
        """
        Clear items from the cache.

        Args:
            url: If provided, clear only the cache for this URL.
                 If None, clear the entire cache.
        """
        if url:
            # Clear specific URL cache
            key = self._get_cache_key(url)
            cache_path = self._get_cache_path(key)
            if os.path.exists(cache_path):
                self.logger.debug(f"Removing cache file: {cache_path}")
                os.remove(cache_path)
                self.logger.debug("Cache cleared for URL")
        else:
            # Clear all cache
            self.logger.debug(f"Clearing all cache files in: {self.cache_dir}")
            count = 0
            for filename in os.listdir(self.cache_dir):
                if filename.endswith(".json"):
                    os.remove(os.path.join(self.cache_dir, filename))
                    count += 1
            self.logger.debug(f"Removed {count} cache files")
