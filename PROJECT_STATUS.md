# PROJECT_STATUS — 스마트전국대리운전·스마트24탁송

최종 점검: 2026-10-19 (GitHub main 브랜치 파일 기준)
저장소: 8882888/smart-bunny-homepage
원칙: 기존 기능 보존, 1877-3015 유지, 영구63 브랜드 분리, 확인되지 않은 후기 생성 금지, 개인정보 비공개.

## 확인된 구현 파일·구조
- index.html: 홈페이지 소스 존재 (기능별 브라우저 테스트는 미완료)
- admin/: 관리자 페이지 디렉터리 존재
- tools/: 자동 생성 도구 디렉터리 존재
- data/: 지역·요금 관련 데이터 디렉터리 존재
- supabase/: DB 스키마·마이그레이션 디렉터리 존재
- README.md: 자동 배포, 후기 검색, 요금계산기, Supabase 관리 기능 안내
- REGIONAL_PAGES.md: 지역 자동 생성 문서. 소규모 시험 데이터라고 기재되어 있어 전국 완성 여부 확인 필요
- supabase-public-config.js: 공개용 Supabase URL 및 publishable 키 설정 존재
- robots.txt, sitemap.xml: 저장소에 파일 존재

## 미완성 또는 검증 필요 (완료로 표시하지 말 것)
1. 전국 시·군·구·읍·면·동·리 실제 생성 범위: 지역 데이터와 배포 결과 수량 대조
2. 각 지역 대리운전·탁송 설명: 중복 템플릿 개선, 고유 정보 및 관련 완료 운행후기 연결
3. 완료 운행후기: 실제 완료 상태만 공개, 날짜·시간·출발·도착·요금 확인, 개인정보 필터 테스트
4. 전국 요금계산기: 시범 산식 명시, 구간별 승인 참고요금과 혼동 방지
5. 관리자: Supabase RLS, admin 역할, 로그인, 등록·수정·삭제 실동작 검증
6. 모바일: 상단 메뉴, 상담 버튼, 상단 이동, 계산기, 지역 검색 반응형 검증
7. SEO: 전국대리운전·전국탁송·24시탁송, canonical, sitemap, robots, 지역 내부링크 및 중복 페이지 점검
8. GitHub Actions: 최신 빌드·배포 성공 여부 및 생성물 링크 점검
9. 실제 검색 노출: 네이버 서치어드바이저·구글 서치콘솔 별도 검증 필요

## 발견한 문서 불일치
- README.md는 전국 지역 자동 생성 기능을 소개하지만 REGIONAL_PAGES.md에는 시험 데이터라고 기록되어 있음. 실제 생성 스크립트·입력 데이터·배포 산출물을 기준으로 판정할 것.
- REGIONAL_PAGES.md의 예전 브랜드 표기 '스마트번개대리운전'을 현재 사이트 명칭과 대조하여 통일 검토할 것.
- PROJECT_STATUS.md가 없어 이번 점검에서 신규 생성함.

## 다음 작업 우선순위
1. tools/generate_pages.py 및 data/regions.json, Actions workflow 검토·테스트
2. 지역별 콘텐츠·실제 완료 후기 매칭과 공개 개인정보 검증
3. 관리자 DB/RLS 및 요금계산기 통합 테스트
4. 모바일·SEO·배포 검증 후 이 문서에 테스트 결과와 수정 커밋 기록

## 변경 이력
- 2026-10-18: 저장소 루트와 README.md, REGIONAL_PAGES.md, Supabase 공개 설정 확인. 미존재 PROJECT_STATUS.md 신규 생성. 기존 사이트 소스는 변경하지 않음.

## 블로그 콘텐츠 연계 규칙
- 전국자동차탁송서비스 기존 기준 유지: 요청 시 약 5,000자, 제목 아래 '전 직원 100% 보험가입 안전운행', 모바일 가독성, 사실 기반 후기, 관련 해시태그 30개 한 줄.
- 대표 1877-3015 / 직통 010-4072-1577 / 카카오 친구추가 010-3471-7001 / 상담 08:00~20:00 / 오픈채팅 https://open.kakao.com/o/sGV88r7h
- 후기 데이터베이스와 블로그 원고는 구분하며 확인되지 않은 후기를 실제 운행으로 표시하지 않음.


## 2026-10-19 deployment audit fixes
- Fixed escaped whitespace in homepage/admin viewport audit; both existing tags are now recognized.
- Fixed consultation message newlines and route duration hour/minute rounding.
- Replaced the 1,000-row live review cap with paginated reads; failures preserve static fallback.
- Local generated-site link validation and structural audit passed (2 seed regions, not a nationwide import).
- Approved reference fares remain empty and pricing rules remain draft; operator review is still required.
- Deployment and Naver verification must be checked after GitHub Actions finishes.
- Also fixed a literal backslash-n outside a string in admin loadRecords that prevented the entire admin script from parsing.

