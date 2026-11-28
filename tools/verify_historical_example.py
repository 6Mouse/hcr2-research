"""Check one upstream Cocos2d-x accessor in the local 1.7.0 ARMv7 APK."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
from zipfile import BadZipFile, ZipFile

from project import digest
from tools.verify_fixture import ROOT, default_ndk, tools


ARCHIVE_HASH = '4c4f911b1e166230fc2c50c133b0783fef96c541410e16971938c0d878a774ed'
LIBRARY_ENTRY = 'lib/armeabi-v7a/libcocos2dcpp.so'
LIBRARY_HASH = '4c28e263a414e709bbb6850039a87050aa25e135eada3cdc371c86020b14df52'
SYMBOL = '_ZNK7cocos2d4Rect7getMinXEv'
REFERENCE_HASH = 'a89b85f8bccd76763270edbe8d4a9000e557118189ef0a663b750b93593d16da'
FLAGS = ['--target=armv7a-linux-androideabi21', '-mthumb', '-O2', '-ffunction-sections']


def reference_bytes(archive, work, readelf):
    with archive.open('rb') as source:
        if digest(source) != ARCHIVE_HASH:
            raise ValueError('Expected the pinned original 1.7.0 APK.')
    with ZipFile(archive) as apk:
        library = apk.read(LIBRARY_ENTRY)
    if sha256(library).hexdigest() != LIBRARY_HASH:
        raise ValueError('The historical library fingerprint differs.')
    local = work / 'historical.so'
    local.write_bytes(library)

    symbols = subprocess.check_output([readelf, '--wide', '--dyn-syms', local], text=True, timeout=30)
    matches = re.findall(rf'^\s*\d+:\s+([0-9a-f]+)\s+(\d+)\s+FUNC\s+\S+\s+\S+\s+(\d+)\s+{SYMBOL}$',
                         symbols, re.MULTILINE)
    if len(matches) != 1:
        raise ValueError(f'Expected one defined {SYMBOL} symbol.')
    address, count, index = matches[0]
    thumb_address = int(address, 16)
    size = int(count)
    sections = subprocess.check_output([readelf, '--wide', '--sections', local], text=True, timeout=30)
    section = re.search(rf'^\s*\[\s*{index}\]\s+\.text\s+PROGBITS\s+(\S+)\s+(\S+)\s+(\S+)',
                        sections, re.MULTILINE)
    if size != 4 or (thumb_address & 1) == 0 or section is None:
        raise ValueError('Unexpected size, instruction set or section for the reference symbol.')
    start, offset, extent = (int(field, 16) for field in section.groups())
    relative = (thumb_address & ~1) - start
    if not 0 <= relative <= extent - size:
        raise ValueError('The reference range is outside .text.')
    code = library[offset + relative:offset + relative + size]
    if sha256(code).hexdigest() != REFERENCE_HASH:
        raise ValueError('The historical function fingerprint differs.')
    return code


def verify(archive, ndk):
    spec = json.loads((ROOT / 'toolchain.json').read_text(encoding='utf-8'))
    clang, objcopy, readelf = tools(ndk or default_ndk(spec['ndk_package']), spec)
    source = ROOT / 'fixtures' / 'historical' / 'rect_min_x.cpp'
    with TemporaryDirectory(prefix='hcr2-historical-check-') as temp:
        work = Path(temp)
        reference = reference_bytes(archive, work, readelf)
        subprocess.run([clang, *FLAGS, '-c', source, '-o', 'candidate.o'],
                       cwd=work, check=True, timeout=30)
        relocs = subprocess.check_output([readelf, '--relocs', 'candidate.o'],
                                        cwd=work, text=True, timeout=30)
        if re.search(r"Relocation section '\.rela?\.text\.", relocs):
            raise ValueError('The candidate has code relocations.')
        for symbol in ('min_x', 'negative_control'):
            subprocess.run([objcopy, f'--dump-section=.text.{symbol}={symbol}.text',
                            'candidate.o', 'discard.o'], cwd=work, check=True, timeout=30)
        if (work / 'min_x.text').read_bytes() != reference:
            raise ValueError('The candidate differed from the historical function.')
        if (work / 'negative_control.text').read_bytes() == reference:
            raise ValueError('The negative control unexpectedly matched.')
    print(f'1.7.0 ARMv7 | {SYMBOL} | {len(reference)} bytes | SHA-256 {REFERENCE_HASH}')
    print('PASS: exact historical function bytes and rejected negative control.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path, help='The pinned local 1.7.0 APK')
    parser.add_argument('--ndk', type=Path, help='Path to the pinned Android NDK')
    args = parser.parse_args()
    try:
        verify(args.archive, args.ndk)
    except (OSError, BadZipFile, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(f'Unable to verify historical example: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
