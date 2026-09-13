"""Download the public educational MovieLens dataset; preserve its license."""
from pathlib import Path
import hashlib
import io
import json
import urllib.request
import zipfile
import argparse

URL = 'https://files.grouplens.org/datasets/movielens/ml-latest-small.zip'
DEST = Path(__file__).resolve().parents[1] / 'backend/data'

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    parser = argparse.ArgumentParser()
    parser.add_argument('--mirror', action='store_true', help='Use the pinned GitHub mirror if the official host is unavailable.')
    args = parser.parse_args()
    if args.mirror:
        base = 'https://raw.githubusercontent.com/smanihwr/ml-latest-small/ba3cd91761e54faa64483456b619d1a1f4d70971/'
        manifest = {'source': base, 'original_source': URL, 'files': {}}
        for name in ('movies.csv', 'links.csv', 'README.txt'):
            with urllib.request.urlopen(base + name, timeout=60) as response:
                content = response.read()
            (DEST / name).write_bytes(content)
            manifest['files'][name] = hashlib.sha256(content).hexdigest()
        (DEST / 'manifest.json').write_text(json.dumps(manifest, indent=2))
        print(f'Dataset saved from pinned mirror to {DEST}')
        return
    with urllib.request.urlopen(URL, timeout=60) as response:
        payload = response.read()
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        # Explicit filenames avoid extracting arbitrary archive paths.
        for name in ('movies.csv', 'links.csv', 'README.txt'):
            (DEST / name).write_bytes(archive.read(f'ml-latest-small/{name}'))
    (DEST / 'manifest.json').write_text(json.dumps({'source': URL, 'sha256': hashlib.sha256(payload).hexdigest()}, indent=2))
    print(f'Dataset saved to {DEST}')

if __name__ == '__main__':
    main()
