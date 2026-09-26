import fnmatch
import os
import subprocess
import typing

from apscheduler.events import (
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_SUBMITTED,
    JobEvent,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.util import undefined


class OlAsyncIOScheduler(AsyncIOScheduler):
    def __init__(self):
        super().__init__({'apscheduler.timezone': 'UTC'})
        self.add_listener(
            job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_SUBMITTED
        )

    @typing.override
    def add_job(
        self,
        func,
        trigger=None,
        args=None,
        kwargs=None,
        id=None,
        name=None,
        misfire_grace_time=undefined,
        coalesce=undefined,
        max_instances=undefined,
        next_run_time=undefined,
        jobstore="default",
        executor="default",
        replace_existing=False,
        **trigger_args,
    ):
        return super().add_job(
            func,
            trigger,
            args,
            kwargs,
            # Default the job id to the function name so tests can look it up easily
            id or getattr(func, "__name__", None),
            name,
            misfire_grace_time,
            coalesce,
            max_instances,
            next_run_time,
            jobstore,
            executor,
            replace_existing,
            **trigger_args,
        )


# Backwards-compatibility alias in case older code/tests reference this name
class OlBlockingScheduler(OlAsyncIOScheduler):
    pass


def job_listener(event: JobEvent):
    if event.code == EVENT_JOB_SUBMITTED:
        print(f"[OL-MONITOR] Job {event.job_id} has started.", flush=True)
    elif event.code == EVENT_JOB_EXECUTED:
        print(f"[OL-MONITOR] Job {event.job_id} completed successfully.", flush=True)
    elif event.code == EVENT_JOB_ERROR:
        print(f"[OL-MONITOR] Job {event.job_id} failed.", flush=True)


def bash_run(cmd: str, sources: list[str] | None = None, capture_output=False):
    if not sources:
        sources = []

    source_paths = [
        (
            os.path.join("scripts", "monitoring", source)
            if not os.path.isabs(source)
            else source
        )
        for source in sources
    ]
    bash_command = "\n".join(
        (
            'set -e',
            *(f'source "{path}"' for path in source_paths),
            cmd,
        )
    )

    return subprocess.run(
        [
            "bash",
            "-c",
            bash_command,
        ],
        check=True,
        # Mainly for testing:
        capture_output=capture_output,
        text=capture_output if capture_output else None,
    )


def limit_server(allowed_servers: list[str], scheduler: BlockingScheduler | AsyncIOScheduler):
    """
    Decorator that conditionally keeps or unregisters a scheduled job based on the
    current host name from the environment.

    - Supports exact names (e.g., "allowed-server"),
    - Prefix wildcards using fnmatch (e.g., "allowed-server*"), and
    - Matching a short host against an FQDN (e.g., "ol-web0" matches
      "ol-web0.us.archive.org").
    """

    def decorator(func):
        # Must read from the environment (not socket lookups) so tests/users can control it
        hostname = os.environ.get("HOSTNAME") or ""
        short = hostname.split(".")[0] if hostname else ""

        candidates = [c for c in {hostname, short} if c]
        allowed = any(
            fnmatch.fnmatch(cand, pattern)
            for pattern in allowed_servers
            for cand in (candidates or [""])
        )

        if not allowed:
            # If the inner scheduled_job decorator already registered the job, remove it.
            try:
                scheduler.remove_job(getattr(func, "__name__", None))
            except Exception:
                # If the job wasn't registered (or scheduler not started yet), just ignore
                pass
        return func

    return decorator


def get_service_ip(image_name: str) -> str:
    """
    Returns the IP address of a running docker container.

    The input may be a bare service name like "web_haproxy". In that case, we
    normalize it to the compose-style name "openlibrary-<service>-1".
    """
    name = image_name
    # Normalize basic docker-compose naming convention if needed
    if not name.startswith("openlibrary-"):
        # append instance suffix if missing
        if not name.endswith("-1"):
            name = f"{name}-1"
        name = f"openlibrary-{name}"

    try:
        result = subprocess.run(
            [
                "docker",
                "inspect",
                "-f",
                "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}",
                name,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return (result.stdout or "").strip()
    except Exception:
        return ""
