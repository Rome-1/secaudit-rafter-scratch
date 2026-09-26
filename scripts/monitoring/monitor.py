#!/usr/bin/env python
"""
Defines various monitoring jobs, that check the health of the system.
"""

import os
import asyncio

from scripts.monitoring.utils import OlAsyncIOScheduler, bash_run, limit_server, get_service_ip
from scripts.monitoring.haproxy_monitor import run_once as haproxy_run_once

scheduler = OlAsyncIOScheduler()


@scheduler.scheduled_job('interval', seconds=60)
async def monitor_haproxy():
    """
    Scheduled job (interval 60s) that resolves the web_haproxy container IP
    via get_service_ip() and invokes the HAProxy monitor's main() with
    production settings (dry_run=False).
    """
    try:
        # Get the HAProxy container IP
        haproxy_ip = get_service_ip('web_haproxy')
        haproxy_url = f'http://{haproxy_ip}/admin?stats'
        
        # Run HAProxy monitoring with production settings
        await haproxy_run_once(
            haproxy_url=haproxy_url,
            graphite_address='graphite.us.archive.org:2004',
            prefix='stats.ol.haproxy',
            dry_run=False,
            agg=None
        )
    except Exception as e:
        print(f"[OL-MONITOR] HAProxy monitoring error: {e}", flush=True)


async def main():
    """
    Entrypoint for the async monitoring service: logs registered jobs,
    starts the OlAsyncIOScheduler, and blocks indefinitely.
    """
    # Print out all jobs
    jobs = scheduler.get_jobs()
    print(f"{len(jobs)} job(s) registered:", flush=True)
    for job in jobs:
        print(job, flush=True)

    # Start the scheduler
    hostname = os.environ.get("HOSTNAME", "unknown")
    print(f"Monitoring started ({hostname})", flush=True)
    
    try:
        scheduler.start()
        # Keep the event loop running indefinitely
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down monitoring...", flush=True)
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
