from openlibrary.core.observations import _sort_values

order_list = [3, 4, 2, 1]
values_list = [
    {'id': 1, 'name': 'order'},
    {'id': 2, 'name': 'in'},
    {'id': 3, 'name': 'this'},
    {'id': 4, 'name': 'is'},
    {'id': 5, 'name': 'extra-ignored'},
]

print(_sort_values(order_list, values_list))
