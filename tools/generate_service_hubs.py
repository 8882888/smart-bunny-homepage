"""Build service-specific, crawlable national guides using existing site templates."""
import json
from pathlib import Path


def generate_hubs(page, site_url):
    root = '/smart-bunny-homepage'
    guides = {
        'nationwide-daeri': {
            'name': '전국대리운전',
            'intro': '회식 후 귀가부터 골프 라운딩, 병원 방문 후 이동, 다른 도시까지의 장거리 운행까지 고객 차량을 운전할 기사를 상담합니다. 출발 지역뿐 아니라 도착지와 이용 시간에 따라 배차 조건이 달라지므로 전체 이동 계획을 먼저 확인합니다.',
            'sections': [
                ('일반 귀가와 장거리 대리운전', '시내 귀가는 정확한 승차 장소와 목적지를, 서울에서 부산처럼 도시를 넘어가는 장거리 이동은 출발 시간·경유지·편도 여부를 함께 알려주세요. 기사 이동과 복귀 여건이 달라 단순 거리만으로 확정 요금을 정하기 어렵습니다. 장거리라고 해서 일일기사로만 접수하는 것은 아니며, 편도 운행인지 대기 일정이 있는지 구분해 상담합니다.'),
                ('골프장·외곽 식당·펜션에서 출발할 때', '골프장이나 캠핑장, 계곡 주변 식당, 읍·면 지역은 기사 접근과 복귀 교통편을 함께 고려해야 합니다. 도심과 같은 대기시간을 약속하기 어렵기 때문에 장소명과 주차장 위치, 희망 출발 시각을 미리 전달하는 편이 좋습니다. 단체 차량은 대수와 각각의 귀가 목적지를 구분해 주세요.'),
                ('심야·새벽 예약과 배차 확인', '늦은 시간 이동은 지역별 기사 수급에 따라 달라집니다. 상담 접수와 기사 배차 완료는 서로 다른 단계입니다. 기사 배정 여부와 예상 도착시간을 확인한 뒤 이동을 준비하세요. 카카오톡 상담은 08:00~20:00이며 시간 외에는 대표번호로 문의할 수 있습니다.'),
                ('대리운전 비용을 확인하는 방법', '출발지·도착지, 희망 시간, 차종, 경유·대기 여부를 알려주시면 조건을 확인할 수 있습니다. 홈페이지의 과거 운행 금액은 해당 기록의 요금이며 오늘의 견적이 아닙니다. 승인 요금이 없는 경로는 상담으로 안내하며 화면에 보이는 지도 정보만으로 배차나 결제가 확정되지 않습니다.'),
            ],
            'questions': [
                ('장거리도 편도로 이용할 수 있나요?', '편도 이동으로 상담할 수 있습니다. 출발·도착지와 시간, 경유 및 대기 여부를 알려주시면 배차 가능 여부를 확인합니다.'),
                ('여러 대를 같은 시간에 예약하려면 무엇이 필요한가요?', '운행 날짜, 차량 대수, 출발 장소, 각 차량의 목적지와 출발 시각을 전달해 주세요. 요청 대수와 실제 배차 가능 대수는 별도로 확인합니다.'),
                ('상담 양식을 작성하면 바로 접수되나요?', '양식은 상담 메시지를 만드는 기능입니다. 생성된 내용을 복사해 카카오톡에 보내거나 전화로 문의해야 상담이 이어집니다.'),
            ],
        },
        'nationwide-transport': {
            'name': '전국탁송 · 24시탁송',
            'intro': '고객이 동승하지 않고 차량을 출발지에서 도착지로 이동해야 할 때 이용하는 자동차탁송 안내입니다. 중고차 인수·인계, 서비스센터 입출고, 렌터카 이동과 장거리 차량 이동은 차량 상태와 현장 인수 조건을 함께 확인합니다.',
            'sections': [
                ('차량 인수부터 도착 인계까지', '출발지와 도착지의 정확한 위치, 차량 종류, 키 전달 방법과 희망 시간을 먼저 확인합니다. 출발 전 차량 상태와 연료·충전 상태, 인수 가능 시간을 확인하고 도착지에서 차량을 받을 수 있는지 협의해 주세요. 현장 연락처 등 개인정보는 공개 후기나 공개 입력란에 남기지 말고 실제 상담 과정에서 전달해 주세요.'),
                ('서비스센터·렌터카·중고차 이동', '서비스센터는 예약 시간과 입고 마감, 렌터카는 인수·반납 순서, 중고차 이동은 키와 차량 인계 장소가 중요합니다. 경유지가 있다면 출발지와 도착지만 입력하지 말고 전체 순서를 알려주세요. 여러 대를 이동할 때는 차종과 차량별 인수 가능 시간을 나누어 확인합니다.'),
                ('1톤 트럭과 특수 조건 차량', '승용차와 다른 차종은 필요한 면허와 보험 적용 조건, 차량 높이와 길이, 적재 여부를 별도로 확인해야 합니다. 수동변속기 차량은 접수할 때 미리 알려주세요. 차량이 정상 주행 가능한지도 중요하며, 고장 차량이나 견인이 필요한 상황은 일반 운전 탁송과 구분해 상담해야 합니다.'),
                ('심야 탁송·산행·자전거 종주 차량 이동', '늦은 밤과 새벽, 산행 출발지나 자전거 종주 지점은 기사 접근과 복귀가 어려울 수 있습니다. 산행 시작 전에 차량 인수 시간을 정하고 도착 주차장과 키 인계 방법을 협의해 주세요. 24시탁송 문의라도 모든 지역에 즉시 배차가 가능한 것은 아니므로 일정이 정해졌다면 예약 가능 여부를 먼저 확인하세요.'),
                ('탁송 요금과 과거 기록을 구분하세요', '이동 거리 외에도 차량 종류, 출발 시간, 도서·외곽 지역, 경유와 기사 수급이 영향을 줍니다. 공개 운행내역의 금액은 실제 과거 기록으로 현재 견적을 보장하지 않습니다. 운영자가 승인한 요금이 없거나 지도 조회가 불가능한 경로는 임의 금액 대신 상담 안내를 제공합니다.'),
            ],
            'questions': [
                ('대리운전과 탁송은 어떻게 다른가요?', '대리운전은 고객 이동을 위해 고객 차량을 운전하는 서비스이고, 탁송은 차량 인수·인계를 중심으로 차량을 이동하는 서비스입니다. 구체적인 이용 조건은 상담에서 확인합니다.'),
                ('차량 번호나 연락처를 후기 입력란에 적어도 되나요?', '공개 후기와 공개 입력란에는 이름·연락처·차량번호 등 개인정보를 입력하지 마세요. 필요한 인수·인계 정보는 실제 상담 과정에서 전달해 주세요.'),
                ('새벽 출발도 예약할 수 있나요?', '출발 지역, 도착지, 차종과 희망 시각으로 예약 가능 여부를 문의할 수 있습니다. 배차 완료 여부는 별도로 확인해야 합니다.'),
            ],
        },
    }
    urls = set()
    for slug, g in guides.items():
        url = f'{site_url}/services/{slug}/'
        other = 'nationwide-transport' if slug == 'nationwide-daeri' else 'nationwide-daeri'
        content = f'<nav aria-label="현재 위치"><a href="{root}/">홈</a> → {g["name"]}</nav><h1>{g["name"]} 이용 안내</h1><p><strong>전 직원 100% 보험가입 안전운행</strong></p><p>{g["intro"]}</p>'
        content += f'<p><a class="btn" href="{root}/#fare-search-form">경로·요금 조회</a><a class="btn" href="{root}/#quick-request">상담 메시지 작성</a></p>'
        for title, text in g['sections']:
            content += f'<section class="card"><h2>{title}</h2><p>{text}</p></section>'
        content += f'<section class="card"><h2>지역 안내와 실제 완료 운행 기록</h2><p>이용 지역의 안내와 공개된 완료 운행내역을 함께 확인할 수 있습니다. 기록이 없는 지역은 실제 후기라고 표시하지 않습니다.</p><p><a href="{root}/region/">전국 시·도·시·군·구·읍·면·동 지역 찾기</a> · <a href="{root}/reviews/">완료 운행일·출발지·도착지·기록 요금 보기</a></p></section>'
        content += '<section class="card"><h2>자주 묻는 질문</h2>' + ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in g['questions']) + '</section>'
        content += f'<p><a href="{root}/services/{other}/">대리운전·탁송 서비스 비교하기</a> · <a href="{root}/special/">산행·자전거 종주 전문 탁송</a></p><p>카카오톡 친구 추가 010-3471-7001 · 상담 08:00~20:00 · 시간 외 대표전화 1877-3015</p>'
        schema = {'@context':'https://schema.org','@graph':[{'@type':'Service','@id':url+'#service','name':g['name'],'url':url,'serviceType':g['name'],'areaServed':{'@type':'Country','name':'대한민국'},'provider':{'@type':'Organization','name':'스마트전국대리운전 스마트24탁송','telephone':'1877-3015','url':site_url+'/'}},{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'홈','item':site_url+'/'},{'@type':'ListItem','position':2,'name':g['name'],'item':url}]}]}
        markup = page(g['name']+' | 예약·비용·지역별 이용 안내 1877-3015', g['intro'], content, url)
        markup = markup.replace('</head>', '<script type="application/ld+json">'+json.dumps(schema, ensure_ascii=False).replace('<','\\u003c')+'</script></head>')
        target=Path('services')/slug/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(markup,encoding='utf-8');urls.add(url)
    return urls
