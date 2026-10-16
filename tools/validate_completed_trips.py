#!/usr/bin/env python3
"""Validate privacy-safe completed-trip records before site generation."""
import json
import re
from pathlib import Path
from datetime import date

DATA = Path("data/completed_trips.json")
ALLOWED_FIELDS = {"운행일", "출발시간", "출발지", "도착지", "금액"}
FORBIDDEN_TERMS = (
    "이름", "고객명", "전화", "휴대폰", "핸드폰", "주민", "등록번호",
    "customer", "phone", "mobile", "resident", "rrn", "password", "email",
)

def fail(message):
    raise SystemExit("완료 운행 데이터 검증 실패: " + message)

def main():
    if not DATA.is_file():
        fail("data/completed_trips.json 파일이 없습니다.")
    try:
        data = json.loads(DATA.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail(f"JSON을 읽을 수 없습니다: {exc}")

    trips = data.get("trips") if isinstance(data, dict) else None
    if not isinstance(trips, list):
        fail("'trips'는 목록이어야 합니다.")

    for index, trip in enumerate(trips, start=1):
        if not isinstance(trip, dict):
            fail(f"{index}번째 운행 기록은 객체여야 합니다.")
        unexpected = set(trip) - ALLOWED_FIELDS
        missing = ALLOWED_FIELDS - set(trip)
        if unexpected:
            fail(f"{index}번째 기록에 허용되지 않은 항목이 있습니다: {', '.join(sorted(unexpected))}")
        if missing:
            fail(f"{index}번째 기록에 필수 항목이 없습니다: {', '.join(sorted(missing))}")

        for key, value in trip.items():
            if any(term in key.lower() for term in FORBIDDEN_TERMS):
                fail(f"개인정보 관련 필드가 발견되었습니다: {key}")
            if key in ("운행일", "출발시간", "출발지", "도착지") and not isinstance(value, str):
                fail(f"{index}번째 기록의 {key}는 문자열이어야 합니다.")
            if isinstance(value, str) and not value.strip():
                fail(f"{index}번째 기록의 {key} 값이 비어 있습니다.")

        try:
            date.fromisoformat(trip["운행일"])
        except (ValueError, TypeError):
            fail(f"{index}번째 운행일은 YYYY-MM-DD 형식이어야 합니다.")
        if not re.fullmatch(r"(?:[01]\\d|2[0-3]):[0-5]\\d", trip["출발시간"]):
            fail(f"{index}번째 출발시간은 HH:MM 24시간 형식이어야 합니다.")
        if isinstance(trip["금액"], bool) or not isinstance(trip["금액"], (int, float)) or trip["금액"] <= 0:
            fail(f"{index}번째 금액은 0보다 큰 숫자여야 합니다.")

    print(f"완료 운행 데이터 검증 완료: {len(trips):,}건, 허용 필드 5개, 개인정보 필드 없음")

if __name__ == "__main__":
    main()
