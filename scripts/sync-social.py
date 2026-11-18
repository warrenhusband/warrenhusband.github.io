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


X_ICON = (
    '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M18.9 2H22l-6.8 7.8L23.2 22h-6.3'
    'l-4.9-6.4L6.4 22H3.3l7.3-8.3L1 2h6.4l4.4 5.9zm-1.1 18h1.7L6.3 3.9H4.5z"/></svg>'
)
LINKEDIN_ICON = (
    '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5z'
    'M3 9.75h4V21H3zM9.5 9.75h3.8v1.6h.05c.53-1 1.83-2.05 3.77-2.05 4.03 0 4.78 2.65 4.78 6.1V21h-4v-5'
    'c0-1.2-.02-2.73-1.66-2.73-1.66 0-1.92 1.3-1.92 2.64V21h-4z"/></svg>'
)


def card(href, post, network, icon):
    """One post card. The "View on" link stretches over the whole card."""
    when = label_date(post["date"])
    label = f"View on {network}: {post['text']} ({when})"
    source = ""
    if post.get("link_domain"):
        source = f'<span class="post-src">Link: {text_escape(post["link_domain"])}</span>'
    return (
        "          <article class=\"post\">\n"
        f'            <p class="post-meta"><span class="post-net">{icon}{network}</span>'
        f'<time datetime="{attr_escape(post["date"])}">{when}</time></p>\n'
        f'            <p class="post-text">{text_escape(post["text"])}</p>\n'
        f'            <p class="post-foot">{source}'
        f'<a class="post-open" href="{attr_escape(href)}" target="_blank" rel="noopener" aria-label="{attr_escape(label)}">'
        f'View on {network} <span aria-hidden="true">&rarr;</span></a></p>\n'
        "          </article>"
    )


def grid(cards):
    return "        <div class=\"posts\">\n" + "\n".join(cards) + "\n        </div>"


def x_markup(posts):
    return grid(card(f"https://x.com/WarrenHusband/status/{post['id']}", post, "X", X_ICON) for post in posts)


def linkedin_markup(posts):
    return grid(card(post["url"], post, "LinkedIn", LINKEDIN_ICON) for post in posts)


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
