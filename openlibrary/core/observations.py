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

def _sort_values(order_list, values_list):
    """
    Sort values by the order specified in order_list.
    
    Args:
        order_list (list): List of integer IDs representing the desired display order
        values_list (list): List of dictionaries with 'id' and 'name' keys
        
    Returns:
        list: List of value names ordered exactly as specified in order_list
        
    Rules:
        - Returns names ordered exactly as in order_list
        - Ignores IDs in order_list that are not found in values_list (no errors)
        - Excludes values whose IDs are not included in order_list
        - Pure function with no side effects
    """
    # Create a mapping from ID to name for quick lookup
    id_to_name = {value['id']: value['name'] for value in values_list}
    
    # Build result list by iterating through order_list and looking up names
    result = []
    for id_val in order_list:
        if id_val in id_to_name:
            result.append(id_to_name[id_val])
    
    return result


@cache.memoize(engine="memcache", key="tbbo_aspects", expires=config.get('tbbo_aspect_cache_duration'))
def get_aspects():
    response = requests.get(TBBO_URL + '/api/aspects')

    return response.text
