#!/usr/bin/env python3
"""Generate useful local service pages for Smart Bunny Driver Service."""
import json
import html
import re
from pathlib import Path
from datetime import date
from urllib.parse import quote, urlsplit, urlunsplit

ROOT = Path(".")
DATA = ROOT / "data" / "regions.json"
TRIP_DATA = ROOT / "data" / "completed_trips.json"
SITE_URL = "https://8882888.github.io/smart-bunny-homepage"
BRAND = "스마트전국대리운전 스마트24탁송"
PHONE = "1877-3015"
SERVICES = [
    {"name": "대리운전", "slug": "daeri", "keyword": "대리운전"},
    {"name": "24시 대리운전", "slug": "24h-daeri", "keyword": "24시 대리운전"},
    {"name": "법인대리운전", "slug": "corporate-daeri", "keyword": "법인대리운전"},
    {"name": "골프대리운전", "slug": "golf-daeri", "keyword": "골프대리운전"},
    {"name": "자동차탁송", "slug": "taksong", "keyword": "자동차탁송"},
    {"name": "장거리탁송", "slug": "long-distance-taksong", "keyword": "장거리탁송"},
]

def esc(value):
    return html.escape(str(value), quote=True)


def load_completed_trips():
    if not TRIP_DATA.is_file():
        return []
    try:
        data = json.loads(TRIP_DATA.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    trips = data.get("trips", []) if isinstance(data, dict) else []
    return [t for t in trips if isinstance(t, dict) and all(
        key in t for key in ("운행일", "출발시간", "출발지", "도착지", "금액")
    )]


def region_aliases(region):
    name = str(region.get("name", "")).strip()
    aliases = [name]
    for suffix in ("특별자치도", "특별자치시", "특별시", "광역시", "자치도", "시", "군", "구", "읍", "면", "동", "리", "도"):
        if name.endswith(suffix) and len(name[:-len(suffix)]) >= 2:
            aliases.append(name[:-len(suffix)])
            break
    return [re.sub(r"\s+", "", alias) for alias in aliases if len(re.sub(r"\s+", "", alias)) >= 2]


def related_trip_html(region, trips, limit=3):
    aliases = region_aliases(region)
    if not aliases or not trips:
        return ""
    matched = []
    for trip in trips:
        route = re.sub(r"\s+", "", str(trip.get("출발지", "")) + str(trip.get("도착지", "")))
        if any(alias in route for alias in aliases):
            matched.append(trip)
            if len(matched) >= limit:
                break
    if not matched:
        return ""
    rows = "".join(
        "<tr>"
        f"<td>{esc(t['운행일'])}</td>"
        f"<td>{esc(t['출발시간'])}</td>"
        f"<td>{esc(t['출발지'])}</td>"
        f"<td>{esc(t['도착지'])}</td>"
        f"<td>{int(t['금액']):,}원</td>"
        "</tr>"
        for t in matched
    )
    return f"""<section class="card"><h2>{esc(region.get("name", "지역"))} 관련 완료 운행 기록</h2>
<p>등록된 운행내역 중 해당 지역과 연결되는 실제 기록입니다. 공개 가능한 항목만 표시합니다.</p>
<div style="overflow-x:auto"><table style="border-collapse:collapse;width:100%;min-width:560px">
<thead><tr><th>운행일</th><th>기록 시각</th><th>출발지</th><th>도착지</th><th>금액</th></tr></thead><tbody>{rows}</tbody></table></div>
<p><a href="/smart-bunny-homepage/reviews/">전국 완료 운행 내역 더 보기 →</a></p></section>"""


def page(title, description, body, canonical):
    return f"""<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canonical)}">
<meta name="robots" content="index,follow">
<style>
*{{box-sizing:border-box}}body{{margin:0;font-family:Arial,'Malgun Gothic',sans-serif;line-height:1.85;color:#172235}}
header,footer{{background:#102544;color:white;padding:18px max(5%,calc((100% - 1000px)/2))}}
header{{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap}}
header a,footer a{{color:#ffd166}}.topnav{{display:flex;align-items:center;justify-content:center;gap:12px;flex-wrap:wrap}}.topnav a{{color:white;text-decoration:none;font-weight:bold;padding:6px 0}}.topnav a.kakao{{background:#FEE500;color:#191919;padding:8px 11px;border-radius:7px;display:inline-flex;align-items:center;gap:6px}}.kakao-icon{{width:18px;height:16px;display:inline-block}}.kakao-hours{{font-size:.9rem;color:white;font-weight:bold;white-space:nowrap}}@media(max-width:700px){{header{{align-items:flex-start}}.topnav{{justify-content:flex-start;gap:10px}}.topnav a{{font-size:.9rem}}.kakao-hours{{font-size:.82rem}}}}main{{max-width:1000px;margin:auto;padding:28px 5% 50px}}
h1{{line-height:1.35;font-size:clamp(28px,5vw,42px)}}h2{{margin-top:32px}}
.card{{border:1px solid #d9e1ea;border-radius:12px;padding:16px;margin:12px 0}}
.btn{{display:inline-block;background:#ffd166;color:#102544;text-decoration:none;padding:10px 16px;border-radius:8px;font-weight:bold;margin:6px 8px 6px 0}}
.muted{{color:#536276;font-size:.95rem}}ul{{padding-left:22px}}
</style></head><body>
<header><strong>{BRAND}</strong><nav class="topnav" aria-label="주요 메뉴"><a href="/smart-bunny-homepage/#services">대리운전</a><a href="/smart-bunny-homepage/#transport">탁송</a><a href="/smart-bunny-homepage/#corporate">법인대리운전</a><a href="/smart-bunny-homepage/#golf">골프대리운전</a><a class="kakao" href="https://open.kakao.com/o/sGV88r7h" target="_blank" rel="noopener noreferrer" aria-label="카톡상담, 상담시간 08:00부터 20:00까지"><svg class="kakao-icon" viewBox="0 0 24 22" aria-hidden="true"><path fill="#191919" d="M12 1C5.9 1 1 4.8 1 9.5c0 3 2 5.7 5.1 7.2l-1 4.1c-.1.4.3.6.6.4l4.8-3.1c.5.1 1 .1 1.5.1 6.1 0 11-3.8 11-8.6S18.1 1 12 1Z"/></svg>카톡상담</a><span class="kakao-hours">상담시간 08:00~20:00</span></nav><a href="tel:18773015">대표 상담 {PHONE}</a></header>
<main>{body}
<div class="card"><h2>전화 상담</h2><p>출발지와 도착지, 차량 종류, 이용 날짜와 희망 시간을 알려주시면 상담이 더 정확해집니다.</p>
<p><strong>{PHONE}</strong></p><a class="btn" href="tel:18773015">전화 상담하기</a>
<a class="btn" href="https://open.kakao.com/o/sGV88r7h">카카오톡 오픈채팅</a>
<p class="muted">요금과 배차 가능 여부는 거리, 시간, 차량 및 현장 상황에 따라 달라질 수 있습니다.</p></div>
</main><footer>{BRAND}<br>대표 상담 전화: {PHONE}<br><a href="/smart-bunny-homepage/">홈페이지 첫 화면</a></footer>
</body></html>"""

def service_body(location, level, service, region, trips=None):
    slug = service["slug"]
    if slug == "daeri":
        intro = f"{location}에서 모임이나 식사, 업무를 마친 뒤 차량을 직접 운전하기 어려운 상황이라면 출발 위치와 목적지를 정리해 대리운전을 상담할 수 있습니다."
        sections = f"""
<h2>{esc(location)} 대리운전이 필요한 상황</h2>
<p>약속이 끝나는 시간이 늦어지거나, 일행과 헤어진 뒤 주차해 둔 차량으로 귀가해야 할 때는 호출 전에 정확한 위치를 확인해 두는 것이 좋습니다. 건물 이름만으로 위치가 분명하지 않다면 도로명 주소나 가까운 출입구를 함께 알려주세요.</p>
<h2>이용 전 확인할 내용</h2>
<ul><li>차량이 주차된 정확한 위치와 만날 장소</li><li>목적지 주소 또는 알아보기 쉬운 건물명</li><li>차종과 차량 이용에 필요한 특이사항</li><li>원하는 출발 시간과 현장 대기 여부</li></ul>
<h2>이용 흐름</h2>
<p>상담 → 출발지·목적지 확인 → 요금 및 배차 가능 여부 확인 → 진행 결정 순서로 확인하면 됩니다. 지역과 시간대에 따라 배차 상황이 달라질 수 있으므로 급한 호출이나 특정 시간 이용은 미리 문의하는 편이 좋습니다.</p>"""
    elif slug == "24h-daeri":
        intro = f"{location}에서 늦은 밤이나 이른 아침 대리운전이 필요하다면 출발 위치와 목적지를 정확히 확인하고 배차 가능 여부를 상담해 주세요."
        sections = f"""
<h2>{esc(location)} 24시 대리운전 이용 안내</h2>
<p>심야·새벽 시간대에는 기사 배차 상황과 현장 위치에 따라 대기 시간이 달라질 수 있습니다. 이용 시각이 정해져 있다면 미리 문의하고, 즉시 호출은 현재 배차 가능 여부를 확인해 주세요.</p>
<h2>심야 호출 전 확인사항</h2>
<ul><li>정확한 출발 위치와 차량 주차 위치</li><li>목적지 주소와 도착 희망 시간</li><li>차종 및 현장 진입·주차 관련 참고사항</li><li>희망 출발 시간과 대기 가능 여부</li></ul>
<h2>배차 확인</h2>
<p>상담 후 현재 시간대의 배차 가능 여부와 요금을 확인한 다음 진행을 결정할 수 있습니다. 24시 상담 문구가 모든 시간대의 즉시 배차를 보장하는 것은 아닙니다.</p>"""
    elif slug == "corporate-daeri":
        intro = f"{location}에서 임직원 귀가, 업무 일정, 회식 후 이동 등 법인 대리운전이 필요할 때 이용 시간과 정산 조건을 먼저 확인해 주세요."
        sections = f"""
<h2>{esc(location)} 법인대리운전 상담</h2>
<p>법인 이용은 운행 요청 방식, 이용 부서, 비용 처리 기준 등 회사 내부 절차를 미리 정리하면 상담이 수월합니다. 실제 제공 가능한 정산 방식과 계약 조건은 상담 시 확인해야 합니다.</p>
<h2>법인 문의 시 확인할 내용</h2>
<ul><li>회사에서 정한 호출·승인 절차</li><li>출발지와 도착지 및 예상 이용 시간</li><li>이용 건별 결제·정산 방식 문의</li><li>반복 이용 여부와 필요한 운영 조건</li></ul>
<h2>이용 절차</h2>
<p>필요 조건 전달 → 이용 가능 범위 및 요금 확인 → 회사 내부 승인 → 배차 요청 순서로 진행하면 됩니다. 별도 계약이나 월 정산이 가능한지는 확정 전에 상담으로 확인해 주세요.</p>"""
    elif slug == "golf-daeri":
        intro = f"{location} 인근 골프장 라운딩 전후로 대리운전이 필요하다면 골프장명, 클럽하우스 또는 주차장 위치와 귀가 목적지를 함께 알려주세요."
        sections = f"""
<h2>{esc(location)} 골프대리운전 이용 안내</h2>
<p>라운딩과 식사 일정이 끝나는 시간은 변동될 수 있으므로 예상 종료 시간과 실제 호출 시간을 구분해 알려주시면 좋습니다. 골프장 내 출입구나 주차 구역이 여러 곳이면 만날 장소를 구체적으로 정해 주세요.</p>
<h2>골프장 호출 전 체크리스트</h2>
<ul><li>골프장명과 차량이 주차된 구역</li><li>클럽하우스·정문 등 기사와 만날 장소</li><li>귀가 목적지와 희망 출발 시간</li><li>라운딩 종료 후 대기 가능 여부</li></ul>
<h2>예약 및 배차</h2>
<p>주말이나 이용이 몰리는 시간대, 외곽 골프장은 배차 상황이 달라질 수 있습니다. 예약이 필요한 일정은 미리 상담하고 최종 배차 가능 여부를 확인해 주세요.</p>"""
    elif slug == "taksong":
        intro = f"{location}에서 차량을 다른 지역으로 이동해야 한다면 출발지와 도착지, 차종, 희망 날짜를 기준으로 자동차탁송 요금과 배차 가능 여부를 상담해 주세요."
        route_note = ""
        if "강릉시" in location:
            route_note = f"""
<h2>{esc(location)} 출발·도착 탁송 경로</h2>
<p>강릉에서 서울·수도권으로 보내는 탁송이나 서울·수도권에서 강릉으로 들어오는 탁송은 정확한 인수 장소와 도착 주소에 따라 조건이 달라집니다. 속초·동해 등 강원 동해안 지역 간 이동도 실제 출발지와 도착지를 기준으로 확인해 주세요. 아래 경로는 상담 시 출발·도착지를 설명하기 위한 예시이며, 고정 요금이나 즉시 배차를 의미하지 않습니다.</p>"""
        sections = f"""
<h2>{esc(location)} 탁송 예약 및 요금 확인</h2>
<p>차량탁송 비용은 이동 거리, 차량 종류, 인수·인계 장소, 희망 시간과 현장 조건에 따라 달라질 수 있습니다. 출발지와 도착지를 확인한 뒤 해당 조건의 견적을 안내받는 방식이 정확합니다. 확인되지 않은 금액을 고정 요금처럼 표시하지 않습니다.</p>
{route_note}
<h2>탁송 견적 문의 시 준비할 내용</h2>
<ul><li>차량을 인수할 정확한 장소와 최종 도착 주소</li><li>차종 및 차량 운행에 필요한 상태 정보</li><li>희망 인수 날짜와 시간</li><li>차량 인수·인계 방법과 현장 접근 안내</li></ul>
<h2>탁송 진행 순서</h2>
<p>출발지·도착지 확인 → 차종·일정 확인 → 요금과 배차 가능 여부 안내 → 조건 확인 후 진행 결정 순서입니다. 장거리 이동이나 일정이 정해진 탁송은 미리 상담하면 조건을 확인하기 좋습니다.</p>"""
    else:
        intro = f"{location}에서 출발해 먼 지역까지 차량을 이동해야 한다면 장거리탁송을 상담할 때 출발지, 도착지, 차량 종류와 희망 일정을 함께 확인하는 것이 중요합니다."
        sections = f"""
<h2>{esc(location)} 장거리탁송에서 중요한 점</h2>
<p>장거리 이동은 단순히 지역명만 전달하기보다 정확한 주소와 원하는 인수 시간을 알려주는 것이 좋습니다. 일정이 정해져 있다면 미리 상담해 가능한 운행 일정과 요금을 확인하세요.</p>
<h2>장거리탁송 상담 체크리스트</h2>
<ul><li>출발지와 도착지의 상세 주소</li><li>차종과 차량 상태</li><li>희망 인수 날짜·시간 및 도착 희망 일정</li><li>차량 인수·인계 담당자 연락 방법</li><li>요금, 운행 조건, 배차 가능 여부</li></ul>
<h2>예약 상담은 미리 진행하세요</h2>
<p>장거리 운행은 거리와 일정, 지역별 배차 여건에 따라 조율이 필요할 수 있습니다. 확정된 운행 사례나 요금은 상담으로 확인하고, 일정에 여유를 두고 문의해 주세요.</p>"""
    local_notes = region.get("local_notes", [])
    local_html = ""
    if local_notes:
        local_html = "<h2>지역 이용 참고사항</h2><ul>" + "".join(f"<li>{esc(note)}</li>" for note in local_notes) + "</ul>"
    trip_html = related_trip_html(region, trips or [], limit=2)
    return f"""<p class="muted">전국 지역별 서비스 안내 · {esc(level)}</p>
<h1>{esc(location)} {esc(service["keyword"])}</h1>
<p>{esc(intro)}</p>
{sections}
{local_html}
{trip_html}
<div class="card"><h2>실제 이용 후기 안내</h2><p>이 페이지는 지역 서비스 이용을 돕기 위한 안내입니다. 실제 운행 후기와 운행 경로, 요금은 확인된 사례가 있을 때에만 추가합니다. 확인되지 않은 고객 경험이나 운행 실적을 임의로 작성하지 않습니다.</p></div>
<p class="muted">지역 정보: {esc(location)} · 안내 업데이트: {date.today().isoformat()}</p>"""

def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    regions = data.get("regions", [])
    completed_trips = load_completed_trips()
    if not regions:
        raise SystemExit("data/regions.json에 지역을 입력해야 합니다.")
    urls = {SITE_URL + "/"}
    # Keep hand-authored specialist transport landing pages in the sitemap.
    special_root = ROOT / "special"
    if special_root.exists():
        if (special_root / "index.html").exists():
            urls.add(f"{SITE_URL}/special/")
        for special_page in special_root.glob("*/index.html"):
            urls.add(f"{SITE_URL}/special/{special_page.parent.name}/")
    count = 0
    location_by_name = {}
    children_by_parent = {}
    for item in regions:
        full_name = " ".join(part for part in [item.get("parent_name", ""), item["name"]] if part).strip()
        location_by_name[full_name] = item
        parent_name = item.get("parent_name", "")
        if parent_name:
            children_by_parent.setdefault(parent_name, []).append(item)
    for r in regions:
        name = r["name"]
        slug = r["slug"].strip("/")
        level = r.get("level", "지역")
        parent = r.get("parent_name", "")
        location = f"{parent} {name}".strip()
        region_url = f"{SITE_URL}/region/{slug}/"
        urls.add(region_url)
        child_items = sorted(children_by_parent.get(location, []), key=lambda x: (x.get("level", ""), x.get("name", "")))
        child_links = "".join(
            f'<li><a href="/smart-bunny-homepage/region/{esc(item["slug"].strip("/"))}/">{esc(item["name"])} ({esc(item.get("level", "지역"))})</a></li>'
            for item in child_items
        )
        child_section = f'<h2>하위 행정구역</h2><ul>{child_links}</ul>' if child_items else ""
        parent_item = location_by_name.get(parent)
        parent_section = (
            f'<p><a href="/smart-bunny-homepage/region/{esc(parent_item["slug"].strip("/"))}/">← {esc(parent)} 상위 지역으로</a></p>'
            if parent_item and parent_item.get("slug", "").strip("/") != slug else ""
        )
        local_services = r.get("services", [s["slug"] for s in SERVICES])
        links = []
        for s in SERVICES:
            if s["slug"] not in local_services:
                continue
            href = f"/smart-bunny-homepage/region/{slug}/{s['slug']}/"
            links.append(f'<div class="card"><h3><a href="{href}">{esc(location)} {esc(s["keyword"])}</a></h3><p>{esc(location)} 지역의 이용 상황, 상담 전 확인사항과 진행 순서를 안내합니다.</p></div>')
            service_url = f"{SITE_URL}/region/{slug}/{s['slug']}/"
            urls.add(service_url)
            body = service_body(location, level, s, r, completed_trips)
            if s["slug"] == "taksong":
                title = f"{location} 탁송 예약·요금 안내 | {BRAND}"
                description = f"{location} 자동차탁송·장거리탁송 상담 안내. 출발지, 도착지, 차종과 희망 시간을 기준으로 요금 및 배차 가능 여부를 확인하세요. 대표 전화 {PHONE}."
            else:
                title = f"{location} {s['keyword']} 이용 안내 | {BRAND}"
                description = f"{location} {s['keyword']} 이용 상황과 상담 전 확인사항 안내. 대표 전화 {PHONE}."
            out = ROOT / "region" / slug / s["slug"] / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(page(title, description, body, service_url), encoding="utf-8")
            count += 1
        body = f"""<p class="muted">전국 지역별 서비스 안내 · {esc(level)}</p>
<h1>{esc(location)} 대리운전 · 자동차탁송</h1>
<p>{esc(location)}에서 대리운전이나 차량 이동이 필요할 때 확인할 상담 정보를 정리했습니다. 실제 배차 가능 여부와 요금은 출발지, 목적지, 차종, 희망 시간에 따라 달라질 수 있습니다.</p>
<h2>{esc(location)} 서비스 안내</h2>
{parent_section}
{child_section}
{''.join(links)}
{related_trip_html(r, completed_trips, limit=4)}
<h2>상담 전에 준비하면 좋은 정보</h2>
<ul><li>출발지와 도착지의 정확한 위치</li><li>차량 종류 및 차량 상태</li><li>이용 날짜와 희망 시간</li><li>현장 연락 담당자와 인수·인계 방법(탁송 시)</li></ul>
<h2>지역별 후기 콘텐츠 운영 기준</h2>
<p>실제 이용 후기가 확인되면 해당 지역, 운행 경로, 차량 정보와 상담 과정 등 공개 가능한 사실을 바탕으로 추가합니다. 실제 사례가 없는 경우에는 이용 안내를 제공하며, 고객 후기나 운행 실적을 만들어 쓰지 않습니다.</p>
<p class="muted">지역 정보: {esc(location)} · 안내 업데이트: {date.today().isoformat()}</p>"""
        out = ROOT / "region" / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(f"{location} 대리운전·탁송 이용 안내 | {BRAND}", f"{location} 대리운전, 자동차탁송, 장거리탁송 상담 전 확인사항. 대표 전화 {PHONE}.", body, region_url), encoding="utf-8")
        count += 1
    # Build a navigable nationwide directory and one landing page per province.
    region_root = ROOT / "region"
    region_root.mkdir(parents=True, exist_ok=True)
    provinces = {}
    for r in regions:
        parts = r["slug"].strip("/").split("/")
        if parts:
            provinces.setdefault(parts[0], []).append(r)

    province_cards = []
    for province_slug, items in sorted(provinces.items()):
        province_name = next((x["name"] for x in items if x.get("level") == "시·도"), None)
        if not province_name:
            province_name = items[0].get("parent_name", "").split()[0] or items[0]["name"]
        province_url = f"{SITE_URL}/region/{province_slug}/"
        urls.add(province_url)
        province_cards.append(
            f'<div class="card"><h3><a href="./{esc(province_slug)}/">{esc(province_name)} 지역 안내</a></h3>'
            f'<p>해당 시·도 내 대리운전·자동차탁송·장거리탁송 지역을 찾아보세요.</p></div>'
        )
        district_links = []
        seen = set()
        for item in sorted(items, key=lambda x: (x.get("level", ""), x.get("name", ""), x.get("slug", ""))):
            if item.get("level") != "시·군·구":
                continue
            item_slug = item["slug"].strip("/")
            item_url = f"{SITE_URL}/region/{item_slug}/"
            if item_url in seen:
                continue
            seen.add(item_url)
            label = " ".join(part for part in [item.get("parent_name", ""), item["name"]] if part)
            district_links.append(f'<li><a href="/smart-bunny-homepage/region/{esc(item_slug)}/">{esc(label)}</a></li>')
        province_body = f"""<p class="muted">전국 지역별 서비스 안내</p>
<h1>{esc(province_name)} 대리운전·자동차탁송 지역 안내</h1>
<p>{esc(province_name)}의 법정동 데이터를 바탕으로 지역별 서비스 페이지를 구성했습니다. 원하는 시·군·구를 선택한 뒤 세부 지역과 서비스를 확인하세요.</p>
{related_trip_html({"name": province_name}, completed_trips, limit=4)}
<h2>시·군·구 찾아보기</h2>
<ul>{''.join(district_links) if district_links else '<li>세부 지역 정보는 데이터 갱신 후 표시됩니다.</li>'}</ul>
<p><a href="/smart-bunny-homepage/region/">전국 지역 안내로 돌아가기</a></p>"""
        out = region_root / province_slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(f"{province_name} 대리운전·탁송 지역 안내 | {BRAND}", f"{province_name} 대리운전, 자동차탁송, 장거리탁송 지역별 안내. 대표 전화 {PHONE}.", province_body, province_url), encoding="utf-8")

    directory_url = f"{SITE_URL}/region/"
    # Search index lets visitors find a locality directly instead of opening province cards one by one.
    search_records = [
        {
            "name": item.get("name", ""),
            "parent_name": item.get("parent_name", ""),
            "level": item.get("level", "지역"),
            "slug": item["slug"].strip("/"),
            "url": "/smart-bunny-homepage/region/" + item["slug"].strip("/") + "/"
        }
        for item in sorted(regions, key=lambda x: (x.get("parent_name", ""), x.get("name", "")))
    ]
    (region_root / "region-index.json").write_text(
        json.dumps(search_records, ensure_ascii=False, separators=(",", ":")) + "\n",
    )
    directory_script = """<script>
(async function () {
  const input = document.getElementById("region-search");
  const results = document.getElementById("region-results");
  const status = document.getElementById("region-search-status");
  let regions = [];
  try {
    const response = await fetch("./region-index.json");
    if (!response.ok) throw new Error("index unavailable");
    regions = await response.json();
    status.textContent = "전국 " + regions.length.toLocaleString("ko-KR") + "개 행정구역 검색 준비 완료";
  } catch (_) {
    status.textContent = "지역 검색 자료를 불러오지 못했습니다. 아래 시·도 목록을 이용해 주세요.";
    return;
  }
  function render() {
    const query = input.value.trim().toLocaleLowerCase("ko-KR");
    results.replaceChildren();
    if (!query) {
      status.textContent = "지역명(예: 강남구, 역삼동, 속초시)을 입력해 주세요.";
      return;
    }
    const matches = regions.filter(item =>
      (item.parent_name + " " + item.name + " " + item.slug).toLocaleLowerCase("ko-KR").includes(query)
    ).slice(0, 100);
    if (!matches.length) {
      status.textContent = "검색 결과가 없습니다. 시·군·구 또는 읍·면·동 이름으로 다시 검색해 주세요.";
      return;
    }
    const list = document.createElement("ul");
    matches.forEach(item => {
      const li = document.createElement("li");
      const link = document.createElement("a");
      link.href = item.url;
      link.textContent = [item.parent_name, item.name].filter(Boolean).join(" ") + " (" + item.level + ")";
      li.appendChild(link);
      list.appendChild(li);
    });
    results.appendChild(list);
    status.textContent = matches.length === 100 ? "검색 결과가 100개로 제한되어 있습니다. 더 구체적인 지역명을 입력해 주세요." : "검색 결과 " + matches.length.toLocaleString("ko-KR") + "개";
  }
  input.addEventListener("input", render);
  input.addEventListener("search", render);
})();
</script>"""
    directory_body = f"""<p class="muted">전국 지역별 서비스 안내</p>
<h1>전국 대리운전·자동차탁송 지역 찾기</h1>
<p>전국 행정구역을 직접 검색하거나 시·도를 선택해 시·군·구, 읍·면·동 등 세부 지역 페이지로 이동할 수 있습니다. 실제 운행 사례와 요금은 확인된 정보만 별도로 안내합니다.</p>
<p><a href="/smart-bunny-homepage/reviews/">실제 완료 운행 내역 {len(completed_trips):,}건 확인하기 →</a></p>
<label for="region-search">지역명 빠른 검색</label>
<input id="region-search" type="search" placeholder="예: 서울 강남구, 역삼동, 속초시" autocomplete="off" style="width:100%;max-width:650px;padding:13px;border:1px solid #b9c5d3;border-radius:8px;font:inherit">
<p id="region-search-status" class="muted" role="status">지역 검색 자료를 불러오는 중입니다.</p>
<div id="region-results"></div>
<h2>시·도별로 찾아보기</h2>
<div class="cards">{''.join(province_cards)}</div>
<p class="muted">지역 데이터 출처: 국토교통부 전국 법정동 데이터. 지역별 배차 가능 여부와 요금은 상담을 통해 확인해 주세요.</p>
{directory_script}"""
    directory_path = region_root / "index.html"
    directory_path.write_text(page("전국 대리운전·자동차탁송 지역 안내 | " + BRAND, "전국 시·도별 대리운전·자동차탁송·장거리탁송 지역 안내. 대표 전화 " + PHONE + ".", directory_body, directory_url), encoding="utf-8")
    urls.add(directory_url)

    def sitemap_safe_url(url):
        parts = urlsplit(url)
        encoded_path = quote(parts.path, safe="/-._~")
        return urlunsplit((parts.scheme, parts.netloc, encoded_path, parts.query, parts.fragment))
    entries = "\n".join(f"  <url><loc>{esc(sitemap_safe_url(url))}</loc></url>" for url in sorted(urls))
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + entries + "\n</urlset>\n", encoding="utf-8")
    print(f"Generated {count} pages from {len(regions)} region records.")
    print("Nationwide expansion requires verified administrative-area data and useful region-specific details.")

if __name__ == "__main__":
    main()
