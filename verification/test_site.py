from __future__ import annotations

import re
import struct
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs"
SITE_URL = "https://stunspot.github.io/yammerknit/"
REQUIRED_PAGES = {
    "index.html",
    "get-started.html",
    "use.html",
    "data.html",
    "troubleshooting.html",
    "validation.html",
    "404.html",
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_lang: str | None = None
        self.titles = 0
        self.h1s = 0
        self.main_ids: set[str] = set()
        self.links: list[str] = []
        self.images: list[dict[str, str]] = []
        self.metas: dict[tuple[str, str], str] = {}
        self.canonical: str | None = None
        self.skip_target: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        if tag == "html":
            self.html_lang = values.get("lang")
        elif tag == "title":
            self.titles += 1
        elif tag == "h1":
            self.h1s += 1
        elif tag == "main" and values.get("id"):
            self.main_ids.add(values["id"])
        elif tag == "a" and values.get("href"):
            self.links.append(values["href"])
            if "skip-link" in values.get("class", "").split():
                self.skip_target = values["href"]
        elif tag == "img":
            self.images.append(values)
        elif tag == "meta":
            for key in ("name", "property"):
                if values.get(key):
                    self.metas[(key, values[key])] = values.get("content", "")
        elif tag == "link" and values.get("rel") == "canonical":
            self.canonical = values.get("href")


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"{path} is not a PNG")
    return struct.unpack(">II", data[16:24])


class DocumentationSiteTests(unittest.TestCase):
    def test_required_pages_and_assets_exist(self) -> None:
        observed = {path.name for path in DOCS.glob("*.html")}
        self.assertEqual(observed, REQUIRED_PAGES)
        for relative in (
            "assets/styles.css",
            "assets/stunspot-icon.png",
            "assets/semantic-mesh.webp",
            "assets/yammerknit-sharecard.png",
            ".nojekyll",
        ):
            self.assertTrue((DOCS / relative).exists(), relative)

    def test_pages_have_accessible_structure_and_resolving_local_links(self) -> None:
        failures: list[str] = []
        for page in sorted(DOCS.glob("*.html")):
            parser = PageParser()
            parser.feed(page.read_text("utf-8"))
            if parser.html_lang != "en":
                failures.append(f"{page.name}: missing lang=en")
            if parser.titles != 1:
                failures.append(f"{page.name}: expected one title")
            if parser.h1s != 1:
                failures.append(f"{page.name}: expected one h1")
            if parser.skip_target != "#main" or "main" not in parser.main_ids:
                failures.append(f"{page.name}: skip link does not target main")
            for image in parser.images:
                if "alt" not in image:
                    failures.append(f"{page.name}: image missing alt attribute")
                source = image.get("src", "")
                if source and not source.startswith(("http://", "https://", "data:")):
                    target = (page.parent / source).resolve()
                    if not target.exists():
                        failures.append(f"{page.name}: missing image {source}")
            for href in parser.links:
                if href.startswith(("#", "http://", "https://", "mailto:")):
                    continue
                target_path = urlparse(href).path
                if not target_path:
                    continue
                target = (page.parent / target_path).resolve()
                if target.is_dir():
                    target = target / "index.html"
                if not target.exists():
                    failures.append(f"{page.name}: broken link {href}")
        self.assertEqual(failures, [])

    def test_public_pages_have_share_metadata(self) -> None:
        failures: list[str] = []
        for page in sorted(DOCS.glob("*.html")):
            if page.name == "404.html":
                continue
            parser = PageParser()
            parser.feed(page.read_text("utf-8"))
            required = {
                ("name", "description"),
                ("property", "og:type"),
                ("property", "og:title"),
                ("property", "og:description"),
                ("property", "og:url"),
                ("property", "og:image"),
                ("property", "og:image:alt"),
                ("name", "twitter:card"),
            }
            missing = required - parser.metas.keys()
            if missing:
                failures.append(f"{page.name}: missing {sorted(missing)}")
            if not parser.canonical or not parser.canonical.startswith(SITE_URL):
                failures.append(f"{page.name}: invalid canonical")
            if parser.metas.get(("property", "og:image")) != (
                SITE_URL + "assets/yammerknit-sharecard.png"
            ):
                failures.append(f"{page.name}: wrong sharecard URL")
        self.assertEqual(failures, [])

    def test_sharecard_contract(self) -> None:
        card = DOCS / "assets/yammerknit-sharecard.png"
        self.assertEqual(png_dimensions(card), (1280, 640))
        self.assertLess(card.stat().st_size, 1_000_000)

    def test_css_preserves_focus_and_reduced_motion(self) -> None:
        css = (DOCS / "assets/styles.css").read_text("utf-8")
        self.assertRegex(css, r":focus-visible\s*\{")
        self.assertIn("@media (prefers-reduced-motion: reduce)", css)
        self.assertNotRegex(css, r"outline\s*:\s*(?:0(?:[;\s}]|$)|none)")


if __name__ == "__main__":
    unittest.main()
