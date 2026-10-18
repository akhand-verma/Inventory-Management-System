# Inventory Management System (Small Shop)

A command-line application that helps a small shop owner keep track of products and stock.
It stores everything in a **PostgreSQL** database, lets you sell / restock / search products,
warns you about low or expired stock, keeps a full transaction history, and produces a
**CSV report** and a **bar chart (PNG)** of stock value by category.

Individual project, written in Python.

---

## 1. What does it do?

| Menu option | What it does |
|---|---|
| 1. Add product | Adds a new product (name, category, price, quantity, optional expiry date). Logs an `initial_stock` transaction. |
| 2. Sell product | Reduces stock by the quantity sold. Refuses if there is not enough stock. Logs a `sale`. |
| 3. Restock product | Increases stock when a new delivery arrives. Logs a `restock`. |
| 4. Delete product | Removes a product by its id. |
| 5. View all products | Lists every product. |
| 6. Search products | Case-insensitive search of product names by keyword. |
| 7. Low stock alerts | Lists products at or below the low-stock threshold (default 10) and expired perishable items, plus the set of affected categories. |
| 8. Total inventory value | Sum of `price x quantity` for all products. |
| 9. Transaction history | Full audit log of initial stock, sales and restocks, newest first. |
| 10. Category summary report | Groups products by category: item count, total units, total value. |
| 11. Export report to CSV | Saves `data/inventory_report.csv` and a chart `data/inventory_by_category.png`. If there are no products, old report files are removed. |
| 0. Exit | Closes the database connection and quits. |

Products and transactions are saved in the database, so they are still there the next time you open the program.
The two files from option 11 are a **snapshot** of the moment you ran it; run option 11 again to refresh them.

---

## 2. Project structure

```
Inventory Management System (small shop)/
├── cli.py          # Terminal menu (entry point) - run this file
├── inventory.py    # Inventory class: business logic (sell, restock, alerts, ...)
├── db.py           # Database class: the ONLY file that runs SQL (psycopg2)
├── models.py       # Product and PerishableProduct classes
├── reports.py      # pandas analysis, CSV export, matplotlib chart
├── exceptions.py   # Custom exception classes
├── config.py       # Reads settings from the .env file
├── .env            # Your database login details (not committed to git)
├── .gitignore
└── data/           # Created automatically; holds the CSV and PNG from option 11
```

---

## 3. How to set it up and use it

### Requirements
- Python 3.10 or newer
- PostgreSQL installed and running
- Python packages:

```
pip install psycopg2-binary python-dotenv pandas matplotlib
```

### Step 1 - Create the database and tables
In pgAdmin or `psql`, create a database called `inventory_db` and run:

```sql
CREATE TABLE categories (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    price       NUMERIC(10,2) NOT NULL,
    quantity    INTEGER NOT NULL,
    expiry_date DATE
);

CREATE TABLE transactions (
    id         SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    action     VARCHAR(50) NOT NULL,
    quantity   INTEGER NOT NULL,
    timestamp  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

(Use the same table and column names your database already has; the code expects exactly these.)

### Step 2 - Create the `.env` file
Put a file named `.env` in the project folder:

```
DB_NAME=inventory_db
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432
LOW_STOCK_THRESHOLD=10
```

Never share this file or upload it to GitHub (it is already listed in `.gitignore`).

### Step 3 - Run
Open a terminal **in the project folder** (or use the Run button in VS Code) and run:

```
python cli.py
```

Type the number of an option and press Enter. Choose `0` to exit.
If you see "Could not connect to database", make sure PostgreSQL is running and the `.env` details are correct.

### Example session
```
Choose an option: 1
Name: Apple Juice
Category: Drink
Price: 20
Quantity: 7
Expiry date (YYYY-MM-DD, leave blank if not perishable): 2027-10-09
Added product #4.

