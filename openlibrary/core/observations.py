"""Module for handling patron observation functionality"""

import requests

from infogami import config
from openlibrary import accounts
from . import cache

# URL for TheBestBookOn
TBBO_URL = config.get('tbbo_url')


def _sort_values(order_list, values_list):
    """
    Sort and filter value names based on a specified order list.
    
    This is a pure function that returns a list of value names ordered by
    the IDs specified in order_list. It ignores IDs in order_list that don't
    exist in values_list, and excludes values whose IDs are not in order_list.
    
    Args:
        order_list: A list of integer IDs representing the desired order
        values_list: A list of dictionaries with 'id' and 'name' keys
        
    Returns:
        A list of names (strings) ordered by the IDs in order_list
        
    Example:
        >>> order_list = [3, 4, 2, 1]
        >>> values_list = [
        ...     {'id': 1, 'name': 'order'},
        ...     {'id': 2, 'name': 'in'},
        ...     {'id': 3, 'name': 'this'},
        ...     {'id': 4, 'name': 'is'}
        ... ]
        >>> _sort_values(order_list, values_list)
        ['this', 'is', 'in', 'order']
    """
    # Create a mapping from ID to name for quick lookup
    id_to_name = {value['id']: value['name'] for value in values_list}
    
    # Build the result list by iterating through order_list
    # Only include names for IDs that exist in values_list
    result = []
    for id_val in order_list:
        if id_val in id_to_name:
            result.append(id_to_name[id_val])
    
    return result


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
