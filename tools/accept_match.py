"""Publish an owner-approved match from a merged pull request."""
import argparse
from datetime import date
import json
from pathlib import Path
import subprocess
import sys

from progress import CATALOG, read_catalog
from tools.record_match import record_match
from tools.verify_fixture import ROOT

REPOSITORY = '6Mouse/hcr2-research'
REMOTE_URLS = {f'https://github.com/{REPOSITORY}', f'https://github.com/{REPOSITORY}.git',
               f'git@github.com:{REPOSITORY}.git', f'ssh://git@github.com/{REPOSITORY}.git'}
REMOTE_URLS = {url.casefold() for url in REMOTE_URLS}


def command(*args):
    return subprocess.check_output(args, cwd=ROOT, encoding='utf-8', timeout=90).rstrip('\r\n')


def candidate_from_pr(pr, catalog):
    if pr['state'] != 'MERGED' or pr['baseRefName'] != 'main' or not pr['mergeCommit']:
        raise ValueError('Merge the reviewed pull request into main first.')
    files = [item['path'] for item in pr['files']]
    for entry in catalog:
        path = f'fixtures/{entry["fixture"]}/candidate.cpp'
        if files == [path] and pr['title'].startswith(f'[{entry["id"]}] '):
            return entry['id'], path
    raise ValueError('The PR must use the catalog ID in its title and change only that candidate.cpp.')


def accept(number, ndk):
    if command('gh', 'api', 'user', '--jq', '.login').casefold() != REPOSITORY.split('/')[0].casefold():
        raise ValueError('Authenticate GitHub CLI as the repository owner to publish progress.')
    if any(command('git', 'remote', 'get-url', *mode, 'origin').casefold() not in REMOTE_URLS
           for mode in ([], ['--push'])):
        raise ValueError(f'Origin must point to {REPOSITORY}.')
    if command('git', 'status', '--porcelain'):
        raise ValueError('Use a clean checkout before publishing a match.')

    fields = 'state,baseRefName,mergeCommit,title,url,files'
    pr = json.loads(command('gh', 'pr', 'view', str(number), '--repo', REPOSITORY, '--json', fields))
    command('git', 'fetch', '--no-tags', 'origin', 'main')
    remote_main = command('git', 'rev-parse', 'FETCH_HEAD')
    catalog = read_catalog(command('git', 'show', f'{remote_main}:{CATALOG}'))
    identifier, path = candidate_from_pr(pr, catalog)
    merged = pr['mergeCommit']['oid']
    command('git', 'merge-base', '--is-ancestor', merged, remote_main)
    # Verify the exact reviewed candidate even if main has advanced since the merge.
    if command('git', 'rev-parse', f'{merged}:{path}') != command('git', 'rev-parse', f'{remote_main}:{path}'):
        raise ValueError('The candidate on main differs from the merged pull request.')

    initial_head = command('git', 'rev-parse', 'HEAD')
    if initial_head != remote_main:
        if command('git', 'branch', '--show-current') != 'main':
            raise ValueError('Switch to main to fast-forward to the merged candidate.')
        command('git', 'merge-base', '--is-ancestor', initial_head, remote_main)
        command('git', 'merge', '--ff-only', remote_main)

    if record_match(identifier, pr['url'], date.today().isoformat(), ndk) != 0:
        return 1
    if (command('git', 'rev-parse', 'HEAD') != remote_main or
            command('git', 'status', '--porcelain') != f' M {CATALOG}'):
        raise ValueError('The checkout changed during verification. The local catalog edit was retained.')
    command('git', 'commit', '--only', '-m', f'Record verified match {identifier}', '--', CATALOG)
    commit = command('git', 'rev-parse', 'HEAD')
    try:
        command('git', 'push', 'origin', f'{commit}:refs/heads/main')
    except subprocess.SubprocessError as exc:
        raise ValueError(f'The verified catalog commit {commit[:12]} is local. Resolve the push failure before retrying.') from exc
    print(f'Published {identifier} in {commit[:12]}. GitHub Actions will update the dashboard.')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pull_request', type=int, help='Number of a reviewed and merged function PR')
    parser.add_argument('--ndk', type=Path, help='Path to the pinned Android NDK')
    args = parser.parse_args()
    try:
        return accept(args.pull_request, args.ndk)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(f'Unable to publish match: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
