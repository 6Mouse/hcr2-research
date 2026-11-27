import unittest

from tools.function_queue import assignment, plan


def request(number, owner, grant=None):
    return {'number': number, 'owner': owner, 'grant': grant}


class FunctionQueueTests(unittest.TestCase):
    def setUp(self):
        self.first = {'id': 'HCR2-006', 'bytes': 16}
        self.second = {'id': 'HCR2-007', 'bytes': 12}
        self.done = {'id': 'HCR2-005', 'bytes': 8, 'matched_on': '2026-11-28'}
        self.catalog = [self.first, self.second, self.done]

    def test_assigns_one_per_account_and_one_per_function(self):
        rows = [request(4, 'Alice'), request(6, 'Bob'), request(5, 'alice'), request(9, 'Chris')]
        self.assertEqual(list(plan(self.catalog, rows)), [(4, self.second), (6, self.first)])

    def test_retains_grants_and_releases_after_close_or_match(self):
        rows = [request(4, 'Alice', (100, 'HCR2-007')), request(5, 'Alice'), request(8, 'Bob')]
        self.assertEqual(list(plan(self.catalog, rows)), [(8, self.first)])
        self.assertEqual(list(plan(self.catalog, rows[1:])), [(5, self.second), (8, self.first)])
        self.second['matched_on'] = '2026-11-28'
        self.assertEqual(list(plan(self.catalog, rows)), [(5, self.first)])

    def test_only_bot_comments_allocate_work(self):
        marker = '<!-- function-queue:v1 HCR2-006 -->'
        human = {'id': 12, 'body': marker, 'user': {'login': 'some-user'}}
        bot = {'id': 13, 'body': marker, 'user': {'login': 'github-actions[bot]'}}
        self.assertIsNone(assignment([human]))
        self.assertEqual(assignment([human, bot]), (13, 'HCR2-006'))
