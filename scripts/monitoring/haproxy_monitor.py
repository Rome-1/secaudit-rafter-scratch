#!/usr/bin/env python
"""
Asynchronous monitoring script for HAProxy stats.

Polls the HAProxy admin CSV endpoint, extracts metrics (scur, rate, qcur),
buffers and optionally aggregates these metrics, and then prints or sends them
as Graphite-formatted events.
"""

import asyncio
import csv
import pickle
import re
import socket
import struct
from collections import defaultdict
from typing import Iterable, Iterator, Literal
from urllib.request import urlopen


class GraphiteEvent:
    """
    Represents a single metric event to send to Graphite.
    
    Bundles the metric path, measured value, and timestamp, and provides
    a serialize() helper for the Graphite wire format.
    """
    
    def __init__(self, path: str, value: float, timestamp: int):
        self.path = path
        self.value = value
        self.timestamp = timestamp
    
    def serialize(self) -> tuple[str, tuple[int, float]]:
        """
        Serializes a GraphiteEvent instance into a tuple format required
        by the Graphite pickle protocol.
        
        :return: Tuple of (path, (timestamp, value))
        """
        return (self.path, (self.timestamp, self.value))


class HaproxyCapture:
    """
    Encapsulates filtering logic for HAProxy CSV rows.
    
    Transforms matching rows into one or more GraphiteEvent instances
    based on the specified fields.
    """
    
    def __init__(self, pxname: str, svname: str, field: list[str]):
        """
        :param pxname: Regex pattern for HAProxy proxy name
        :param svname: Regex pattern for HAProxy service name
        :param field: List of CSV column names to capture
        """
        self.pxname_pattern = re.compile(pxname)
        self.svname_pattern = re.compile(svname)
        self.field = field
    
    def matches(self, row: dict) -> bool:
        """
        Checks whether a HAProxy stats row matches the capture criteria.
        
        :param row: Dictionary representing a CSV row from HAProxy stats
        :return: True if row matches, False otherwise
        """
        if 'pxname' not in row or 'svname' not in row:
            return False
        
        pxname_match = self.pxname_pattern.match(row['pxname'])
        svname_match = self.svname_pattern.match(row['svname'])
        
        # Check if all required fields exist and have values
        has_fields = all(
            field in row and row[field] and row[field] != ''
            for field in self.field
        )
        
        return bool(pxname_match and svname_match and has_fields)
    
    def to_graphite_events(
        self, prefix: str, row: dict, ts: float
    ) -> Iterator[GraphiteEvent]:
        """
        Transforms matching HAProxy CSV row fields into GraphiteEvent instances.
        
        :param prefix: Graphite metric namespace
        :param row: Dictionary representing a CSV row
        :param ts: Current timestamp
        :return: Iterator of GraphiteEvent instances
        """
        for field_name in self.field:
            if field_name in row and row[field_name]:
                try:
                    value = float(row[field_name])
                    path = f"{prefix}.{row['pxname']}.{row['svname']}.{field_name}"
                    yield GraphiteEvent(path, value, int(ts))
                except (ValueError, KeyError):
                    # Skip fields that can't be converted to float
                    continue


# Define what metrics to capture
TO_CAPTURE = [
    HaproxyCapture(pxname=r'.*', svname=r'FRONTEND', field=['scur', 'rate']),
    HaproxyCapture(pxname=r'.*', svname=r'BACKEND', field=['scur', 'rate', 'qcur']),
]


async def fetch_events(
    haproxy_url: str, prefix: str, ts: float
) -> Iterable[GraphiteEvent]:
    """
    Fetches the HAProxy CSV stats endpoint, parses each row, filters via TO_CAPTURE,
    and yields metric events for Graphite.
    
    :param haproxy_url: Base admin stats URL (e.g., 'http://openlibrary.org/admin?stats')
    :param prefix: Graphite metric namespace (e.g., 'stats.ol.haproxy')
    :param ts: Current timestamp
    :return: Iterable of GraphiteEvent instances
    """
    events = []
    
    # Ensure URL ends with CSV format parameter
    csv_url = f"{haproxy_url};csv"
    
    # Use asyncio to run the blocking urlopen in an executor
    loop = asyncio.get_event_loop()
    
    def fetch_url():
        with urlopen(csv_url) as response:
            return response.read().decode('utf-8')
    
    try:
        content = await loop.run_in_executor(None, fetch_url)
    except Exception as e:
        print(f"Error fetching HAProxy stats: {e}", flush=True)
        return events
    
    # Parse CSV content (skip comment lines starting with #)
    lines = [line for line in content.strip().split('\n') if not line.startswith('#')]
    
    if not lines:
        return events
    
    # First line after comments is the header
    reader = csv.DictReader(lines)
    
    for row in reader:
        for capture in TO_CAPTURE:
            if capture.matches(row):
                events.extend(capture.to_graphite_events(prefix, row, ts))
    
    return events


