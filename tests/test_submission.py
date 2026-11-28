import unittest

from tools.check_submission import validate


class SubmissionTests(unittest.TestCase):
    catalog = [{'fixture': 'rotate-byte'}, {'fixture': 'limit-score'}]
    candidate = 'fixtures/rotate-byte/candidate.cpp'

    def test_contributors_can_submit_an_enrolled_candidate_or_a_research_change(self):
        self.assertEqual(validate({self.candidate}, self.catalog), self.candidate)
        self.assertIsNone(validate({'README.md'}, self.catalog))

    def test_contributors_cannot_record_official_progress(self):
        with self.assertRaisesRegex(ValueError, 'repository owner'):
            validate({'function_catalog.json'}, self.catalog)

    def test_contributors_cannot_change_build_inputs_or_submit_multiple_candidates(self):
        for extra in ('toolchain.json', 'fixtures/rotate-byte/match.json',
                      'fixtures/limit-score/candidate.cpp'):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                validate({self.candidate, extra}, self.catalog)
        with self.assertRaises(ValueError):
            validate({'fixtures/unknown/candidate.cpp'}, self.catalog)
