"""Metadata for isolated function matches against the pinned ARM64 core."""
from datetime import date
import json
from pathlib import Path
import re
from urllib.parse import urlparse

CATALOG = 'core_matches.json'


def candidate_path(identifier):
    return Path('matching') / 'candidates' / f'{identifier}.cpp'


def read_matches(data, baseline, root=None):
    catalog = json.loads(data)
    if (catalog['version'], catalog['abi'], catalog['core_sha256']) != (
            baseline['version'], baseline['abi'], baseline['engine_sha256']):
        raise ValueError('The matching catalog must use the pinned ARM64 core build.')
    entries = catalog['functions']
    if not isinstance(entries, list):
        raise ValueError('Functions must be an array.')
    ids, symbols, spans = set(), set(), []
    for entry in entries:
        identifier, symbol = entry['id'], entry['symbol']
        if not re.fullmatch(r'ARM64-\d{3,}', identifier) or identifier in ids:
            raise ValueError(f'Invalid or repeated ID: {identifier}')
        if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,99}', symbol) or symbol in symbols:
            raise ValueError(f'{identifier}: invalid or repeated candidate symbol.')
        ids.add(identifier)
        symbols.add(symbol)
        offset, size = entry['file_offset'], entry['bytes']
        if (type(offset) is not int or offset < 0 or offset % 4 or
                type(size) is not int or size <= 0 or size % 4):
            raise ValueError(f'{identifier}: invalid ARM64 file offset or byte length.')
        spans.append((offset, offset + size))
        if not re.fullmatch(r'[0-9a-f]{64}', entry['sha256']) or not entry['note'].strip():
            raise ValueError(f'{identifier}: missing digest or reference note.')
        if entry.get('verified_on'):
            stamp = entry['verified_on']
            evidence = urlparse(entry['evidence'])
            if date.fromisoformat(stamp).isoformat() != stamp or evidence.scheme != 'https' or not evidence.hostname:
                raise ValueError(f'{identifier}: expected a verification date and HTTPS review evidence.')
            if root is not None and not (root / candidate_path(identifier)).is_file():
                raise ValueError(f'{identifier}: accepted source is missing.')
    spans.sort()
    if any(right > next_left for (_, right), (next_left, _) in zip(spans, spans[1:])):
        raise ValueError('Reference ranges overlap. Each core byte may count once.')
    return catalog


def counts(entries):
    verified = [entry for entry in entries if entry.get('verified_on')]
    return dict(enrolled_functions=len(entries), verified_functions=len(verified),
                enrolled_machine_code_bytes=sum(entry['bytes'] for entry in entries),
                verified_machine_code_bytes=sum(entry['bytes'] for entry in verified))
