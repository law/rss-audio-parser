import os
import tempfile
import xml.etree.ElementTree as ET

import requests
from pydub import AudioSegment


def extract_episode_number(url):
    """Extract episode identifier from the filename in the URL."""
    # Extract filename from URL, remove .m4a extension
    filename = url.split("/")[-1]
    return filename.rsplit(".m4a", 1)[0].strip()


def parse_rss_feed(url, limit=5):
    response = requests.get(url)
    response.raise_for_status()

    root = ET.fromstring(response.content)

    # Find all enclosure tags (usually contains media files)
    # Using XML namespace wildcard since RSS feeds might use different
    # namespaces
    items = root.findall(".//*enclosure")

    # Extract audio/mp4 URLs and lengths, build a list
    audio_files = []
    for item in items:
        url = item.get("url")
        content_type = item.get("type")
        length = item.get("length")

        if (
            url
            and content_type
            and "audio/mp4" in content_type.lower()
            and url.lower().endswith(".m4a")
        ):
            # Extract episode number from filename
            episode_num = extract_episode_number(url)

            # Store the raw length value from XML
            audio_files.append(
                {
                    "url": url,
                    "length": length if length else "Unknown",
                    "episode": episode_num,
                }
            )
    # lambda is unneeded b/c this RSS feed is pre-sorted
    # audio_files.sort(key=lambda x: x['episode'], reverse=True)
    return audio_files[:limit]


def analyze_audio_durations(audio_files):
    """Download and analyze audio files to get their actual duration."""
    for file in audio_files:
        try:
            # Create a temporary file to store the download
            with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as temp_file:
                print(f"\nDownloading episode {file['episode']}...")
                response = requests.get(file["url"], stream=True)
                response.raise_for_status()

                # Write the file
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)

                temp_file.flush()

                # Load with pydub, get duration (in ms), convert to minutes
                audio = AudioSegment.from_file(temp_file.name, format="m4a")
                duration_seconds = len(audio) / 1000.0

                file[
                    "duration"
                ] = f"{int(duration_seconds // 60)}:{int(duration_seconds % 60):02d}"

                # Clean up the temporary file
                os.unlink(temp_file.name)

                print(f"Episode {file['episode']} duration: {file['duration']}")

        except (requests.RequestException, IOError) as e:
            print(f"Error analyzing episode {file['episode']}: {e}")
            file["duration"] = "Error"

    return audio_files


def check_duration_threshold(audio_files, threshold_minutes=30):
    """Check if any audio files are shorter than the threshold and print warnings.

    Args:
        audio_files: List of dictionaries containing audio file information
        threshold_minutes: Minimum duration threshold in minutes (default: 30)
    """
    for file in audio_files:
        if "duration" in file and file["duration"] != "Error":
            minutes, seconds = map(int, file["duration"].split(":"))
            duration_minutes = minutes + seconds / 60

            if duration_minutes < threshold_minutes:
                # pylint: disable=line-too-long
                print(
                    f"\nWARNING: Episode {file['episode']} is below the {threshold_minutes} minute threshold"
                )
                print(f"         Duration: {file['duration']}")


def main():
    # pylint: disable=line-too-long
    rss_url = "https://url-ending-in-.xml-goes-here"
    limit = 10  # Show only the 10 most recent episodes

    try:
        audio_files = parse_rss_feed(rss_url, limit)

        if audio_files:
            print("\nFound audio/mp4 files:")
            print("\nAnalyzing audio durations...")
            audio_files_analyzed = analyze_audio_durations(audio_files)

            for file in audio_files_analyzed:
                print(f"\n{file['episode']}. URL: {file['url']}")
                print(f"   Size: {file['length']}")
                print(f"   Duration: {file['duration']}")

            # Check for episodes below threshold
            check_duration_threshold(audio_files_analyzed)
        else:
            print("\nNo audio/mp4 files found in the feed.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching RSS feed: {e}")
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
    except (requests.RequestException, ET.ParseError, IOError) as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
