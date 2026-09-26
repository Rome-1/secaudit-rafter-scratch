#!/usr/bin/env python3
"""
Asynchronous monitoring script that polls the HAProxy admin CSV endpoint,
extracts session counts (scur), rates (rate), and queue lengths (qcur),
buffers and optionally aggregates these metrics, and then prints or sends
them as Graphite‐formatted events.
"""

import asyncio
import aiohttp
import re
import time
import socket
import pickle
from typing import Iterator, Iterable, Literal
from dataclasses import dataclass


@dataclass
class GraphiteEvent:
    """
    Represents a single metric event to send to Graphite, bundling the metric path,
    measured value, and timestamp, and providing a serialize() helper for the Graphite
    wire format.
    """
    path: str
    value: float
    timestamp: int
    
    def serialize(self) -> tuple[str, tuple[int, float]]:
        """
        Serializes a GraphiteEvent instance into a tuple format required by the
        Graphite pickle protocol.
        """
        return (self.path, (self.timestamp, self.value))


class HaproxyCapture:
    """
    Encapsulates filtering logic for HAProxy CSV rows and transforms matching rows
    into one or more GraphiteEvent instances based on the specified fields.
    """
    
    def __init__(self, pxname: str, svname: str, field: list[str]):
        """
        :param pxname: regex for HAProxy proxy name
        :param svname: regex for HAProxy service name  
        :param field: list of CSV column names to capture
        """
        self.pxname_pattern = re.compile(pxname)
        self.svname_pattern = re.compile(svname)
        self.fields = field
    
    def matches(self, row: dict) -> bool:
        """
        Checks whether a HAProxy stats row matches the capture criteria for
        proxy name, service name, and selected fields.
        """
        pxname = row.get('# pxname', '')
        svname = row.get('svname', '')
        
        if not self.pxname_pattern.match(pxname):
            return False
        if not self.svname_pattern.match(svname):
            return False
            
        # Check if any of the desired fields have values
        return any(row.get(field, '') not in ('', 'N/A', None) for field in self.fields)
    
    def to_graphite_events(self, prefix: str, row: dict, ts: float) -> Iterator[GraphiteEvent]:
        """
        Transforms matching HAProxy CSV row fields into GraphiteEvent instances
        with appropriate metric paths.
        """
        pxname = row.get('# pxname', '')
        svname = row.get('svname', '')
        
        for field in self.fields:
            value_str = row.get(field, '')
            if value_str not in ('', 'N/A', None):
                try:
                    value = float(value_str)
                    # Construct metric path: prefix.pxname.svname.field
                    metric_path = f"{prefix}.{pxname}.{svname}.{field}"
                    yield GraphiteEvent(metric_path, value, int(ts))
                except (ValueError, TypeError):
                    # Skip non-numeric values
                    continue


# Define what to capture from HAProxy stats
TO_CAPTURE = [
    HaproxyCapture(r'.*', r'FRONTEND', ['scur', 'rate', 'qcur']),
    HaproxyCapture(r'.*', r'BACKEND', ['scur', 'rate', 'qcur']),
    HaproxyCapture(r'.*', r'(?!FRONTEND|BACKEND).*', ['scur', 'rate', 'qcur']),
]


async def fetch_events(haproxy_url: str, prefix: str, ts: float) -> Iterable[GraphiteEvent]:
    """
    Fetches the HAProxy CSV stats endpoint, parses each row, filters via TO_CAPTURE,
    and yields metric events for Graphite.
    
    :param haproxy_url: base admin stats URL
    :param prefix: Graphite metric namespace  
    :param ts: current timestamp
    :return: Iterable of GraphiteEvent instances
    """
    events = []
    
    # Ensure URL ends with CSV format parameter
    if '?' in haproxy_url:
        csv_url = f"{haproxy_url}&stats;csv"
    else:
        csv_url = f"{haproxy_url}?stats;csv"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(csv_url) as response:
                if response.status != 200:
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status
                    )
                
                content = await response.text()
                lines = content.strip().split('\n')
                
                if not lines:
                    return events
                
                # First line should be headers
                headers = [h.strip() for h in lines[0].split(',')]
                
                for line in lines[1:]:
                    if not line.strip():
                        continue
                        
                    values = [v.strip() for v in line.split(',')]
                    if len(values) != len(headers):
                        continue
                        
                    row = dict(zip(headers, values))
                    
                    # Apply all capture filters
                    for capture in TO_CAPTURE:
                        if capture.matches(row):
                            events.extend(capture.to_graphite_events(prefix, row, ts))
                            
    except Exception as e:
        print(f"Error fetching HAProxy stats: {e}", flush=True)
        
    return events


async def send_to_graphite(events: list[GraphiteEvent], graphite_address: str):
    """
    Send events to Graphite using the pickle protocol.
    """
    if not events:
        return
        
    host, port = graphite_address.split(':')
    port = int(port)
    
    payload = [event.serialize() for event in events]
    payload_pickle = pickle.dumps(payload)
    
    try:
        # Use asyncio socket operations
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        
        await asyncio.get_event_loop().sock_connect(sock, (host, port))
        await asyncio.get_event_loop().sock_sendall(sock, payload_pickle)
        sock.close()
        
        print(f"Sent {len(events)} events to Graphite", flush=True)
        
    except Exception as e:
        print(f"Error sending to Graphite: {e}", flush=True)