Choose an option: 2
Product id: 4
Quantity sold: 2
Sold. Remaining stock: 5
```

---

## 4. Programming concepts used (and where, why, how)

The project demonstrates all of the following concepts.

### 1. Control flow (loops and conditionals) used non-trivially
- **Where:** `cli.py`, function `main()`.
- **How:** A `while True` loop keeps the menu running until the user chooses `0` (`break`). Inside it, a long `if / elif / else` chain sends each menu choice to the right action. Option 1 has nested conditionals (blank expiry date -> skip; invalid date -> warn and save without expiry). Option 7 branches on whether any low-stock items exist, and option 11 branches on whether the product list is empty, with a `for` loop that deletes stale files.
- **Also:** `prompt_int()` and `prompt_float()` use `while True` loops that keep asking until the input is valid.
- **Why:** The program must keep running, react to different choices, and refuse bad input rather than crash.

### 2. Functions with meaningful parameters and return values
- **Where:** `cli.py` (`prompt_int(message)`, `prompt_float(message)`), `reports.py` (`products_to_dataframe(rows)`, `category_summary(df)`, `top_products(df, n=5)`, `export_to_csv(df, path)`, `plot_stock_by_category(summary_df, path)`), and the methods in `inventory.py` and `db.py`.
- **How:** Each function does one job, takes what it needs as parameters and returns a result. For example `sell_product(product_id, quantity)` returns the new stock level, `get_low_stock_alerts(threshold)` returns two values (the low-stock list and the set of categories), and `export_to_csv(df, path)` returns the path it saved to. `top_products` has a default parameter `n=5`.
- **Why:** Small, reusable functions keep the code readable and easy to test.

### 3. Data structures (lists, dictionaries, tuples, sets) used purposefully
- **Tuples:** Database rows come back from PostgreSQL as tuples `(id, name, category, price, quantity, expiry_date)` and are unpacked in `Product.from_row()`. `get_low_stock_alerts()` returns a tuple of `(list, set)`.
- **Lists:** `inventory.py` builds lists of `Product` objects and the `low_stock` list with list comprehensions. `reports.py` has the `PRODUCT_COLUMNS` list.
- **Dictionaries:** `config.py` defines `DB_CONFIG`, a dictionary of connection settings, passed to `psycopg2.connect(**self.config)`.
- **Sets:** `affected_categories = {p.category for p in low_stock}` in `inventory.py` uses a set so a category that has several low-stock items is only listed once.
- **Why:** Each structure is chosen for what it does best: tuples for fixed rows, lists for ordered collections, a dictionary for named settings, a set for unique values.

### 4. File handling (text / CSV)
- **Where:** `reports.py` -> `export_to_csv()` and `plot_stock_by_category()`; `cli.py` -> option 11; `config.py` -> reads `.env`.
- **How:** Option 11 writes `inventory_report.csv` with `df.to_csv()`, creates the `data/` folder if it does not exist (`os.makedirs`), saves a PNG chart with `fig.savefig()`, and deletes old files with `os.remove()` when there are no products. `DATA_DIR` is built from `__file__` so the files are always saved inside the project folder, wherever the program is run from. `config.py` reads the `.env` settings file using `python-dotenv`.
- **Why:** The shop owner gets a report they can open in Excel and keep after the program is closed.

### 5. Exception handling
- **Where:** `exceptions.py`, `db.py`, `inventory.py`, `cli.py`.
- **How:**
  - `exceptions.py` defines custom exceptions: `InventoryError` (base), `ProductNotFoundError`, `InsufficientStockError`, `InvalidQuantityError`, `DatabaseConnectionError`.
  - `db.py` wraps `psycopg2.connect` in `try / except` and raises `DatabaseConnectionError`; `update_stock` and `delete_product` raise `ProductNotFoundError` when no row is affected.
  - `inventory.py` raises `InvalidQuantityError` and `InsufficientStockError` for bad quantities or overselling.
  - `cli.py` catches `InventoryError` around the whole menu (`except InventoryError as e: print(...)`), so a mistake shows a friendly message instead of crashing. `ValueError` is caught in `prompt_int`, `prompt_float` and the date parsing. A `try / finally` block always closes the database connection.
- **Why:** Typing a wrong id, selling too much stock or entering text instead of a number should never crash the shop's program.

### 6. Object-Oriented Programming (classes, encapsulation, inheritance)
- **Classes:** `Database` (db.py), `Inventory` (inventory.py), `Product` and `PerishableProduct` (models.py), and the custom exception classes.
- **Encapsulation:** In `Product`, `price` and `quantity` are stored in private attributes (`_price`, `_quantity`) and accessed through `@property` getters and setters, which reject negative values and convert to the right type.
- **Inheritance:** `PerishableProduct` extends `Product`, adds `expiry_date` and `is_expired()`, and **overrides** `is_low_stock()` so expired items always count as needing attention. The custom exceptions also inherit from `InventoryError`.
- **Other OOP ideas:** a `@classmethod` factory, `Product.from_row()`, returns a `PerishableProduct` when the row has an expiry date and a normal `Product` otherwise. `__repr__` gives readable output.
- **Separation of jobs:** `Database` is the only class that writes SQL; `Inventory` holds the shop rules and uses a `Database` object.

### 7. Modules / packages (self-written across multiple files)
- **Where:** the whole project.
- **How:** The code is split into seven modules (`cli`, `inventory`, `db`, `models`, `reports`, `exceptions`, `config`), each with one responsibility, and they import from each other (for example `from db import Database`, `from inventory import Inventory`, `import reports`). Imports are organised at the top of each file.
- **Why:** Smaller files are easier to understand, change and debug than one huge script.

### 8. Standard / third-party libraries that process the data
- **pandas** (`reports.py`): converts database rows into a DataFrame, adds a calculated `total_value` column, then uses `groupby`, `agg` (count, sum), `sort_values` and `reset_index` to build the category summary and `sort_values().head(n)` for top products. This transforms the data rather than just printing it.
- **matplotlib** (`reports.py`): turns the summary into a bar chart PNG.
- **psycopg2** (`db.py`): connects to PostgreSQL and runs parameterised SQL queries (`%s` placeholders, which protect against SQL injection).
- **python-dotenv** (`config.py`): loads secrets from `.env`.
- **Standard library:** `datetime` (parses expiry dates, checks `date.today()`), `os` (paths, folders, deleting files).

### 9. Docstrings and comments
- Every module starts with a docstring explaining its purpose, and the classes and functions have docstrings describing what they do, what they return and what errors they raise (for example `sell_product` lists `ProductNotFoundError`, `InvalidQuantityError`, `InsufficientStockError`).
- Inline comments explain the less obvious choices, such as why a set is used for categories and what exceptions are caught in `cli.py`.

---

## 5. Notes
- Low-stock threshold is set in `.env` (`LOW_STOCK_THRESHOLD`, default 10).
- Money is shown as plain numbers (no currency symbol).
- Author: Akhand Verma
