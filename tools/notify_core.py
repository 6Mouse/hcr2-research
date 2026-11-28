"""Announce newly verified core-library research on the existing Discord webhook."""
import argparse
import json
import os
import re
import subprocess
import sys

from core_matches import CATALOG, counts, read_matches
from project import read_tasks
from tools.notify_matches import DASHBOARD, post


def data_at(revision, path):
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError('Expected a full Git commit ID.')
    return subprocess.check_output(['git', 'show', f'{revision}:{path}'], timeout=30)


def tasks_at(revision):
    return [] if revision == '0' * 40 else read_tasks(data_at(revision, 'tasks.json'))


def matches_at(revision, *, allow_missing=False):
    if revision == '0' * 40 and allow_missing:
        return []
    baseline = json.loads(data_at(revision, 'baseline.json'))
    if allow_missing and not subprocess.check_output(['git', 'ls-tree', revision, '--', CATALOG], timeout=30):
        return []
    return read_matches(data_at(revision, CATALOG), baseline)['functions']


def update_message(before, after, before_matches=(), after_matches=()):
    seen = {task['id'] for task in before if task['state'] == 'verified'}
    verified = [task['id'] for task in after if task['state'] == 'verified']
    new = [identifier for identifier in verified if identifier not in seen]
    prior = {entry['id'] for entry in before_matches if entry.get('verified_on')}
    matched = [entry for entry in after_matches if entry.get('verified_on') and entry['id'] not in prior]
    if not new and not matched:
        return ''
    lines = ['**HCR2 1.76.1 ARM64 core research**']
    if new:
        identifiers = ', '.join(new[:12])
        if len(new) > 12:
            identifiers += f' and {len(new) - 12} more'
        lines.append(f'New verified observations: {identifiers}')
    if matched:
        lines.extend(f'New match: {entry["id"]} · {entry["bytes"]:,} bytes · {entry["verified_on"]}'
                     for entry in matched[:16])
        if len(matched) > 16:
            lines.append(f'And {len(matched) - 16} more matches.')
    metrics = counts(after_matches)
    lines.extend((f'Observations verified: {len(verified)}/{len(after)}',
                  f'Machine code verified: {metrics["verified_machine_code_bytes"] / 1_000_000:.6f} MB · '
                  f'{metrics["enrolled_machine_code_bytes"] / 1_000_000:.6f} MB enrolled', f'<{DASHBOARD}>'))
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--test', action='store_true', help='Send a labeled test message')
    args = parser.parse_args()
    webhook = os.environ.get('DISCORD_MATCH_WEBHOOK', '').strip()
    if not webhook:
        print('Discord is disabled until DISCORD_MATCH_WEBHOOK is configured.')
        return 2 if args.test else 0
    try:
        if args.test:
            message = f'HCR2 1.76.1 ARM64 core webhook test · <{DASHBOARD}>'
        else:
            before, after = os.environ['BEFORE'], os.environ['AFTER']
            message = update_message(tasks_at(before), tasks_at(after),
                                     matches_at(before, allow_missing=True), matches_at(after))
        if message:
            post(webhook, message)
            print('Discord accepted the update.')
        else:
            print('No newly verified core observations or function matches.')
        return 0
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
