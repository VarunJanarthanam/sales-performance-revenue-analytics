"""
Superstore Sales Data — Cleaning Script
=========================================
Reads the raw 'Orders', 'People', and 'Returns' sheets, applies cleaning
and standardization, engineers a few analysis-ready columns, and writes:
  - superstore_clean.csv   (cleaned, analysis-ready order line items)
  - superstore.db          (SQLite database for SQL analysis)

Data quality checks performed (see printed log):
  - duplicate rows / duplicate Row IDs
  - Ship Date < Order Date (logical impossibility)
  - negative Sales or non-positive Quantity
  - Postal Code type inconsistency (US ints vs Canadian alphanumeric)
  - Product ID reused across different Product Names
  - missing values across all columns
"""

import pandas as pd
import sqlite3

RAW_PATH = "../data/sample_-_superstore.xlsx"  # place the raw source workbook here
OUT_CSV = "../data/superstore_clean.csv"
OUT_DB = "../data/superstore.db"

print("Loading raw workbook...")
orders = pd.read_excel(RAW_PATH, sheet_name="Orders")
people = pd.read_excel(RAW_PATH, sheet_name="People")
returns = pd.read_excel(RAW_PATH, sheet_name="Returns")

print(f"Raw Orders shape: {orders.shape}")

# ---------------------------------------------------------------------
# 1. Data quality checks (log only — nothing silently dropped)
# ---------------------------------------------------------------------
log = []
log.append(f"Duplicate full rows: {orders.duplicated().sum()}")
log.append(f"Duplicate Row IDs: {orders['Row ID'].duplicated().sum()}")
log.append(f"Missing values (any column): {orders.isna().sum().sum()}")

orders["Order Date"] = pd.to_datetime(orders["Order Date"])
orders["Ship Date"] = pd.to_datetime(orders["Ship Date"])
bad_dates = (orders["Ship Date"] < orders["Order Date"]).sum()
log.append(f"Rows where Ship Date < Order Date: {bad_dates}")

log.append(f"Negative Sales: {(orders['Sales'] < 0).sum()}")
log.append(f"Non-positive Quantity: {(orders['Quantity'] <= 0).sum()}")

dup_line = orders.duplicated(subset=["Order ID", "Product ID"]).sum()
log.append(f"Duplicate Order ID + Product ID line items: {dup_line}")

reused_ids = orders.groupby("Product ID")["Product Name"].nunique()
log.append(f"Product IDs mapped to >1 Product Name: {(reused_ids > 1).sum()}")

print("\n".join(log))

# ---------------------------------------------------------------------
# 2. Cleaning / standardization
# ---------------------------------------------------------------------
# Trim whitespace on all text/object columns
text_cols = orders.select_dtypes(include=["object", "string"]).columns.tolist()
for c in set(text_cols):
    orders[c] = orders[c].astype(str).str.strip()

# Postal Code: standardize to string (US postal codes were read as int,
# Canadian ones are alphanumeric — forcing both to zero-padded strings
# keeps the column consistent and avoids losing leading zeros like 02135)
def clean_postal(v):
    v = str(v).strip()
    if v.replace(".0", "").isdigit():
        return v.replace(".0", "").zfill(5)
    return v

orders["Postal Code"] = orders["Postal Code"].apply(clean_postal)

# Engineered columns for analysis
orders["Profit Margin"] = (orders["Profit"] / orders["Sales"]).round(4)
orders["Days to Ship"] = (orders["Ship Date"] - orders["Order Date"]).dt.days
orders["Order Year"] = orders["Order Date"].dt.year
orders["Order Month"] = orders["Order Date"].dt.month
orders["Order Year-Month"] = orders["Order Date"].dt.to_period("M").astype(str)
orders["Is Loss"] = orders["Profit"] < 0
orders["Is Returned"] = orders["Order ID"].isin(
    returns.loc[returns["Returned"].str.strip().str.lower() == "yes", "Order ID"]
)

# Attach regional manager
orders = orders.merge(people, on="Region", how="left")

# ---------------------------------------------------------------------
# 3. Write outputs
# ---------------------------------------------------------------------
orders.to_csv(OUT_CSV, index=False)
print(f"\nWrote cleaned CSV: {OUT_CSV}  shape={orders.shape}")

conn = sqlite3.connect(OUT_DB)
orders.to_sql("orders", conn, if_exists="replace", index=False)
people.to_sql("people", conn, if_exists="replace", index=False)
returns.to_sql("returns", conn, if_exists="replace", index=False)
conn.close()
print(f"Wrote SQLite database: {OUT_DB}  (tables: orders, people, returns)")
