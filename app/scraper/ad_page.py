from __future__ import annotations

import re
from typing import Optional

from selectolax.parser import HTMLParser

from app.repository import CarAdDTO
from app.scraper.parser_utils import parse_price_usd, parse_odometer_km, clean_phone_to_int

def _text_first(tree: HTMLParser, selectors: list[str]) -> str:
    for sel in selectors:
        node = tree.css_first(sel)
        if node and node.text(strip=True):
            return node.text(strip=True)
    return ""

def _attr_first(tree: HTMLParser, selectors: list[tuple[str, str]]) -> str:
    for sel, attr in selectors:
        node = tree.css_first(sel)
        if node and node.attributes.get(attr):
            return node.attributes[attr]
    return ""

def parse_ad(html: str, url: str, phone_number: int | None) -> CarAdDTO:
    tree = HTMLParser(html)

    title = _text_first(tree, ["h1", "h1.head", "h1#heading"])
    if not title:
        # fallback: meta og:title
        title = _attr_first(tree, [("meta[property='og:title']", "content")]) or "Unknown"

    # price
    price_text = _text_first(tree, ["span.price_value", ".price_value", "[data-currency='USD']"])
    if not price_text:
        # fallback: search in raw html
        m = re.search(r"(\d[\d\s]*)\s*\$", html)
        price_text = m.group(0) if m else "0"
    price_usd = parse_price_usd(price_text)

    # odometer
    odo_text = _text_first(tree, [".base-information span", ".base-information", ".boxed span", "span.size18"])
    # try to find something that looks like пробіг
    if "проб" not in odo_text.lower() and "км" not in odo_text.lower():
        m = re.search(r"(\d[\d\s.,]*\s*(?:тис\.|тыс\.)?\s*км)", html, flags=re.IGNORECASE)
        odo_text = m.group(1) if m else "0"
    odometer = parse_odometer_km(odo_text)

    # username (seller)
    username = _text_first(tree, [".seller_info_name", ".seller_info_name a", ".seller_info_title", ".seller_info"])
    if not username:
        m = re.search(r"seller[^<]{0,40}>([^<]{2,40})<", html, flags=re.IGNORECASE)
        username = m.group(1).strip() if m else "Unknown"

    # main image url
    image_url = _attr_first(tree, [
        ("meta[property='og:image']", "content"),
        (".photo-620x465 img", "src"),
        ("img#photo", "src"),
    ]) or ""

    if not image_url:
        # fallback: first big image
        img = tree.css_first("img")
        image_url = img.attributes.get("src", "") if img else ""

    # images count (photos)
    images_count = 0
    node = tree.css_first(".action_disp_all_block a, a.show-all")
    if node and node.text():
        images_count = int(re.sub(r"\D+", "", node.text()) or 0)
    if images_count == 0:
        m = re.search(r"(\d+)\s*фото", html, flags=re.IGNORECASE)
        images_count = int(m.group(1)) if m else 0

    car_number = _text_first(tree, [".state-num", ".state-num ua", ".plate-number", ".car-number"])
    if not car_number:
        m = re.search(r"([A-ZА-ЯІЇЄ]{2}\s?\d{4}\s?[A-ZА-ЯІЇЄ]{2})", html)
        car_number = m.group(1).replace("  ", " ").strip() if m else ""

    for n in tree.css("*"):
        t = n.text(strip=True)
        if t and ("vin" in t.lower()) and len(t) <= 40:
            break
    m = re.search(r"VIN[^A-Z0-9]*([A-HJ-NPR-Z0-9]{11,17})", html, flags=re.IGNORECASE)
    car_vin = m.group(1) if m else ""
    if not car_vin:
        m2 = re.search(r"([A-HJ-NPR-Z0-9]{17})", html)
        car_vin = m2.group(1) if m2 else ""


    return CarAdDTO(
        url=url,
        title=title.strip(),
        price_usd=int(price_usd),
        odometer=int(odometer),
        username=username.strip() or "Unknown",
        phone_number=phone_number,
        image_url=image_url.strip() or "",
        images_count=int(images_count),
        car_number=car_number.strip() or "",
        car_vin=car_vin.strip() or "",
    )
