"""
The Database class is the ONLY place in the codebase that talks
directly to PostgreSQL (via psycopg2). Every other module goes
through this class instead of writing raw SQL itself.
Keeping all SQL in one class:
:-makes the rest of the project easier to read/test
:-is a clean demonstration of OOP + a third-party library
:-makes it obvious where exception handling around the DB belongs
"""


import psycopg2
from psycopg2 import Error as PgError

from config import DB_CONFIG
from exceptions import DatabaseConnectionError, ProductNotFoundError


class Database:

    """Wraps a PostgreSQL connection and all operations."""

    def __init__(self, config=None):
        self.config = config or DB_CONFIG
        self.conn = None
        self.cur = None
        self.connect()

    def connect(self):
        """Open the connection. Raises DatabaseConnectionError on failure."""
        try:
            self.conn = psycopg2.connect(**self.config)
            self.cur = self.conn.cursor()
        except PgError as e:
            raise DatabaseConnectionError(
                f"Could not connect to database: {e}"
            )

    def close(self):
        """Close cursor and connection cleanly."""
        if self.cur:
            self.cur.close()

        if self.conn:
            self.conn.close()

    def get_or_create_category(self, name):
        """Return the id of a category, inserting it first if it doesn't exist."""

        self.cur.execute(
            "SELECT id FROM categories WHERE name = %s;",
            (name,)
        )

        row = self.cur.fetchone()

        if row:
            return row[0]

        self.cur.execute(
            "INSERT INTO categories (name) VALUES (%s) RETURNING id;",
            (name,)
        )

        self.conn.commit()

        return self.cur.fetchone()[0]

    def add_product(self, name, category, price, quantity):
        """Insert a new product row. Returns the new product's id."""

        category_id = self.get_or_create_category(category)

        self.cur.execute(
            """INSERT INTO products
               (name, category_id, price, quantity)
               VALUES (%s, %s, %s, %s)
               RETURNING id;""",
            (name, category_id, price, quantity),
        )

        self.conn.commit()

        return self.cur.fetchone()[0]

    def update_stock(self, product_id, new_quantity):
        """Set a product's quantity directly. Raises if the id doesn't exist."""

        self.cur.execute(
            "UPDATE products SET quantity = %s WHERE id = %s;",
            (new_quantity, product_id)
        )

        self.conn.commit()

        if self.cur.rowcount == 0:
            raise ProductNotFoundError(product_id)

    def delete_product(self, product_id):
        """Delete a product by id. Raises if the id doesn't exist."""

        self.cur.execute(
            "DELETE FROM products WHERE id = %s;",
            (product_id,)
        )

        self.conn.commit()

        if self.cur.rowcount == 0:
            raise ProductNotFoundError(product_id)

    def get_product(self, product_id):
        """Fetch a single product row joined with category name, or None."""

        self.cur.execute(
            """SELECT p.id, p.name, c.name, p.price, p.quantity
               FROM products p
               JOIN categories c ON p.category_id = c.id
               WHERE p.id = %s;""",
            (product_id,),
        )

        return self.cur.fetchone()

    def get_all_products(self):
        """Fetch every product row, joined with category name."""

        self.cur.execute(
            """SELECT p.id, p.name, c.name, p.price, p.quantity
               FROM products p
               JOIN categories c ON p.category_id = c.id
               ORDER BY p.id;"""
        )

        return self.cur.fetchall()

    def search_products(self, keyword):
        """Case-insensitive search of product names."""

        self.cur.execute(
            """SELECT p.id, p.name, c.name, p.price, p.quantity
               FROM products p
               JOIN categories c ON p.category_id = c.id
               WHERE p.name ILIKE %s;""",
            (f"%{keyword}%",),
        )

        return self.cur.fetchall()

    def log_transaction(self, product_id, action, quantity):
        """Insert a row into the transactions audit table."""

        self.cur.execute(
            """INSERT INTO transactions
               (product_id, action, quantity)
               VALUES (%s, %s, %s);""",
            (product_id, action, quantity),
        )

        self.conn.commit()

    def get_transactions(self):
        """Fetch full transaction history, newest first."""

        self.cur.execute(
            """SELECT t.id, p.name, t.action, t.quantity, t.timestamp
               FROM transactions t
               JOIN products p ON t.product_id = p.id
               ORDER BY t.timestamp DESC;"""
        )

        return self.cur.fetchall()