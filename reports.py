"""
Turns raw product/transaction rows into analysis, using pandas to
TRANSFORM the data (group, aggregate, sort) -- not just display it.
Also handles CSV export and a matplotlib chart.
"""

import os

import matplotlib
matplotlib.use("Agg")        
import matplotlib.pyplot as plt
import pandas as pd


PRODUCT_COLUMNS = ["id", "name", "category", "price", "quantity", "expiry_date"]
TRANSACTION_COLUMNS = ["id", "product", "category", "action", "quantity", "timestamp", "price"]
ACTION_COLORS = {
    "sale": "#DD8452",
    "restock": "#55A868",
    "initial_stock": "#4C72B0",
}
FALLBACK_COLOR = "#999999"

def products_to_dataframe(rows):
    """Convert raw (id, name, category, price, quantity) tuples to a DataFrame."""
    df = pd.DataFrame(rows,columns=PRODUCT_COLUMNS)
    df["price"] = df["price"].astype(float)
    df["total_value"] = df["price"] * df["quantity"]
    return df


def transactions_to_dataframe(rows):
    """
    Convert (id, product, category, action, quantity, timestamp, price)
    tuples to a DataFrame, adding value = price * quantity per transaction.
    """
    df = pd.DataFrame(rows, columns=TRANSACTION_COLUMNS)
    df["price"] = df["price"].astype(float)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["value"] = df["price"] * df["quantity"]
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
    os.makedirs(os.path.dirname(path), exist_ok=True)   # <-- add this line
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


def _save(fig, path):
    """Tidy, save and close a figure. Every chart function ends with this."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def _top_n_with_other(series, n=6):
    """Keep the n biggest slices and fold the rest into one 'Other' slice."""
    series = series.sort_values(ascending=False)
    if len(series) <= n:
        return series
    top = series.iloc[:n].copy()
    top["Other"] = series.iloc[n:].sum()
    return top


# ----------------------------------------------------------------------
# New charts (each returns the saved path, or None if there is no data)
# ----------------------------------------------------------------------
def plot_stock_share_pie(summary_df, path):
    """PIE: each category's share of the total stock value."""
    values = summary_df.set_index("category")["total_value"]
    values = values[values > 0]
    if values.empty:
        return None
    values = _top_n_with_other(values)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(values, labels=values.index, autopct="%1.1f%%", startangle=90,
           wedgeprops={"edgecolor": "white"})
    ax.set_title("Share of Stock Value by Category")
    return _save(fig, path)


def plot_transactions_by_category(tx_df, path):
    """GROUPED BARS: units moved per category, split by sale / restock / initial stock."""
    if tx_df.empty:
        return None
    pivot = tx_df.pivot_table(index="category", columns="action",
                              values="quantity", aggfunc="sum", fill_value=0)
    colors = [ACTION_COLORS.get(a, FALLBACK_COLOR) for a in pivot.columns]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    pivot.plot(kind="bar", ax=ax, color=colors)
    ax.set_xlabel("Category")
    ax.set_ylabel("Units")
    ax.set_title("Transactions by Category (units)")
    ax.legend(title="Type")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    return _save(fig, path)


