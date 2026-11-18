#!/usr/bin/env python3
"""Rewrite the marked On X and On LinkedIn blocks in index.html."""

import html
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
DATA = ROOT / "data" / "social-posts.json"
MAX_PER_PLATFORM = 4


def text_escape(value):
    return html.escape(value, quote=False)


def attr_escape(value):
    return html.escape(value, quote=True)


def label_date(iso):
    posted = date.fromisoformat(iso)
    month = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()[posted.month - 1]
    return f"{month} {posted.day}, {posted.year}"


def x_markup(posts):
    cards = []
    for post in posts:
        href = f"https://x.com/WarrenHusband/status/{post['id']}"
        cards.append(
            "          <div class=\"x-card\">\n"
            "            <blockquote class=\"twitter-tweet\" data-dnt=\"true\">"
            f'<a href="{attr_escape(href)}" target="_blank" rel="noopener">{text_escape(post["text"])}</a>'
            "</blockquote>\n"
            "          </div>"
        )
    return "        <div class=\"x-grid\">\n" + "\n".join(cards) + "\n        </div>"


def linkedin_markup(posts):
    cards = []
    for post in posts:
        src = "https://www.linkedin.com/embed/feed/update/" + post["urn"]
        label = f"{post['text']} (LinkedIn post, {label_date(post['date'])})"
        cards.append(
            "          <figure class=\"li-card\">\n"
            f'            <iframe src="{attr_escape(src)}" loading="lazy" title="{attr_escape(post["text"])}" height="740"></iframe>\n'
            f'            <a class="li-open" href="{attr_escape(post["url"])}" target="_blank" rel="noopener" aria-label="{attr_escape(label)}"></a>\n'
            "          </figure>"
        )
    return "        <div class=\"li-grid\">\n" + "\n".join(cards) + "\n        </div>"


def replace_marked(page, start, end, inner):
    start_at = page.find(start)
    end_at = page.find(end)
    if start_at < 0 or end_at < 0 or end_at < start_at:
        raise SystemExit(f"missing markers around {start}")
    head = page[: start_at + len(start)]
    tail = page[end_at:]
    return head + "\n" + inner + "\n        " + tail


def main():
    posts = json.loads(DATA.read_text(encoding="utf-8"))
    page = INDEX.read_text(encoding="utf-8")
    page = replace_marked(page, "<!-- social:x:start -->", "<!-- social:x:end -->", x_markup(posts["x"][:MAX_PER_PLATFORM]))
    page = replace_marked(page, "<!-- social:li:start -->", "<!-- social:li:end -->", linkedin_markup(posts["linkedin"][:MAX_PER_PLATFORM]))
    INDEX.write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
