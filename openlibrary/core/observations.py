"""Module for handling patron observation functionality"""

import requests

from infogami import config
from openlibrary import accounts
from . import cache

# URL for TheBestBookOn
TBBO_URL = config.get('tbbo_url')

def post_observation(data, s3_keys):
    headers = {
        'x-s3-access': s3_keys['access'],
        'x-s3-secret': s3_keys['secret']
    }

    response = requests.post(TBBO_URL + '/api/observations', data=data, headers=headers)

    return response.text

@cache.memoize(engine="memcache", key="tbbo_aspects", expires=config.get('tbbo_aspect_cache_duration'))
def get_aspects():
    response = requests.get(TBBO_URL + '/api/aspects')

    return response.text



def _sort_values(order_list, values_list):
    """Return a list of names ordered according to order_list.

    Args:
        order_list (list[int]): Desired ordering of IDs.
        values_list (list[dict]): List of dicts each containing at least 'id' and 'name'.

    Returns:
        list[str]: Names ordered as specified, ignoring missing IDs and excluding extra values.
    """
    # Build a mapping from id to name for quick lookup.
    id_to_name = {v.get('id'): v.get('name') for v in values_list if 'id' in v and 'name' in v}
    # Generate list preserving order, ignoring unknown ids.
    sorted_names = []
    for vid in order_list:
        name = id_to_name.get(vid)
        if name is not None:
            sorted_names.append(name)
    return sorted_names
