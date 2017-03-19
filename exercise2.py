"""Exercise2 module."""
#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import Counter
from collections import OrderedDict
import json
import logging
import random

class Order(object):
    """An order.

    Attributes:
        header (int): order ID
        lines (dict of str: int): lines on the order 
    """

    def __init__(self, order_id):
        """Initialize self."""
        self.header = order_id
        self.lines = {}

    def get_header(self):
        """Return the header."""
        return self.header

    def get_lines(self):
        """Return the lines on the order."""
        return self.lines

    def add_line(self, item, qty):
        """Add a line to the order.

        Args:
            item (str): product name
            qty (int): order quantity
        """
        if item not in self.lines:
            self.lines[item] = qty

class DataSource(object):
    """An order generator.

    Attributes:
        orders (list of Order objects): all orders created (since reset)
        total (int): the number of orders created (since reset)
    """

    def __init__(self):
        """Initialize self."""
        self.orders = []
        self.total = 0

    def get_orders(self):
        """Return the all orders created."""
        return self.orders

    def get_total(self):
        """Return the number of orders created."""
        return self.total

    def get_next_id(self):
        """Return the next ID."""
        return self.total + 1

    def reset_all(self):
        """Delete all orders and reset total."""
        del self.orders[:]
        self.total = 0

    def create_order(self, lines, header=None):
        """Create an order based on the given header and lines. 
        A header (= order ID) is assigned if not given.

        Args:
            lines (dict of str: int): lines on the order 
            header (int): order ID (default None)
        """
        order = Order(self.get_next_id() if not header else header)
        if lines and isinstance(lines, dict):
            for item, qty in sorted(lines.items()):
                order.add_line(item, qty)
        self.orders.append(order)
        self.total += 1

    def create_orders(self, item_list, min_qty, max_qty, n=1):
        """Create n orders with random contents, where n >= 1.
        Each order contains a random number of lines [1..len(item_list)].
        Each line contains a random item (from item_list) and a random
        quantity [min_qty..max_qty].

        Args:
            item_list (list of str): product names
            min_qty (int): minimum order quantity
            max_qty (int): maximum order quantity
            n (int): the number of orders to create (default 1)
        """
        if item_list and isinstance(item_list, list) and min_qty <= max_qty and n >= 1:
            for i in range(n):
                order = Order(self.get_next_id())
                lines = {}
                names = list(item_list)
                for x in range(random.randint(1, len(names))):
                    name = random.choice(names)
                    lines[name] = random.randint(min_qty, max_qty)
                    names.remove(name)
                for item, qty in sorted(lines.items()):
                    order.add_line(item, qty)
                self.orders.append(order)
                self.total += 1

    def to_json(self, order):
        """Convert order data to JSON.

        Args:
            order (Order object): the order
        Returns:
            str: a JSON-formatted string
        """
        if order and isinstance(order, Order):
            header = order.get_header()
            original_lines = order.get_lines()
            lines = []
            for item, qty in sorted(original_lines.items()):
                lines.append(OrderedDict([('Product', item), ('Quantity', qty)]))
            return json.dumps(OrderedDict([('Header', header), ('Lines', lines)])) + '\n'

class Inventory(object):
    """An inventory of products.

    Attributes:
        inventory (dict of str: int): product names and quantities in stock
    """

    def __init__(self):
        """Initialize self."""
        self.inventory = Counter()

    def get_items(self):
        """Return the entire inventory."""
        return self.inventory

    def get_item_list(self):
        """Return a list of items in inventory."""
        return list(self.inventory.keys())

    def item_list_generator(self):
        """Return a generator for a list of items."""
        for item in self.inventory.keys():
            yield item

    def add(self, new_items, replace=False):
        """Add one or more products to inventory.

        Args:
            new_items (dict of str: int): new items to add to inventory
            replace (bool): replace existing data if set to True (default False)
        """
        if new_items and isinstance(new_items, dict):
            for item, qty in new_items.items():
                if item not in self.inventory or replace:
                    self.inventory[item] = qty

    def remove(self, item):
        """Remove a product from inventory.

        Args:
            item (str): product name
        """
        self.inventory.pop(item, None)

    def display(self):
        """Output inventory information."""
        if self.inventory:
            for item, qty in sorted(self.inventory.items()):
                print('{0} x {1}'.format(item, qty))
            print()

    def is_empty(self):
        """Return True if inventory is empty."""
        if self.inventory:
            for qty in self.inventory.values():
                if qty > 0:
                    return False
        return True

class InventoryAllocator(object):
    """An inventory allocator.

    Attributes:
        inventory (Inventory object): inventory data
        min_qty (int): the minimum order quantity per line
        max_qty (int): the maximum order quantity per line
        total (int): successful processing count
        log (str): log filename
    """

    def __init__(self, inventory, min_qty, max_qty, logfile='result.log'):
        """Initialize self."""
        self.inventory = inventory
        self.min = min_qty
        self.max = max_qty
        self.total = 0
        self.logfile= logfile
        logging.basicConfig(format='%(asctime)s: %(message)s',
                            filename=logfile,
                            filemode='w',
                            level=logging.INFO)

    def get_total(self):
        """Return the number of valid orders processed."""
        return self.total

    def get_log_name(self):
        """Return the name of log file."""
        return self.logfile

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
            line (dict of str: int): a line on the order
        Return:
            bool: True if the line is valid, False otherwise
        """
        if 'Product' not in line or 'Quantity' not in line:
            return False
        if line['Product'] not in self.inventory.get_item_list():
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
        if 'Header' not in order or 'Lines' not in order:
            logging.warning('[Invalid]: {0}'.format(stream.strip()))
            return ''

        # Initialize counters ("o"rdered/"a"llocated/"b"ackordered)
        cnt_o = Counter()
        for name in self.inventory.item_list_generator():
            cnt_o[name] = 0
        cnt_a = Counter(cnt_o)
        cnt_b = Counter(cnt_o)

        is_valid_order = False

        if isinstance(order['Header'], (int, float)):
            if order['Header'] < 1 or isinstance(order['Header'], float):
                logging.warning('[Invalid]: {0}'.format(stream.strip()))
                return ''
        else:
            logging.warning('[Invalid]: {0}'.format(stream.strip()))
            return ''

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

        if is_valid_order:
            self.total += 1
            result = '{0}: {1}::{2}::{3}\n'.format(order['Header'],
                                            self.format_cnt(cnt_o),
                                            self.format_cnt(cnt_a),
                                            self.format_cnt(cnt_b))
            logging.info(result.strip())
            return result
        else:
            logging.warning('[Invalid]: {0}'.format(stream.strip()))
            return ''

if __name__ == '__main__':
    pass
