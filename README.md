# RSS Audio Parser

A Python utility for parsing RSS feeds containing audio content, specifically designed to work with .m4a audio files. This tool downloads audio files from an RSS feed, analyzes their duration, and provides detailed information about each episode.

## Features

- Parses RSS feeds to extract audio file information
- Downloads and analyzes audio file durations
- Supports .m4a audio format
- Configurable limit for number of episodes to process
- Displays episode information including URL, file size, and duration
- Checks and warns if episode durations are below a configurable threshold (default: 30 minutes)

## Requirements

- Python 3.9 or higher
- Required packages:
  - requests>=2.31.0
  - pydub>=0.25.1

For development:
- black>=23.11.0
- pylint>=3.0.2
- pre-commit>=3.5.0

## Installation

1. Clone this repository
2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the script with:
```bash
python rss_audio_parser.py
```

The script will:
1. Fetch the RSS feed
2. Extract information about the audio files
3. Download each file temporarily to analyze its duration
4. Display information about each episode including:
   - Episode identifier
   - Download URL
   - File size
   - Duration
   - Warnings for episodes below the duration threshold

## Development

This project uses:
- Black for code formatting
- Pylint for code linting
- pre-commit hooks for code quality

To set up the development environment:
```bash
pip install -r requirements.txt
pre-commit install
```

To run pre-commit checks manually:
```bash
pre-commit run --all-files
```

This will run both black formatting and pylint checks on all files.
