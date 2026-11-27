"""Local baseline verification, exact comparison, and dashboard generation."""
import argparse
from collections import Counter
import hashlib
from html import escape
import json
from pathlib import Path
import re
import subprocess
import sys
from tempfile import SpooledTemporaryFile
from urllib.parse import urlparse
from zipfile import BadZipFile, ZipFile

from progress import CATALOG, read_catalog, totals

ROOT = Path(__file__).resolve().parent
BLOCK = 1024 * 1024


def digest(stream):
    result = hashlib.sha256()
    for block in iter(lambda: stream.read(BLOCK), b''):
        result.update(block)
    return result.hexdigest()


def compare(reference, candidate):
    first_difference = None
    offset = 0
    left_hash, right_hash = hashlib.sha256(), hashlib.sha256()
    left_size = right_size = 0
    with reference.open('rb') as left, candidate.open('rb') as right:
        while True:
            a, b = left.read(BLOCK), right.read(BLOCK)
            if not a and not b:
                break
            if first_difference is None and a != b:
                relative = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
                first_difference = offset + relative
            left_hash.update(a)
            right_hash.update(b)
            left_size += len(a)
            right_size += len(b)
            offset += BLOCK
    return dict(match=first_difference is None, first_difference=first_difference,
                reference_bytes=left_size, candidate_bytes=right_size,
                reference_sha256=left_hash.hexdigest(), candidate_sha256=right_hash.hexdigest())


def verify_release(path, baseline):
    with path.open('rb') as source:
        sha = digest(source)
    report = dict(match=False, archive_sha256=sha, archive_bytes=path.stat().st_size)
    with ZipFile(path) as archive:
        with archive.open(baseline['base_entry']) as base:
            report['base_sha256'] = digest(base)
        with archive.open(baseline['arm64_entry']) as split, SpooledTemporaryFile(max_size=BLOCK) as local:
            arm64_hash = hashlib.sha256()
            for block in iter(lambda: split.read(BLOCK), b''):
                arm64_hash.update(block)
                local.write(block)
            report['arm64_sha256'] = arm64_hash.hexdigest()
            with ZipFile(local) as apk, apk.open(baseline['engine_entry']) as engine:
                report['engine_sha256'] = digest(engine)
    report['archive_match'] = (sha == baseline['archive_sha256'] and
                               report['archive_bytes'] == baseline['archive_bytes'])
    report['match'] = all(report[key] == baseline[key] for key in
                          ('base_sha256', 'arm64_sha256', 'engine_sha256'))
    return report


def load_tasks():
    tasks = json.loads((ROOT / 'tasks.json').read_text(encoding='utf-8'))
    seen = set()
    for task in tasks:
        identifier = task['id']
        if not re.fullmatch(r'HCR2-\d{3,}', identifier) or identifier in seen:
            raise ValueError(f'Invalid or duplicate task ID: {identifier}')
        seen.add(identifier)
        if task['state'] not in {'open', 'claimed', 'in review', 'verified'}:
            raise ValueError(f'Invalid status for {identifier}')
        if not all(task[k].strip() for k in ('title', 'area', 'acceptance')):
            raise ValueError(f'Missing task description for {identifier}')
        evidence = task.get('evidence', '')
        if evidence:
            url = urlparse(evidence)
            if url.scheme != 'https' or not url.hostname:
                raise ValueError(f'{identifier} requires an HTTPS evidence URL')
        if task['state'] == 'verified':
            contributor = task.get('contributor', '').strip()
            reviewer = task.get('reviewer', '').strip()
            if not contributor or not reviewer or contributor.casefold() == reviewer.casefold() or not evidence:
                raise ValueError(f'{identifier} requires an independent reviewer and HTTPS evidence')
    return tasks


