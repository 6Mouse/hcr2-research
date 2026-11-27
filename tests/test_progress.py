import json
import unittest
from unittest.mock import patch

from progress import new_matches, read_catalog, totals
from tools.notify_matches import messages, post


def entry(number, size, matched=False):
    row = {'id': f'HCR2-{number:03}', 'symbol': f'function_{number}', 'bytes': size}
    if matched:
        row.update(matched_on='2026-11-28', fixture=f'fixture-{number}',
                   evidence='https://example.com/build')
    return row


class ProgressTests(unittest.TestCase):
    def test_functions_and_bytes_use_separate_denominators(self):
        before = [entry(1, 2_000_000, True), entry(2, 8_000_000), entry(3, 20_000_000)]
        after = read_catalog(json.dumps([before[0], entry(2, 8_000_000, True), before[2]]))
        metrics = totals(after)
        self.assertEqual(metrics, dict(matched_functions=2, total_functions=3,
                                       matched_bytes=10_000_000, total_bytes=30_000_000))
        new = new_matches(before, after)
        self.assertEqual([row['id'] for row in new], ['HCR2-002'])
        notice, = messages(new, metrics)
        self.assertIn('8,000,000 bytes · 2026-11-28', notice)
        self.assertIn('2/3 functions', notice)
        self.assertIn('10.000000/30.000000 MB', notice)
        self.assertEqual(messages(new_matches(after, after), metrics), [])

    def test_large_batches_fit_discord_message_limit(self):
        rows = [entry(n, n + 1, True) for n in range(100)]
        notices = messages(rows, totals(rows))
        self.assertGreater(len(notices), 1)
        self.assertTrue(all(len(notice) <= 1900 for notice in notices))
        self.assertEqual(sum(notice.count(' · 2026-11-28') for notice in notices), 100)

    def test_webhook_suppresses_mentions_and_rejects_non_discord_urls(self):
        with self.assertRaises(ValueError):
            post('https://example.com/api/webhooks/123/token', 'test')
        with patch('tools.notify_matches.build_opener') as opener:
            post('https://discord.com/api/webhooks/123/test_token', 'test')
            request = opener.return_value.open.call_args.args[0]
            self.assertEqual(json.loads(request.data),
                             {'content': 'test', 'allowed_mentions': {'parse': []}})
            self.assertTrue(request.full_url.endswith('?wait=true'))
