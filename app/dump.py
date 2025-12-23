from __future__ import annotations
import os
import subprocess
from pathlib import Path
from datetime import datetime
from app.config import settings

def dump_db() -> Path:
    dumps_dir = Path("dumps")
    dumps_dir.mkdir(exist_ok=True)

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_path = dumps_dir / f"autoria_{ts}.sql.gz"

    env = os.environ.copy()
    env["PGPASSWORD"] = settings.db_password

    cmd = [
        "bash", "-lc",
        'pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" | gzip -c > "$OUT"'
    ]

    env.update({
        "DB_HOST": settings.db_host,
        "DB_PORT": str(settings.db_port),
        "DB_USER": settings.db_user,
        "DB_NAME": settings.db_name,
        "OUT": str(out_path),
    })

    subprocess.run(cmd, check=True, env=env)
    return out_path
