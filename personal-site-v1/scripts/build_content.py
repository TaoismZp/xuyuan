#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import math
import os
import re
import shutil
from collections import Counter
from datetime import date, datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

import yaml
from markdown_it import MarkdownIt

DEFAULT_SITE = Path(__file__).resolve().parents[1]
SITE = Path(os.environ.get("PERSONAL_SITE_ROOT", str(DEFAULT_SITE))).resolve()
CONTENT = SITE / "content" / "essays"
ARTICLE_TEMPLATE = SITE / "templates" / "article.html"
HOME = SITE / "index.html"
ARCHIVE = SITE / "essays" / "index.html"
MANIFEST = SITE / "content-manifest.json"
BASE_URL = "https://taoismzp.github.io/xuyuan/personal-site-v1"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

md = MarkdownIt("commonmark", {"html": False, "breaks": False, "typographer": False})


class ContentError(RuntimeError):
    pass


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def parse_date(value: object) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError as exc:
        raise ContentError(f"invalid ISO date: {value}") from exc


def reading_minutes(body: str) -> int:
    cjk = len(re.findall(r"[\u3400-\u9fff]", body))
    latin_words = len(re.findall(r"\b[A-Za-z0-9][A-Za-z0-9'-]*\b", body))
    minutes = (cjk / 450.0) + (latin_words / 220.0)
    return max(1, math.ceil(minutes))


def parse_source(path: Path, include_drafts: bool) -> dict:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---\n"):
        raise ContentError(f"{path.name}: missing YAML front matter")
    try:
        _, front, body = raw.split("---", 2)
    except ValueError as exc:
        raise ContentError(f"{path.name}: malformed YAML front matter") from exc
    meta = yaml.safe_load(front) or {}
    if not isinstance(meta, dict):
        raise ContentError(f"{path.name}: front matter must be a mapping")

    for key in ("title", "slug", "date", "draft"):
        if key not in meta:
            raise ContentError(f"{path.name}: missing required field '{key}'")

    title = str(meta["title"]).strip()
    slug = str(meta["slug"]).strip()
    dek = str(meta.get("dek") or "").strip()
    tags_raw = meta.get("tags") or []
    if isinstance(tags_raw, str):
        tags = [tags_raw.strip()] if tags_raw.strip() else []
    elif isinstance(tags_raw, list):
        tags = [str(tag).strip() for tag in tags_raw if str(tag).strip()]
    else:
        raise ContentError(f"{path.name}: tags must be a string list")
    draft = bool(meta["draft"])
    published_date = parse_date(meta["date"])
    body = body.strip()

    if not title:
        raise ContentError(f"{path.name}: empty title")
    if not SLUG_RE.fullmatch(slug):
        raise ContentError(f"{path.name}: slug must match {SLUG_RE.pattern}")
    if path.stem != slug:
        raise ContentError(f"{path.name}: filename must equal slug ({slug}.md)")
    if not body:
        raise ContentError(f"{path.name}: empty body")

    return {
        "source": path,
        "title": title,
        "dek": dek,
        "slug": slug,
        "date": published_date,
        "tags": tags,
        "draft": draft,
        "publishable": include_drafts or not draft,
        "minutes": reading_minutes(body),
        "body_html": md.render(body),
    }


def load_entries(include_drafts: bool) -> list[dict]:
    CONTENT.mkdir(parents=True, exist_ok=True)
    entries = [parse_source(path, include_drafts) for path in sorted(CONTENT.glob("*.md"))]
    seen: set[str] = set()
    for entry in entries:
        if entry["slug"] in seen:
            raise ContentError(f"duplicate slug: {entry['slug']}")
        seen.add(entry["slug"])
    entries.sort(key=lambda x: (x["date"], x["slug"]), reverse=True)
    return entries


def replace_block(text: str, name: str, replacement: str) -> str:
    start = f"<!-- CMS:{name}_START -->"
    end = f"<!-- CMS:{name}_END -->"
    if start not in text or end not in text:
        raise ContentError(f"missing content markers for {name}")
    before, rest = text.split(start, 1)
    _, after = rest.split(end, 1)
    return f"{before}{start}{replacement}{end}{after}"


def meta_label(entry: dict) -> str:
    label = " / ".join(entry["tags"][:2]) if entry["tags"] else "长文"
    return f"{esc(label)}<br>约 {entry['minutes']} 分钟"


def home_rows(entries: list[dict]) -> str:
    if not entries:
        return '<div class="content-empty">还没有公开长文。第一篇发布后会自动出现在这里。</div>'
    rows = []
    for entry in entries[:3]:
        rows.append(
            f'<a class="essay-row" href="essays/{esc(entry["slug"])}/">'
            f'<span class="essay-row__meta">{meta_label(entry)}</span>'
            f'<span class="essay-row__title">《{esc(entry["title"])}》</span>'
            f'<span class="essay-row__year">{entry["date"].year}</span></a>'
        )
    return "".join(rows)


def tag_key(value: str) -> str:
    return value


def archive_filters(entries: list[dict]) -> str:
    counts: Counter[str] = Counter(tag for entry in entries for tag in entry["tags"])
    buttons = ['<button class="filter-button" type="button" data-filter="all" aria-pressed="true">全部</button>']
    for tag, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        buttons.append(
            f'<button class="filter-button" type="button" data-filter="{esc(tag_key(tag))}" aria-pressed="false">{esc(tag)}</button>'
        )
    return "".join(buttons)


