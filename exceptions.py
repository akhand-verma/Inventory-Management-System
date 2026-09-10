"""
Custom exceptions for the Inventory Management System.
Helps handle specific errors.
"""

class InventoryError(Exception):
    pass


class ProductNotFoundError(InventoryError):
    def __init__(self,product_id):
        self.product_id = product_id
        super().__init__(f"Product with id {product_id} was not found.")

class InsufficientStockError(InventoryError):
    def __init__(self,product_id,requested,available):
        self.product_id = product_id
        self.requested = requested
        self.available = available
        super().__init__(
            f"Cannot sell {requested} units of product {product_id}; "
            f"only {available} in stock."
        )
class InvalidQuantityError(InventoryError):
    pass

class DatabaseConnectionError(InventoryError):
    pass
    