def dashboard(baseline):
    tasks = load_tasks()
    counts = Counter(task['state'] for task in tasks)
    cards = ''.join(f'<div><strong>{counts[state]}</strong><span>{state.title()}</span></div>'
                    for state in ('open', 'claimed', 'in review', 'verified'))
    rows = []
    for task in tasks:
        evidence = '—'
        if task['state'] == 'verified':
            url = escape(task['evidence'], quote=True)
            evidence = f'<a href="{url}">Review evidence</a> · {escape(task["reviewer"])}'
        elif task.get('evidence'):
            url = escape(task['evidence'], quote=True)
            evidence = f'<a href="{url}">Run evidence</a>'
        rows.append(f'<tr data-state="{escape(task["state"])}"><td><code>{task["id"]}</code></td>'
                    f'<td><b>{escape(task["title"])}</b><small>{escape(task["acceptance"])}</small></td>'
                    f'<td>{escape(task["area"])}</td><td>{escape(task["state"].title())}</td><td>{evidence}</td></tr>')
    page = (ROOT / 'dashboard.html').read_text(encoding='utf-8')
    for key, value in {'BASELINE': escape(f'{baseline["version"]} · {baseline["abi"]}'),
                       'HASH': escape(baseline['archive_sha256']), 'CARDS': cards, 'ROWS': '\n'.join(rows)}.items():
        page = page.replace('%%' + key + '%%', value)
    output = ROOT / 'dist' / 'index.html'
    output.parent.mkdir(exist_ok=True)
    catalog = read_catalog((ROOT / CATALOG).read_text(encoding='utf-8'), ROOT)
    metrics = totals(catalog)
    (output.parent / 'progress.json').write_text(json.dumps({
        'scope': 'original-arm64-fixtures', 'game_progress': None,
        **metrics, 'functions': catalog,
    }, indent=2) + '\n', encoding='utf-8')
    page = page.replace('%%PROGRESS%%', render_progress(catalog, metrics))
    output.write_text(page, encoding='utf-8')
    print(output)


def render_progress(catalog, metrics):
    def measure(label, done, total, display):
        percent = f'{done / total:.1%}' if total else 'No target yet'
        bar = (f'<progress aria-label="{label}" value="{done}" max="{total}"></progress>'
               if total else '')
        return (f'<article><div class="measure"><b>{label}</b><span>{percent}</span></div>'
                f'<strong>{display}</strong>{bar}</article>')

    done, total = metrics['matched_functions'], metrics['total_functions']
    size, extent = metrics['matched_bytes'], metrics['total_bytes']
    match_rows = []
    for entry in sorted(catalog, key=lambda row: row.get('matched_on') or '', reverse=True):
        if entry.get('matched_on'):
            url = escape(entry['evidence'], quote=True)
            match_rows.append(f'<li><code>{escape(entry["symbol"])}</code> '
                              f'<span>{entry["bytes"]:,} bytes · {entry["matched_on"]} · '
                              f'<a href="{url}">Evidence</a></span></li>')
    return (measure('Functions matched', done, total, f'{done:,} / {total:,}') +
            measure('Machine code matched', size, extent,
                    f'{size / 1_000_000:,.6f} / {extent / 1_000_000:,.6f} MB '
                    f'<small>{size:,} / {extent:,} bytes</small>') +
            '<div class="matches"><h3>Recent exact matches</h3><ul>' +
            (''.join(match_rows[:10]) or '<li>No verified matches yet.</li>') + '</ul></div>')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    verify = commands.add_parser('verify-release', help='Verify the original base and ARM64 split in a local APKS archive')
    verify.add_argument('archive', type=Path)
    verify.add_argument('--exact-archive', action='store_true',
                        help='Also require the entire archive to match the shared fingerprint')
    diff = commands.add_parser('compare', help='Compare two local artifacts byte for byte')
    diff.add_argument('reference', type=Path)
    diff.add_argument('candidate', type=Path)
    commands.add_parser('dashboard', help='Validate task data and render the local dashboard')
    commands.add_parser('check', help='Run the starter checks without the APK or Android NDK')
    args = parser.parse_args()
    try:
        baseline = json.loads((ROOT / 'baseline.json').read_text(encoding='utf-8'))
        if args.command == 'check':
            subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests'],
                           cwd=ROOT, check=True, timeout=30)
            subprocess.run([sys.executable, 'replay_drift_fixture.py'], cwd=ROOT,
                           check=True, timeout=30)
            dashboard(baseline)
            return 0
        if args.command == 'dashboard':
            dashboard(baseline)
            return 0
        report = (compare(args.reference, args.candidate) if args.command == 'compare'
                  else verify_release(args.archive, baseline))
        if args.command == 'verify-release' and args.exact_archive:
            report['match'] = report['match'] and report['archive_match']
        print(json.dumps(report, indent=2))
        return 0 if report['match'] else 1
    except (OSError, BadZipFile, KeyError, ValueError, subprocess.SubprocessError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
