from __future__ import annotations
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.config import settings
from app.scraper.scrape import scrape_once
from app.dump import dump_db

def _parse_hhmm(hhmm: str) -> tuple[int, int]:
    parts = hhmm.strip().split(":")
    if len(parts) != 2:
        raise ValueError("Time must be HH:MM")
    return int(parts[0]), int(parts[1])

async def start_scheduler() -> None:
    sh, sm = _parse_hhmm(settings.scrape_at)
    dh, dm = _parse_hhmm(settings.dump_at)

    scheduler = AsyncIOScheduler(timezone=settings.timezone)

    scheduler.add_job(
        scrape_once,
        CronTrigger(hour=sh, minute=sm),
        name="daily_scrape",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=3600,
    )

    scheduler.add_job(
        dump_db,
        CronTrigger(hour=dh, minute=dm),
        name="daily_dump",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=3600,
    )

    scheduler.start()

    while True:
        await asyncio.sleep(3600)
