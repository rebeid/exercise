#!/usr/bin/python
from exercise2 import *
import json

# Set to True for detailed output, False for simple output
show_details = False

# Test data
initial_inventory = {'A': 15, 'B': 15, 'C': 10, 'D': 10, 'E': 20}

# Initialization
src = DataSource()
inv = Inventory()
inv.add(initial_inventory)
me = InventoryAllocator(inv, 1, 5)
processing_results = []
orders = []

if show_details:
    print('Initial Inventory:')
    inv.display()

# Create some orders
# No "Header"
orders.append(json.dumps(OrderedDict([('ID', 1), ('Lines', [{"Product": "A", "Quantity": 1}])])) + '\n')
# No "Lines"
orders.append(json.dumps(OrderedDict([('Header', 2), ('Items', [{"Product": "A", "Quantity": 1}])])) + '\n')
# Empty header
orders.append(json.dumps(OrderedDict([('Header', ''), ('Lines', [{"Product": "A", "Quantity": 1}])])) + '\n')
# Empty lines
src.create_order({}, header=3)
# Non-positive integer as header
src.create_order({'A': 1}, header=-4)
# Non-integer value as header
src.create_order({'A': 1}, header=3.14)
# String-integer as header
src.create_order({'A': 1}, header='#0005')
# Non-existent product name
src.create_order({'Yoda': 1})
# Quantity < MIN 
src.create_order({'A': 1, 'B': 0})
# Quantity > MAX 
src.create_order({'C': 6, 'D': 5})
# Existing product name in lowercase
src.create_order({'e': 3})
# Duplicate lines on the same order
src.create_order({'A': 3, 'A': 1})
# Duplicate header
src.create_order({'A': 1, 'B': 2}, header=10)
src.create_order({'C': 4, 'D': 5}, header=10)

for order in src.get_orders():
    orders.append(src.to_json(order))

# Process orders; stop once inventory is empty
for order in orders:
    if inv.is_empty():
        break
    result = me.process(order)
    if result:
        processing_results.append(result)

if show_details:
    print('Input:')
    print(''.join(order for order in orders))
    print('Output:')

# Output processing results
print(''.join(result for result in processing_results))
