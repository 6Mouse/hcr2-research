"""Limit public PRs to observations or one enrolled matching candidate."""
import argparse
import json
import re
import subprocess
import sys

from project import read_tasks
from core_matches import CATALOG, candidate_path, read_matches


def check_paths(paths, task_ids, matching_ids=()):
    allowed = {candidate_path(identifier).as_posix() for identifier in matching_ids}
    if len(paths) == 1 and paths[0] in allowed:
        return paths[0]
    for path in paths:
        match = re.fullmatch(r'notes/(HCR2-\d{3,})(?:-[a-z0-9-]+)?\.md', path)
        if not match or match[1] not in task_ids:
            raise ValueError(f'Use notes/<task-id>-<short-name>.md for core observations: {path}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base')
    parser.add_argument('result')
    parser.add_argument('--title', help='PR title for a function submission')
    args = parser.parse_args()
    try:
        catalog = subprocess.check_output(['git', 'show', f'{args.base}:tasks.json'])
        task_ids = {task['id'] for task in read_tasks(catalog)}
        baseline = json.loads(subprocess.check_output(['git', 'show', f'{args.base}:baseline.json']))
        matches = subprocess.check_output(['git', 'show', f'{args.base}:{CATALOG}'])
        matching_ids = [entry['id'] for entry in read_matches(matches, baseline)['functions']
                        if not entry.get('verified_on')]
        output = subprocess.check_output(['git', 'diff', '--no-renames', '--name-only', '-z',
                                          args.base, args.result, '--'])
        paths = output.decode('utf-8').rstrip('\0').split('\0') if output else []
        candidate = check_paths(paths, task_ids, matching_ids)
        if candidate:
            tree = subprocess.check_output(['git', 'ls-tree', args.result, '--', candidate])
            if not tree.startswith(b'100644 blob '):
                raise ValueError('The submitted candidate must be a regular C++ source file.')
            identifier = candidate.rsplit('/', 1)[-1][:-4]
            if args.title is not None and not args.title.startswith(f'[{identifier}] '):
                raise ValueError(f'Start the PR title with [{identifier}].')
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(f'Core submission check failed: {exc}', file=sys.stderr)
        return 1
    print('Core contribution paths passed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
