#!/usr/bin/env python
"""
Defines various monitoring jobs, that check the health of the system.
"""

import asyncio
import os

from scripts.monitoring.utils import (
    OlAsyncIOScheduler,
    OlBlockingScheduler,
    bash_run,
    get_service_ip,
    limit_server,
)

HOST = os.getenv("HOSTNAME")  # eg "ol-www0.us.archive.org"

if not HOST:
    raise ValueError("HOSTNAME environment variable not set.")

SERVER = HOST.split(".")[0]  # eg "ol-www0"
scheduler = OlBlockingScheduler()


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


# Async scheduler for async jobs like HAProxy monitoring
async_scheduler = OlAsyncIOScheduler()


@limit_server(["ol-www0"], async_scheduler)
@async_scheduler.scheduled_job('interval', seconds=60)
async def monitor_haproxy():
    """
    Scheduled job that monitors HAProxy stats.
    
    Resolves the web_haproxy container IP via get_service_ip() and invokes
    the HAProxy monitor's fetch and send functions with production settings.
    """
    from scripts.monitoring import haproxy_monitor
    import time
    
    try:
        # Get the IP address of the HAProxy container
        haproxy_ip = get_service_ip("web_haproxy")
        haproxy_url = f"http://{haproxy_ip}/admin?stats"
        
        # Fetch events from HAProxy
        ts = time.time()
        events = await haproxy_monitor.fetch_events(
            haproxy_url=haproxy_url,
            prefix='stats.ol.haproxy',
            ts=ts
        )
        
        # Send events to Graphite
        await haproxy_monitor.send_events(
            events=list(events),
            graphite_address='graphite.us.archive.org:2004',
            dry_run=False
        )
    except Exception as e:
        print(f"Error in monitor_haproxy: {e}", flush=True)


async def main():
    """
    Entrypoint for the async monitoring service.
    
    Logs registered jobs, starts the OlAsyncIOScheduler, and blocks indefinitely.
    """
    # Print out all jobs from both schedulers
    blocking_jobs = scheduler.get_jobs()
    print(f"{len(blocking_jobs)} blocking job(s) registered:", flush=True)
    for job in blocking_jobs:
        print(job, flush=True)
    
    async_jobs = async_scheduler.get_jobs()
    print(f"{len(async_jobs)} async job(s) registered:", flush=True)
    for job in async_jobs:
        print(job, flush=True)
    
    # Start both schedulers
    print(f"Monitoring started ({HOST})", flush=True)
    
    # Start the async scheduler
    async_scheduler.start()
    
    # Start the blocking scheduler in a separate thread
    import threading
    blocking_thread = threading.Thread(target=scheduler.start, daemon=True)
    blocking_thread.start()
    
    try:
        # Keep the async event loop running
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        async_scheduler.shutdown()
        scheduler.shutdown()


if __name__ == "__main__":
    # Check if we should run in async mode
    if os.getenv("ASYNC_MODE", "false").lower() == "true":
        asyncio.run(main())
    else:
        # Legacy blocking mode
        jobs = scheduler.get_jobs()
        print(f"{len(jobs)} job(s) registered:", flush=True)
        for job in jobs:
            print(job, flush=True)

        print(f"Monitoring started ({HOST})", flush=True)
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
