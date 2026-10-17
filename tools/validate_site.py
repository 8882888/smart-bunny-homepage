#!/usr/bin/env python3
"""Validate generated pages, sitemap targets, and local navigation links."""
import os
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(".")
SITE_URL = os.environ.get("SITE_URL", "https://8882888.github.io/smart-bunny-homepage").rstrip("/")
SITE_PARTS = urlsplit(SITE_URL)
SITE_PREFIX = SITE_PARTS.path.rstrip("/")
REQUIRED = [
    ROOT / "index.html",
    ROOT / "robots.txt",
    ROOT / "sitemap.xml",
    ROOT / "special" / "index.html",
]


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("name"):
            self.ids.add(attrs["name"])
        if tag in ("a", "area", "link", "script", "img", "source") and attrs.get("href" if tag in ("a", "area", "link") else "src"):
            key = "href" if tag in ("a", "area", "link") else "src"
            self.links.append((tag, attrs[key]))


def local_file_for_url(url):
    parsed = urlsplit(url)
    if parsed.scheme not in ("http", "https") or parsed.netloc != SITE_PARTS.netloc:
        return None
    path = unquote(parsed.path)
    if SITE_PREFIX:
        if path == SITE_PREFIX or path == SITE_PREFIX + "/":
            return ROOT / "index.html"
        if not path.startswith(SITE_PREFIX + "/"):
            return None
        path = path[len(SITE_PREFIX) + 1:]
    else:
        path = path.lstrip("/")
    candidate = ROOT / path
    if path.endswith("/") or (not candidate.suffix and not candidate.is_file()):
        candidate = candidate / "index.html"
    return candidate


def main():
    missing = [str(path) for path in REQUIRED if not path.is_file()]
    if missing:
        raise SystemExit("필수 파일 누락: " + ", ".join(missing))

    html_files = sorted(ROOT.rglob("*.html"))
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
            local_sitemap = local_file_for_url(sitemap_url)
            if not local_sitemap or not local_sitemap.is_file():
                raise SystemExit("하위 사이트맵 파일이 없습니다: " + sitemap_url)
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

    broken_sitemap = []
    for url in urls:
        local = local_file_for_url(url)
        if not local or not local.is_file():
            broken_sitemap.append((url, str(local) if local else "사이트 기본 경로와 다름"))
    if broken_sitemap:
        preview = "\\n".join(f"- {url} -> {target}" for url, target in broken_sitemap[:20])
        raise SystemExit(f"사이트맵 링크 오류 {len(broken_sitemap)}건:\\n{preview}")

    # Verify local pages, assets, and in-page anchors so broken navigation is caught before publishing.
    parsed_pages = {}
    for file_path in html_files:
        parser = LinkParser()
        try:
            parser.feed(file_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            raise SystemExit(f"HTML을 읽을 수 없습니다: {file_path}: {exc}")
        parsed_pages[file_path.resolve()] = parser

    broken_links = []
    for file_path in html_files:
        parser = parsed_pages[file_path.resolve()]
        relative = file_path.as_posix().removeprefix("./")
        if relative == "index.html":
            public_path = "/"
        elif relative.endswith("/index.html"):
            public_path = "/" + relative[:-len("index.html")]
        else:
            public_path = "/" + relative
        current_url = SITE_URL + public_path
        for tag, raw_url in parser.links:
            raw_url = (raw_url or "").strip()
            if not raw_url or raw_url.startswith(("#", "data:", "javascript:", "mailto:", "tel:")):
                if raw_url.startswith("#") and len(raw_url) > 1:
                    fragment = unquote(urlsplit(raw_url).fragment)
                    if fragment and fragment not in parser.ids:
                        broken_links.append((file_path, raw_url, "페이지 내 대상 ID 없음"))
                continue
            resolved = urljoin(current_url, raw_url)
            target = local_file_for_url(resolved)
            if target is None:
                continue
            if not target.is_file():
                broken_links.append((file_path, raw_url, str(target)))
                continue
            if target.suffix.lower() == ".html":
                target_parser = parsed_pages.get(target.resolve())
                if target_parser is None:
                    target_parser = LinkParser()
                    target_parser.feed(target.read_text(encoding="utf-8"))
                    parsed_pages[target.resolve()] = target_parser
                fragment = unquote(urlsplit(resolved).fragment)
                if fragment and fragment not in target_parser.ids:
                    broken_links.append((file_path, raw_url, f"{target}에 ID #{fragment} 없음"))

    if broken_links:
        preview = "\\n".join(f"- {source}: {link} -> {target}" for source, link, target in broken_links[:30])
        raise SystemExit(f"내부 링크/앵커 오류 {len(broken_links)}건:\\n{preview}")

    print(f"검증 완료: HTML {len(html_files)}개, 사이트맵 URL {len(urls)}개, 내부 링크·앵커 오류 0개")


if __name__ == "__main__":
    main()