def aggregate_events(events: list[GraphiteEvent], agg_method: str) -> list[GraphiteEvent]:
    """
    Aggregate events by metric path using the specified method.
    """
    if not events or not agg_method:
        return events
        
    # Group by metric path
    grouped = {}
    for event in events:
        if event.path not in grouped:
            grouped[event.path] = []
        grouped[event.path].append(event)
    
    aggregated = []
    for path, path_events in grouped.items():
        if len(path_events) == 1:
            aggregated.append(path_events[0])
            continue
            
        values = [e.value for e in path_events]
        timestamp = path_events[-1].timestamp  # Use latest timestamp
        
        if agg_method == 'max':
            agg_value = max(values)
        elif agg_method == 'min':
            agg_value = min(values)
        elif agg_method == 'sum':
            agg_value = sum(values)
        else:
            # Default to last value
            agg_value = values[-1]
            
        aggregated.append(GraphiteEvent(path, agg_value, timestamp))
    
    return aggregated


async def main(
    haproxy_url: str = 'http://openlibrary.org/admin?stats',
    graphite_address: str = 'graphite.us.archive.org:2004',
    prefix: str = 'stats.ol.haproxy',
    dry_run: bool = True,
    fetch_freq: int = 10,
    commit_freq: int = 30,
    agg: Literal['max', 'min', 'sum', None] = None
):
    """
    Asynchronous loop that periodically collects HAProxy metrics via fetch_events,
    buffers and optionally aggregates them, then either prints or sends them to
    a Graphite server.
    
    :param haproxy_url: HAProxy admin stats URL
    :param graphite_address: Graphite server address (host:port)
    :param prefix: Metric prefix for Graphite
    :param dry_run: If True, print events instead of sending to Graphite
    :param fetch_freq: How often to fetch metrics (seconds)
    :param commit_freq: How often to send buffered metrics (seconds)
    :param agg: Aggregation method for buffered events
    """
    print(f"Starting HAProxy monitor (dry_run={dry_run})", flush=True)
    print(f"HAProxy URL: {haproxy_url}", flush=True)
    print(f"Fetch frequency: {fetch_freq}s, commit frequency: {commit_freq}s", flush=True)
    
    event_buffer = []
    last_commit = time.time()
    
    while True:
        try:
            ts = time.time()
            
            # Fetch new events
            new_events = await fetch_events(haproxy_url, prefix, ts)
            event_buffer.extend(new_events)
            
            # Check if it's time to commit/send events
            if ts - last_commit >= commit_freq:
                if event_buffer:
                    # Apply aggregation if specified
                    final_events = aggregate_events(event_buffer, agg)
                    
                    if dry_run:
                        print(f"Would send {len(final_events)} events:", flush=True)
                        for event in final_events[:10]:  # Show first 10 events
                            print(f"  {event.path}: {event.value} at {event.timestamp}", flush=True)
                        if len(final_events) > 10:
                            print(f"  ... and {len(final_events) - 10} more", flush=True)
                    else:
                        await send_to_graphite(final_events, graphite_address)
                    
                    event_buffer.clear()
                
                last_commit = ts
            
            # Wait for next fetch
            await asyncio.sleep(fetch_freq)
            
        except Exception as e:
            print(f"Error in main loop: {e}", flush=True)
            await asyncio.sleep(fetch_freq)


async def run_once(
    haproxy_url: str = 'http://openlibrary.org/admin?stats',
    graphite_address: str = 'graphite.us.archive.org:2004',
    prefix: str = 'stats.ol.haproxy',
    dry_run: bool = True,
    agg: Literal['max', 'min', 'sum', None] = None
):
    """
    Single run of HAProxy monitoring - fetches metrics and sends them to Graphite once.
    This is suitable for use in scheduled jobs.
    """
    try:
        ts = time.time()
        
        # Fetch events
        events = await fetch_events(haproxy_url, prefix, ts)
        
        if events:
            # Apply aggregation if specified
            final_events = aggregate_events(events, agg)
            
            if dry_run:
                print(f"[HAProxy Monitor] Would send {len(final_events)} events", flush=True)
                for event in final_events[:3]:  # Show first 3 events
                    print(f"  {event.path}: {event.value} at {event.timestamp}", flush=True)
                if len(final_events) > 3:
                    print(f"  ... and {len(final_events) - 3} more", flush=True)
            else:
                await send_to_graphite(final_events, graphite_address)
                print(f"[HAProxy Monitor] Sent {len(final_events)} events to Graphite", flush=True)
        else:
            print("[HAProxy Monitor] No events collected", flush=True)
            
    except Exception as e:
        print(f"[HAProxy Monitor] Error: {e}", flush=True)


if __name__ == '__main__':
    asyncio.run(main())