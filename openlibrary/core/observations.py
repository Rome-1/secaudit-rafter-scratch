"""Module for handling patron observation functionality"""

import requests

from infogami import config
from openlibrary import accounts
from . import cache

# URL for TheBestBookOn
TBBO_URL = config.get('tbbo_url')



def _sort_values(order_list, values_list):
    """Return list of value names ordered exactly by the IDs in order_list.

    - Unknown IDs in order_list are ignored.
    - Values in values_list whose IDs are not in order_list are excluded.
    - Pure function: no mutation, no I/O.

    Parameters:
        order_list (list[int]): Desired ordering of IDs.
        values_list (list[dict]): Each dict has keys 'id' and 'name'.

    Returns:
        list[str]: Names corresponding to IDs in order_list, in order.
    """
    # Build a mapping of id -> name. If duplicate IDs appear, prefer the first
    # occurrence to avoid unexpected overrides based on later entries.
    id_to_name = {}
    for v in values_list or []:
        # Be defensive: skip malformed entries gracefully
        if not isinstance(v, dict):
            continue
        if 'id' not in v or 'name' not in v:
            continue
        vid = v['id']
        if vid not in id_to_name:
            id_to_name[vid] = v['name']

    # Produce names in the exact order specified by order_list, skipping
    # any IDs not present in id_to_name.
    return [id_to_name[i] for i in (order_list or []) if i in id_to_name]

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
