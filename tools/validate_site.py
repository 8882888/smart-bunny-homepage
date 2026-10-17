#!/usr/bin/env python3
"""Validate generated static pages and sitemap targets before GitHub Pages deployment."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(".")
SITE_PREFIX = "/smart-bunny-homepage"
REQUIRED = [
    ROOT / "index.html",
    ROOT / "robots.txt",
    ROOT / "sitemap.xml",
    ROOT / "special" / "index.html",
]

def main():
    missing = [str(path) for path in REQUIRED if not path.is_file()]
    if missing:
        raise SystemExit("필수 파일 누락: " + ", ".join(missing))

    html_files = list(ROOT.rglob("*.html"))
    if len(html_files) > 160000:
        raise SystemExit(f"지역별 서비스 확장 안전 한도를 넘습니다: HTML {len(html_files)}개")

    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    root_tree = ET.parse(ROOT / "sitemap.xml")
    root_tag = root_tree.getroot().tag.rsplit("}", 1)[-1]
    if root_tag == "sitemapindex":
        child_sitemaps = [node.text for node in root_tree.findall(".//sm:sitemap/sm:loc", namespace) if node.text]
        if not child_sitemaps:
            raise SystemExit("sitemap.xml에 하위 사이트맵이 없습니다.")
        urls = []
        for sitemap_url in child_sitemaps:
            parsed_sitemap = urlsplit(sitemap_url)
            sitemap_path = unquote(parsed_sitemap.path)
            if not sitemap_path.startswith(SITE_PREFIX + "/"):
                raise SystemExit("하위 사이트맵 경로가 잘못되었습니다: " + sitemap_url)
            local_sitemap = ROOT / sitemap_path[len(SITE_PREFIX) + 1:]
            if not local_sitemap.is_file():
                raise SystemExit("하위 사이트맵 파일이 없습니다: " + str(local_sitemap))
            child_tree = ET.parse(local_sitemap)
            child_urls = [node.text for node in child_tree.findall(".//sm:url/sm:loc", namespace) if node.text]
            if len(child_urls) > 50000:
                raise SystemExit("하위 사이트맵이 50,000 URL 한도를 초과했습니다: " + str(local_sitemap))
            urls.extend(child_urls)
    else:
        urls = [node.text for node in root_tree.findall(".//sm:url/sm:loc", namespace) if node.text]
        if len(urls) > 50000:
            raise SystemExit("단일 사이트맵이 50,000 URL 한도를 초과했습니다. 사이트맵 분할이 필요합니다.")
    if not urls:
        raise SystemExit("sitemap.xml에 URL이 없습니다.")

    broken = []
    for url in urls:
        parsed = urlsplit(url)
        path = unquote(parsed.path)
        if path == SITE_PREFIX or path == SITE_PREFIX + "/":
            local = ROOT / "index.html"
        elif path.startswith(SITE_PREFIX + "/"):
            relative = path[len(SITE_PREFIX) + 1:]
            local = ROOT / relative
            if path.endswith("/"):
                local = local / "index.html"
        else:
            broken.append((url, "사이트 기본 경로와 다름"))
            continue
        if not local.is_file():
            broken.append((url, str(local)))

    if broken:
        preview = "\n".join(f"- {url} -> {target}" for url, target in broken[:20])
        raise SystemExit(f"사이트맵 링크 오류 {len(broken)}건:\n{preview}")

    print(f"검증 완료: HTML {len(html_files)}개, 사이트맵 URL {len(urls)}개, 누락 링크 0개")

if __name__ == "__main__":
    main()
