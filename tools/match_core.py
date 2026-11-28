"""Enroll and check isolated functions against the original ARM64 core."""
import argparse
from datetime import date
from io import BytesIO
import json
from pathlib import Path
import re
from struct import unpack_from
import subprocess
import sys
from tempfile import NamedTemporaryFile, TemporaryDirectory
from zipfile import BadZipFile, ZipFile

from core_matches import CATALOG, candidate_path, read_matches
from project import verify_release
from tools.verify_fixture import ROOT, compile_fixture, default_ndk, sha, tools


def in_executable_segment(core, offset, size):
    header = core.read(64)
    if len(header) != 64 or header[:6] != b'\x7fELF\x02\x01' or unpack_from('<H', header, 18)[0] != 183:
        return False
    table = unpack_from('<Q', header, 32)[0]
    stride, count = unpack_from('<HH', header, 54)
    if stride < 56:
        return False
    for index in range(count):
        core.seek(table + index * stride)
        segment = core.read(56)
        if len(segment) != 56:
            return False
        kind, flags, start, _, _, length, _, _ = unpack_from('<IIQQQQQQ', segment)
        if kind == 1 and (flags & 1) and start <= offset and offset + size <= start + length:
            return True
    return False


def reference_bytes(archive, baseline, entry):
    fingerprint = verify_release(archive, baseline)
    if not (fingerprint['match'] and fingerprint['archive_match']):
        raise ValueError('Use the pinned 1.76.1 APKS archive from baseline.json.')
    with (ZipFile(archive) as outer, ZipFile(BytesIO(outer.read(baseline['arm64_entry']))) as split,
          split.open(baseline['engine_entry']) as core):
        offset, size = entry['file_offset'], entry['bytes']
        if offset + size > split.getinfo(baseline['engine_entry']).file_size:
            raise ValueError('The range falls outside the pinned library.')
        if not in_executable_segment(core, offset, size):
            raise ValueError('The range must be inside one file-backed ARM64 executable segment.')
        core.seek(offset)
        return core.read(size)


def check_code(code, entry, reference=None):
    if len(code) != entry['bytes'] or sha(code) != entry['sha256']:
        raise ValueError(f'{entry["id"]}: mismatch, got {len(code)} bytes · SHA-256 {sha(code)}.')
    if reference is not None and code != reference:
        raise ValueError(f'{entry["id"]}: the candidate differs from the archive bytes.')


def check(entry, source, compiler, spec, reference=None):
    with TemporaryDirectory(prefix='hcr2-core-match-') as temp:
        out = Path(temp) / 'candidate'
        symbol = entry['symbol']
        _, code = compile_fixture(source, out, *compiler, {**spec, 'symbol': symbol})
        dump = subprocess.check_output([compiler[2], '--wide', '--symbols', '--section-headers',
                                        out / 'fixture.o'], text=True, timeout=15)
        section = re.search(rf'^\s*\[\s*(\d+)\]\s+\.text\.{symbol}\s+PROGBITS\s', dump, re.MULTILINE)
        declaration = (rf'^\s*\d+:\s+0+\s+{len(code)}\s+FUNC\s+GLOBAL\s+\S+\s+'
                       rf'{section[1] if section else "undefined"}\s+{symbol}\s*$')
        if not section or re.search(declaration, dump, re.MULTILINE) is None:
            raise ValueError(f'{entry["id"]}: expected one global function covering its code section.')
        check_code(code, entry, reference)
    mode = 'exact archive bytes' if reference is not None else 'pinned size and SHA-256'
    print(f'PASS {entry["id"]} · {symbol} · {len(code)} bytes · {mode}')


