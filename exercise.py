"""Exercise module."""
#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import Counter
from collections import OrderedDict
from io import StringIO
import json
import random

class DataSource(object):
    """An order generator.

    Attributes:
        io (StringIO): A text buffer
        names (list): the names of items in inventory
        min (int): the minimum quantity allowed per item per order
        max (int): the maximum quantity allowed per item per order
        total (int): the number of orders generated
    """

    def __init__(self, item_names, min, max):
        """Initialize self."""
        self.io = StringIO()
        self.item_names = item_names
        self.min = min
        self.max = max
        self.total = 0

    def get_io(self):
        """Return the text buffer."""
        return self.io

    def get_next_id(self):
        """Return a string of the next 4-digit ID."""
        return format(self.total, '04')

    def format_line(self, name, qty):
        """Format a line on the order.

        Args:
            name (str): an item name
            qty (int): order quantity
        Returns:
            OrderedDict: the formatted line
        """
        return OrderedDict([('Product', name), ('Quantity', qty)])

    def generate_stream(self, lines_data={}):
        """Generate an in-memory stream of order in JSON format.
        A random number of lines are generated if not supplied.

        Args:
            lines_data (dict): baseline data (products and their quantities)
                               for generating lines on an order (default {})
                               e.g. {'A': 1, 'B': 2}
        """
        lines = []
        if lines_data:
            # Use the supplied lines
            for name, qty in sorted(lines_data.items()):
                lines.append(self.format_line(name, qty))
        else:
            # Generate a random number of lines
            picks = []
            names = list(self.item_names)
            for i in range(random.randint(1, len(names))):
                n = random.choice(names)
                picks.append(n)
                names.remove(n)
            for name in sorted(picks):
                qty = random.randint(self.min, self.max)
                lines.append(self.format_line(name, qty))

        self.total += 1
        header = self.get_next_id()
        s = json.dumps(OrderedDict([('Header', header), ('Lines', lines)]))
        self.io.write('{0}\n'.format(s))

class Inventory(object):
    """An inventory of products.

    Attributes:
        inventory (Counter): a collection of products and their counts in stock
    """

    def __init__(self):
        """Initialize self."""
        self.inventory = Counter()

    def get_product_names(self):
        """Return a list of the names of items in inventory."""
        return self.inventory.keys()

    def add(self, products, replace=False):
        """Add one or more products to inventory.

        Args:
            products (dict): the names and counts of products
            replace (bool): Replace existing inventory if set to True (default False)
        """
        for name, count in products.items():
            if name not in self.inventory or replace:
                self.inventory[name] = count

    def remove(self, name):
        """Remove an inventory item.

        Args:
            name (str): the item name
        """
        if name in self.inventory:
            del self.inventory[name]

    def display(self):
        """Output inventory information."""
        if self.inventory:
            for name, count in sorted(self.inventory.items()):
                print('{0} x {1}'.format(name, count))

    def is_empty(self):
        """Return True if inventory is empty, False otherwise."""
        if self.inventory:
            for qty in self.inventory.values():
                if qty > 0:
                    return False
        return True

class InventoryAllocator(object):
    """An inventory allocator.

    Attributes:
        inventory (Counter): a collection of products and their counts in stock
        min (int): the minimum quantity allowed per item per order
        max (int): the maximum quantity allowed per item per order
    """

    def __init__(self, inventory, min, max):
        """Initialize self."""
        self.inventory = inventory
        self.min = min
        self.max = max

    def format_cnt(self, cnt):
        """Format counter values for output.

        Args:
            cnt (Counter): a collection of keys and their counts
        Returns:
            str: a string of sequence of quantities sorted by product name
        """
        return ','.join('{0}'.format(v) for (k, v) in sorted(cnt.items()))

    def is_valid_line(self, line):
        """Validate a line on the order.

        Args:
            line (dict): a pair of product name and quantity
        Return:
            bool: True if the line is valid, False otherwise
        """
        if 'Product' not in line.keys() or 'Quantity' not in line.keys():
            return False
        if line['Product'] not in self.inventory.get_product_names():
            return False
        if line['Quantity'] < self.min or line['Quantity'] > self.max:
            return False
        return True 

    def process(self, stream):
        """Process an inbound order; allocate inventory or place backorder.

        Args:
            stream (str): a JSON formatted stream of order
        Returns:
            str: the processing result
        """
        order = json.loads(stream)
        if 'Header' not in order.keys() or 'Lines' not in order.keys():
            return ''

        # Initialize counters ("o"rdered/"a"llocated/"b"ackordered)
        cnt_o = Counter()
        for name in self.inventory.get_product_names():
            cnt_o[name] = 0
        cnt_a = Counter(cnt_o)
        cnt_b = Counter(cnt_o)

        is_valid_order = False
        for line in order['Lines']:
            if not self.is_valid_line(line):
                continue

            is_valid_order = True
            name = line['Product']
            qty = line['Quantity']
            cnt_o[name] = qty
            diff = self.inventory.inventory[name] - qty
            if diff >= 0:
                # Allocate inventory
                cnt_a[name] = qty
                # Update inventory
                self.inventory.add({name: diff}, replace=True)
            else:
                # Place backorder
                cnt_b[name] = abs(diff)

        return '{0}: {1}::{2}::{3}'.format(order['Header'],
                                           self.format_cnt(cnt_o),
                                           self.format_cnt(cnt_a),
                                           self.format_cnt(cnt_b)
                                          ) if is_valid_order else ''

if __name__ == '__main__':
    pass
