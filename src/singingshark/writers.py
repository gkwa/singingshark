import sys


def write_transcript(transcript: str, output_file: str) -> None:
    """
    Write transcript content to a file or stdout.

    Args:
        transcript: The transcript content to write
        output_file: The file to write to, or '-' for stdout
    """
    if output_file == "-":
        # Write to stdout
        sys.stdout.write(transcript)
    else:
        # Write to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcript)
