"""Source failure must preserve a verified CSV, never accept an error page."""
import csv
import io
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from download_regions import PRIMARY, PUBLISHED, acquire, validate_csv


def fixture():
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(['법정동코드', '시도명', '시군구명', '읍면동명'])
    for i in range(1001):
        writer.writerow([str(1000000000 + i), '검증용지역' * 12, '검증구', '검증동'])
    return stream.getvalue().encode('cp949')


class RegionDownloadTests(unittest.TestCase):
    def test_primary(self):
        data = fixture()
        payload, source, count = acquire(lambda url: data)
        self.assertEqual((payload, source, count), (data, PRIMARY, 1001))

    def test_fallback_after_primary_failure(self):
        data = fixture()
        def fetch(url):
            if url == PRIMARY:
                raise TimeoutError('test timeout')
            return data
        self.assertEqual(acquire(fetch)[1], PUBLISHED)

    def test_rejects_html_and_small_or_invalid_code_data(self):
        for data in (b'<html>error</html>' * 10000, b'too small', fixture().replace(b'1000000000', b'not-a-code')):
            with self.assertRaises((ValueError, csv.Error)):
                validate_csv(data)

    def test_both_fail_without_silent_pilot(self):
        with self.assertRaises(RuntimeError):
            acquire(lambda url: b'<html>not a csv</html>' * 10000)


if __name__ == '__main__':
    unittest.main()
