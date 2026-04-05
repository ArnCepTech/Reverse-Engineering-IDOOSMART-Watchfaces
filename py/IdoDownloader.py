import os
import sys
import argparse
import requests
import zipfile
from pathlib import Path
from urllib.parse import urljoin

# Constants
BASE_URL = "https://life-content.idoocloud.com"
DIAL_PATH = "/dial/"
SPORT_ICON_PATH = "/sportIcon/appFile/"
FILE_EXTENSION = ".zip"


class IdoDownloader:
    """Main downloader class for Idoo Cloud content (ZIP files only)."""

    def __init__(self, output_dir="downloads", extract=False, verbose=False):
        self.output_dir = Path(output_dir)
        self.extract = extract
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'IdoDownloader/1.0 (Cross-platform Console App)'
        })

    def log(self, message, error=False):
        """Print log messages if verbose mode is on or if it's an error."""
        if self.verbose or error:
            prefix = "[ERROR] " if error else "[INFO] "
            print(prefix + message, file=sys.stderr if error else sys.stdout)

    def ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download_zip(self, url, destination_path, description=""):
        """
        Download a ZIP file from URL to destination path.
        Returns True on success, False on failure.
        """
        try:
            self.log(f"Downloading {description} from {url}")
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()

            # Check if content is ZIP (or at least has reasonable size)
            content_type = response.headers.get('Content-Type', '')
            if 'zip' not in content_type and not url.endswith('.zip'):
                self.log(f"Warning: Expected ZIP but got {content_type}", error=False)

            # Write file
            with open(destination_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = destination_path.stat().st_size
            self.log(f"Successfully downloaded: {destination_path} ({file_size} bytes)")

            # Extract if requested
            if self.extract:
                self.extract_zip(destination_path)

            return True

        except requests.exceptions.RequestException as e:
            self.log(f"Download failed: {e}", error=True)
            return False
        except Exception as e:
            self.log(f"Unexpected error: {e}", error=True)
            return False

    def extract_zip(self, zip_path):
        """Extract ZIP file to a folder named after the ZIP file (without extension)."""
        try:
            extract_dir = zip_path.parent / zip_path.stem
            extract_dir.mkdir(exist_ok=True)

            self.log(f"Extracting {zip_path} to {extract_dir}")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            self.log(f"Extraction complete: {extract_dir}")
        except zipfile.BadZipFile:
            self.log(f"Error: {zip_path} is not a valid ZIP file", error=True)
        except Exception as e:
            self.log(f"Extraction failed: {e}", error=True)

    def download_dial(self, uuid, output_filename=None):
        """
        Download a dial ZIP file by UUID.
        URL pattern: https://life-content.idoocloud.com/dial/{uuid}.zip
        """
        if not output_filename:
            output_filename = f"dial_{uuid}{FILE_EXTENSION}"

        url = urljoin(BASE_URL, f"{DIAL_PATH}{uuid}{FILE_EXTENSION}")
        destination = self.output_dir / output_filename

        self.ensure_output_dir()
        return self.download_zip(url, destination, description=f"Dial (UUID: {uuid})")

    def download_sport_icon(self, uuid, output_filename=None):
        """
        Download a sport icon ZIP file by UUID.
        URL pattern: https://life-content.idoocloud.com/sportIcon/appFile/{uuid}.zip
        """
        if not output_filename:
            output_filename = f"sporticon_{uuid}{FILE_EXTENSION}"

        url = urljoin(BASE_URL, f"{SPORT_ICON_PATH}{uuid}{FILE_EXTENSION}")
        destination = self.output_dir / output_filename

        self.ensure_output_dir()
        return self.download_zip(url, destination, description=f"Sport Icon (UUID: {uuid})")

    def download_batch(self, items):
        """
        Download multiple items.
        items: list of tuples (type, uuid, [optional filename])
        type: 'dial' or 'sport'
        """
        success_count = 0
        total = len(items)

        for idx, item in enumerate(items, 1):
            item_type = item[0].lower()
            uuid = item[1]
            filename = item[2] if len(item) > 2 else None

            self.log(f"Processing {idx}/{total}: {item_type} - {uuid}")

            if item_type == 'dial':
                if self.download_dial(uuid, filename):
                    success_count += 1
            elif item_type == 'sport' or item_type == 'sporticon':
                if self.download_sport_icon(uuid, filename):
                    success_count += 1
            else:
                self.log(f"Unknown type: {item_type}. Use 'dial' or 'sport'", error=True)

        self.log(f"Batch download complete: {success_count}/{total} successful")
        return success_count


def main():
    parser = argparse.ArgumentParser(
        description="IdoDownloader - Download dials and sport icons (.zip files) from life-content.idoocloud.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s dial 550e8400-e29b-41d4-a716-446655440000
  %(prog)s sport 550e8400-e29b-41d4-a716-446655440000
  %(prog)s dial 550e8400-e29b-41d4-a716-446655440000 -o my_dial.zip
  %(prog)s dial uuid1 dial uuid2 sport uuid3 -d ./my_downloads --extract
  %(prog)s -f uuids.txt
        """
    )

    parser.add_argument(
        'items',
        nargs='*',
        help='Items to download: type UUID [type UUID ...] where type is "dial" or "sport"'
    )

    parser.add_argument(
        '-d', '--output-dir',
        default='downloads',
        help='Output directory (default: downloads)'
    )

    parser.add_argument(
        '-o', '--output-filename',
        help='Output filename for single download (use with single UUID)'
    )

    parser.add_argument(
        '--extract',
        action='store_true',
        help='Extract ZIP files after download'
    )

    parser.add_argument(
        '-f', '--file',
        help='Read UUIDs from file (format: type UUID per line, e.g., "dial 1234-5678" or "sport 8765-4321")'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Create downloader instance
    downloader = IdoDownloader(
        output_dir=args.output_dir,
        extract=args.extract,
        verbose=args.verbose
    )

    # Collect items to download
    items = []

    # Read from file if provided
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)

        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) < 2:
                    print(f"Warning: Line {line_num} invalid (expected 'type UUID'), skipping: {line}", file=sys.stderr)
                    continue
                item_type = parts[0].lower()
                uuid = parts[1]
                filename = parts[2] if len(parts) > 2 else None
                if item_type in ('dial', 'sport', 'sporticon'):
                    items.append((item_type, uuid, filename))
                else:
                    print(f"Warning: Line {line_num} unknown type '{item_type}', skipping", file=sys.stderr)

    # Parse command line items
    i = 0
    while i < len(args.items):
        item_type = args.items[i].lower()
        if item_type in ('dial', 'sport', 'sporticon'):
            if i + 1 >= len(args.items):
                print(f"Error: Missing UUID for type '{item_type}'", file=sys.stderr)
                sys.exit(1)
            uuid = args.items[i + 1]
            # Handle optional filename (if next arg isn't a known type)
            filename = None
            if i + 2 < len(args.items) and args.items[i + 2].lower() not in ('dial', 'sport', 'sporticon'):
                filename = args.items[i + 2]
                i += 3
            else:
                i += 2
            items.append((item_type, uuid, filename))
        else:
            print(f"Error: Unknown type '{item_type}'. Use 'dial' or 'sport'", file=sys.stderr)
            sys.exit(1)

    # Handle single item with output filename
    if len(items) == 1 and args.output_filename and args.output_filename != 'downloads':
        # Override the filename for the single item
        items[0] = (items[0][0], items[0][1], args.output_filename)

    # Check if we have items to download
    if not items:
        print("Error: No items specified. Use 'dial UUID' or 'sport UUID', or provide a file with -f", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    # Execute downloads
    success_count = downloader.download_batch(items)

    if success_count == len(items):
        print(f"\n✓ All {success_count} downloads completed successfully!")
        sys.exit(0)
    elif success_count > 0:
        print(f"\n⚠ Completed: {success_count}/{len(items)} downloads successful")
        sys.exit(1)
    else:
        print(f"\n✗ All {len(items)} downloads failed", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
