# 스마트번개대리운전 지역 페이지 자동 생성

- 브랜드: 스마트번개대리운전
- 대표 전화: 1877-3015
- GitHub Pages: https://8882888.github.io/smart-bunny-homepage/

## 작동 방식
GitHub Actions가 실행될 때 `tools/generate_pages.py`를 실행해 `data/regions.json`의 지역별 페이지와 `sitemap.xml`을 생성하고 배포합니다.

## 지역 데이터 형식
각 항목은 `name`, `slug`, `level`, `parent_name`, `services`를 가집니다.
- `slug`: 영문/숫자/하이픈을 사용한 URL 경로
- `level`: 도/시/군/구/읍/면/동/리 등
- `services`: `daeri`, `taksong`, `long-distance-taksong` 중 필요한 서비스

현재 데이터는 자동 생성 기능을 확인하기 위한 소규모 시험 데이터입니다. 전국 모든 행정구역을 완성하려면 공식 행정구역 원본 데이터를 확보해 `data/regions.json`으로 변환한 후 배포해야 합니다. 데이터가 완성되기 전에는 전국 모든 지역 페이지가 생성되었다고 간주하면 안 됩니다.

## 주의
- 대표 전화는 1877-3015로 유지합니다.
- 영구63전국대리운전탁송/1811-0963 브랜드는 이 프로젝트에 포함하지 않습니다.
- 자동 생성 페이지의 문구는 기본 템플릿입니다. 실제 지역별 운행 사실이나 확정 요금을 임의로 주장하지 않습니다.
