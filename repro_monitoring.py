import os
os.environ['HOSTNAME'] = 'ol-web0.us.archive.org'

from scripts.monitoring.utils import OlAsyncIOScheduler, limit_server
from scripts.monitoring import monitor as monitor_mod
from scripts.monitoring.haproxy_monitor import GraphiteEvent, HaproxyCapture

print('Scheduler type:', type(monitor_mod.scheduler).__name__)
print('Has monitor_haproxy:', hasattr(monitor_mod, 'monitor_haproxy'))
print('Jobs:', [j.id for j in monitor_mod.scheduler.get_jobs()])

# Test GraphiteEvent
ge = GraphiteEvent('stats.ol.haproxy.test', 1.23, 1234567890)
print('GraphiteEvent:', ge.serialize())

# Test HaproxyCapture
cap = HaproxyCapture('.*', '(FRONTEND|BACKEND)', ['scur'])
row = {'# pxname': 'test', 'svname':'FRONTEND', 'scur':'5'}
print('Capture matches:', cap.matches(row))
print('Events from row:', [e.serialize() for e in cap.to_graphite_events('prefix', row, 123.0)])
