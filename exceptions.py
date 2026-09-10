"""
Custom exceptions for the Inventory Management System.
Helps handle specific errors.
"""



"""Base class for all custom errors raised by this application."""
class InventoryError(Exception):
    pass



"""Raised when a product id does not exist in the database."""
class ProductNotFoundError(InventoryError):
    def __init__(self,product_id):
        self.product_id = product_id
        super().__init__(f"Product with id {product_id} was not found.")



"""Raised when trying to sell more units than are currently in stock."""
class InsufficientStockError(InventoryError):
    def __init__(self,product_id,requested,available):
        self.product_id = product_id
        self.requested = requested
        self.available = available
        super().__init__(
        f"Cannot sell {requested} units of product {product_id}; "
        f"only {available} in stock."
    )



"""Raised when a quantity or price value is invalid (e.g. negative)."""
class InvalidQuantityError(InventoryError):
    pass


"""Raised when the app cannot connect to the PostgreSQL database."""
class DatabaseConnectionError(InventoryError):
     pass
    

