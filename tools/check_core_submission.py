"""Keep public contributions in the core observation notes directory."""
import argparse
import re
import subprocess
import sys

from project import read_tasks


def check_paths(paths, task_ids):
    for path in paths:
        match = re.fullmatch(r'notes/(HCR2-\d{3,})(?:-[a-z0-9-]+)?\.md', path)
        if not match or match[1] not in task_ids:
            raise ValueError(f'Use notes/<task-id>-<short-name>.md for core observations: {path}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base')
    parser.add_argument('result')
    args = parser.parse_args()
    try:
        catalog = subprocess.check_output(['git', 'show', f'{args.base}:tasks.json'])
        task_ids = {task['id'] for task in read_tasks(catalog)}
        output = subprocess.check_output(['git', 'diff', '--no-renames', '--name-only', '-z',
                                          args.base, args.result, '--'])
        check_paths(output.decode('utf-8').rstrip('\0').split('\0') if output else [], task_ids)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(f'Core submission check failed: {exc}', file=sys.stderr)
        return 1
    print('Core observation paths passed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
