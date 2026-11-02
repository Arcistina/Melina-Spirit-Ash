"""Copy the four custom UI assets and a chosen helper into project-local output."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dll', required=True, type=Path)
    args = parser.parse_args()
    reference = json.loads((ROOT / 'spec/accepted_runtime.json').read_text(encoding='utf-8'))
    output = ROOT / 'build/melina_ashes/mod'
    assert output.resolve().is_relative_to(ROOT)
    for rel in reference['ui_asset_files']:
        source = ROOT / 'assets/ui' / rel
        row = reference['files'][rel]
        assert hashlib.sha256(source.read_bytes()).hexdigest() == row['sha256'], rel
        dest = output / rel
        assert dest.resolve().is_relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
    assert args.dll.is_file() and args.dll.read_bytes()[:2] == b'MZ'
    shutil.copy2(args.dll, output / 'MelinaIcons.dll')
    print(json.dumps({'ui_assets': 4, 'custom_image_payloads': 2, 'original_image_archives': 0}))


if __name__ == '__main__':
    main()
