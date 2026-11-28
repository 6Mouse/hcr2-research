import json
import unittest
from unittest.mock import patch

from tools.automatic_matches import apply, discover


class AutomaticMatchTests(unittest.TestCase):
    repo = '6Mouse/hcr2-research'
    candidate = 'fixtures/rotate-byte/candidate.cpp'
    catalog = [{'id': 'HCR2-006', 'fixture': 'rotate-byte'}]

    def approvals(self, *, pr_changes=None, file_changes=None, mode='100644', linked=True):
        pr = {'merged_at': '2026-11-28T11:00:00Z', 'merged_by': {'login': '6Mouse'},
              'base': {'ref': 'main', 'repo': {'full_name': self.repo}}, 'merge_commit_sha': 'merge',
              'changed_files': 1, 'title': '[HCR2-006] Match rotate_byte'}
        file = {'filename': self.candidate, 'status': 'added', 'sha': 'candidate-blob'}
        responses = {'commits/merge/pulls': [{'number': 17}] if linked else [],
                     'pulls/17': {**pr, **(pr_changes or {})}, 'pulls/17/files': [{**file, **(file_changes or {})}]}
        with (patch('tools.automatic_matches.git', side_effect=[f'{mode} blob candidate-blob', 'merge']),
              patch('tools.automatic_matches.github', side_effect=lambda repo, path: responses[path])):
            return discover(self.repo, self.catalog)

    def test_approves_only_reviewed_candidate_and_records_its_pr(self):
        approvals = self.approvals()
        self.assertEqual(approvals, {'HCR2-006': 17})
        catalog = [row.copy() for row in self.catalog]
        result = json.loads(apply(catalog, approvals, self.repo, '2026-11-28'))
        self.assertEqual(result[0]['matched_on'], '2026-11-28')
        self.assertEqual(result[0]['evidence'], f'https://github.com/{self.repo}/pull/17')
        with self.assertRaises(ValueError):
            apply(result, approvals, self.repo, '2026-11-28')

    def test_other_mergers_and_unrelated_or_modified_prs_do_not_count(self):
        for changes in ({'merged_by': {'login': 'another-user'}}, {'merged_at': None},
                        {'merge_commit_sha': 'older'}, {'title': 'Missing catalog tag'},
                        {'base': {'ref': 'test', 'repo': {'full_name': self.repo}}},
                        {'changed_files': 2}):
            with self.subTest(pr_changes=changes):
                self.assertEqual(self.approvals(pr_changes=changes), {})
        for changes in ({'status': 'removed'}, {'status': 'renamed'}, {'filename': 'other.cpp'},
                        {'sha': 'earlier-review'}):
            with self.subTest(file_changes=changes):
                self.assertEqual(self.approvals(file_changes=changes), {})
        self.assertEqual(self.approvals(mode='120000'), {})
        self.assertEqual(self.approvals(linked=False), {})