## 2026-10-19 national service guides
- Added distinct nationwide driver and vehicle transport guides generated during the existing regional build.
- Added service/breadcrumb structured data, service FAQ content, consultation steps, and links to actual records and regional directory.
- Updated home H1 and primary links; existing calculator/admin/region functions retained.
- New service URLs included in generated sitemap. No unverified trip or price added.
- Local generation, link/anchor validation and structural audit passed on seed-region fixture.

## 2026-10-19 calculator, public records and deployment validation
- Live regional search index verified: 20,561 records. Both new national service guides returned HTTP 200.
- Fare requests now wait for approved data, time out on stalled network calls, preserve submitted options, and discard stale responses.
- Region suggestions load on focus and render at most 100 matching fully qualified region names instead of thousands of DOM options at initial load.
- Added global border-box sizing and responsive form/dropdown constraints for narrow screens.
- Removed 21 records containing internal instructions or possible personal-name fragments from the public dataset pending review; no synthetic replacement records added. Added value-level privacy rejection to build validation and route filters.
- Added CI parsing of inline JavaScript/JSON-LD and a mocked fare-search integration check.
- Local generation, links, audit, JS syntax, and race/snapshot/lazy-suggestion regression checks passed. Local data uses two seed regions; nationwide count above was checked on deployment.
- Visual mobile emulation remains unverified: browser binary download failed in this runtime. Admin authenticated CRUD and approval of price rules still require operational verification.

## 2026-10-19 admin import and mobile first screen
- Moved the main service heading and consultation buttons before animated review content. Mobile buttons fill the available width.
- Added shared browser/Node input validation for admin manual entry and CSV imports: real calendar dates, time format, allowed service/status, route length, private contact patterns and PostgreSQL integer range.
- CSV parser handles BOM, quoted commas/escaped quotes and CRLF. Missing/extra/unknown columns, malformed quotes or invalid later rows stop the entire import before any write.
- Prevented repeated clicks while saving/importing; network errors restore controls and report failure.
- Added CI regression tests for CSV boundaries and invalid dates; prior fare-search tests and generated-site validation passed.
- Authenticated database writes were not performed; browser mobile viewport visual testing remains outstanding.

## 2026-10-19 lightweight dynamic homepage reviews
- Homepage review ticker reads only the five-field public Supabase view (latest 40 rows) on load/refresh; it no longer downloads/parses the entire reviews HTML page.
- Build produces data/latest_public_trips.json from the same filtered records as the static reviews page. Current payload 6,357 bytes versus 432,677 bytes for the full reviews HTML.
- Empty, unavailable or timed-out public DB reads fall back to the small published feed; failed refresh keeps the existing display. Public fields are validated and allowlisted in the browser.
- Added explicit pause/resume and refresh buttons, loading state and inert duplicate animation cards for keyboard accessibility.
- Public DB read returned HTTP 200 with zero rows; no authenticated write test was performed. New records appear on reload or explicit refresh after completed status publication.
- Added CI regression checks for live/fallback behavior, timeout, privacy filtering and the 40-record cap.
- Also fixed route-card multi-word searches by searching joined table-cell text token by token; regression checks verify origin + destination matching.

## 2026-10-19 two-step admin CSV review
- CSV selection now validates and previews up to 50 rows without writing records. A distinct confirmation action registers the full validated batch.
- Changing files, cancellation and invalid data clear stale preview state. Registration locks related controls; duplicate clicks cannot trigger a second active write.
- Failed/uncertain writes clear pending retry state and require checking the record list before re-upload to avoid blind duplicates.
- Added a mocked integration check of the actual admin event handlers. Preview/cancel/validation/declined confirmation produced zero writes; successful and failed mocked registration restored controls.
- All local generation, structure, JS and regression checks passed. No real authenticated database writes were performed.
- Deployment follow-up: government CSV downloads stalled. Added a 30-second network timeout and an explicit fallback to the last successfully published official CSV, validated for size, encoding, headers, code format and coverage. Both sources failing stops deployment rather than publishing pilot-only coverage. CI records the chosen source and hash; regression tests cover timeout, invalid HTML and failure of both sources.

## 2026-10-19 관리자 이메일 링크 로그인
- admin/index.html: 비밀번호 입력/변경/재설정 UI를 이메일 일회용 링크 로그인으로 교체. 자동 가입 금지, 관리자 역할/RLS 유지, 중복 요청 방지 및 오류 표시.
- tests/admin_email_login.cjs: 요청 인자·중복 요청·발송 실패·역할 확인 회귀 검사.
- Supabase redirect URL/메일 발송 설정 및 실제 수신·로그인 성공은 별도 확인 필요. 실제 운행 DB 쓰기 미검증.
