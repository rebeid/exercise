#!/usr/bin/python
# -*- coding: utf-8 -*-
from exercise import *

if __name__ == '__main__':

    # Set to True for detailed output, False for simple output
    show_details = False

    # Baseline data
    initial_inventory = {'A': 150, 'B': 150, 'C': 100, 'D': 100, 'E': 200}

    # Initialization
    inventory = Inventory()
    inventory.add(initial_inventory)
    src = DataSource(inventory.get_product_names(), min=1, max=5)
    me = InventoryAllocator(inventory, min=1, max=5)
    results = []

    if show_details:
        print('Initial Inventory:')
        inventory.display()

    # Generate 150 streams of orders
    for i in range(150):
        src.generate_stream()

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
