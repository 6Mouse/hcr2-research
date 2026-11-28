"""Announce newly verified core-library research on the existing Discord webhook."""
import argparse
import os
import re
import subprocess
import sys

from project import read_tasks
from tools.notify_matches import DASHBOARD, post


def tasks_at(revision):
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError('Expected a full Git commit ID.')
    if revision == '0' * 40:
        return []
    data = subprocess.check_output(['git', 'show', f'{revision}:tasks.json'], timeout=30)
    return read_tasks(data)


def update_message(before, after):
    seen = {task['id'] for task in before if task['state'] == 'verified'}
    verified = [task['id'] for task in after if task['state'] == 'verified']
    new = [identifier for identifier in verified if identifier not in seen]
    if not new:
        return ''
    identifiers = ', '.join(new[:20])
    if len(new) > 20:
        identifiers += f' and {len(new) - 20} more'
    return (f'**HCR2 1.76.1 ARM64 core research**\n'
            f'New verified observations: {identifiers}\n'
            f'Observations verified: {len(verified)}/{len(after)}\n'
            f'Machine code verified: 0.000000 MB · total unmeasured\n<{DASHBOARD}>')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--test', action='store_true', help='Send a labeled test message')
    args = parser.parse_args()
    webhook = os.environ.get('DISCORD_MATCH_WEBHOOK', '').strip()
    if not webhook:
        print('Discord is disabled until DISCORD_MATCH_WEBHOOK is configured.')
        return 2 if args.test else 0
    try:
        message = (f'HCR2 1.76.1 ARM64 core webhook test · <{DASHBOARD}>' if args.test else
                   update_message(tasks_at(os.environ['BEFORE']), tasks_at(os.environ['AFTER'])))
        if message:
            post(webhook, message)
            print('Discord accepted the update.')
        else:
            print('No newly verified core observations.')
        return 0
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
