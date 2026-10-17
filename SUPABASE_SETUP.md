# Supabase 연결 안내 — 스마트전국대리운전 스마트 24시탁송

현재 홈페이지는 GitHub Pages에서 정적 사이트로 배포됩니다. 지역 안내 페이지는 자동 생성되지만, 관리자 운행기록을 저장하려면 별도 Supabase 프로젝트 연결이 필요합니다.

## 1. Supabase 프로젝트 만들기
1. https://supabase.com 에 로그인하고 새 프로젝트를 만듭니다.
2. 프로젝트가 준비되면 Project URL과 공개용 anon/publishable key를 확인합니다.
3. 비밀번호와 키는 안전하게 보관합니다. 이 저장소의 공개 파일이나 채팅에 비밀번호, service_role/secret key를 올리지 마세요.

## 2. 데이터베이스 테이블 만들기
1. Supabase 대시보드의 SQL Editor를 엽니다.
2. 이 저장소의 `supabase/schema.sql` 파일 전체 내용을 붙여 넣고 실행합니다.
3. 실행 결과에 오류가 없는지 확인합니다. 이 스키마는 관리자 테이블 접근을 RLS 정책으로 제한하고, 공개 조회용 뷰에는 운행일·출발 시간·출발지·도착지·금액만 제공합니다.

## 3. 브라우저 설정 파일 준비하기
저장소 루트의 `supabase-public-config.example.js`를 복사해 `supabase-public-config.js`라는 이름으로 추가하고 아래 두 값만 실제 값으로 바꿉니다.

- `url`: Supabase Project URL
- `anonKey`: 공개용 anon/publishable key

이 파일은 `admin/index.html`에서 루트 경로의 `supabase-public-config.js`로 불러옵니다. 따라서 `admin/config.js`가 아닙니다.

**절대 넣으면 안 되는 값:** `service_role` 또는 secret key, 데이터베이스 비밀번호, 개인 API 토큰. 공개용 키만 사용하고 RLS 정책을 유지해야 합니다.

## 4. 관리자 계정과 권한
1. Supabase Authentication에서 관리자용 사용자를 생성합니다.
2. 로그인만 만든다고 관리자 권한이 자동 부여되지는 않습니다. 사용자에게 `app_metadata.role = "admin"`을 신뢰할 수 있는 서버 측 Supabase Admin API 경로로 부여해야 합니다.
3. Admin API의 service_role/secret key는 브라우저 파일, 공개 저장소, 공개 웹페이지에 넣지 마세요. 안전한 서버 측 권한 설정 절차가 준비되기 전에는 관리자 데이터 입력 기능을 운영용으로 간주하지 마세요.

## 5. 기존 데이터베이스 업데이트 (기존 프로젝트에만 필요)

이미 `trip_records` 테이블을 운영 중이면 `supabase/migrations/20261017_service_type.sql`의 내용을 SQL Editor에서 실행해 `service_type` 열, 공개 후기 뷰 및 권한을 업데이트하세요. 기존 기록은 이 마이그레이션에서 기본값 `daeri`로 분류되므로, 과거에 탁송이 포함되어 있었다면 관리자 화면에서 서비스 구분을 확인·수정하기 전까지 요금 후보 승인에 사용하지 마세요.

새 프로젝트라면 먼저 `supabase/schema.sql`을 실행하고, 기존 프로젝트라면 위 마이그레이션을 적용하세요. 둘 다 무조건 연속 실행할 필요는 없습니다.

## 6. 배포 및 확인
1. 설정 파일을 추가해 main 브랜치에 반영하면 GitHub Actions가 사이트를 다시 배포합니다.
2. `/admin/`에서 관리자 로그인을 시험합니다.
3. 테스트 운행기록을 등록하고, 완료 상태인 기록만 `/reviews/` 공개 목록에 나타나는지 확인합니다.
4. 테스트가 끝나면 테스트 기록을 삭제합니다.

## 공개 운행기록 개인정보 원칙
공개 후기에는 운행일, 출발 시간, 출발지, 도착지, 금액만 표시합니다. 고객 이름, 전화번호, 주민등록번호, 차량번호 등 개인정보는 입력하거나 공개하지 않습니다. 완료된 운행만 공개 대상입니다.
