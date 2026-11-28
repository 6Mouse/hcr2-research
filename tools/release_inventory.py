"""Report metadata for the core ARM64 library in a verified local 1.76.1 archive."""
import argparse
from contextlib import redirect_stdout
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
from zipfile import BadZipFile, ZipFile

from project import verify_release
from tools.verify_fixture import ROOT, default_ndk, tools


def elf_metadata(report):
    executable_bytes = 0
    dynamic_functions = None
    frame_entries = None
    build_id = None
    has_text_section = False
    for line in report.splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0] == 'LOAD' and 'E' in fields[6:-1]:
            executable_bytes += int(fields[4], 16)
        if re.match(r'^\s*\[\s*\d+\]\s+\.text\s', line):
            has_text_section = True
        if line.startswith('Symbol table '):
            dynamic_functions = 0
        if (dynamic_functions is not None and fields[0].endswith(':') and len(fields) >= 8
                and fields[0][:-1].isdigit()
                and fields[3] in {'FUNC', 'IFUNC'} and fields[6] != 'UND'):
            dynamic_functions += 1
        if fields[0] == 'fde_count:':
            frame_entries = int(fields[1], 0)
        if fields[:2] == ['Build', 'ID:']:
            build_id = fields[2]
    return dict(executable_load_file_bytes=executable_bytes, text_section_present=has_text_section,
                defined_dynamic_function_symbols=dynamic_functions,
                eh_frame_index_entries=frame_entries, gnu_build_id=build_id)


def inventory(path, baseline, readelf):
    verified = verify_release(path, baseline)
    if not (verified['match'] and verified['archive_match']):
        raise ValueError('The original archive fingerprint does not match baseline.json.')
    entry, member = baseline['arm64_entry'], baseline['engine_entry']
    with (ZipFile(path) as outer, ZipFile(BytesIO(outer.read(entry))) as split,
          TemporaryDirectory(prefix='hcr2-elf-headers-') as temp):
        data = split.read(member)
        local_library = Path(temp) / 'libcocos2dcpp.so'
        local_library.write_bytes(data)
        report = subprocess.check_output([
            readelf, '--program-headers', '--sections', '--dyn-syms', '--notes',
            '--unwind', '--wide', local_library,
        ], text=True, encoding='utf-8', errors='replace', timeout=40)
    library = dict(abi=baseline['abi'], apk=entry, entry=member,
                   sha256=sha256(data).hexdigest(), file_bytes=len(data), **elf_metadata(report))
    return dict(version=baseline['version'], archive_sha256=baseline['archive_sha256'],
                complete_function_count=None, complete_function_bytes=None, libraries=[library])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path, help='Local 1.76.1 APKS matching baseline.json')
    parser.add_argument('--ndk', type=Path, help='Path to the pinned Android NDK')
    parser.add_argument('--output', type=Path, help='Write JSON to this file')
    args = parser.parse_args()
    try:
        baseline = json.loads((ROOT / 'baseline.json').read_text(encoding='utf-8'))
        spec = json.loads((ROOT / 'toolchain.json').read_text(encoding='utf-8'))
        with redirect_stdout(sys.stderr):
            _, _, readelf = tools(args.ndk or default_ndk(spec['ndk_package']), spec)
        report = json.dumps(inventory(args.archive, baseline, readelf), indent=2) + '\n'
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(report.encode('utf-8'))
        else:
            sys.stdout.write(report)
    except (OSError, BadZipFile, ValueError, subprocess.SubprocessError) as exc:
        print(f'Unable to inventory release: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
