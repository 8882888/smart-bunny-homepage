#!/usr/bin/env python3
"""Check generated regional pages and sitemap without external dependencies."""
import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
regions = json.loads((ROOT / "data/regions.json").read_text(encoding="utf-8"))["regions"]
issues = []
slugs = [r["slug"].strip("/") for r in regions]
if len(slugs) != len(set(slugs)):
    issues.append("Duplicate region slugs")
for r in regions:
    path = ROOT / "region" / r["slug"].strip("/") / "index.html"
    if not path.is_file():
        issues.append(f"Missing region page: {path.relative_to(ROOT)}")
        continue
    page = path.read_text(encoding="utf-8")
    if page.count('rel="canonical"') != 1:
        issues.append(f"Invalid canonical count: {path.relative_to(ROOT)}")
    if "1877-3015" not in page or "1811-0963" in page:
        issues.append(f"Brand contact mismatch: {path.relative_to(ROOT)}")
    if not re.search(r"<h1[^>]*>", page):
        issues.append(f"Missing H1: {path.relative_to(ROOT)}")
index_path = ROOT / "region/region-index.json"
if index_path.is_file():
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if len(index) != len(regions):
        issues.append(f"Search index count mismatch: {len(index)} vs {len(regions)}")
else:
    issues.append("Missing region search index")
sitemap = ROOT / "sitemap.xml"
if sitemap.is_file():
    tree = ET.parse(sitemap)
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    chunks = [node.text for node in tree.findall(".//s:loc", namespace)]
    if not chunks:
        issues.append("No sitemap chunks listed")
    for chunk in chunks:
        filename = unquote(urlsplit(chunk).path.rsplit("/", 1)[-1])
        if not filename or not (ROOT / filename).is_file():
            issues.append(f"Missing sitemap chunk: {filename}")
else:
    issues.append("Missing sitemap.xml")
print(f"Checked {len(regions)} region records, {len(set(slugs))} unique slugs.")
if issues:
    print("\n".join("ERROR: " + issue for issue in issues[:50]))
    sys.exit(1)
print("Regional page, search index, brand and sitemap structural checks passed.")
