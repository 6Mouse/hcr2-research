"""Count exact matches against the explicitly enrolled fixture catalog."""
from datetime import date
import json
import re
from urllib.parse import urlparse

CATALOG = 'function_catalog.json'


def read_catalog(data, root=None):
    entries = json.loads(data)
    if not isinstance(entries, list):
        raise ValueError('Function catalog must be an array')
    seen = set()
    for entry in entries:
        task = entry['id']
        if not re.fullmatch(r'HCR2-\d{3,}', task) or task in seen:
            raise ValueError(f'Invalid or duplicate function ID: {task}')
        seen.add(task)
        if not re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]{0,99}', entry['symbol']):
            raise ValueError(f'{task}: invalid fixture symbol')
        if type(entry['bytes']) is not int or entry['bytes'] <= 0:
            raise ValueError(f'{task}: expected a positive byte count')
        if not entry.get('matched_on'):
            continue
        if date.fromisoformat(entry['matched_on']).isoformat() != entry['matched_on']:
            raise ValueError(f'{task}: expected a YYYY-MM-DD match date')
        evidence = urlparse(entry['evidence'])
        if evidence.scheme != 'https' or not evidence.hostname:
            raise ValueError(f'{task}: a match needs HTTPS evidence')
        folder = entry['fixture']
        if not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', folder):
            raise ValueError(f'{task}: invalid fixture directory')
        if root is not None:
            manifest = json.loads((root / 'fixtures' / folder / 'match.json').read_text(encoding='utf-8'))
            if (manifest['id'], manifest['symbol'], manifest['function_bytes']) != (task, entry['symbol'], entry['bytes']):
                raise ValueError(f'{task}: catalog disagrees with its fixture manifest')
    return entries


def totals(entries):
    matched = [entry for entry in entries if entry.get('matched_on')]
    return {
        'matched_functions': len(matched), 'total_functions': len(entries),
        'matched_bytes': sum(entry['bytes'] for entry in matched),
        'total_bytes': sum(entry['bytes'] for entry in entries),
    }


def new_matches(before, after):
    previous = {entry['id'] for entry in before if entry.get('matched_on')}
    return [entry for entry in after if entry.get('matched_on') and entry['id'] not in previous]
