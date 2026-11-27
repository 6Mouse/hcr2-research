import hashlib
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from project import BLOCK, compare, verify_release


class VerificationTests(unittest.TestCase):
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
