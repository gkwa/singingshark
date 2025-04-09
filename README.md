# Singingshark {#singingshark-1}

Claude.ai wrote this as a one-off to help me convert this transcript:

https://play.pocketcasts.com/podcasts/d2c229f0-53fc-013c-9ec8-0acc26574db2/776ef7aa-e647-40b8-be34-703ae66bff92

to different formats.




## Overview

Singingshark is a command-line utility that extracts transcript data
from web pages and lets you format it in various ways. It\'s especially
useful for podcast transcripts that use WebVTT format embedded in HTML.

## Features

- Extract transcripts from web pages
- Convert between multiple output formats using customizable templates
- Replace generic speaker identifiers with actual names
- Cache transcript data to avoid redundant network requests
- Write output to files or stdout
- Control verbosity with granular logging levels

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/singingshark.git
cd singingshark

# Install the package
pip install -e .
```

## Usage Examples

### Basic Usage

```bash
# Download and save a transcript with default formatting
singingshark --url "https://www.therecipepodcast.com/episodes/ep24-hummus" --output transcript.txt

# Output transcript to stdout
singingshark --output -

# Pipe transcript to another command
singingshark --output - | grep "specific text"
```

### Verbosity Control

The tool runs silently by default, showing no output unless there\'s an
error:

```bash
# Increase verbosity (each -v adds more detail)
singingshark -v
singingshark -vv
singingshark -vvv
```

### Available Templates

```bash
# List all available templates
singingshark --list-templates

# Save as plain text without timestamps
singingshark --template plain --output transcript.txt

# Save as markdown
singingshark --template markdown --output transcript.md

# Save as JSON for programmatic use
singingshark --template json --output transcript.json

# Save in conversation format (grouped by speaker)
singingshark --template conversation --output transcript.txt

# Save without timestamps
singingshark --template no_timestamps --output transcript.txt
```

### Working with Speakers

```bash
# List speakers found in the transcript
singingshark --list-speakers

# Replace generic speaker identifiers with real names
singingshark --speakers "SPEAKER_1=Robin,SPEAKER_2=Deb,SPEAKER_3=Kenji" --output transcript.txt

# Use JSON format for speaker mapping
singingshark --speakers '{"SPEAKER_1":"Robin","SPEAKER_2":"Deb"}' --output transcript.txt
```

### Cache Management

```bash
# Fetch without using cache
singingshark --no-cache

# Ignore cache for reading but still update it with new data
singingshark --ignore-cache

# Clear the cache for a specific URL before fetching
singingshark --url "https://example.com/podcast" --clear-cache

# Clear the entire cache
singingshark --clear-cache
```

### Combining Options

```bash
# Use markdown template with named speakers
singingshark --template markdown --speakers "SPEAKER_1=Robin" --output transcript.md

# Save a conversation-style transcript with named speakers
singingshark --template conversation --speakers "SPEAKER_1=Robin,SPEAKER_2=Deb" --output transcript.txt

# Force fresh data with named speakers
singingshark --no-cache --speakers "SPEAKER_1=Host,SPEAKER_2=Guest" --output transcript.txt

# Refresh cache but use named speakers and no timestamps
singingshark --ignore-cache --output output.txt --template no_timestamps --speakers "SPEAKER_1=Robin,SPEAKER_2=Deb,SPEAKER_3=Kenji"

# Output conversation format to stdout with verbose logging
singingshark --template conversation --speakers "SPEAKER_1=Host" --output - -v
```

## Cheatsheet

Here are some common command patterns:

```bash
# Basic transcript extraction
singingshark

# Using a specific URL
singingshark --url "https://example.com/podcast-episode"

# Using a specific template
singingshark --template markdown --output transcript.md

# Replacing speakers and using no timestamps
singingshark --output output.txt --template no_timestamps --speakers "SPEAKER_1=Robin,SPEAKER_2=Deb,SPEAKER_3=Kenji"

# Creating JSON output with named speakers for data processing
singingshark --template json --speakers "SPEAKER_1=Host,SPEAKER_2=Guest" --output data.json

# Fetch fresh data (bypass cache)
singingshark --no-cache --url "https://example.com/podcast-episode"

# Refresh cache data but still use it to update the cache
singingshark --ignore-cache --url "https://example.com/podcast-episode"

# Output directly to stdout for piping to other tools
singingshark --template plain --output - | grep "interesting phrase"
```

## Creating Custom Templates

Add new templates to the `src/singingshark/templates`{.verbatim}
directory with a `.j2`{.verbatim} extension. Templates use Jinja2 syntax
and have access to the `lines`{.verbatim} variable, which is a list of
tuples: `(timestamp, speaker, text)`{.verbatim}.

Example template:

```jinja
{# Custom template example #}
# {{ lines|length }} Lines Transcript

{% for timestamp, speaker, text in lines %}
- {{ speaker }} ({{ timestamp }}): {{ text }}
{% endfor %}
```

## Cache

Singingshark caches transcripts to improve performance and reduce
bandwidth usage. The cache is stored in
`~/.singingshark/cache/`{.verbatim} and entries expire after 24 hours by
default.

To manage the cache:

- Use `--no-cache`{.verbatim} to disable caching completely (don\'t read
  from or write to cache)
- Use `--ignore-cache`{.verbatim} to fetch fresh data but still update
  the cache with it
- Use `--clear-cache`{.verbatim} to clear the entire cache
- Use `--clear-cache`{.verbatim} with `--url`{.verbatim} to clear the
  cache for a specific URL

## Logging

Singingshark provides different levels of verbosity:

- No flag (default): Silent operation, only errors displayed
- `-v`{.verbatim}: Basic information about processing steps
- `-vv`{.verbatim}: More detailed information about operations
- `-vvv`{.verbatim}: Full debug information including HTML parsing
  details
