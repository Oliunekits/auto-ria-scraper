from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from typing import Optional

import aiohttp

from app.config import settings

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
}

@dataclass
class HttpClient:
    session: aiohttp.ClientSession

    async def get_text(self, url: str, *, referer: str | None = None) -> str:
        if settings.request_delay_max > 0:
            await asyncio.sleep(random.uniform(settings.request_delay_min, settings.request_delay_max))

        headers = dict(DEFAULT_HEADERS)
        if referer:
            headers["Referer"] = referer

        timeout = aiohttp.ClientTimeout(total=settings.request_timeout)
        async with self.session.get(url, headers=headers, timeout=timeout) as resp:
            resp.raise_for_status()
            return await resp.text()

    async def get_json(self, url: str, *, referer: str | None = None) -> dict:
        if settings.request_delay_max > 0:
            await asyncio.sleep(random.uniform(settings.request_delay_min, settings.request_delay_max))

        headers = dict(DEFAULT_HEADERS)
        headers["Accept"] = "application/json,*/*;q=0.8"
        if referer:
            headers["Referer"] = referer

        timeout = aiohttp.ClientTimeout(total=settings.request_timeout)
        async with self.session.get(url, headers=headers, timeout=timeout) as resp:
            resp.raise_for_status()
            return await resp.json()