async def send_events(
    events: list[GraphiteEvent],
    graphite_address: str,
    dry_run: bool = True,
) -> None:
    """
    Send events to Graphite or print them.
    
    :param events: List of GraphiteEvent instances to send
    :param graphite_address: Graphite server address (host:port)
    :param dry_run: If True, print events instead of sending to Graphite
    """
    if dry_run:
        for event in events:
            print(f"{event.path} {event.value} {event.timestamp}")
    else:
        # Send to Graphite using pickle protocol
        if events:
            host, port = graphite_address.split(':')
            port = int(port)
            
            # Serialize events
            payload = pickle.dumps(
                [event.serialize() for event in events],
                protocol=2
            )
            header = struct.pack("!L", len(payload))
            message = header + payload
            
            # Send to Graphite
            loop = asyncio.get_event_loop()
            
            def send_to_graphite():
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sock.connect((host, port))
                    sock.sendall(message)
                finally:
                    sock.close()
            
            await loop.run_in_executor(None, send_to_graphite)


async def main(
    haproxy_url: str = 'http://openlibrary.org/admin?stats',
    graphite_address: str = 'graphite.us.archive.org:2004',
    prefix: str = 'stats.ol.haproxy',
    dry_run: bool = True,
    fetch_freq: int = 10,
    commit_freq: int = 30,
    agg: Literal['max', 'min', 'sum', None] = None,
) -> None:
    """
    Asynchronous loop that periodically collects HAProxy metrics.
    
    Buffers and optionally aggregates them, then either prints or sends them
    to a Graphite server.
    
    :param haproxy_url: Base admin stats URL
    :param graphite_address: Graphite server address (host:port)
    :param prefix: Graphite metric namespace
    :param dry_run: If True, print events instead of sending to Graphite
    :param fetch_freq: How often to fetch metrics (seconds)
    :param commit_freq: How often to commit/send metrics (seconds)
    :param agg: Aggregation method ('max', 'min', 'sum', or None)
    """
    buffer: dict[str, list[GraphiteEvent]] = defaultdict(list)
    last_commit = asyncio.get_event_loop().time()
    
    while True:
        try:
            # Fetch events
            ts = asyncio.get_event_loop().time()
            events = await fetch_events(haproxy_url, prefix, ts)
            
            # Buffer events
            for event in events:
                buffer[event.path].append(event)
            
            # Check if it's time to commit
            current_time = asyncio.get_event_loop().time()
            if current_time - last_commit >= commit_freq:
                # Aggregate if needed
                events_to_send = []
                
                for path, event_list in buffer.items():
                    if not event_list:
                        continue
                    
                    if agg == 'max':
                        aggregated = max(event_list, key=lambda e: e.value)
                        events_to_send.append(aggregated)
                    elif agg == 'min':
                        aggregated = min(event_list, key=lambda e: e.value)
                        events_to_send.append(aggregated)
                    elif agg == 'sum':
                        total_value = sum(e.value for e in event_list)
                        latest_ts = max(e.timestamp for e in event_list)
                        events_to_send.append(GraphiteEvent(path, total_value, latest_ts))
                    else:
                        # No aggregation, send all
                        events_to_send.extend(event_list)
                
                # Send or print events
                await send_events(events_to_send, graphite_address, dry_run)
                
                # Clear buffer and update last_commit time
                buffer.clear()
                last_commit = current_time
            
            # Wait before next fetch
            await asyncio.sleep(fetch_freq)
            
        except Exception as e:
            print(f"Error in HAProxy monitor: {e}", flush=True)
            await asyncio.sleep(fetch_freq)
