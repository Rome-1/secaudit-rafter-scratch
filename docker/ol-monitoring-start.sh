#!/bin/bash

echo "Starting monitoring on $HOSTNAME"

PYTHONPATH=. python -m scripts.monitoring.monitor
