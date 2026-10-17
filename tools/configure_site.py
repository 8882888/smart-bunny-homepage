#!/usr/bin/env python3
"""Apply the configured public site URL to static HTML and crawler metadata."""
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(".")
SITE_URL = os.environ.get(
    "SITE_URL", "https://8882888.github.io/smart-bunny-homepage"
).strip().rstrip("/")
if not SITE_URL.startswith("https://"):
    raise SystemExit("SITE_URL must be an HTTPS URL.")
parsed = urlsplit(SITE_URL)
if not parsed.netloc:
    raise SystemExit("SITE_URL must include a hostname.")
BASE_PATH = parsed.path.rstrip("/")


def public_path(path: str) -> str:
    if path == "index.html":
        suffix = "/"
    elif path.endswith("/index.html"):
        suffix = "/" + path[: -len("/index.html")].strip("/") + "/"
    else:
        suffix = "/" + path.lstrip("/")
    return BASE_PATH + suffix


def main():
    html_files = sorted(ROOT.rglob("*.html"))
    for file_path in html_files:
        relative = file_path.as_posix().removeprefix("./")
        text = file_path.read_text(encoding="utf-8")
        # Internal links authored for the GitHub project path must also work at a custom-domain root.
        text = text.replace("/smart-bunny-homepage/", (BASE_PATH + "/") if BASE_PATH else "/")
        canonical = SITE_URL + public_path(relative)
        tag = f'<link rel="canonical" href="{canonical}">'
        if re.search(r'<link\b[^>]*\brel=["\']canonical["\'][^>]*>', text, flags=re.I):
            text = re.sub(
                r'<link\b[^>]*\brel=["\']canonical["\'][^>]*>',
                tag,
                text,
                count=1,
                flags=re.I,
            )
        elif re.search(r"</head\s*>", text, flags=re.I):
            text = re.sub(r"</head\s*>", tag + "\n</head>", text, count=1, flags=re.I)
        if relative == "index.html" and not re.search(r'<meta\s+name=["\']description["\']', text, flags=re.I):
            text = re.sub(
                r"(<title>.*?</title>)",
                r'\1\n<meta name="description" content="스마트전국대리운전 스마트24탁송. 전국 대리운전, 자동차탁송, 장거리탁송 상담. 대표전화 1877-3015.">',
                text,
                count=1,
                flags=re.I | re.S,
            )
        file_path.write_text(text, encoding="utf-8")

    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: " + SITE_URL + "/sitemap.xml\n",
        encoding="utf-8",
    )
    print(f"Configured public URL: {SITE_URL}")
    print(f"Updated canonical URLs and internal paths in {len(html_files)} HTML files.")
    print("Updated robots.txt sitemap URL.")


if __name__ == "__main__":
    main()
