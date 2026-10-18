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
# Check homepage service navigation, visual descriptions, and customer contact.
home = (ROOT / "index.html").read_text(encoding="utf-8")
required_sections = ("services", "transport", "corporate", "golf", "quick-request", "regions")
for section in required_sections:
    if not re.search(r'\bid="' + re.escape(section) + r'"', home):
        issues.append(f"Missing homepage service section: {section}")
home_ids = set(re.findall(r'\bid="([^"]+)"', home))
for target in re.findall(r'href="#([^"]+)"', home):
    if target not in home_ids:
        issues.append(f"Broken homepage section link: #{target}")
if "1877-3015" not in home or "1811-0963" in home:
    issues.append("Homepage brand contact mismatch")
service_images = re.findall(r'<img\b[^>]*class="service-image"[^>]*>', home)
if len(service_images) < 4:
    issues.append("Missing homepage service images")
for img in service_images:
    if not re.search(r'\balt="[^"]+"', img):
        issues.append("Service image without descriptive alt text")
if not (ROOT / "reviews/index.html").is_file():
    issues.append("Missing completed-trip reviews page")

# Smoke-test presence of fare search, responsive viewport and admin integration.
if not re.search(r'<meta\s+name="viewport"', home):
    issues.append("Homepage mobile viewport missing")
for element_id in ("fare-search-form", "fare-origin", "fare-destination", "fare-search-result", "quick-request-form"):
    if element_id not in home_ids:
        issues.append(f"Homepage calculator or consultation element missing: {element_id}")
if 'form.addEventListener("submit"' not in home:
    issues.append("Fare search submit handler missing")
admin_path = ROOT / "admin/index.html"
if not admin_path.is_file():
    issues.append("Missing admin page")
else:
    admin = admin_path.read_text(encoding="utf-8")
    for marker in ("signInWithPassword", 'client.from("trip_records")', "supabase-public-config.js"):
        if marker not in admin:
            issues.append(f"Admin integration marker missing: {marker}")
    if not re.search(r'<meta\s+name="viewport"', admin):
        issues.append("Admin mobile viewport missing")
fare_path = ROOT / "data/reference_fares.json"
if not fare_path.is_file():
    issues.append("Missing approved reference fare data file")
else:
    fare_data = json.loads(fare_path.read_text(encoding="utf-8"))
    if not isinstance(fare_data.get("fares"), list):
        issues.append("Approved reference fares must be a list")
    elif not fare_data["fares"]:
        print("NOTICE: Approved reference fare list is empty; calculator cannot quote approved route prices.")
if not (ROOT / "supabase-public-config.js").is_file():
    issues.append("Missing Supabase public configuration")

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
