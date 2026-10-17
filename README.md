# 스마트전국대리운전 스마트24탁송

전국 대리운전·자동차탁송 안내 사이트입니다.

- 홈페이지: https://8882888.github.io/smart-bunny-homepage/
- 관리자 운행관리: https://8882888.github.io/smart-bunny-homepage/admin/
- 완료 운행 후기: https://8882888.github.io/smart-bunny-homepage/reviews/
- 전문 탁송 안내: https://8882888.github.io/smart-bunny-homepage/special/
- 대표 상담 전화: 1877-3015
- 카카오톡 상담: https://open.kakao.com/o/sGV88r7h (상담시간 08:00~20:00)

## 자동 배포

`main` 브랜치에 변경사항이 올라오면 GitHub Actions가 공식 행정구역 데이터를 받아 검증하고, 지역별 안내 페이지·사이트맵·완료 운행 후기 페이지를 생성한 뒤 GitHub Pages에 배포합니다. 실행 결과는 GitHub 저장소의 Actions 탭에서 확인합니다.

## 주요 기능

- 전국 지역별 대리운전·자동차탁송 안내 페이지 자동 생성
- 경로별 예상요금 계산기(초기 시범 산식이며 확정요금이 아님)
- 전화·카카오톡 상담 및 상담 내용 복사
- 개인정보를 제외한 완료 운행 후기와 구간 검색
- Supabase 기반 관리자 운행 기록 등록·수정·삭제 및 경로별 참고요금 검토

## 관리자/실시간 후기 설정

관리자와 실시간 후기 기능은 Supabase 데이터베이스, RLS 정책, 공개용 Publishable/anon 키, 그리고 `app_metadata.role = "admin"`인 관리자 계정이 필요합니다. `supabase/schema.sql`을 처음 설치할 때 실행하세요. 기존 프로젝트에 서비스 구분을 추가하는 경우 `supabase/migrations/20261017_service_type.sql`도 SQL Editor에서 실행해야 합니다. 관리자 기능은 데이터베이스 권한과 실제 로그인까지 확인하기 전에는 운영 준비 완료로 간주하지 마세요.

**절대 공개 저장소에 넣지 말 것:** Supabase `service_role`/secret 키, 데이터베이스 비밀번호, 고객 개인정보.

## 개인정보 원칙

공개 후기에는 운행일, 출발 시간, 출발지, 도착지, 금액 및 서비스 구분만 표시합니다. 고객 이름, 전화번호, 주민등록번호, 차량번호 등 개인정보는 입력하거나 공개하지 않습니다.

## 요금 안내

`data/pricing_rules.json`은 운영자가 실제 운행 실적과 원가를 확인하기 전까지 시범 산식입니다. 경로별 참고요금은 운영자가 확인하고 승인한 뒤 `data/reference_fares.json`에 반영해야 합니다. 자동 계산 결과를 확정 견적 또는 공식 요금으로 안내하지 않습니다.
