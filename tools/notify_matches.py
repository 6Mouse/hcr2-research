"""Post new catalog matches to Discord after a successful main-branch build."""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from progress import CATALOG, new_matches, read_catalog, totals

DASHBOARD = 'https://6mouse.github.io/hcr2-research/'


def catalog_at(revision, *, allow_missing=False):
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError('Expected a full Git commit ID')
    if revision == '0' * 40 and allow_missing:
        return []
    subprocess.run(['git', 'cat-file', '-e', f'{revision}^{{commit}}'], check=True)
    blob = subprocess.run(['git', 'show', f'{revision}:{CATALOG}'], capture_output=True, check=False)
    if blob.returncode and allow_missing:
        return []
    blob.check_returncode()
    return read_catalog(blob.stdout)


def messages(matches, metrics):
    if not matches:
        return []
    count, functions = metrics['matched_functions'], metrics['total_functions']
    size, extent = metrics['matched_bytes'], metrics['total_bytes']
    footer = (f'\n\nFixture progress: **{count:,}/{functions:,} functions** · '
              f'**{size / 1_000_000:.6f}/{extent / 1_000_000:.6f} MB** '
              f'({size:,}/{extent:,} bytes)\n<{DASHBOARD}>')
    header = '**New verified ARM64 fixture matches**\n'
    chunks = []
    body = header
    for item in matches:
        line = f'- `{item["symbol"]}` ({item["id"]}) · {item["bytes"]:,} bytes · {item["matched_on"]}\n'
        if len(body) + len(line) + len(footer) > 1900:
            chunks.append(body.rstrip() + footer)
            body = header
        body += line
    return chunks + [body.rstrip() + footer]


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def post(url, content):
    if not re.fullmatch(r'https://discord\.com/api/(?:v\d+/)?webhooks/\d+/[A-Za-z0-9_.-]+', url):
        raise ValueError('The repository secret must contain a Discord webhook URL')
    payload = json.dumps({'content': content, 'allowed_mentions': {'parse': []}}).encode()
    request = Request(url + '?wait=true', data=payload, headers={
        'Content-Type': 'application/json', 'User-Agent': 'HCR2-Research-GitHub-Actions/1.0',
    }, method='POST')
    client = build_opener(NoRedirects())
    for attempt in range(3):
        try:
            with client.open(request, timeout=15):
                return
        except HTTPError as err:
            code = err.code
            retry = err.headers.get('Retry-After', '2')
            err.close()
            if code == 429 and attempt < 2:
                time.sleep(min(20, max(1, float(retry))))
                continue
            raise ValueError(f'Discord rejected the notification (HTTP {code})') from None
        except (URLError, TimeoutError):
            raise ValueError('Discord delivery could not be confirmed') from None


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
            post(webhook, f'HCR2 Research webhook test · <{DASHBOARD}>')
            print('Discord accepted the test message.')
            return 0
        after = catalog_at(os.environ['AFTER'])
        before = catalog_at(os.environ['BEFORE'], allow_missing=True)
        pending = new_matches(before, after)
        for content in messages(pending, totals(after)):
            post(webhook, content)
        print(f'New matches announced: {len(pending)}')
        return 0
    except (ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
