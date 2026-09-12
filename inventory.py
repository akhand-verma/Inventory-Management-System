"""
The Inventory class contains all the BUSINESS LOGIC of the shop
(selling, restocking, searching, low-stock alerts). It uses a
Database instance for persistence, but never writes SQL itself --
that separation keeps each class focused on one job.
"""
from models import Product
from exceptions import (
    InsufficientStockError,
    InvalidQuantityError,
    ProductNotFoundError,
)

class Inventory:
    """Operations on the shop's inventory."""


    def __init__(self,db):
        self.db = db # a Database instance 


    def add_product(self, name, category, price, quantity, expiry_date=None):
      """
      Add a brand-new product to the shop.
      Returns: the new product's database id.
      Raises: InvalidQuantityError if price/quantity are invalid.
    """
      if(price<0 or quantity<0):
        raise InvalidQuantityError("Price and quantity must be >= 0.")
      product_id = self.db.add_product(name, category, price, quantity, expiry_date)
      self.db.log_transaction(product_id, "initial_stock", quantity)
      return product_id


    def sell_product(self, product_id, quantity):
        """
        Sell `quantity` units of a product, decreasing stock.
        Raises:
            ProductNotFoundError      if the id doesn't exist
            InvalidQuantityError      if quantity <= 0
            InsufficientStockError    if not enough stock is available
        """
        if quantity <= 0:
            raise InvalidQuantityError("Sale quantity must be positive.")

        row = self.db.get_product(product_id)
        if row is None:
            raise ProductNotFoundError(product_id)

        current_qty = row[4]
        if quantity > current_qty:
            raise InsufficientStockError(product_id, quantity, current_qty)

        new_qty = current_qty - quantity
        self.db.update_stock(product_id, new_qty)
        self.db.log_transaction(product_id, "sale", quantity)
        return new_qty

    def restock_product(self, product_id, quantity):
        """Add `quantity` units back into stock (e.g. new delivery arrives)."""
        if quantity <= 0:
            raise InvalidQuantityError("Restock quantity must be positive.")

        row = self.db.get_product(product_id)
        if row is None:
            raise ProductNotFoundError(product_id)

        new_qty = row[4] + quantity
        self.db.update_stock(product_id, new_qty)
        self.db.log_transaction(product_id, "restock", quantity)
        return new_qty

    def delete_product(self, product_id):
        """Remove a product entirely from the inventory."""
        self.db.delete_product(product_id)

    def search(self, keyword):
        """Return all products whose name contains `keyword`."""
        return self.db.search_products(keyword)

    def all_products(self):
        """Return every product currently in the inventory."""
        return self.db.get_all_products()

    def get_low_stock_alerts(self, threshold=10):
        """
        Return a list of products at/below `threshold`, and the SET
        of unique categories affected (a set is used here purposefully
        to avoid duplicate category names when many low-stock items
        share a category).
        """
        products = [Product.from_row(row) for row in self.db.get_all_products()]
        low_stock = [p for p in products if p.is_low_stock(threshold)]
        affected_categories = {p.category for p in low_stock}
        return low_stock, affected_categories

    
    def calculate_total_value(self):
        """Return the total monetary value (price * quantity) of all stock."""
        products = [Product.from_row(row) for row in self.db.get_all_products()]
        return round(sum(p.total_value() for p in products), 2)

    def transaction_history(self):
        """Return the full audit log of sales/restocks."""
        return self.db.get_transactions()
