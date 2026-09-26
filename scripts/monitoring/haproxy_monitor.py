#!/usr/bin/env python3
"""
Asynchronous monitoring script that polls the HAProxy admin CSV endpoint, extracts
session counts (scur), rates (rate), and queue lengths (qcur), buffers and optionally
aggregates these metrics, and then prints or sends them as Graphite‐formatted events.

Public interfaces:
- class GraphiteEvent
- class HaproxyCapture
- async def fetch_events(...)
- async def main(...)

This module is purposely lightweight for testability. The Graphite client is
implemented using the pickle protocol format only when dry_run is False; otherwise we
print serialized events.
"""
from __future__ import annotations

import asyncio
import csv
import io
import os
import pickle
import re
import socket
import struct
import time
from dataclasses import dataclass
from typing import Iterable, Iterator, Literal

import httpx


@dataclass
class GraphiteEvent:
    path: str
    value: float
    timestamp: int

    def serialize(self) -> tuple[str, tuple[int, float]]:
        """Return the tuple format Graphite's pickle protocol expects."""
        return (self.path, (self.timestamp, self.value))


class HaproxyCapture:
    """
    Encapsulates filtering logic for HAProxy CSV rows and transforms matching rows
    into GraphiteEvent instances based on the specified fields.
    """

    def __init__(self, pxname: str, svname: str, field: list[str]):
        self.pxname_re = re.compile(pxname)
        self.svname_re = re.compile(svname)
        self.fields = field

    def matches(self, row: dict) -> bool:
        """Check whether the row matches our selection criteria."""
        return bool(
            self.pxname_re.search(row.get("# pxname", ""))
            and self.svname_re.search(row.get("svname", ""))
        )

    def to_graphite_events(self, prefix: str, row: dict, ts: float) -> Iterator[GraphiteEvent]:
        for f in self.fields:
            if f not in row or row[f] in ("", "-", None):
                continue
            try:
                value = float(row[f])
            except ValueError:
                continue
            metric = f"{prefix}.{row['# pxname']}.{row['svname']}.{f}"
            yield GraphiteEvent(metric, value, int(ts))


# What to capture from haproxy stats
TO_CAPTURE: list[HaproxyCapture] = [
    # frontends/backends, current sessions, current queue length, and rate
    HaproxyCapture(pxname=".*", svname="(FRONTEND|BACKEND)", field=["scur", "qcur", "rate"]),
]


def fetch_events(haproxy_url: str, prefix: str, ts: float) -> Iterable[GraphiteEvent]:
    """
    Fetch CSV from HAProxy admin endpoint and yield GraphiteEvent objects.
    """
    url = haproxy_url
    if not url.endswith(";csv") and "csv" not in url:
        url = f"{haproxy_url};csv"

    resp = httpx.get(url, timeout=10)
    resp.raise_for_status()
    text = resp.text

    # Parse CSV
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        for capture in TO_CAPTURE:
            if capture.matches(row):
                for e in capture.to_graphite_events(prefix, row, ts):
                    yield e


async def _send_to_graphite_pickle(address: str, events: list[GraphiteEvent]) -> None:
    host, port_s = address.split(":")
    port = int(port_s)
    payload = [e.serialize() for e in events]
    body = pickle.dumps(payload, protocol=2)
    header = struct.pack("!L", len(body))

    loop = asyncio.get_running_loop()
    # Use a threadpool for blocking socket ops
    def _send():
        with socket.create_connection((host, port), timeout=10) as sock:
            sock.sendall(header + body)

    await loop.run_in_executor(None, _send)


async def main(
    haproxy_url: str = "http://openlibrary.org/admin?stats",
    graphite_address: str = "graphite.us.archive.org:2004",
    prefix: str = "stats.ol.haproxy",
    dry_run: bool = True,
    fetch_freq: int = 10,
    commit_freq: int = 30,
    agg: Literal['max','min','sum',None] = None,
) -> None:
    """
    Periodically collect HAProxy metrics via fetch_events, buffer and optionally
    aggregate, then either print or send them to Graphite.
    """
    buffer: dict[str, list[GraphiteEvent]] = {}

    async def flush(now: float) -> None:
        if not buffer:
            return
        events: list[GraphiteEvent] = []
        if agg:
            # reduce events by key
            tmp: dict[str, GraphiteEvent] = {}
            for bucket in buffer.values():
                for e in bucket:
                    k = e.path
                    if k not in tmp:
                        tmp[k] = e
                        continue
                    if agg == 'max' and e.value > tmp[k].value:
                        tmp[k] = e
                    elif agg == 'min' and e.value < tmp[k].value:
                        tmp[k] = e
                    elif agg == 'sum':
                        tmp[k].value += e.value
                        tmp[k].timestamp = e.timestamp
            events = list(tmp.values())
        else:
            for bucket in buffer.values():
                events.extend(bucket)

        if dry_run:
            for e in events:
                print(e.serialize())
        else:
            await _send_to_graphite_pickle(graphite_address, events)
        buffer.clear()

    last_commit = 0.0
    try:
        while True:
            now = time.time()
            # fetch and buffer
            for e in fetch_events(haproxy_url, prefix, now):
                buffer.setdefault(e.path, []).append(e)

            if now - last_commit >= commit_freq:
                await flush(now)
                last_commit = now

            await asyncio.sleep(fetch_freq)
    except asyncio.CancelledError:  # pragma: no cover - shutdown path
        pass
    finally:
        await flush(time.time())
