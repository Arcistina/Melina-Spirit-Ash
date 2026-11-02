"""Compare a local rebuild or player installation with the accepted release."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', required=True, type=Path)
    parser.add_argument('--allow-rebuilt-helper', action='store_true')
    args = parser.parse_args()
    expected = json.loads((ROOT / 'spec/accepted_runtime.json').read_text(encoding='utf-8'))['files']
    actual = {p.relative_to(args.directory).as_posix() for p in args.directory.rglob('*')
              if p.is_file() and p.name != 'MelinaIcons.log'}
    assert actual == set(expected), ('Unexpected or missing files', actual ^ set(expected))
    changed = []
    for name, row in expected.items():
        path = args.directory / name
        if path.stat().st_size != row['size'] or hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
            changed.append(name)
    permitted = ['MelinaIcons.dll'] if args.allow_rebuilt_helper else []
    assert all(n in permitted for n in changed), ('Files differ from accepted snapshot', changed)
    print(json.dumps({'files': len(expected), 'matched': len(expected) - len(changed),
        'rebuilt_helper_differs': bool(changed), 'runtime_gameplay_test_performed': False}))


if __name__ == '__main__':
    main()
