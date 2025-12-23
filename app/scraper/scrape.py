from __future__ import annotations
import asyncio
import aiohttp
from urllib.parse import urlparse, parse_qs
from app.config import settings
from app.db import SessionMaker, engine
from app.models import Base
from app.repository import insert_ignore
from app.scraper.http_client import HttpClient
from app.scraper.listing_pages import parse_ad_urls
from app.scraper.ad_page import parse_ad
from app.scraper.parser_utils import (
    update_query,
    extract_ad_id_from_url,
    clean_phone_to_int,
)


async def ensure_schema() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def fetch_phone(http: HttpClient, ad_url: str) -> int | None:
    ad_id = extract_ad_id_from_url(ad_url)
    if not ad_id:
        return None

    try:
        rotator = await http.get_json(
            f"https://auto.ria.com/demo/bu/mainPage/rotator/item/{ad_id}?type=bu&langId=4",
            referer=ad_url,
        )
        hash_ = (rotator.get("userSecure") or {}).get("hash")
        if not hash_:
            return None

        phones = await http.get_json(
            f"https://auto.ria.com/users/phones/{ad_id}?hash={hash_}",
            referer=ad_url,
        )

        ph_list = phones.get("phones") or []
        if not ph_list:
            return None

        formatted = ph_list[0].get("phoneFormatted") or ph_list[0].get("phone") or ""
        return clean_phone_to_int(str(formatted))
    except Exception:
        return None


async def scrape_once() -> None:
    await ensure_schema()

    connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=300)

    async with aiohttp.ClientSession(connector=connector) as session:
        http = HttpClient(session)

        queue: asyncio.Queue[str | None] = asyncio.Queue(maxsize=settings.concurrency * 5)

        async def worker() -> None:
            async with SessionMaker() as db:
                while True:
                    ad_url = await queue.get()
                    try:
                        if ad_url is None:
                            return

                        html = await http.get_text(ad_url)
                        phone = await fetch_phone(http, ad_url)
                        ad = parse_ad(html, ad_url, phone)
                        await insert_ignore(db, ad)
                    except Exception:
                        pass
                    finally:
                        queue.task_done()

        workers = [asyncio.create_task(worker()) for _ in range(settings.concurrency)]

        seen_urls: set[str] = set()

        qs = parse_qs(urlparse(settings.start_url).query)
        start_page = int(qs.get("page", ["1"])[0]) if qs.get("page") else 1

        for page in range(start_page, start_page + settings.max_pages):
            page_url = settings.start_url if page == start_page else update_query(settings.start_url, page=page)

            try:
                listing_html = await http.get_text(page_url, referer=settings.start_url)
            except Exception:
                break

            ad_urls = parse_ad_urls(listing_html, page_url)
            if not ad_urls:
                break

            new_count = 0
            for u in ad_urls:
                if u in seen_urls:
                    continue
                seen_urls.add(u)
                new_count += 1
                await queue.put(u)

            if new_count == 0:
                break

        await queue.join()

        for _ in workers:
            await queue.put(None)
        await asyncio.gather(*workers)