def plot_revenue_by_category(tx_df, path):
    """BAR: sales revenue (price * units sold) per category."""
    sales = tx_df[tx_df["action"] == "sale"]
    if sales.empty:
        return None
    revenue = sales.groupby("category")["value"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(revenue.index, revenue.values, color=ACTION_COLORS["sale"])
    ax.set_xlabel("Category")
    ax.set_ylabel("Sales Revenue")
    ax.set_title("Sales Revenue by Category")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    return _save(fig, path)


def plot_action_mix_donut(tx_df, path):
    """DONUT: how many transactions were sales vs restocks vs initial stock."""
    if tx_df.empty:
        return None
    counts = tx_df["action"].value_counts()
    colors = [ACTION_COLORS.get(a, FALLBACK_COLOR) for a in counts.index]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(counts, labels=counts.index, colors=colors, autopct="%1.1f%%",
           startangle=90, wedgeprops={"width": 0.45, "edgecolor": "white"})
    ax.set_title("Transactions by Type (count)")
    return _save(fig, path)


def plot_sales_trend(tx_df, path):
    """LINE: units sold per day."""
    sales = tx_df[tx_df["action"] == "sale"]
    if sales.empty:
        return None
    daily = sales.set_index("timestamp")["quantity"].resample("D").sum()

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(daily.index, daily.values, marker="o", color=ACTION_COLORS["sale"])
    ax.fill_between(daily.index, daily.values, alpha=0.15, color=ACTION_COLORS["sale"])
    ax.set_xlabel("Date")
    ax.set_ylabel("Units Sold")
    ax.set_title("Daily Sales Trend")
    fig.autofmt_xdate()
    return _save(fig, path)


def plot_top_selling_products(tx_df, path, n=5):
    """HORIZONTAL BARS: the n products with the most units sold."""
    sales = tx_df[tx_df["action"] == "sale"]
    if sales.empty:
        return None
    top = sales.groupby("product")["quantity"].sum().nlargest(n).sort_values()

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(top.index, top.values, color=ACTION_COLORS["sale"])
    ax.set_xlabel("Units Sold")
    ax.set_title(f"Top {len(top)} Selling Products")
    return _save(fig, path)


def plot_stock_levels(df, path, threshold=10, n=15):
    """BARS: the n lowest-stock products; red = at/below the low-stock threshold."""
    if df.empty:
        return None
    lowest = df.nsmallest(n, "quantity").sort_values("quantity")
    colors = ["#C44E52" if q <= threshold else "#4C72B0" for q in lowest["quantity"]]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(lowest["name"], lowest["quantity"], color=colors)
    ax.axhline(threshold, color="#C44E52", linestyle="--", linewidth=1,
               label=f"Low-stock threshold ({threshold})")
    ax.set_xlabel("Product")
    ax.set_ylabel("Units in Stock")
    ax.set_title("Lowest Stock Levels")
    ax.legend()
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    return _save(fig, path)


def plot_expiry_status(df, path, soon_days=30):
    """PIE: expired / expiring soon / fresh / no expiry date."""
    if df.empty:
        return None
    today = pd.Timestamp.today().normalize()
    expiry = pd.to_datetime(df["expiry_date"])
    days_left = (expiry - today).dt.days

    labels = pd.Series("No expiry date", index=df.index)
    labels[days_left < 0] = "Expired"
    labels[(days_left >= 0) & (days_left <= soon_days)] = f"Expires within {soon_days} days"
    labels[days_left > soon_days] = "Fresh"

    counts = labels.value_counts()
    palette = {
        "Expired": "#C44E52",
        f"Expires within {soon_days} days": "#DD8452",
        "Fresh": "#55A868",
        "No expiry date": "#B0B0B0",
    }
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(counts, labels=counts.index, colors=[palette[c] for c in counts.index],
           autopct="%1.0f%%", startangle=90, wedgeprops={"edgecolor": "white"})
    ax.set_title("Product Expiry Status")
    return _save(fig, path)


def generate_all_charts(df, tx_df, out_dir, threshold=10):
    """
    Build every chart into out_dir and return the list of files created.
    A chart is skipped automatically if there is no data for it
    (e.g. no sales yet -> no sales trend).
    """
    summary = category_summary(df)
    jobs = [
        ("stock_share_pie.png",           lambda p: plot_stock_share_pie(summary, p)),
        ("transactions_by_category.png",  lambda p: plot_transactions_by_category(tx_df, p)),
        ("revenue_by_category.png",       lambda p: plot_revenue_by_category(tx_df, p)),
        ("transaction_types_donut.png",   lambda p: plot_action_mix_donut(tx_df, p)),
        ("sales_trend.png",               lambda p: plot_sales_trend(tx_df, p)),
        ("top_selling_products.png",      lambda p: plot_top_selling_products(tx_df, p)),
        ("stock_levels.png",              lambda p: plot_stock_levels(df, p, threshold)),
        ("expiry_status.png",             lambda p: plot_expiry_status(df, p)),
    ]
    saved = []
    for filename, make_chart in jobs:
        result = make_chart(os.path.join(out_dir, filename))
        if result:
            saved.append(result)
    return saved
