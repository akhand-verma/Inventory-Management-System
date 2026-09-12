"""
Turns raw product/transaction rows into analysis, using pandas to
TRANSFORM the data (group, aggregate, sort) -- not just display it.
Also handles CSV export and a matplotlib chart.
"""

import pandas as pd
import matplotlib.pyplot as plt

PRODUCT_COLUMNS = ["id","name","category","price","quantity"]

def products_to_dataframe(rows):
    """Convert raw (id, name, category, price, quantity) tuples to a DataFrame."""
    df = pd.DataFrame(rows,columns=PRODUCT_COLUMNS)
    df["total_value"] = df["price"]*df["quantity"]
    return df

def category_summary(df):
    """
    Group products by category and aggregate: item count, total units,
    and total monetary value per category.
    """
    summary = (
        df.groupby("category")
        .agg(
            item_count=("id", "count"),
            total_units=("quantity", "sum"),
            total_value=("total_value", "sum"),
        )
        .sort_values("total_value", ascending=False)
        .reset_index()
    )
    return summary

def top_products(df,n=5):
    """Return the n most valuable products (price * quantity)."""
    return df.sort_values("total_value", ascending=False).head(n)

def export_to_csv(df, path):
    """Write a DataFrame out to a CSV file for the shop owner to keep."""
    df.to_csv(path, index=False)
    return path


def plot_stock_by_category(summary_df, path):
    """Save a bar chart of total stock value per category as a PNG."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(summary_df["category"], summary_df["total_value"], color="#4C72B0")
    ax.set_xlabel("Category")
    ax.set_ylabel("Total Stock Value")
    ax.set_title("Inventory Value by Category")
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return path
