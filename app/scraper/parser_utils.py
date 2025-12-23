from __future__ import annotations
import re
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse

def absolutize(base: str, href: str) -> str:
    return urljoin(base, href)

def update_query(url: str, **params: str | int) -> str:
    parts = urlparse(url)
    q = parse_qs(parts.query)
    for k, v in params.items():
        q[k] = [str(v)]
    query = urlencode(q, doseq=True)
    return urlunparse((parts.scheme, parts.netloc, parts.path, parts.params, query, parts.fragment))

def parse_int_from_text(text: str) -> int:
    digits = re.findall(r"\d+", text.replace(" ", ""))
    return int("".join(digits)) if digits else 0

def parse_price_usd(text: str) -> int:
    text = text.replace("\u00a0", " ")
    m = re.search(r"(\d[\d\s.,]*)\s*\$", text)
    if not m:
        return parse_int_from_text(text)
    raw = m.group(1).replace(" ", "").replace(",", "").replace(".", "")
    return int(raw) if raw.isdigit() else parse_int_from_text(m.group(1))

def parse_odometer_km(text: str) -> int:
    t = text.lower().replace("\u00a0", " ").strip()
    t = t.replace(",", ".")
    m = re.search(r"(\d+(?:\.\d+)?)", t)
    if not m:
        return 0
    num = float(m.group(1))
    if "тис" in t or "тыс" in t:
        return int(num * 1000)
    return int(num)

def clean_phone_to_int(phone: str) -> int | None:
    digits = re.sub(r"\D+", "", phone)
    return int(digits) if digits else None

def extract_ad_id_from_url(url: str) -> int | None:
    m = re.search(r"_(\d+)\.html", url)
    return int(m.group(1)) if m else None
