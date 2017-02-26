#!/usr/bin/python
# -*- coding: utf-8 -*-
from exercise import *

if __name__ == '__main__':

    # Set to True for detailed output, False for simple output
    show_details = False

    # Baseline data
    initial_inventory = {'A': 2, 'B': 3, 'C': 1, 'D': 0, 'E': 0}
    unformatted_lines = [{'F': 1},
                         {'A': 1, 'C': 1},
                         {'E': 5},
                         {'C': 6},
                         {'B': 0, 'D': 4, 'F': 2},
                         {'E': 0},
                         {'A': 1, 'B': 6, 'C': 1},
                         {'A': 6, 'B': 3},
                         {'D': 4},
                         {'C': 0},
                        ]

    # Initialization
    inventory = Inventory()
    inventory.add(initial_inventory)
    src = DataSource(inventory.get_product_names(), min=1, max=5)
    me = InventoryAllocator(inventory, min=1, max=5)
    results = []

    if show_details:
        print('Initial Inventory:')
        inventory.display()

    # Generate streams of orders based on the above lines data
    for x in unformatted_lines:
        src.generate_stream(x)

    if show_details:
        print('\nInput:')
        print(src.get_io().getvalue())

    # Simulate inbound orders and process them; stop once inventory is empty
    src.get_io().seek(0)
    for order in src.get_io():
        if inventory.is_empty():
            break
        result = me.process(order)
        if len(result) > 0:
            results.append(result)

    # Output the processing results
    if show_details:
        print('Output:')
    print('\n'.join('{0}'.format(s) for s in results))

    src.get_io().close()
