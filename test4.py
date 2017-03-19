#!/usr/bin/python
from exercise2 import *

# Set to True for detailed output, False for simple output
show_details = False

# Test data
initial_inventory = {'A': 150, 'B': 150, 'C': 100, 'D': 100, 'E': 200}

# Initialization
src = DataSource()
inv = Inventory()
inv.add(initial_inventory)
me = InventoryAllocator(inv, 1, 5)
processing_results = []

if show_details:
    print('Initial Inventory:')
    inv.display()

# Create 150 orders
src.create_orders(inv.get_item_list(), 1, 5, 150)

# Process orders; stop once inventory is empty
for order in src.get_orders():
    if inv.is_empty():
        break
    result = me.process(src.to_json(order))
    if result:
        processing_results.append(result)

if show_details:
    print('Input:')
    print(''.join(src.to_json(order) for order in src.get_orders()))
    print('Output:')

# Output processing results
print(''.join(result for result in processing_results))
