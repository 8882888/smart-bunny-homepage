#!/usr/bin/env python3
"""Generate static local SEO pages for Smart Bunny Driver Service."""
import json
import html
from pathlib import Path
from datetime import date

ROOT = Path(".")
DATA = ROOT / "data" / "regions.json"
SITE_URL = "https://8882888.github.io/smart-bunny-homepage"
BRAND = "스마트번개대리운전"
PHONE = "1877-3015"
SERVICES = [
    {"name": "대리운전", "slug": "daeri", "keyword": "대리운전"},
    {"name": "자동차탁송", "slug": "taksong", "keyword": "탁송"},
    {"name": "장거리탁송", "slug": "long-distance-taksong", "keyword": "장거리탁송"},
]

def esc(value):
    return html.escape(str(value), quote=True)

def page(title, description, body, canonical):
    return f"""<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canonical)}">
<meta name="robots" content="index,follow">
<style>
*{{box-sizing:border-box}}body{{margin:0;font-family:Arial,'Malgun Gothic',sans-serif;line-height:1.8;color:#172235}}
header,footer{{background:#102544;color:white;padding:18px max(5%,calc((100% - 1000px)/2))}}
header a,footer a{{color:#ffd166}}main{{max-width:1000px;margin:auto;padding:28px 5% 50px}}
h1{{line-height:1.35;font-size:clamp(28px,5vw,42px)}}h2{{margin-top:32px}}
.card{{border:1px solid #d9e1ea;border-radius:12px;padding:16px;margin:12px 0}}
.btn{{display:inline-block;background:#ffd166;color:#102544;text-decoration:none;padding:10px 16px;border-radius:8px;font-weight:bold;margin:6px 8px 6px 0}}
.muted{{color:#536276;font-size:.95rem}}ul{{padding-left:22px}}
</style></head><body>
<header><strong>{BRAND}</strong> · <a href="tel:18773015">대표 상담 {PHONE}</a></header>
<main>{body}
<div class="card"><h2>전화 상담</h2><p>출발지와 도착지, 차량 종류, 희망 시간을 알려주시면 상담에 도움이 됩니다.</p>
<p><strong>{PHONE}</strong></p><a class="btn" href="tel:18773015">전화 상담하기</a>
<a class="btn" href="https://open.kakao.com/o/sGV88r7h">카카오톡 오픈채팅</a>
<p class="muted">요금과 배차 가능 여부는 거리, 시간, 차량 및 현장 상황에 따라 달라질 수 있습니다.</p></div>
</main><footer>{BRAND}<br>대표 상담 전화: {PHONE}<br><a href="/smart-bunny-homepage/">홈페이지 첫 화면</a></footer>
</body></html>"""

def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    regions = data.get("regions", [])
    if not regions:
        raise SystemExit("data/regions.json에 지역을 입력해야 합니다.")
    urls = {SITE_URL + "/"}
    count = 0
    for r in regions:
        name = r["name"]
        slug = r["slug"].strip("/")
        level = r.get("level", "지역")
        parent = r.get("parent_name", "")
        location = f"{parent} {name}".strip()
        region_url = f"{SITE_URL}/region/{slug}/"
        urls.add(region_url)
        local_services = r.get("services", [s["slug"] for s in SERVICES])
        links = []
        for s in SERVICES:
            if s["slug"] in local_services:
                href = f"/smart-bunny-homepage/region/{slug}/{s['slug']}/"
                links.append(f'<div class="card"><h3><a href="{href}">{esc(location)} {esc(s["keyword"])}</a></h3><p>{esc(location)} 지역의 {esc(s["name"])} 상담 안내입니다. 실제 배차 가능 여부와 요금은 전화로 확인해 주세요.</p></div>')
                urls.add(f"{SITE_URL}/region/{slug}/{s['slug']}/")
                body = f"""<p class="muted">전국 지역별 서비스 안내 · {esc(level)}</p>
<h1>{esc(location)} {esc(s["keyword"])}</h1>
<p>{esc(location)}에서 대리운전 또는 차량 이동이 필요하실 때 스마트번개대리운전으로 상담해 주세요.</p>
<h2>{esc(location)} {esc(s["name"])} 상담 안내</h2>
<p>상담 시 정확한 출발 위치와 도착 위치, 차량 종류, 이용 희망 시간을 알려주세요. 지역과 시간대에 따라 배차 가능 여부가 달라질 수 있어 사전에 확인하는 것이 좋습니다.</p>
<ul><li>대표 상담 전화: {PHONE}</li><li>출발지와 도착지 확인</li><li>차량 종류 및 희망 시간 확인</li><li>요금과 배차 가능 여부 확인 후 진행</li></ul>
<p class="muted">지역 정보: {esc(location)} · 페이지 업데이트 기준일: {date.today().isoformat()}</p>"""
                out = ROOT / "region" / slug / s["slug"] / "index.html"
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(page(f"{location} {s['keyword']} | {BRAND}", f"{location} {s['keyword']} 상담. 대표 전화 {PHONE}. 출발지, 도착지, 차량 종류와 희망 시간을 알려주세요.", body, f"{SITE_URL}/region/{slug}/{s['slug']}/"), encoding="utf-8")
                count += 1
        body = f"""<p class="muted">전국 지역별 서비스 안내 · {esc(level)}</p>
<h1>{esc(location)} 대리운전 · 자동차탁송</h1>
<p>{esc(location)} 지역에서 이용할 수 있는 스마트번개대리운전 상담 페이지입니다. 필요한 서비스와 이동 경로를 확인한 뒤 대표 전화로 문의해 주세요.</p>
<h2>{esc(location)} 서비스</h2>
{''.join(links)}
<h2>상담 전에 준비하면 좋은 정보</h2><ul><li>출발지와 도착지</li><li>차량 종류</li><li>희망 이용 날짜와 시간</li></ul>
<p class="muted">지역 정보: {esc(location)} · 페이지 업데이트 기준일: {date.today().isoformat()}</p>"""
        out = ROOT / "region" / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(f"{location} 대리운전·탁송 | {BRAND}", f"{location} 대리운전 및 자동차탁송 상담 안내. 대표 전화 {PHONE}.", body, region_url), encoding="utf-8")
        count += 1
    # XML sitemap for generated region pages and service pages.
    entries = "\n".join(f"  <url><loc>{esc(url)}</loc></url>" for url in sorted(urls))
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + entries + "\n</urlset>\n", encoding="utf-8")
    print(f"Generated {count} pages from {len(regions)} region records.")
    print("Reminder: add the complete official nationwide administrative-area dataset to data/regions.json.")

if __name__ == "__main__":
    main()
