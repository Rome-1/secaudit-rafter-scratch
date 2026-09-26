import fnmatch
import os
import subprocess
import typing
import json

from apscheduler.events import (
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_SUBMITTED,
    JobEvent,
)
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.util import undefined


class OlBlockingScheduler(BlockingScheduler):
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
            # Override to avoid duplicating the function name everywhere
            id or func.__name__,
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
            # Override to avoid duplicating the function name everywhere
            id or func.__name__,
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


def limit_server(allowed_servers: list[str], scheduler):
    """
    Decorate that un-registers a job if the server does not match any of the allowed servers.

    :param allowed_servers: List of allowed servers. Can include `*` for globbing, eg "ol-web*"
    :param scheduler: Either BlockingScheduler or AsyncIOScheduler
    """

    def decorator(func):
        hostname = os.environ.get("HOSTNAME")
        if not hostname:
            # If no hostname is set, don't register the job
            return func
        
        server = hostname
        if hostname.endswith(".us.archive.org"):
            server = hostname.split(".")[0]

        if not any(fnmatch.fnmatch(server, pattern) for pattern in allowed_servers):
            # Try to remove the job if it doesn't match allowed servers
            try:
                scheduler.remove_job(func.__name__)
            except Exception:
                # Job might not be registered yet, which is fine
                pass
        return func

    return decorator


def get_service_ip(image_name: str) -> str:
    """
    Uses docker inspect to retrieve the IP address of the specified container,
    normalizing the image name if needed.
    
    :param image_name: The name of the Docker container/image
    :return: The IP address of the container
    """
    # Normalize the image name - ensure it doesn't have leading/trailing whitespace
    image_name = image_name.strip()
    
    try:
        # Run docker inspect to get container info
        result = subprocess.run(
            ["docker", "inspect", image_name, "--format={{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"],
            capture_output=True,
            text=True,
            check=True
        )
        ip_address = result.stdout.strip()
        
        if not ip_address:
            raise ValueError(f"No IP address found for container {image_name}")
            
        return ip_address
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get IP for container {image_name}: {e}")
    except Exception as e:
        raise RuntimeError(f"Error inspecting container {image_name}: {e}")
