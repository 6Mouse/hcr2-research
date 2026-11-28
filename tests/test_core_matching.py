import hashlib
import json
import unittest
from unittest.mock import patch

from core_matches import counts, read_matches
from tools.automatic_matches import find_owner_merges, mark_verified
from tools.check_core_submission import check_paths
from tools.match_core import check_code
from tools.notify_core import update_message


BASELINE = dict(version='1.76.1', abi='arm64-v8a', engine_sha256='a' * 64)
CODE = b'\x1f\x20\x03\xd5'
ENTRY = dict(id='ARM64-001', symbol='example', file_offset=0x1000, bytes=len(CODE),
             sha256=hashlib.sha256(CODE).hexdigest(), note='Synthetic test range.')


def catalog(*entries):
    return json.dumps(dict(version=BASELINE['version'], abi=BASELINE['abi'],
                           core_sha256=BASELINE['engine_sha256'], functions=entries))


class CoreMatchingTests(unittest.TestCase):
    def test_only_recorded_matches_count(self):
        verified = {**ENTRY, 'verified_on': '2026-11-28', 'evidence': 'https://example.com/pull/1'}
        open_entry = {**ENTRY, 'id': 'ARM64-002', 'symbol': 'other', 'file_offset': 0x1004}
        entries = read_matches(catalog(verified, open_entry), BASELINE)['functions']
        self.assertEqual(counts(entries), dict(enrolled_functions=2, verified_functions=1,
                                              enrolled_machine_code_bytes=8, verified_machine_code_bytes=4))
        self.assertIn('New match: ARM64-001 · 4 bytes', update_message([], [], [], entries))
        self.assertEqual(update_message([], [], entries, entries), '')

    def test_ranges_must_match_the_pinned_core_and_count_once(self):
        other = {**ENTRY, 'id': 'ARM64-002', 'symbol': 'other'}
        with self.assertRaisesRegex(ValueError, 'overlap'):
            read_matches(catalog(ENTRY, other), BASELINE)
        with self.assertRaisesRegex(ValueError, 'pinned'):
            read_matches(catalog(ENTRY), {**BASELINE, 'abi': 'armeabi-v7a'})

    def test_length_digest_and_exact_reference_checks(self):
        check_code(CODE, ENTRY, CODE)
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            check_code(bytes(4), ENTRY)
        with self.assertRaisesRegex(ValueError, 'archive bytes'):
            check_code(CODE, ENTRY, bytes(4))

    def test_public_candidate_pr_can_change_only_the_enrolled_source(self):
        path = 'matching/candidates/ARM64-001.cpp'
        self.assertEqual(check_paths([path], set(), {'ARM64-001'}), path)
        for paths, ids in (([path], set()), ([path, 'core_matches.json'], {'ARM64-001'})):
            with self.subTest(paths=paths, ids=ids), self.assertRaises(ValueError):
                check_paths(paths, set(), ids)

    def test_owner_only_publication_can_record_a_core_candidate_once(self):
        repo = '6Mouse/hcr2-research'
        path = 'matching/candidates/ARM64-001.cpp'
        pr = {'merged_at': '2026-11-28T11:00:00Z', 'merged_by': {'login': '6Mouse'},
              'base': {'ref': 'main', 'repo': {'full_name': repo}}, 'merge_commit_sha': 'merge',
              'changed_files': 1, 'title': '[ARM64-001] Match example'}
        responses = {'commits/merge/pulls': [{'number': 11}], 'pulls/11': pr,
                     'pulls/11/files': [{'filename': path, 'status': 'added', 'sha': 'blob'}]}
        with (patch('tools.automatic_matches.git', side_effect=['100644 blob blob', 'merge'] * 2),
              patch('tools.automatic_matches.github', side_effect=lambda repo, endpoint: responses[endpoint])):
            approved = find_owner_merges(repo, {ENTRY['id']: path})
            self.assertEqual(approved, {ENTRY['id']: 11})
            pr['merged_by']['login'] = 'SomeoneElse'
            self.assertEqual(find_owner_merges(repo, {ENTRY['id']: path}), {})
        entries = [ENTRY.copy()]
        mark_verified(entries, approved, repo, '2026-11-28', date_field='verified_on')
        self.assertEqual(counts(entries)['verified_machine_code_bytes'], len(CODE))
        self.assertEqual(entries[0]['evidence'], f'https://github.com/{repo}/pull/11')
        with self.assertRaises(ValueError):
            mark_verified(entries, approved, repo, '2026-11-28', date_field='verified_on')
