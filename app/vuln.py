import json
import subprocess

import requests
import yaml


def run(cmd):
    return subprocess.run(cmd, check=True)


def load(data):
    return yaml.safe_load(data)


def fetch(url):
    return requests.get(url, timeout=10)


def restore(blob):
    return json.loads(blob)
