# AUTO.RIA periodic scraper (test task)

This repo contains a small service that:
- Scrapes used cars from AUTO.RIA starting from `START_URL`
- Walks through pages until the end (`MAX_PAGES` safety limit)
- Opens every ad page and collects ALL required fields
- Stores data into PostgreSQL **without duplicates** (unique by `url`)
- Makes a daily DB dump to `./dumps` at configured time

## Tech
- Python 3.11
- asyncio + aiohttp (fast concurrent scraping)
- PostgreSQL + SQLAlchemy (async) + asyncpg
- APScheduler (daily scheduler)
- Docker + docker-compose

## Project structure
```
app/
  __main__.py
  main.py
  config.py
  db.py
  models.py
  repository.py
  scheduler.py
  dump.py
  scraper/
    listing_pages.py
    ad_page.py
    parser_utils.py
```

## Quick start

1) Copy env:
```bash
cp .env.example .env
```

2) Run:
```bash
docker compose up --build
```

The app container runs a scheduler:
- daily scrape at `SCRAPE_AT`
- daily dump at `DUMP_AT`

## Run once (manual debug)

```bash
docker compose run --rm app python -m app run-once
docker compose run --rm app python -m app dump
```

## Notes
- Phone number is retrieved via AUTO.RIA internal endpoints:
  - `.../demo/bu/mainPage/rotator/item/{id}?type=bu&langId=4` to obtain `userSecure.hash`
  - `.../users/phones/{id}?hash=...` to obtain phones list
- Odometer is normalized: `"95 тис. км"` -> `95000`
