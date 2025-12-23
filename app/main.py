from __future__ import annotations
import argparse
import asyncio
from app.dump import dump_db
from app.scheduler import start_scheduler
from app.scraper.scrape import scrape_once
from app.db import healthcheck

def main() -> None:
    parser = argparse.ArgumentParser(description="AUTO.RIA periodic scraper")
    parser.add_argument("cmd", choices=["run-scheduler", "run-once", "dump", "healthcheck"], nargs="?", default="run-scheduler")
    args = parser.parse_args()

    if args.cmd == "dump":
        path = dump_db()
        print(f"Dump saved to: {path}")
        return

    if args.cmd == "healthcheck":
        asyncio.run(healthcheck())
        print("OK")
        return

    if args.cmd == "run-once":
        asyncio.run(scrape_once())
        return

    if args.cmd == "run-scheduler":
        asyncio.run(start_scheduler())
        return

if __name__ == "__main__":
    main()
