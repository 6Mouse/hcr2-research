"""Check changed paths in a pull request opened by a contributor."""
import argparse
from pathlib import Path
import subprocess
import sys

from progress import CATALOG, read_catalog


def validate(paths, catalog):
    if CATALOG in paths:
        raise ValueError(f'The repository owner records progress in {CATALOG}.')
    candidates = {path for path in paths
                  if path.startswith('fixtures/') and path.endswith('/candidate.cpp')}
    if not candidates:
        return None
    expected = {f'fixtures/{entry["fixture"]}/candidate.cpp' for entry in catalog}
    if len(candidates) != 1 or paths != candidates or not candidates <= expected:
        raise ValueError('A function submission must change only one enrolled candidate.cpp.')
    return next(iter(candidates))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base')
    parser.add_argument('result')
    args = parser.parse_args()
    try:
        data = subprocess.check_output(['git', 'show', f'{args.base}:{CATALOG}'])
        paths = subprocess.check_output(['git', 'diff', '--no-renames', '--name-only', '-z',
                                         args.base, args.result, '--']).decode('utf-8')
        candidate = validate(set(paths.split('\0')) - {''}, read_catalog(data))
        if candidate and not Path(candidate).is_file():
            raise ValueError('A function submission must provide a candidate.cpp to compile.')
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f'Submission check failed: {exc}', file=sys.stderr)
        return 1
    print('Contributor submission scope passed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
