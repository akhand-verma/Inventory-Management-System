"""
models.py
Defines the data model classes used across the application:
    Product -- base class for any item in the inventory
    PerishableProduct -- subclass for items that can expire
These classes demonstrate OOP concepts: encapsulation (private attrs
with validated properties) and inheritance (PerishableProduct extends
Product and overrides behaviour).
"""

from datetime import date
from exceptions import InvalidQuantityError




"""
Represents a single product/item in the shop's inventory.
Attributes are encapsulated behind properties so that invalid
values (negative price/quantity) can never be set directly.
"""
class Product:
    def __init__(self, name, category, price, quantity, product_id=None):
        self.id = product_id        
        self.name = name
        self.category = category
        self.price = price            
        self.quantity = quantity     

    # ---- encapsulated price ----
    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if value < 0:
            raise InvalidQuantityError("Price cannot be negative.")
        self._price = round(float(value), 2)

    # ---- encapsulated quantity ----
    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        if value < 0:
            raise InvalidQuantityError("Quantity cannot be negative.")
        self._quantity = int(value)

    def total_value(self):
        """Return price * quantity for this product (used in reports)."""
        return round(self.price * self.quantity, 2)

    def is_low_stock(self, threshold):
        """Return True if quantity has fallen at/below the given threshold."""
        return self.quantity <= threshold

    def __repr__(self):
        return f"<Product id={self.id} name={self.name!r} qty={self.quantity}>"



"""
A Product that also has an expiry date (e.g. food, cosmetics).
Demonstrates inheritance: reuses everything from Product but adds
expiry-specific data and overrides is_low_stock() with an extra
safety rule (treat expired stock as effectively "low/unusable").
"""
class PerishableProduct(Product):
    def __init__(self, name, category, price, quantity, expiry_date, product_id=None):
        super().__init__(name, category, price, quantity, product_id)
        self.expiry_date = expiry_date  # a datetime.date
    def is_expired(self):
        """Return True if today's date is past the expiry date."""
        return date.today() > self.expiry_date
    def is_low_stock(self, threshold):
        """Override: expired stock always counts as low/needs attention."""
        return self.is_expired() or super().is_low_stock(threshold)

    def __repr__(self):
        return (f"<PerishableProduct id={self.id} name={self.name!r} "
                f"qty={self.quantity} expires={self.expiry_date}>")

