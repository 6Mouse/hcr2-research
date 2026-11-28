"""Find and record owner-approved matches after the pinned build passes on main."""
import argparse
from datetime import date
import json
import os
from pathlib import Path
import subprocess
import sys

from progress import CATALOG, read_catalog


def git(*args):
    return subprocess.check_output(['git', *args], text=True, encoding='utf-8', timeout=30).strip()


def github(repo, endpoint):
    data = subprocess.check_output(['gh', 'api', f'repos/{repo}/{endpoint}'], timeout=30)
    return json.loads(data)


def owner_merge(pr, repo, revision, identifier):
    merger = (pr.get('merged_by') or {}).get('login', '')
    base = pr['base']
    return (bool(pr.get('merged_at')) and merger.casefold() == repo.split('/')[0].casefold()
            and base['ref'] == 'main' and base['repo']['full_name'].casefold() == repo.casefold()
            and pr.get('merge_commit_sha') == revision and pr['changed_files'] == 1
            and pr['title'].startswith(f'[{identifier}] '))


def find_owner_merges(repo, candidates):
    approvals = {}
    for identifier, path in candidates.items():
        tree = git('ls-tree', 'HEAD', '--', path)
        if not tree.startswith('100644 blob '):
            continue
        blob = tree.split()[2]
        revision = git('log', '--first-parent', '-1', '--format=%H', 'HEAD', '--', path)
        for linked in github(repo, f'commits/{revision}/pulls'):
            number = linked['number']
            pr = github(repo, f'pulls/{number}')
            if not owner_merge(pr, repo, revision, identifier):
                continue
            files = github(repo, f'pulls/{number}/files')
            if (len(files) == 1 and files[0]['filename'] == path
                    and files[0]['status'] in {'added', 'modified'} and files[0]['sha'] == blob):
                approvals[identifier] = number
                break
    return approvals


def discover(repo, catalog):
    return find_owner_merges(repo, {entry['id']: f'fixtures/{entry["fixture"]}/candidate.cpp'
                                    for entry in catalog if not entry.get('matched_on')})


def mark_verified(catalog, approvals, repo, stamp, *, date_field):
    pending = {row['id'] for row in catalog if not row.get(date_field)}
    if not isinstance(approvals, dict) or not approvals.keys() <= pending:
        raise ValueError('Expected approvals for pending catalog entries.')
    for entry in catalog:
        if entry['id'] in approvals:
            number = approvals[entry['id']]
            if type(number) is not int or number <= 0:
                raise ValueError('Expected a positive GitHub pull request number.')
            entry[date_field] = stamp
            entry['evidence'] = f'https://github.com/{repo}/pull/{number}'


def apply(catalog, approvals, repo, matched_on):
    mark_verified(catalog, approvals, repo, matched_on, date_field='matched_on')
    return json.dumps(catalog, indent=2) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('discover', 'apply'))
    args = parser.parse_args()
    try:
        root = Path(__file__).resolve().parents[1]
        path = root / CATALOG
        catalog = read_catalog(path.read_bytes(), root)
        repo = os.environ['GITHUB_REPOSITORY']
        if args.operation == 'discover':
            print(json.dumps(discover(repo, catalog), separators=(',', ':')))
        else:
            approvals = json.loads(os.environ['MATCH_APPROVALS'])
            updated = apply(catalog, approvals, repo, date.today().isoformat())
            read_catalog(updated, root)
            path.write_bytes(updated.encode('utf-8'))
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(f'Automatic match recording failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
