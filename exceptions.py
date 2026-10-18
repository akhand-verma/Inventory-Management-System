"""
Custom exceptions for the Inventory Management System.
Helps handle specific errors.
"""




class InventoryError(Exception):
    """Base class for all custom errors raised by this application."""
    pass



class ProductNotFoundError(InventoryError):
    """Raised when a product id does not exist in the database."""
    def __init__(self,product_id):
        self.product_id = product_id
        super().__init__(f"Product with id {product_id} was not found.")




class InsufficientStockError(InventoryError):
    """Raised when trying to sell more units than are currently in stock."""
    def __init__(self,product_id,requested,available):
        self.product_id = product_id
        self.requested = requested
        self.available = available
        super().__init__(
        f"Cannot sell {requested} units of product {product_id}; "
        f"only {available} in stock."
    )




class InvalidQuantityError(InventoryError):
    """Raised when a quantity or price value is invalid (e.g. negative)."""
    pass



class DatabaseConnectionError(InventoryError):
     """Raised when the app cannot connect to the PostgreSQL database."""
     pass
    

