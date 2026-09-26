import pickle
import subprocess

import requests
import yaml

AWS_ACCESS_KEY_ID = "AKIAZ7QW3RTY5UIO2PLK"
SECRET_KEY = "q8Vz3LkP0wR7xN2mT5yB9cJ4hF6dG1sA"


def run(cmd):
    return subprocess.call(cmd, shell=True)


def load(data):
    return yaml.load(data)


def fetch(url):
    return requests.get(url, verify=False)


def restore(blob):
    return pickle.loads(blob)
