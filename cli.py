"""
A simple terminal menu for the Inventory Management System.
Demonstrates non-trivial control flow (a menu loop with branching
and nested validation) and exception handling around user input.
"""
import reports
from db import Database
from inventory import Inventory
from exceptions import InventoryError
from config import LOW_STOCK_THRESHOLD

MENU = """
𝐼𝓃𝓋𝑒𝓃𝓉𝑜𝓇𝓎 𝑀𝒶𝓃𝒶𝑔𝑒𝓂𝑒𝓃𝓉 𝒮𝓎𝓈𝓉𝑒𝓂
1. Add product
2. Sell product
3. Restock product
4. Delete product
5. View all products
6. Search products
7. Low stock alerts
8. Total inventory value
9. Transaction history
10. Category summary report
11. Export report to CSV
0. Exit
"""


def prompt_int(message):
    """Keep asking until the user types a valid integer."""
    while True:
        try:
            return int(input(message))
        except ValueError:
            print("Please enter a whole number.")


def prompt_float(message):
    """Keep asking until the user types a valid number."""
    while True:
        try:
            return float(input(message))
        except ValueError:
            print("Please enter a valid price (e.g. 67.69).")


def main():
    db = Database()
    inv = Inventory(db)

    try:
        while True:
            print(MENU)
            choice = input("Choose an option: ").strip()

            try:
                if choice == "1":
                    name = input("Name: ")
                    category = input("Category: ")
                    price = prompt_float("Price: ")
                    qty = prompt_int("Quantity: ")
                    pid = inv.add_product(name, category, price, qty)
                    print(f"Added product #{pid}.")

                elif choice == "2":
                    pid = prompt_int("Product id: ")
                    qty = prompt_int("Quantity sold: ")
                    remaining = inv.sell_product(pid, qty)
                    print(f"Sold. Remaining stock: {remaining}")

                elif choice == "3":
                    pid = prompt_int("Product id: ")
                    qty = prompt_int("Quantity restocked: ")
                    remaining = inv.restock_product(pid, qty)
                    print(f"Restocked. New stock: {remaining}")

                elif choice == "4":
                    pid = prompt_int("Product id to delete: ")
                    inv.delete_product(pid)
                    print("Deleted.")

                elif choice == "5":
                    for p in inv.all_products():
                        print(p)

                elif choice == "6":
                    keyword = input("Search keyword: ")
                    for p in inv.search(keyword):
                        print(p)

                elif choice == "7":
                    low, categories = inv.get_low_stock_alerts(LOW_STOCK_THRESHOLD)
                    if not low:
                        print("No low stock items.")
                    else:
                        print(f"{len(low)} low-stock item(s) in categories: {categories}")
                        for p in low:
                            print(p)

                elif choice == "8":
                    print(f"Total inventory value: {inv.calculate_total_value()}")

                elif choice == "9":
                    for t in inv.transaction_history():
                        print(t)

                elif choice == "10":
                    df = reports.products_to_dataframe(inv.all_products())
                    if df.empty:
                        print("No products yet.")
                    else:
                        summary = reports.category_summary(df)
                        print(summary)

                elif choice == "11":
                    df = reports.products_to_dataframe(inv.all_products())
                    path = reports.export_to_csv(df, "data/inventory_report.csv")
                    print(f"Report saved to {path}")
                elif choice == "0":
                    print("𝔾𝕠𝕠𝕕𝕓𝕪𝕖!")
                    break  
                              
                else:
                    print("Invalid option, try again.")

            except InventoryError as e:
                # Catches ProductNotFoundError, InsufficientStockError, etc.
                print(f"Error: {e}")

    finally:
        db.close()
