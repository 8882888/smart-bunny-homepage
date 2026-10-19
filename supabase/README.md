# Supabase 관리자·운행 후기 설정

이 폴더는 스마트번개대리운전 홈페이지의 관리자 기능을 위한 데이터베이스 기반 준비 파일입니다.

## 공개 개인정보 원칙

공개 후기에는 아래 다섯 항목만 표시합니다.

1. 운행일
2. 출발 시간
3. 출발지
4. 도착지
5. 금액

고객 이름, 전화번호, 주민등록번호, 차량번호 등은 입력하지 않습니다. 운행이 완료된 자료만 `status = 'completed'`로 지정합니다. 취소·대기 건은 공개 뷰에서 제외됩니다.

## 설정 순서

1. Supabase 프로젝트를 생성합니다.
2. Dashboard의 SQL Editor에서 `schema.sql` 전체를 실행합니다.
3. Supabase Auth에서 관리자 사용자를 생성합니다.
4. 신뢰할 수 있는 관리자 전용 경로를 통해 해당 사용자의 `app_metadata.role`을 `admin`으로 설정합니다. 브라우저에서 사용자가 직접 바꿀 수 있는 `user_metadata`를 권한 확인에 사용하지 마세요.
5. 저장소 루트의 `supabase-public-config.example.js`를 `supabase-public-config.js`로 복사하고 Supabase Project URL과 공개 anon/publishable key를 입력합니다. 이 설정은 브라우저에 공개되는 파일이므로 공개 키만 넣습니다.
6. `supabase-public-config.js`를 GitHub 저장소에 커밋해 GitHub Pages의 관리자·공개 후기 화면에서 공통으로 사용하도록 합니다. 공개 anon/publishable key는 브라우저용 키이지만 RLS 정책을 반드시 검증해야 합니다.
7. `admin/` 페이지에서 관리자 로그인을 테스트합니다. 로그인 후 등록·수정·삭제 기능은 데이터베이스의 RLS 정책에 의해 제한됩니다.
8. 공개 후기 페이지는 `completed_trip_reviews` 뷰에서 완료 운행만 불러옵니다. 비로그인 접근·일반 계정·관리자 계정·취소 건을 각각 테스트합니다. 설정 파일이 없거나 연결 오류가 나면 기존 정적 후기 자료를 대신 표시합니다.

## 보안 주의

- GitHub Pages는 정적 호스팅이므로 서버 측 비밀값을 보관할 수 없습니다.
- Supabase의 공개 anon/publishable 키는 RLS 정책이 올바르게 설정된 경우에만 브라우저에 사용할 수 있습니다.
- `service_role` 키, 관리자 비밀번호, 토큰은 HTML/JavaScript, JSON, GitHub 저장소에 절대 커밋하지 마세요.
- `supabase-public-config.js`에는 Supabase Project URL과 공개 anon/publishable key만 넣어 GitHub Pages에서 읽을 수 있게 합니다. 이는 비밀키가 아니지만, 데이터베이스 권한은 RLS로 보호해야 합니다.
- 이 페이지는 관리자 화면의 프런트엔드입니다. Supabase 프로젝트 연결, 관리자 역할 부여, 데이터베이스 SQL 실행 및 보안 테스트 전에는 실제 운영에 사용할 수 없습니다.

## 비밀번호 없는 관리자 로그인 (2026-10-19)
관리자 화면은 `signInWithOtp` 이메일 로그인 링크를 사용합니다. `shouldCreateUser:false`로 자동 가입을 막고 기존 `app_metadata.role=admin`과 DB RLS를 유지합니다.
Supabase Authentication → URL Configuration의 Redirect URLs에 `https://8882888.github.io/smart-bunny-homepage/admin/`를 등록하세요. 사용자 지정 도메인을 연결하면 해당 도메인의 `/admin/`도 등록해야 합니다. Email 인증/로그인 메일 템플릿 및 SMTP 발송 설정도 필요합니다. 기존 관리자 계정이 없다면 신뢰할 수 있는 Supabase 관리 화면에서 먼저 생성하고 관리자 역할을 설정해야 합니다. 공개 코드에 서비스 키를 넣거나 이메일 일치만으로 권한을 주지 마세요.
코드 테스트는 실제 이메일 수신 또는 관리자 세션 성공을 보장하지 않습니다. 메일 링크를 실제로 눌러 권한 확인까지 검증해야 합니다.
