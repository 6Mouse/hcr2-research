import hashlib
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from project import BLOCK, compare, verify_release
from tools.release_inventory import elf_metadata


class VerificationTests(unittest.TestCase):
    def test_elf_inventory_separates_symbols_and_unwind_entries(self):
        metadata = elf_metadata('''
  [ 2] .text PROGBITS 0000000000000180 000180 000020 00 AX 0 0 4
  LOAD 0x000000 0x0000000000000000 0x0000000000000000 0x000200 0x000200 R E 0x4000
  LOAD 0x000200 0x0000000000004200 0x0000000000004200 0x000080 0x000100 RW 0x4000
Symbol table '.dynsym' contains 3 entries:
     0: 0000000000000000 0 NOTYPE LOCAL DEFAULT UND
     1: 0000000000000000 0 FUNC GLOBAL DEFAULT UND free
     2: 0000000000000180 32 FUNC GLOBAL DEFAULT 2 fixture_function
    fde_count: 5
    Build ID: 1234
''')
        self.assertEqual(metadata, dict(executable_load_file_bytes=512, text_section_present=True,
                                        defined_dynamic_function_symbols=1,
                                        eh_frame_index_entries=5, gnu_build_id='1234'))
        self.assertIsNone(elf_metadata('')['defined_dynamic_function_symbols'])

    def test_comparer_finds_first_difference_and_trailing_bytes(self):
        with TemporaryDirectory() as root:
            left = Path(root) / 'reference'
            right = Path(root) / 'candidate'
            prefix = b'a' * BLOCK
            left.write_bytes(prefix + b'bc')
            self.assertTrue(compare(left, left)['match'])
            right.write_bytes(prefix + b'bd')
            self.assertEqual(compare(left, right)['first_difference'], BLOCK + 1)
            right.write_bytes(prefix + b'bcd')
            self.assertEqual(compare(left, right)['first_difference'], BLOCK + 2)

    def test_archive_and_split_matches_are_reported_separately(self):
        def sha(data):
            return hashlib.sha256(data).hexdigest()

        engine = b'synthetic ARM64 engine placeholder'
        base = b'synthetic base APK placeholder'
        nested = BytesIO()
        with ZipFile(nested, 'w') as split:
            split.writestr('lib/fixture.so', engine)
        arm64 = nested.getvalue()
        with TemporaryDirectory() as root:
            archive = Path(root) / 'fixture.apks'
            with ZipFile(archive, 'w') as output:
                output.writestr('base.apk', base)
                output.writestr('arm64.apk', arm64)
            baseline = dict(archive_sha256=sha(archive.read_bytes()),
                            archive_bytes=archive.stat().st_size,
                            base_entry='base.apk', base_sha256=sha(base),
                            arm64_entry='arm64.apk', arm64_sha256=sha(arm64),
                            engine_entry='lib/fixture.so', engine_sha256=sha(engine))
            report = verify_release(archive, baseline)
            self.assertTrue(report['match'])
            self.assertTrue(report['archive_match'])
            with ZipFile(archive, 'a') as output:
                output.comment = b'only the wrapper changed'
            report = verify_release(archive, baseline)
            self.assertTrue(report['match'])
            self.assertFalse(report['archive_match'])
