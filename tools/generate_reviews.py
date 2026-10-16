#!/usr/bin/env python3
"""Generate a public completed-trip list using only approved, non-identifying fields."""
import html
import json
from pathlib import Path

DATA = Path("data/completed_trips.json")
OUT = Path("reviews/index.html")
SITE_URL = "https://8882888.github.io/smart-bunny-homepage"
BRAND = "스마트전국대리운전 스마트24탁송"
PHONE = "1877-3015"

def esc(value):
    return html.escape(str(value), quote=True)

def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    trips = data.get("trips", [])
    if trips:
        rows = "".join(
            "<tr>" +
            f"<td>{esc(t['운행일'])}</td>" +
            f"<td>{esc(t['출발시간'])}</td>" +
            f"<td>{esc(t['출발지'])}</td>" +
            f"<td>{esc(t['도착지'])}</td>" +
            f"<td class=\"amount\">{int(t['금액']):,}원</td>" +
            "</tr>"
            for t in sorted(trips, key=lambda t: (t["운행일"], t["출발시간"]), reverse=True)
        )
        table = f"""<div class="table-wrap"><table><thead><tr><th>운행일</th><th>출발 시간</th><th>출발지</th><th>도착지</th><th>금액</th></tr></thead><tbody>{rows}</tbody></table></div>"""
    else:
        table = '<div class="empty"><h2>등록된 운행 후기가 아직 없습니다.</h2><p>확인된 완료 운행 자료를 정리한 뒤 이곳에 공개합니다.</p></div>'

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>실제 운행 후기 | {BRAND}</title>
<meta name="description" content="확인된 완료 운행의 운행일, 출발 시간, 출발지, 도착지, 금액만 공개하는 운행 후기 목록입니다.">
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
.table-wrap{{overflow-x:auto;margin:24px 0}}table{{border-collapse:collapse;width:100%;min-width:600px}}th,td{{border:1px solid #d9e1ea;padding:12px;text-align:left}}th{{background:#f3f7fb}}.amount{{white-space:nowrap;font-weight:bold}}.empty{{padding:22px;border:1px solid #d9e1ea;border-radius:12px;background:#f8fafc}}
.btn{{display:inline-block;background:#ffd166;color:#102544;text-decoration:none;padding:10px 16px;border-radius:8px;font-weight:bold;margin:6px 8px 6px 0}}
@media(max-width:700px){{header{{align-items:flex-start}}.topnav{{justify-content:flex-start;gap:10px}}.topnav a{{font-size:.9rem}}.kakao-hours{{font-size:.82rem}}}}
</style></head><body>
<header><strong>{BRAND}</strong><nav class="topnav" aria-label="주요 메뉴">
<a href="/smart-bunny-homepage/#services">대리운전</a><a href="/smart-bunny-homepage/#transport">탁송</a><a href="/smart-bunny-homepage/#corporate">법인대리운전</a><a href="/smart-bunny-homepage/#golf">골프대리운전</a>
<a class="kakao" href="https://open.kakao.com/o/sGV88r7h" target="_blank" rel="noopener noreferrer" aria-label="카톡상담, 상담시간 08:00부터 20:00까지"><svg class="kakao-icon" viewBox="0 0 24 22" aria-hidden="true"><path fill="#191919" d="M12 1C5.9 1 1 4.8 1 9.5c0 3 2 5.7 5.1 7.2l-1 4.1c-.1.4.3.6.6.4l4.8-3.1c.5.1 1 .1 1.5.1 6.1 0 11-3.8 11-8.6S18.1 1 12 1Z"/></svg>카톡상담</a><span class="kakao-hours">상담시간 08:00~20:00</span></nav><a href="tel:18773015">대표 상담 {PHONE}</a></header>
<main><p>완료 운행 기록 · 개인정보 비공개</p><h1>실제 운행 후기</h1>
<p>확인된 완료 운행 자료 중 운행일, 출발 시간, 출발지, 도착지, 금액만 공개합니다. 고객 이름, 전화번호, 주민등록번호 등 개인정보는 공개하지 않습니다.</p>
<div id="live-review-status" class="small" role="status">완료 운행 후기를 확인하고 있습니다.</div>
<div id="review-table">{table}</div>
<p><a class="btn" href="/smart-bunny-homepage/">홈페이지 첫 화면</a><a class="btn" href="https://open.kakao.com/o/sGV88r7h" target="_blank" rel="noopener noreferrer">카카오톡 상담</a></p>
</main><footer>{BRAND}<br>대표 상담 전화: {PHONE}</footer>
<script src="../supabase-public-config.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<script>
(async function () {{
  const cfg = window.SMART_BUNNY_SUPABASE;
  const status = document.getElementById("live-review-status");
  const container = document.getElementById("review-table");
  if (!cfg || !cfg.url || !cfg.anonKey || !window.supabase) {{
    status.textContent = "현재 공개된 완료 운행 기록을 표시하고 있습니다.";
    return;
  }}
  const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}}[c]));
  try {{
    const client = window.supabase.createClient(cfg.url, cfg.anonKey);
    const {{data, error}} = await client.from("completed_trip_reviews")
      .select('"운행일","출발 시간","출발지","도착지","금액"')
      .order("운행일", {{ascending:false}})
      .order("출발 시간", {{ascending:false}})
      .limit(1000);
    if (error) throw error;
    if (!data || data.length === 0) {{
      container.innerHTML = '<div class="empty"><h2>등록된 운행 후기가 아직 없습니다.</h2><p>확인된 완료 운행 자료를 정리한 뒤 이곳에 공개합니다.</p></div>';
    }} else {{
      const rows = data.map(t => '<tr><td>'+esc(t["운행일"])+'</td><td>'+esc(String(t["출발 시간"]).slice(0,5))+'</td><td>'+esc(t["출발지"])+'</td><td>'+esc(t["도착지"])+'</td><td class="amount">'+Number(t["금액"]).toLocaleString("ko-KR")+'원</td></tr>').join("");
      container.innerHTML = '<div class="table-wrap"><table><thead><tr><th>운행일</th><th>출발 시간</th><th>출발지</th><th>도착지</th><th>금액</th></tr></thead><tbody>'+rows+'</tbody></table></div>';
    }}
    status.textContent = "완료된 운행 기록 · 개인정보 비공개";
  }} catch (e) {{
    status.textContent = "실시간 후기 연결을 확인할 수 없어 현재 공개 페이지 자료를 표시합니다.";
  }}
}})();
</script></body></html>""", encoding="utf-8")
    print(f"운행 후기 페이지 생성 완료: {len(trips):,}건")

if __name__ == "__main__":
    main()
