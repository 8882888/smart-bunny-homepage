#!/usr/bin/env python3
"""Download official regions, or explicitly reuse the last verified publication."""
import csv
import hashlib
import io
import os
import re
from pathlib import Path
from urllib.request import urlopen

PRIMARY = 'https://www.data.go.kr/cmm/cmm/fileDownload.do?atchFileId=FILE_000000003687312&fileDetailSn=1'
PUBLISHED = 'https://8882888.github.io/smart-bunny-homepage/data/official_legal_dong.csv'
MAX_BYTES = 10 * 1024 * 1024


def validate_csv(payload):
    if not 100_000 < len(payload) <= MAX_BYTES:
        raise ValueError('Region CSV size is outside the expected range')
    text = None
    for encoding in ('utf-8-sig', 'cp949', 'euc-kr'):
        try:
            text = payload.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        raise ValueError('Unsupported region CSV encoding')
    rows = csv.DictReader(io.StringIO(text))
    headers = {str(name).strip(): name for name in (rows.fieldnames or [])}
    if not {'법정동코드', '시도명', '시군구명'}.issubset(headers):
        raise ValueError('Official region CSV headers are missing')
    count = 0
    for row in rows:
        code = str(row.get(headers['법정동코드']) or '').strip()
        if not code:
            continue
        if not re.fullmatch(r'\d{10}', code):
            raise ValueError('Invalid legal-dong code in downloaded CSV')
        count += 1
    if count < 1000:
        raise ValueError('Region CSV contains too few records')
    return count


def fetch_bytes(url):
    with urlopen(url, timeout=30) as response:
        return response.read(MAX_BYTES + 1)


def acquire(fetcher=fetch_bytes):
    errors = []
    for url in (PRIMARY, PUBLISHED):
        try:
            payload = fetcher(url)
            count = validate_csv(payload)
            return payload, url, count
        except Exception as error:
            errors.append(f'{url}: {error}')
            print(f'::warning::Region source unavailable or invalid: {error}')
    raise RuntimeError('No verified region CSV is available. ' + ' | '.join(errors))


def main():
    payload, source, count = acquire()
    output = Path('data/official_legal_dong.csv')
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix('.csv.part')
    temporary.write_bytes(payload)
    temporary.replace(output)
    fallback = source != PRIMARY
    if fallback:
        print('::warning::Using the last published verified official CSV; a fresh government download was unavailable.')
    digest = hashlib.sha256(payload).hexdigest()
    print(f'Region CSV validated: {count:,} rows; source={source}; reused_publication={fallback}; sha256={digest}')
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as summary:
            summary.write(f'### Region data source\n- Source: {source}\n- Records: {count:,}\n- Reused last verified publication: {fallback}\n- SHA-256: `{digest}`\n')


if __name__ == '__main__':
    main()
