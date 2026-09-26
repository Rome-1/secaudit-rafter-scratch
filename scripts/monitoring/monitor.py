#!/usr/bin/env python
"""
Defines various monitoring jobs, that check the health of the system.

This module exposes:
- monitor_haproxy: an async scheduled job to collect HAProxy metrics
- main(): async entrypoint to start the scheduler and block forever
"""

import asyncio
import os

from scripts.monitoring.utils import (
    OlAsyncIOScheduler,
    bash_run,
    limit_server,
    get_service_ip,
)

try:
    from scripts.monitoring import haproxy_monitor
except Exception:  # pragma: no cover - optional at import time
    haproxy_monitor = None

HOST = os.environ.get("HOSTNAME", "")  # eg "ol-www0.us.archive.org"

SERVER = HOST.split(".")[0] if HOST else "localhost"  # eg "ol-www0"
scheduler = OlAsyncIOScheduler()


@limit_server(["ol-web*", "ol-covers0"], scheduler)
@scheduler.scheduled_job('interval', seconds=60)
def log_workers_cur_fn():
    """Logs the state of the gunicorn workers."""
    bash_run(f"log_workers_cur_fn stats.{SERVER}.workers.cur_fn", sources=["utils.sh"])


@limit_server(["ol-www0", "ol-covers0"], scheduler)
@scheduler.scheduled_job('interval', seconds=60)
def log_recent_bot_traffic():
    """Logs the state of the gunicorn workers."""
    match SERVER:
        case "ol-www0":
            bucket = "ol"
            container = "openlibrary-web_nginx-1"
        case "ol-covers0":
            bucket = "ol-covers"
            container = "openlibrary-covers_nginx-1"
        case _:
            raise ValueError(f"Unknown server: {SERVER}")

    bash_run(
        f"log_recent_bot_traffic stats.{bucket}.bot_traffic {container}",
        sources=["utils.sh"],
    )


@limit_server(["ol-www0", "ol-covers0"], scheduler)
@scheduler.scheduled_job('interval', seconds=60)
def log_recent_http_statuses():
    """Logs the recent HTTP statuses."""
    match SERVER:
        case "ol-www0":
            bucket = "ol"
            container = "openlibrary-web_nginx-1"
        case "ol-covers0":
            bucket = "ol-covers"
            container = "openlibrary-covers_nginx-1"
        case _:
            raise ValueError(f"Unknown server: {SERVER}")

    bash_run(
        f"log_recent_http_statuses stats.{bucket}.http_status {container}",
        sources=["utils.sh"],
    )


@limit_server(["ol-www0", "ol-covers0"], scheduler)
@scheduler.scheduled_job('interval', seconds=60)
def log_top_ip_counts():
    """Logs the recent HTTP statuses."""
    match SERVER:
        case "ol-www0":
            bucket = "ol"
            container = "openlibrary-web_nginx-1"
        case "ol-covers0":
            bucket = "ol-covers"
            container = "openlibrary-covers_nginx-1"
        case _:
            raise ValueError(f"Unknown server: {SERVER}")

    bash_run(
        f"log_top_ip_counts stats.{bucket}.top_ips {container}",
        sources=["utils.sh"],
    )


@limit_server(["ol-web*"], scheduler)
@scheduler.scheduled_job('interval', seconds=60)
async def monitor_haproxy():
    """Collect HAProxy metrics on web hosts and send them to Graphite.

    Resolves the web_haproxy container IP and invokes the haproxy monitor's
    main() with production settings (dry_run=False).
    """
    if haproxy_monitor is None:  # safety, though this should always import
        return

    ip = get_service_ip("web_haproxy")
    if not ip:
        return

    url = f"http://{ip}:7008/admin?stats"
    await haproxy_monitor.main(haproxy_url=url, dry_run=False)


async def main() -> None:
    # Print out all jobs
    jobs = scheduler.get_jobs()
    print(f"{len(jobs)} job(s) registered:", flush=True)
    for job in jobs:
        print(job, flush=True)

    # Start the scheduler and block forever
    print(f"Monitoring started ({HOST})", flush=True)
    scheduler.start()
    try:
        # Block forever; scheduler runs in the asyncio loop
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main())
