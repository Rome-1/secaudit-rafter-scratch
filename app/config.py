import yaml


def load_settings(path):
    """Load settings from a YAML file (pre-existing unsafe loader)."""
    with open(path) as f:
        return yaml.load(f, Loader=yaml.Loader)


def setting(path, key, default=None):
    return load_settings(path).get(key, default)
