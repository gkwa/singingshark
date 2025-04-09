import argparse
import logging
import os
import sys

import singingshark.cache
import singingshark.formatters
import singingshark.logger
import singingshark.parsers
import singingshark.speakers
import singingshark.writers

# Import specific items from our logger module
from singingshark.logger import LOGGING_LEVELS, SilentFilter


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch and reconstitute transcript from a webpage"
    )
    parser.add_argument(
        "--url",
        default="https://www.therecipepodcast.com/episodes/ep24-hummus",
        help="URL of the webpage containing the transcript",
    )
    parser.add_argument(
        "--output",
        default="transcript.txt",
        help="Output file to save the transcript, or '-' for stdout",
    )
    parser.add_argument(
        "--template",
        default="default",
        help="Template to use for formatting the transcript",
    )
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List available templates and exit",
    )
    parser.add_argument(
        "--speakers",
        help="Speaker mapping, format: 'SPEAKER_1=Alice,SPEAKER_2=Bob' or JSON '{\"SPEAKER_1\":\"Alice\"}'",
    )
    parser.add_argument(
        "--list-speakers",
        action="store_true",
        help="List speakers found in the transcript and exit",
    )

    # Cache-related arguments
    cache_group = parser.add_argument_group("Cache options")
    cache_group.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching (don't read or write to cache)",
    )
    cache_group.add_argument(
        "--ignore-cache",
        action="store_true",
        help="Ignore cache for reading but still update it with new data",
    )
    cache_group.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear the cache before fetching",
    )

    # Verbosity level
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase output verbosity (-v, -vv, -vvv)",
    )

    args = parser.parse_args()

    # Set up logger
    logger = singingshark.logger.setup_logger(args.verbose)

    # When outputting to stdout, we need to be careful not to mix log messages
    is_stdout_output = args.output == "-"

    # If using stdout for output, redirect logger to stderr
    if is_stdout_output:
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Create stderr handler for logging
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(LOGGING_LEVELS.get(args.verbose, logging.WARNING))

        # Re-add formatter and filter
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        stderr_handler.setFormatter(formatter)
        silent_filter = SilentFilter(args.verbose)
        stderr_handler.addFilter(silent_filter)

        # Add handler to logger
        logger.addHandler(stderr_handler)

    # Handle cache clearing if requested
    if args.clear_cache:
        cache = singingshark.cache.TranscriptCache()
        if args.url:
            logger.info(f"Clearing cache for {args.url}")
            cache.clear(args.url)
        else:
            logger.info("Clearing all cache entries")
            cache.clear()

    if args.list_templates:
        if args.verbose > 0:
            singingshark.formatters.list_available_templates()
        else:
            templates = singingshark.formatters.get_template_env().list_templates(
                extensions=["j2"]
            )
            for template in templates:
                print(f"{os.path.splitext(template)[0]}")
        sys.exit(0)

    # Cache settings
    use_cache = not args.no_cache
    ignore_cache = args.ignore_cache

    logger.info(f"Fetching transcript from {args.url}...")
    lines = singingshark.parsers.fetch_and_parse_transcript(
        args.url, use_cache=use_cache, ignore_cache=ignore_cache, verbosity=args.verbose
    )

    if not lines:
        logger.error("No transcript found or error occurred.")
        sys.exit(1)

    if args.list_speakers:
        speakers = singingshark.speakers.extract_speakers(lines)
        if args.verbose > 0:
            print("Speakers found in transcript:")
            for speaker in speakers:
                print(f"  - {speaker}")
            print("\nUse with --speakers option to map names, for example:")
            speaker_map_example = ",".join(
                f"{s}=Person{i + 1}" for i, s in enumerate(speakers[:2])
            )
            print(f'  --speakers "{speaker_map_example}"')
        else:
            for speaker in speakers:
                print(speaker)
        sys.exit(0)

    speaker_map = singingshark.speakers.parse_speaker_map(args.speakers)
    if speaker_map and args.verbose > 0:
        for orig, mapped in speaker_map.items():
            logger.info(f"Speaker mapping: {orig} -> {mapped}")

    transcript = singingshark.formatters.format_transcript_with_template(
        lines, args.template, speaker_map
    )
    singingshark.writers.write_transcript(transcript, args.output)

    # Only log the save message if not outputting to stdout
    if args.verbose > 0 and not is_stdout_output:
        logger.info(f"Transcript saved to {args.output}")