def save_catalog(path, catalog, baseline, original):
    updated = json.dumps(catalog, indent=2) + '\n'
    read_matches(updated, baseline, ROOT)
    with NamedTemporaryFile(dir=path.parent, delete=False) as output:
        temp = Path(output.name)
    try:
        temp.write_bytes(updated.encode('utf-8'))
        if path.read_bytes() != original:
            raise ValueError('The catalog changed during the check. Retry with the updated catalog.')
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('list', 'candidate-count'):
        commands.add_parser(name)
    enroll = commands.add_parser('enroll', help='Pin a reviewed reference range from the local archive')
    enroll.add_argument('id')
    enroll.add_argument('symbol')
    enroll.add_argument('--offset', type=lambda value: int(value, 0), required=True)
    enroll.add_argument('--size', type=int, required=True)
    enroll.add_argument('--note', required=True, help='Explain how you verified the function boundary and role')
    enroll.add_argument('--archive', type=Path, required=True)
    check_one = commands.add_parser('check', help='Compile and verify one candidate')
    check_one.add_argument('id')
    check_one.add_argument('--candidate', type=Path)
    check_one.add_argument('--archive', type=Path, help='Also compare the original function bytes directly')
    check_all = commands.add_parser('check-all', help='Check every candidate present in the working tree')
    record = commands.add_parser('record', help='Record a reviewed exact match in the local catalog')
    record.add_argument('id')
    record.add_argument('--archive', type=Path, required=True)
    record.add_argument('--evidence', required=True, help='URL of the reviewed PR or evidence')
    for command in (check_one, check_all, record):
        command.add_argument('--ndk', type=Path, help='Location of the pinned Android NDK')
    args = parser.parse_args()
    try:
        baseline = json.loads((ROOT / 'baseline.json').read_bytes())
        path = ROOT / CATALOG
        original = path.read_bytes()
        catalog = read_matches(original, baseline, ROOT)
        entries = catalog['functions']
        available = [entry for entry in entries if (ROOT / candidate_path(entry['id'])).is_file()]
        if args.command == 'candidate-count':
            print(len(available))
        elif args.command == 'list':
            for entry in entries:
                state = 'verified' if entry.get('verified_on') else 'open'
                print(f'{entry["id"]} · {entry["symbol"]} · {entry["bytes"]} bytes · {state} · '
                      f'{candidate_path(entry["id"]).as_posix()}')
            if not entries:
                print('No original 1.76.1 core functions enrolled yet.')
        elif args.command == 'enroll':
            entry = dict(id=args.id, symbol=args.symbol, file_offset=args.offset,
                         bytes=args.size, note=args.note, sha256='0' * 64)
            entries.append(entry)
            read_matches(json.dumps(catalog), baseline, ROOT)
            entry['sha256'] = sha(reference_bytes(args.archive, baseline, entry))
            save_catalog(path, catalog, baseline, original)
            print(f'Enrolled {args.id}. Review and commit {CATALOG} to publish it.')
        else:
            if args.command == 'check-all' and not available:
                print('No enrolled candidates to compile.')
                return 0
            targets = available if args.command == 'check-all' else [
                next(entry for entry in entries if entry['id'] == args.id)]
            spec = json.loads((ROOT / 'toolchain.json').read_bytes())
            compiler = tools(args.ndk or default_ndk(spec['ndk_package']), spec)
            for entry in targets:
                if args.command == 'record' and entry.get('verified_on'):
                    raise ValueError(f'{entry["id"]} is already verified.')
                source = getattr(args, 'candidate', None) or ROOT / candidate_path(entry['id'])
                archive = getattr(args, 'archive', None)
                ref = reference_bytes(archive, baseline, entry) if archive else None
                check(entry, source, compiler, spec, ref)
            if args.command == 'record':
                targets[0].update(verified_on=date.today().isoformat(), evidence=args.evidence)
                save_catalog(path, catalog, baseline, original)
                print(f'Recorded {args.id}. Commit {CATALOG} to publish it.')
        return 0
    except StopIteration:
        print(f'Unknown function {args.id}. Use list to see enrolled functions.', file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, BadZipFile, subprocess.SubprocessError) as exc:
        print(f'Core match check failed: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
