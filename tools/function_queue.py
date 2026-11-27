"""Allocate original fixture tasks to GitHub issue authors."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess

from progress import CATALOG, read_catalog

ROOT = Path(__file__).resolve().parents[1]
MARKER = re.compile(r'<!-- function-queue:v1 (HCR2-\d{3,}) -->')
BOT = 'github-actions[bot]'


def assignment(comments):
    for comment in reversed(comments):
        if comment['user']['login'] == BOT:
            marker = MARKER.search(comment.get('body') or '')
            if marker:
                return comment['id'], marker[1]
    return None


def plan(catalog, requests):
    available = {entry['id']: entry for entry in catalog if not entry.get('matched_on')}
    taken = set()
    owners = set()
    # The newer grant wins if a previously released request has been reopened.
    grants = sorted((row for row in requests if row['grant']), key=lambda row: row['grant'][0], reverse=True)
    for row in grants:
        task = row['grant'][1]
        owner = row['owner'].casefold()
        if task in available and task not in taken and owner not in owners:
            taken.add(task)
            owners.add(owner)

    remaining = sorted((entry for task, entry in available.items() if task not in taken),
                       key=lambda entry: (entry['bytes'], entry['id']))
    choices = iter(remaining)
    for row in sorted(requests, key=lambda row: row['number']):
        owner = row['owner'].casefold()
        if row['grant'] or owner in owners:
            continue
        candidate = next(choices, None)
        if candidate is None:
            return
        owners.add(owner)
        yield row['number'], candidate


def gh(path, *, payload=None, pages=False):
    cmd = ['gh', 'api', path]
    if pages:
        cmd += ['--paginate', '--slurp']
    if payload is not None:
        cmd += ['--method', 'POST', '--input', '-']
    output = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                            text=True, capture_output=True, timeout=60, check=True).stdout
    data = json.loads(output)
    return [row for page in data for row in page] if pages else data


def body(entry, repo):
    task, symbol, folder = (entry[name] for name in ('id', 'symbol', 'fixture'))
    path = f'fixtures/{folder}'
    return (f'<!-- function-queue:v1 {task} -->\n'
            f'### Assigned {task}\n\n`{symbol}` · {entry["bytes"]:,} reference bytes\n\n'
            f'Read the [task packet](https://github.com/{repo}/blob/main/{path}/TASK.md) and '
            f'[shared toolchain](https://github.com/{repo}/blob/main/toolchain.json). '
            f'Write your candidate in `{path}/candidate.cpp`, then run:\n\n'
            f'```sh\npython tools/verify_fixture.py --fixture {path}\n```\n\n'
            'Open a PR that links this issue and includes the verifier output. '
            'Close this issue to release the assignment. Open a new request for your next function.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true', help='Show planned assignments without posting')
    args = parser.parse_args()
    repo = os.environ['GITHUB_REPOSITORY']
    catalog = read_catalog((ROOT / CATALOG).read_text(encoding='utf-8'), ROOT)
    rows = []
    path = f'repos/{repo}/issues?state=open&labels=function-queue&per_page=100'
    for item in gh(path, pages=True):
        if 'pull_request' in item or not item.get('user') or item['user']['type'] != 'User':
            continue
        number = item['number']
        comments = (gh(f'repos/{repo}/issues/{number}/comments?per_page=100', pages=True)
                    if item['comments'] else [])
        rows.append({'number': number, 'owner': item['user']['login'], 'grant': assignment(comments)})
    requests = list(plan(catalog, rows))
    for number, entry in requests:
        if not args.dry_run:
            gh(f'repos/{repo}/issues/{number}/comments', payload={'body': body(entry, repo)})
        print(f'Issue #{number}: {entry["id"]}')
    print(f'{len(rows)} open queue requests, {len(requests)} new assignments.')


if __name__ == '__main__':
    main()
