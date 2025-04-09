import json
import sys
import typing


def parse_speaker_map(speaker_arg: typing.Optional[str]) -> typing.Dict[str, str]:
    """Parse speaker mapping from command line argument."""
    speaker_map = {}
    if not speaker_arg:
        return speaker_map

    # Handle JSON format
    if speaker_arg.startswith("{"):
        try:
            return json.loads(speaker_arg)
        except json.JSONDecodeError:
            print(
                "Error parsing speaker map JSON. Using original speaker labels.",
                file=sys.stderr,
            )
            return speaker_map

    # Handle key=value format
    for mapping in speaker_arg.split(","):
        try:
            key, value = mapping.split("=")
            speaker_map[key.strip()] = value.strip()
        except ValueError:
            print(
                f"Invalid speaker mapping format: {mapping}. Skipping.", file=sys.stderr
            )

    return speaker_map


def extract_speakers(
    lines: typing.List[typing.Tuple[str, str, str]],
) -> typing.List[str]:
    """Extract unique speaker identifiers from transcript lines."""
    return sorted(set(speaker for _, speaker, _ in lines))
