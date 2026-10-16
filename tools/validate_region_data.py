#!/usr/bin/env python3
"""Validate imported official legal-dong data before generating static pages."""
import json
import re
from pathlib import Path

DATA = Path("data/regions.json")
EXPECTED_BRAND = "스마트번개대리운전"
EXPECTED_PHONE = "1877-3015"
EXPECTED_SERVICES = {"daeri", "taksong", "long-distance-taksong"}
MAX_HTML_FILES = 100_000


def fail(message):
    raise SystemExit("지역 데이터 검증 실패: " + message)


def main():
    if not DATA.is_file():
        fail("data/regions.json 파일이 없습니다.")
    try:
        data = json.loads(DATA.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail(f"regions.json을 읽을 수 없습니다: {exc}")

    if data.get("brand") != EXPECTED_BRAND or data.get("phone") != EXPECTED_PHONE:
        fail("브랜드 또는 대표 전화가 프로젝트 설정과 일치하지 않습니다.")

    regions = data.get("regions")
    if not isinstance(regions, list) or len(regions) < 1000:
        fail(f"전국 데이터가 충분하지 않습니다. 현재 지역 수: {len(regions) if isinstance(regions, list) else 0}")

    codes, slugs = set(), set()
    for index, item in enumerate(regions, start=1):
        for field in ("name", "slug", "level", "legal_dong_code", "services"):
            if not item.get(field):
                fail(f"{index}번째 지역에 필수 항목 {field}가 없습니다.")
        code = str(item["legal_dong_code"]).strip()
        slug = str(item["slug"]).strip("/")
        if not re.fullmatch(r"\d{10}", code):
            fail(f"법정동 코드 형식이 잘못되었습니다: {code}")
        if code in codes:
            fail(f"법정동 코드 중복: {code}")
        if slug in slugs:
            fail(f"지역 URL 경로 중복: {slug}")
        if any(part in ("", ".", "..") for part in slug.split("/")):
            fail(f"지역 URL 경로가 잘못되었습니다: {slug}")
        if not EXPECTED_SERVICES.issubset(set(item["services"])):
            fail(f"서비스 종류 누락: {slug}")
        # Public regional records must not contain customer-identifying fields.
        forbidden = {"customer_name", "name_of_customer", "phone", "phone_number",
                     "mobile", "resident_registration_number", "rrn", "customer_phone"}
        if forbidden.intersection(item.keys()):
            fail(f"개인정보 관련 필드가 지역 데이터에 포함되어 있습니다: {slug}")
        codes.add(code)
        slugs.add(slug)

    # Each record produces a region landing page plus up to three service pages.
    estimated_html = len(regions) * 4 + 40
    if estimated_html >= MAX_HTML_FILES:
        fail(f"예상 HTML 파일 수가 안전 한도를 넘습니다: 약 {estimated_html}개")

    print(
        f"지역 데이터 검증 완료: {len(regions):,}개 지역, "
        f"법정동 코드 중복 0건, URL 경로 중복 0건, "
        f"예상 HTML 약 {estimated_html:,}개"
    )


if __name__ == "__main__":
    main()
