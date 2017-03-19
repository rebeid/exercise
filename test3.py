#!/usr/bin/python
from exercise2 import *

# Set to True for detailed output, False for simple output
show_details = False

# Test data
initial_inventory = {'E': 0, 'D': 0, 'C': 1, 'B': 3, 'A': 2}
line_data = [{'A': 1, 'C': 1},
             {'E': 5},
             {'D': 4},
             {'A': 1, 'C': 1},
             {'B': 3},
             {'D': 4},
            ]

# Initialization
src = DataSource()
inv = Inventory()
inv.add(initial_inventory)
me = InventoryAllocator(inv, 1, 5)
processing_results = []

if show_details:
    print('Initial Inventory:')
    inv.display()

# Create orders based on the above data
for data in line_data:
    src.create_order(data)

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