def archive_rows(entries: list[dict]) -> str:
    if not entries:
        return '<div class="content-empty">还没有公开长文。</div>'
    rows = []
    for entry in entries:
        tags = "|".join(tag_key(tag) for tag in entry["tags"])
        tag_text = " / ".join(entry["tags"][:2]) if entry["tags"] else "长文"
        ym = entry["date"].strftime("%Y · %m")
        rows.append(
            f'<a class="archive-row" data-tags="{esc(tags)}" href="{esc(entry["slug"])}/">'
            f'<span class="archive-row__meta">{esc(tag_text)}<br>约 {entry["minutes"]} 分钟</span>'
            f'<h2>《{esc(entry["title"])}》</h2>'
            f'<time class="archive-row__date" datetime="{entry["date"].isoformat()}">{esc(ym)}</time></a>'
        )
    return "".join(rows)


def render_article(entry: dict, template: str) -> str:
    description = entry["dek"] or f"TaoismZp 长文：{entry['title']}"
    tag_text = " / ".join(entry["tags"]) if entry["tags"] else "长文"
    meta = f"{esc(tag_text)} · {entry['date'].isoformat()} · 约 {entry['minutes']} 分钟"
    dek_html = f'<p class="article-head__dek">{esc(entry["dek"])}</p>' if entry["dek"] else ""
    return (
        template.replace("@@DESCRIPTION@@", esc(description))
        .replace("@@TITLE@@", esc(entry["title"]))
        .replace("@@META@@", meta)
        .replace("@@DEK@@", dek_html)
        .replace("@@BODY@@", entry["body_html"])
    )


def cleanup_stale(valid_slugs: set[str]) -> None:
    previous: list[str] = []
    if MANIFEST.exists():
        try:
            previous = [str(item["slug"]) for item in json.loads(MANIFEST.read_text(encoding="utf-8")).get("entries", [])]
        except Exception:
            previous = []
    for slug in previous:
        if slug not in valid_slugs:
            target = SITE / "essays" / slug
            if target.is_dir() and slug != "sample":
                shutil.rmtree(target)


def write_feed(entries: list[dict]) -> None:
    items = []
    for entry in entries:
        dt = datetime(entry["date"].year, entry["date"].month, entry["date"].day, tzinfo=timezone.utc)
        url = f"{BASE_URL}/essays/{entry['slug']}/"
        description = entry["dek"] or entry["title"]
        items.append(
            "<item>"
            f"<title>{xml_escape(entry['title'])}</title>"
            f"<link>{xml_escape(url)}</link>"
            f"<guid>{xml_escape(url)}</guid>"
            f"<pubDate>{format_datetime(dt)}</pubDate>"
            f"<description>{xml_escape(description)}</description>"
            "</item>"
        )
    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<rss version="2.0"><channel>'
        '<title>TaoismZp 长文</title>'
        f'<link>{BASE_URL}/essays/</link>'
        '<description>交易、写作、研究。</description>'
        + "".join(items)
        + '</channel></rss>'
    )
    (SITE / "feed.xml").write_text(feed + "\n", encoding="utf-8")


def write_sitemap(entries: list[dict]) -> None:
    urls = [f"{BASE_URL}/", f"{BASE_URL}/essays/", f"{BASE_URL}/projects/", f"{BASE_URL}/about/"]
    urls.extend(f"{BASE_URL}/essays/{entry['slug']}/" for entry in entries)
    body = "".join(f"<url><loc>{xml_escape(url)}</loc></url>" for url in urls)
    sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + body + '</urlset>'
    (SITE / "sitemap.xml").write_text(sitemap + "\n", encoding="utf-8")


def build(include_drafts: bool) -> None:
    entries_all = load_entries(include_drafts=include_drafts)
    entries = [entry for entry in entries_all if entry["publishable"]]

    home = HOME.read_text(encoding="utf-8")
    HOME.write_text(replace_block(home, "RECENT", home_rows(entries)), encoding="utf-8")

    archive = ARCHIVE.read_text(encoding="utf-8")
    archive = replace_block(archive, "FILTERS", archive_filters(entries))
    archive = replace_block(archive, "ROWS", archive_rows(entries))
    ARCHIVE.write_text(archive, encoding="utf-8")

    template = ARTICLE_TEMPLATE.read_text(encoding="utf-8")
    valid_slugs = {entry["slug"] for entry in entries}
    cleanup_stale(valid_slugs)
    for entry in entries:
        out = SITE / "essays" / entry["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_article(entry, template), encoding="utf-8")

    manifest = {
        "schema": 1,
        "entries": [
            {
                "title": entry["title"],
                "dek": entry["dek"],
                "slug": entry["slug"],
                "date": entry["date"].isoformat(),
                "tags": entry["tags"],
                "minutes": entry["minutes"],
            }
            for entry in entries
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_feed(entries)
    write_sitemap(entries)
    print(f"Built {len(entries)} published essay(s); validated {len(entries_all)} source file(s).")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-drafts", action="store_true", help="test-only: render drafts in the selected SITE root")
    args = parser.parse_args()
    build(include_drafts=args.include_drafts)


if __name__ == "__main__":
    main()