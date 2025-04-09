import html.parser
import logging
import re
import typing
import urllib.request

import singingshark.cache


class TranscriptParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_transcript = False
        self.current_time = None
        self.current_speaker = None
        self.lines = []
        self.in_p_tag = False
        self.current_text = ""
        self.logger = logging.getLogger("singingshark")

    def handle_starttag(self, tag, attrs):
        self.logger.debug(f"Start tag: {tag}")
        if tag == "div" and any(
            attr
            for attr in attrs
            if attr[0] == "class" and "accordion-item__dropdown" in attr[1]
        ):
            self.logger.debug("Found transcript container div")
            self.in_transcript = True
        elif tag == "p" and self.in_transcript:
            self.in_p_tag = True
            self.current_text = ""

    def handle_endtag(self, tag):
        self.logger.debug(f"End tag: {tag}")
        if tag == "div" and self.in_transcript:
            self.logger.debug("Exiting transcript container div")
            self.in_transcript = False
        elif tag == "p" and self.in_transcript:
            self.in_p_tag = False
            if self.current_text.strip().startswith("00:"):
                # This is a timestamp line
                self.current_time = self.current_text.strip()
                self.logger.debug(f"Found timestamp: {self.current_time}")
            elif self.current_text.strip().startswith("<v "):
                # This is a speaker line with text
                match = re.match(r"<v ([^>]+)>(.+)", self.current_text.strip())
                if match:
                    self.current_speaker = match.group(1)
                    text = match.group(2)
                    self.logger.debug(
                        f"Found line - Speaker: {self.current_speaker}, Text: {text[:30]}..."
                    )
                    if self.current_time:
                        self.lines.append(
                            (self.current_time, self.current_speaker, text)
                        )
            self.current_text = ""

    def handle_data(self, data):
        if self.in_p_tag and self.in_transcript:
            self.current_text += data


def fetch_and_parse_transcript(
    url: str, use_cache: bool = True, ignore_cache: bool = False, verbosity: int = 0
) -> typing.List[typing.Tuple[str, str, str]]:
    """
    Fetch and parse a transcript from a URL, with optional caching.

    Args:
        url: The URL to fetch the transcript from
        use_cache: Whether to use the cache (default: True)
        ignore_cache: Whether to ignore the cache but still update it (default: False)
        verbosity: Verbosity level

    Returns:
        A list of transcript lines as (timestamp, speaker, text) tuples
    """
    logger = logging.getLogger("singingshark")
    cache = singingshark.cache.TranscriptCache()

    # Try to get from cache first if caching is enabled and not ignoring cache
    if use_cache and not ignore_cache:
        logger.info("Checking cache...")
        cached_data = cache.get(url)
        if cached_data:
            logger.info("Using cached transcript data")
            logger.debug(f"Found {len(cached_data)} lines in cache")
            return cached_data
        else:
            logger.info("No cached data found or cache expired")
    elif ignore_cache:
        logger.info("Ignoring cache for reading")
    elif not use_cache:
        logger.info("Cache disabled")

    try:
        logger.info(f"Fetching transcript from {url}...")
        with urllib.request.urlopen(url) as response:
            html = response.read().decode("utf-8")
            logger.debug(f"Received {len(html)} bytes of HTML")

            parser = TranscriptParser()
            parser.feed(html)

            logger.info(f"Parsed {len(parser.lines)} lines from transcript")

            # Cache the results if caching is enabled (even if we ignored it for reading)
            if use_cache and parser.lines:
                logger.info("Updating cache with new data")
                cache.set(url, parser.lines)

            return parser.lines
    except Exception as e:
        logger.error(f"Error fetching or parsing the transcript: {e}")
        return []
