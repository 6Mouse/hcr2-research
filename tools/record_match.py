"""Recheck a canonical candidate and record the owner's acceptance locally."""
import argparse
from datetime import date
import json
from pathlib import Path
import subprocess
import sys
from tempfile import NamedTemporaryFile

from progress import CATALOG, read_catalog
from tools.verify_fixture import ROOT, load_spec, verify


def record_match(identifier, evidence, matched_on, ndk):
    catalog_path = ROOT / CATALOG
    original = catalog_path.read_bytes()
    entries = read_catalog(original, ROOT)
    entry = next((entry for entry in entries if entry['id'] == identifier), None)
    if entry is None:
        raise ValueError(f'Unknown function ID {identifier}. See {CATALOG}.')
    if entry.get('matched_on'):
        raise ValueError(f'{identifier} was already recorded on {entry["matched_on"]}.')
    entry.update(matched_on=matched_on, evidence=evidence)
    updated = json.dumps(entries, indent=2) + '\n'
    read_catalog(updated, ROOT)

    fixture = ROOT / 'fixtures' / entry['fixture']
    args = argparse.Namespace(ndk=ndk, fixture=fixture, candidate=None, reference_only=False)
    if verify(args, load_spec(fixture)) != 0:
        return 1

    with NamedTemporaryFile(dir=ROOT, prefix='.function-catalog-', delete=False) as output:
        temp = Path(output.name)
    try:
        temp.write_bytes(updated.encode('utf-8'))
        if catalog_path.read_bytes() != original:
            raise ValueError(f'{CATALOG} changed while verifying. Retry from the current catalog.')
        temp.replace(catalog_path)
    finally:
        temp.unlink(missing_ok=True)
    print(f'Recorded {identifier} in {CATALOG}. Review and commit the change to publish it.')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('function', help='Stable ID from function_catalog.json')
    parser.add_argument('--evidence', required=True, help='HTTPS link to the reviewed PR or verification run')
    parser.add_argument('--date', default=date.today().isoformat(), help='Match date in YYYY-MM-DD format')
    parser.add_argument('--ndk', type=Path, help='Path to the pinned Android NDK')
    args = parser.parse_args()
    try:
        return record_match(args.function, args.evidence, args.date, args.ndk)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(f'Unable to record match: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
