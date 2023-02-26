"""Contains Item class

:return: Item object instance
:rtype: object
"""


class Item:

    items_dict = {}

    def __init__(self, name, quantity):
        self.name = name
        self.quantity = quantity
        Item.items_dict[self.name] = self

    def update_quantity(self, new_quantity):
        self.quantity = new_quantity

    def __str__(self):
        list_name = self.name + ":" + " " + self.quantity
        return list_name

    def rename(self, new_name):
        del Item.items_dict[self.name]
        self.name = new_name
        Item.items_dict[self.name] = self

    def __repr__(self):
        return f"{self.name}"
