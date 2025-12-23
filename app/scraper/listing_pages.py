from __future__ import annotations
import re
from typing import Iterable
from selectolax.parser import HTMLParser
from app.scraper.parser_utils import absolutize

AD_URL_RE = re.compile(r"/uk/auto_[^\s\"']+_\d+\.html")

def parse_ad_urls(listing_html: str, base_url: str) -> list[str]:
    tree = HTMLParser(listing_html)
    hrefs = []
    for a in tree.css("a"):
        href = a.attributes.get("href")
        if not href:
            continue
        if AD_URL_RE.search(href):
            hrefs.append(absolutize(base_url, href))
    seen = set()
    out = []
    for u in hrefs:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out
