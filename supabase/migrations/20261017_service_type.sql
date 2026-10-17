-- 기존 Supabase 프로젝트에 서비스 구분 기능을 추가하는 마이그레이션입니다.
-- Supabase SQL Editor에서 한 번 실행하세요. 기존 기록은 대리운전(daeri)으로 기본 지정됩니다.
alter table public.trip_records
  add column if not exists service_type text not null default 'daeri';

alter table public.trip_records
  drop constraint if exists trip_records_service_type_check;

alter table public.trip_records
  add constraint trip_records_service_type_check
  check (service_type in ('daeri', 'transport'));

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

-- SECURITY INVOKER 뷰가 service_type을 조회할 수 있도록 공개 역할에 해당 열의 SELECT 권한을 부여합니다.
grant select (service_type) on table public.trip_records to anon;
revoke all on public.completed_trip_reviews from public;
grant select on public.completed_trip_reviews to anon, authenticated;
