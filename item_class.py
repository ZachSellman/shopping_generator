"""Contains Item class

:return: Item object instance
:rtype: object
"""


class Item:
    """Item objects track attributes like name, quantity for grocery items"""

    items_dict = {}

    def __init__(self, name, quantity):
        """Constructor method

        :param name: name of item
        :type name: str
        :param quantity: quantity of item
        :type quantity: str
        """
        self.name = name
        self.quantity = quantity
        Item.items_dict[self.name] = self

    def update_quantity(self, new_quantity):
        """Updates quantity attribute of the item

        :param new_quantity: new quantity value
        :type new_quantity: str
        """
        self.quantity = new_quantity

    def __str__(self):
        """String representation of object

        :return: formatted str for ListBox window
        :rtype: str
        """
        list_name = self.name + ":" + " " + self.quantity
        return list_name

    def rename(self, new_name):
        """Updates name of item

        :param new_name: new name
        :type new_name: str
        """
        del Item.items_dict[self.name]
        self.name = new_name
        Item.items_dict[self.name] = self

    def __repr__(self):
        return f"{self.name}"
