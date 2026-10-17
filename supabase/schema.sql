-- 스마트번개대리운전 관리자용 운행 후기 데이터베이스
-- Supabase SQL Editor에서 실행하세요. 비밀키/비밀번호를 이 파일에 넣지 마세요.

create extension if not exists pgcrypto;

create table if not exists public.trip_records (
  id uuid primary key default gen_random_uuid(),
  trip_date date not null,
  departure_time time not null,
  origin text not null check (length(trim(origin)) between 1 and 200),
  destination text not null check (length(trim(destination)) between 1 and 200),
  fare_krw integer not null check (fare_krw > 0),
  service_type text not null default 'daeri' check (service_type in ('daeri', 'transport')),
  status text not null default 'completed'
    check (status in ('pending', 'completed', 'cancelled')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists trip_records_public_completed_idx
  on public.trip_records (trip_date desc, departure_time desc)
  where status = 'completed';

alter table public.trip_records enable row level security;

-- 익명 방문자는 완료된 운행의 공개용 열만 조회할 수 있습니다.
-- SECURITY INVOKER 뷰가 기본 테이블 권한/RLS를 그대로 따르도록 설정합니다.
revoke all on table public.trip_records from anon;
grant select (trip_date, departure_time, origin, destination, fare_krw, status, service_type)
  on table public.trip_records to anon;
grant select, insert, update, delete on table public.trip_records to authenticated;

drop policy if exists "public can read completed trips" on public.trip_records;
create policy "public can read completed trips"
  on public.trip_records for select to anon
  using (status = 'completed');

-- 관리자 역할은 Supabase Auth의 app_metadata.role = 'admin'으로 부여합니다.
drop policy if exists "admin can read trip records" on public.trip_records;
create policy "admin can read trip records"
  on public.trip_records for select to authenticated
  using ((auth.jwt() -> 'app_metadata' ->> 'role') = 'admin');

drop policy if exists "admin can insert trip records" on public.trip_records;
create policy "admin can insert trip records"
  on public.trip_records for insert to authenticated
  with check ((auth.jwt() -> 'app_metadata' ->> 'role') = 'admin');

drop policy if exists "admin can update trip records" on public.trip_records;
create policy "admin can update trip records"
  on public.trip_records for update to authenticated
  using ((auth.jwt() -> 'app_metadata' ->> 'role') = 'admin')
  with check ((auth.jwt() -> 'app_metadata' ->> 'role') = 'admin');

drop policy if exists "admin can delete trip records" on public.trip_records;
create policy "admin can delete trip records"
  on public.trip_records for delete to authenticated
  using ((auth.jwt() -> 'app_metadata' ->> 'role') = 'admin');

-- 공개 페이지에 제공되는 열은 아래 5개뿐입니다.
-- 기본 테이블의 id, status, created_at, updated_at 등은 공개 뷰에 포함하지 않습니다.
drop view if exists public.completed_trip_reviews;
create view public.completed_trip_reviews
with (security_barrier = true, security_invoker = true)
as
select
  trip_date as "운행일",
  to_char(departure_time, 'HH24:MI') as "출발 시간",
  origin as "출발지",
  destination as "도착지",
  fare_krw as "금액",
  service_type as "서비스구분"
from public.trip_records
where status = 'completed';

revoke all on public.completed_trip_reviews from public;
grant select on public.completed_trip_reviews to anon, authenticated;

-- 중요:
-- 1) 공개 화면은 trip_records가 아니라 completed_trip_reviews 뷰만 조회하세요.
-- 2) 관리자 계정은 Supabase Auth에서 만든 뒤, 신뢰할 수 있는 관리자 경로로
--    해당 사용자의 app_metadata에 {"role":"admin"}을 설정하세요.
-- 3) service_role 키는 브라우저 코드나 GitHub 저장소에 절대 넣지 마세요.
