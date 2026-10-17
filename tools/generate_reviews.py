#!/usr/bin/env python3
"""Generate public completed-trip records and route summaries using non-identifying fields."""
import html
import json
import os
from collections import defaultdict
from pathlib import Path

DATA = Path("data/completed_trips.json")
OUT = Path("reviews/index.html")
SITE_URL = os.environ.get("SITE_URL", "https://8882888.github.io/smart-bunny-homepage").rstrip("/")
BRAND = "스마트전국대리운전 스마트24탁송"
PHONE = "1877-3015"

def esc(value):
    return html.escape(str(value), quote=True)

def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    trips = data.get("trips", [])
    ordered = sorted(trips, key=lambda t: (t["운행일"], t["출발시간"]), reverse=True)

    if ordered:
        rows = "".join(
            "<tr>" +
            f"<td>{esc(t['운행일'])}</td>" +
            f"<td>{esc(t['출발시간'])}</td>" +
            f"<td>{esc(t['출발지'])}</td>" +
            f"<td>{esc(t['도착지'])}</td>" +
            f"<td class=\"amount\">{int(t['금액']):,}원" + (' <span class="service-label">탁송 · 금액 기준 분류</span>' if int(t["금액"]) >= 60000 else "") + "</td>" +
            "</tr>"
            for t in ordered
        )
        table = f"""<div class="table-wrap"><table id="trip-table"><thead><tr><th>운행일</th><th>출발 시간</th><th>출발지</th><th>도착지</th><th>금액</th></tr></thead><tbody>{rows}</tbody></table></div>"""
    else:
        table = '<div class="empty"><h2>등록된 운행 후기가 아직 없습니다.</h2><p>확인된 완료 운행 자료를 정리한 뒤 이곳에 공개합니다.</p></div>'

    route_map = defaultdict(list)
    for trip in trips:
        route_map[(str(trip["출발지"]).strip(), str(trip["도착지"]).strip())].append(trip)
    route_cards = []
    route_groups = sorted(
        route_map.items(),
        key=lambda pair: (-len(pair[1]), max((x["운행일"], x["출발시간"]) for x in pair[1]))
    )[:30]
    for (origin, destination), items in route_groups:
        fares = [int(item["금액"]) for item in items]
        fare_label = f"{min(fares):,}원" if min(fares) == max(fares) else f"{min(fares):,}~{max(fares):,}원"
        route_query = esc(origin + " " + destination)
        route_cards.append(
            f'<button class="route-card" type="button" data-route="{route_query}">'
            f'<strong>{esc(origin)} → {esc(destination)}</strong>'
            f'<span>실제 기록 {len(items)}건 · 과거 기록 요금 {fare_label}</span>' + (f'<span class="service-label">6만원 이상 탁송 기준 기록 포함</span>' if any(int(item["금액"]) >= 60000 for item in items) else "") + '</button>'
        )
    route_section = (
        '<section id="route-search"><h2>구간별 실제 운행 사례</h2>'
        '<p>완료 운행 기록에서 확인되는 출발지와 도착지별 사례입니다. 운행 구분이 없는 기록은 60,000원 이상을 탁송으로 분류합니다. 표시된 요금은 과거 기록이며 현재 확정요금이 아닙니다.</p>'
        + ('<div class="route-grid">' + ''.join(route_cards) + '</div>' if route_cards else
           '<p class="empty">구간별 사례를 표시할 수 있는 운행 기록이 아직 없습니다.</p>')
        + '</section>'
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>구간별 탁송·대리운전 실제 운행 후기 | {BRAND}</title>
<meta name="description" content="전국 대리운전과 자동차탁송의 확인된 완료 운행 기록을 출발지, 도착지, 운행일, 요금으로 검색하고 구간별 사례를 확인하세요.">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{SITE_URL}/reviews/">
<style>
*{{box-sizing:border-box}}body{{margin:0;font-family:Arial,'Malgun Gothic',sans-serif;line-height:1.75;color:#172235}}
header,footer{{background:#102544;color:white;padding:18px max(5%,calc((100% - 1000px)/2))}}
header{{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap}}
header a,footer a{{color:#ffd166}}.topnav{{display:flex;align-items:center;justify-content:center;gap:12px;flex-wrap:wrap}}
.topnav a{{color:white;text-decoration:none;font-weight:bold;padding:6px 0}}
.topnav a.kakao{{background:#FEE500;color:#191919;padding:8px 11px;border-radius:7px;display:inline-flex;align-items:center;gap:6px}}
.kakao-icon{{width:18px;height:16px;display:inline-block}}.kakao-hours{{font-size:.9rem;color:white;font-weight:bold;white-space:nowrap}}
main{{max-width:1000px;margin:auto;padding:30px 5% 55px}}h1{{font-size:clamp(28px,5vw,42px);line-height:1.35}}
.table-wrap{{overflow-x:auto;margin:24px 0}}table{{border-collapse:collapse;width:100%;min-width:600px}}th,td{{border:1px solid #d9e1ea;padding:12px;text-align:left}}th{{background:#f3f7fb}}.amount{{white-space:nowrap;font-weight:bold}}.service-label{{display:inline-block;margin:4px 0;padding:2px 6px;border-radius:5px;background:#e8f3ff;color:#174d7a;font-size:12px;font-weight:700;white-space:normal}}.empty{{padding:22px;border:1px solid #d9e1ea;border-radius:12px;background:#f8fafc}}
.btn{{display:inline-block;background:#ffd166;color:#102544;text-decoration:none;padding:10px 16px;border-radius:8px;font-weight:bold;margin:6px 8px 6px 0}}
.search-box{{width:100%;max-width:620px;padding:13px 14px;border:1px solid #aebdce;border-radius:9px;font-size:16px;margin:8px 0}}
.route-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin:18px 0}}
.route-card{{display:flex;flex-direction:column;align-items:flex-start;gap:7px;text-align:left;padding:15px;border:1px solid #d9e1ea;border-radius:10px;background:#f8fafc;color:#172235;cursor:pointer;font:inherit}}
.route-card:hover{{border-color:#1769aa;background:#eef6ff}}.route-card span{{font-size:.9rem;color:#526276}}tr.filtered-out{{display:none}}
@media(max-width:700px){{header{{align-items:flex-start}}.topnav{{justify-content:flex-start;gap:10px}}.topnav a{{font-size:.9rem}}.kakao-hours{{font-size:.82rem}}}}
</style></head><body>
<header><strong>{BRAND}</strong><nav class="topnav" aria-label="주요 메뉴">
<a href="/smart-bunny-homepage/#services">대리운전</a><a href="/smart-bunny-homepage/#transport">탁송</a><a href="/smart-bunny-homepage/#corporate">법인대리운전</a><a href="/smart-bunny-homepage/#golf">골프대리운전</a>
<a class="kakao" href="https://open.kakao.com/o/sGV88r7h" target="_blank" rel="noopener noreferrer" aria-label="카톡상담, 상담시간 08:00부터 20:00까지"><svg class="kakao-icon" viewBox="0 0 24 22" aria-hidden="true"><path fill="#191919" d="M12 1C5.9 1 1 4.8 1 9.5c0 3 2 5.7 5.1 7.2l-1 4.1c-.1.4.3.6.6.4l4.8-3.1c.5.1 1 .1 1.5.1 6.1 0 11-3.8 11-8.6S18.1 1 12 1Z"/></svg>카톡상담</a><span class="kakao-hours">상담시간 08:00~20:00</span></nav><a href="tel:18773015">대표 상담 {PHONE}</a></header>
<main><p>완료 운행 기록 · 개인정보 비공개</p><h1>구간별 실제 운행 후기</h1>
<p>확인된 완료 운행 자료 중 운행일, 출발 시간, 출발지, 도착지, 금액만 공개합니다. 고객 이름, 전화번호, 주민등록번호 등 개인정보는 공개하지 않습니다. 운행 구분 자료가 없는 과거 기록은 금액 60,000원 이상을 탁송으로 분류하는 기준을 적용합니다.</p>
{route_section}
<section id="fare-guide" class="empty"><h2>탁송 요금은 어떻게 결정되나요?</h2>
<p>실제 운행 사례의 요금은 각 운행 기록에 저장된 금액을 그대로 표시합니다. 다만 기존 기록에 세부 산정 사유가 별도로 저장되어 있지 않은 경우, 특정 요금이 왜 책정되었는지 단정하지 않습니다.</p>
<ul><li><strong>이동 구간:</strong> 정확한 출발지와 도착지, 실제 이동 거리</li><li><strong>차량 조건:</strong> 차종, 차량 상태, 운행에 필요한 조건</li><li><strong>일정과 시간:</strong> 희망 인수 시간, 야간·주말 등 배차 여건</li><li><strong>현장 조건:</strong> 인수·인계 장소, 접근성 및 대기 필요 여부</li></ul>
<p>위 항목은 일반적으로 견적에 영향을 줄 수 있는 요소이며, 개별 과거 운행의 실제 요금 산정 사유를 뜻하지는 않습니다. 현재 요금은 출발지·도착지와 차량·일정을 확인한 뒤 상담으로 안내받으세요.</p></section>
<h2 id="all-trips">전체 운행 기록 검색</h2>
<label for="trip-search">출발지·도착지·운행일 검색</label><br>
<input class="search-box" id="trip-search" type="search" placeholder="예: 강릉, 부산, 성남, 출발지 또는 도착지">
<p id="search-count" aria-live="polite">전체 완료 운행 기록</p>
<div id="live-review-status" role="status">완료 운행 후기를 확인하고 있습니다.</div>
<div id="review-table">{table}</div>
<p><a class="btn" href="/smart-bunny-homepage/">홈페이지 첫 화면</a><a class="btn" href="https://open.kakao.com/o/sGV88r7h" target="_blank" rel="noopener noreferrer">카카오톡 상담</a></p>
</main><footer>{BRAND}<br>대표 상담 전화: {PHONE}</footer>
<script src="../supabase-public-config.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<script>
const tripSearch = document.getElementById("trip-search");
const searchCount = document.getElementById("search-count");
function filterTripRows(query) {{
  const q = String(query || "").trim().toLocaleLowerCase("ko-KR");
  const rows = Array.from(document.querySelectorAll("#review-table tbody tr"));
  let shown = 0;
  rows.forEach(row => {{
    const match = !q || row.textContent.toLocaleLowerCase("ko-KR").includes(q);
    row.classList.toggle("filtered-out", !match);
    if (match) shown++;
  }});
  searchCount.textContent = q ? "검색 결과 " + shown.toLocaleString("ko-KR") + "건" : "전체 운행 기록 " + shown.toLocaleString("ko-KR") + "건";
}}
tripSearch.addEventListener("input", () => filterTripRows(tripSearch.value));
document.querySelectorAll(".route-card").forEach(button => button.addEventListener("click", () => {{
  tripSearch.value = button.dataset.route || "";
  filterTripRows(tripSearch.value);
  document.getElementById("all-trips").scrollIntoView({{behavior:"smooth",block:"start"}});
}}));
(async function () {{
  const cfg = window.SMART_BUNNY_SUPABASE;
  const status = document.getElementById("live-review-status");
  const container = document.getElementById("review-table");
  if (!cfg || !cfg.url || !cfg.anonKey || !window.supabase) {{
    status.textContent = "현재 공개된 완료 운행 기록을 표시하고 있습니다.";
    filterTripRows(tripSearch.value);
    return;
  }}
  const escJs = value => String(value ?? "").replace(/[&<>"']/g, c => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}}[c]));
  try {{
    const client = window.supabase.createClient(cfg.url, cfg.anonKey);
    const {{data, error}} = await client.from("completed_trip_reviews")
      .select('"운행일","출발 시간","출발지","도착지","금액"')
      .order("운행일", {{ascending:false}})
      .order("출발 시간", {{ascending:false}})
      .limit(1000);
    if (error) throw error;
    if (!data || data.length === 0) {{
      status.textContent = "실시간 데이터에 새 기록이 없어 공개용 완료 운행 내역을 표시합니다.";
      filterTripRows(tripSearch.value);
      return;
    }}
    const rows = data.map(t => {{ const amount = Number(t["금액"]); const badge = Number.isFinite(amount) && amount >= 60000 ? ' <span class="service-label">탁송 · 금액 기준 분류</span>' : ''; return '<tr><td>'+escJs(t["운행일"])+'</td><td>'+escJs(String(t["출발 시간"]).slice(0,5))+'</td><td>'+escJs(t["출발지"])+'</td><td>'+escJs(t["도착지"])+'</td><td class="amount">'+(Number.isFinite(amount) ? amount.toLocaleString("ko-KR") : '금액 확인 필요')+'원'+badge+'</td></tr>'; }}).join("");
    container.innerHTML = '<div class="table-wrap"><table id="trip-table"><thead><tr><th>운행일</th><th>출발 시간</th><th>출발지</th><th>도착지</th><th>금액</th></tr></thead><tbody>'+rows+'</tbody></table></div>';
    filterTripRows(tripSearch.value);
    status.textContent = "완료된 운행 기록 · 개인정보 비공개";
  }} catch (e) {{
    status.textContent = "실시간 후기 연결을 확인할 수 없어 현재 공개 페이지 자료를 표시합니다.";
    filterTripRows(tripSearch.value);
  }}
}})();
</script></body></html>""", encoding="utf-8")
    print(f"운행 후기 페이지 생성 완료: {len(trips):,}건, 구간 사례 {len(route_groups):,}개")

if __name__ == "__main__":
    main()
