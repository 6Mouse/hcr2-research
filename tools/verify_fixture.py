"""Compile and check the original HCR2-005 ARM64 fixture."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'fixtures' / 'arm64'


def load_spec(directory):
    toolchain = json.loads((ROOT / 'toolchain.json').read_text(encoding='utf-8'))
    fixture = json.loads((directory / 'match.json').read_text(encoding='utf-8'))
    if toolchain.keys() & fixture.keys():
        raise ValueError('Fixture manifests may not override the shared toolchain')
    return {**toolchain, **fixture}


def default_ndk(package):
    sdk = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
    if sdk:
        return Path(sdk) / 'ndk' / package
    if os.name == 'nt' and os.environ.get('LOCALAPPDATA'):
        return Path(os.environ['LOCALAPPDATA']) / 'Android' / 'Sdk' / 'ndk' / package
    raise ValueError('Set ANDROID_HOME or pass --ndk with the pinned NDK directory.')


def tools(ndk, spec):
    props = (ndk / 'source.properties').read_text(encoding='utf-8').splitlines()
    revision = next((line.partition('=')[2].strip() for line in props
                     if line.partition('=')[0].strip() == 'Pkg.Revision'), '')
    if revision != spec['ndk_revision']:
        raise ValueError(f'Expected NDK {spec["ndk_revision"]}, got {revision or "unknown"}.')
    host = {'Windows': 'windows-x86_64', 'Linux': 'linux-x86_64', 'Darwin': 'darwin-x86_64'}
    directory = ndk / 'toolchains' / 'llvm' / 'prebuilt' / host[platform.system()] / 'bin'
    suffix = '.exe' if os.name == 'nt' else ''
    clang, objcopy, readelf = (directory / (name + suffix)
                              for name in ('clang++', 'llvm-objcopy', 'llvm-readelf'))
    version = subprocess.check_output([clang, '--version'], text=True, timeout=15).splitlines()[0]
    if f'clang version {spec["clang_version"]} ' not in version or spec['clang_revision'] not in version:
        raise ValueError(f'Unexpected compiler: {version}')
    print(version, flush=True)
    return clang, objcopy, readelf


def compile_fixture(source, out, clang, objcopy, readelf, spec):
    out.mkdir()
    # Use the same relative source name so the ELF source symbol is reproducible.
    shutil.copyfile(source, out / 'fixture.cpp')
    subprocess.run([clang, *spec['flags'], '-c', 'fixture.cpp', '-o', 'fixture.o'],
                   cwd=out, check=True, timeout=30)
    relocs = subprocess.check_output([readelf, '--relocs', 'fixture.o'], cwd=out,
                                    text=True, timeout=15)
    if relocs.strip() != 'There are no relocations in this file.':
        raise ValueError(f'{source.name} must produce a relocation-free object for this pilot.')
    subprocess.run([objcopy, f'--dump-section=.text.{spec["symbol"]}=fixture.text',
                    'fixture.o', 'discard.o'], cwd=out, check=True, timeout=15)
    return (out / 'fixture.o').read_bytes(), (out / 'fixture.text').read_bytes()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify(args, spec):
    ndk = (args.ndk or default_ndk(spec['ndk_package'])).resolve()
    compiler_tools = tools(ndk, spec)
    print(f'Host: {platform.system()} | NDK: {spec["ndk_revision"]}', flush=True)
    print('Flags:', ' '.join(spec['flags']), flush=True)
    with TemporaryDirectory(prefix='arm64-match-') as temp:
        root = Path(temp)
        ref_source = args.fixture / 'reference.cpp'
        reference, code = compile_fixture(ref_source, root / 'reference', *compiler_tools, spec)
        repeat, _ = compile_fixture(ref_source, root / 'repeat', *compiler_tools, spec)
        print(f'Reference object SHA-256: {sha(reference)}', flush=True)
        print(f'Reference function: {len(code)} bytes, SHA-256 {sha(code)}', flush=True)
        if (reference != repeat or sha(reference) != spec['object_sha256'] or
                len(code) != spec['function_bytes'] or sha(code) != spec['function_sha256']):
            print('FAIL: reference build differs from the locked artifact.', file=sys.stderr)
            return 1
        _, control = compile_fixture(args.fixture / 'nonmatch.cpp', root / 'control',
                                     *compiler_tools, spec)
        if control == code:
            print('FAIL: negative control unexpectedly matches.', file=sys.stderr)
            return 1
        if args.reference_only:
            print('PASS: reference hashes and negative control.')
            return 0
        candidate_source = args.candidate or args.fixture / 'candidate.cpp'
        _, candidate = compile_fixture(candidate_source, root / 'candidate', *compiler_tools, spec)
        if candidate != code:
            print(f'FAIL: candidate {len(candidate)} bytes, SHA-256 {sha(candidate)}', file=sys.stderr)
            return 1
    print('PASS: repeated reference object, exact candidate function, and rejected negative control.')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ndk', type=Path, help='Path to the pinned Android NDK')
    parser.add_argument('--fixture', type=Path, default=FIXTURE,
                        help='Directory containing match.json and the three fixture sources')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--candidate', type=Path, help='Compile this C++ source as the candidate')
    modes.add_argument('--reference-only', action='store_true', help='Verify an unsolved reference')
    args = parser.parse_args()
    try:
        spec = load_spec(args.fixture)
        print(f'Fixture: {spec["id"]} | Symbol: {spec["symbol"]}', flush=True)
        return verify(args, spec)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(f'Unable to check fixture: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
