#!/usr/bin/env python3
"""Create a review-only Korean driver/vehicle-transport keyword catalog.

This tool does NOT publish pages or assert search volume. Every candidate is
marked for manual review; only useful, accurate terms should become public pages.
"""
import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGIONS_FILE = ROOT / "data" / "regions.json"
DEFAULT_OUTPUT = ROOT / "data" / "keyword_catalog.csv"

SERVICE_TERMS = [
    ("대리운전", "대리운전"),
    ("전국대리운전", "대리운전"),
    ("24시대리운전", "대리운전"),
    ("심야대리운전", "대리운전"),
    ("예약대리운전", "대리운전"),
    ("자동차탁송", "탁송"),
    ("전국탁송", "탁송"),
    ("전국자동차탁송", "탁송"),
    ("장거리탁송", "탁송"),
    ("24시탁송", "탁송"),
    ("예약탁송", "탁송"),
    ("골프장탁송", "탁송"),
    ("캠핑카탁송", "탁송"),
    ("1톤탁송", "탁송"),
    ("승합차탁송", "탁송"),
    ("공항탁송", "탁송"),
]
DAERI_SCENARIOS = [
    "골프장대리운전", "펜션대리운전", "계곡대리운전", "캠핑장대리운전",
    "리조트대리운전", "호텔대리운전", "식당대리운전", "회식대리운전",
    "관광지대리운전", "터미널대리운전", "역대리운전", "심야대리운전",
    "새벽대리운전", "주말대리운전", "법인대리운전", "골프대리운전",
]
TAKSONG_SCENARIOS = [
    "골프장탁송", "펜션탁송", "계곡탁송", "캠핑장탁송", "캠핑카탁송",
    "1톤탁송", "공항탁송", "장거리탁송", "중고차탁송", "정비소탁송",
    "렌터카탁송", "승합차탁송", "전기차탁송", "수입차탁송",
    "산행탁송", "종주탁송", "자전거종주탁송",
]

def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(REGIONS_FILE))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--limit", type=int, default=100000)
    args = parser.parse_args()
    if args.limit < 1 or args.limit > 100000:
        parser.error("--limit must be between 1 and 100000")

    source = json.loads(Path(args.input).read_text(encoding="utf-8"))
    regions = source.get("regions", [])
    if not regions:
        raise SystemExit("No region records found; import and validate official region data first.")

    candidates = {}
    def add(keyword, category, region="", parent="", kind="서비스 조합"):
        keyword = clean(keyword)
        key = keyword.casefold()
        if not keyword or key in candidates or len(candidates) >= args.limit:
            return
        candidates[key] = {
            "keyword": keyword,
            "category": category,
            "region": clean(region),
            "parent_region": clean(parent),
            "candidate_type": kind,
            "status": "검수필요",
            "publish_page": "아니오",
        }

    normalized_regions = []
    for item in regions:
        name = clean(item.get("name"))
        parent = clean(item.get("parent_name"))
        if not name:
            continue
        full = clean(f"{parent} {name}")
        normalized_regions.append((full, name, parent, item))
        for term, category in SERVICE_TERMS:
            add(f"{full} {term}", category, full, parent, "지역+핵심서비스")
        for term in DAERI_SCENARIOS:
            add(f"{full} {term}", "대리운전", full, parent, "지역+이용상황")
        for term in TAKSONG_SCENARIOS:
            add(f"{full} {term}", "탁송", full, parent, "지역+차량/목적")
        for term in ("골프장", "펜션", "계곡", "캠핑장", "리조트", "호텔", "관광지"):
            add(f"{full} {term} 대리운전", "대리운전", full, parent, "지역+시설")
            add(f"{full} {term} 탁송", "탁송", full, parent, "지역+시설")

    # Build plausible directional route candidates only from distinct, verified
    # region names. The catalog is for review; these are not claims of service availability.
    for origin, _, origin_parent, _ in normalized_regions:
        for destination, _, destination_parent, _ in normalized_regions:
            if origin == destination:
                continue
            if len(candidates) >= args.limit:
                break
            add(f"{origin} {destination} 탁송", "경로탁송", origin, destination_parent, "출발지+도착지")
            if len(candidates) >= args.limit:
                break
        if len(candidates) >= args.limit:
            break

    rows = list(candidates.values())[:args.limit]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["keyword", "category", "region", "parent_region",
                        "candidate_type", "status", "publish_page"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Region records read: {len(regions)}")
    print(f"Unique keyword candidates written: {len(rows)}")
    print(f"Output: {output}")
    if len(rows) < args.limit:
        print("The current region dataset did not produce the requested number of unique candidates.")
    print("All rows require review. No pages were published.")

if __name__ == "__main__":
    main()
