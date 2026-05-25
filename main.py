import pandas as pd
import os
from datetime import datetime

# ─────────────────────────────────────────────
# 1. SAFE FILE PATH SETUP
# ─────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(BASE_DIR, "data", "customers.csv")

print("\n📂 Loading file from:", file_path)

# Check if file exists BEFORE loading
if not os.path.exists(file_path):
    raise FileNotFoundError(f"CSV file not found at: {file_path}")

# Load data
customers = pd.read_csv(file_path)

print("✅ Data loaded successfully!\n")
print(customers.head())


# ─────────────────────────────────────────────
# 2. DATA PREPARATION
# ─────────────────────────────────────────────

customers["last_contacted"] = pd.to_datetime(customers["last_contacted"])


# ─────────────────────────────────────────────
# 3. CORE LOGIC (SMARTOPS BRAIN)
# ─────────────────────────────────────────────

def get_inactive_customers(days=7):
    today = datetime.now()

    customers["days_inactive"] = (
        today - customers["last_contacted"]
    ).dt.days

    inactive = customers[customers["days_inactive"] > days]

    return inactive


def generate_message(name):
    return f"Hi {name}, we miss you! Just checking in to see how you’re doing."


# ─────────────────────────────────────────────
# 4. OUTPUT LAYER (WHAT BUSINESS SEES)
# ─────────────────────────────────────────────

def show_followups():
    inactive = get_inactive_customers()

    print("\n🔥 SMARTOPS - FOLLOW-UP LIST 🔥\n")

    if inactive.empty:
        print("No customers need follow-up today.")
        return

    for _, row in inactive.iterrows():
        print(f"""
────────────────────────────
Name: {row['name']}
Phone: {row['phone']}
Plan: {row['plan']}
Last Contact: {row['last_contacted'].date()}
Days Inactive: {row['days_inactive']}

ACTION:
{generate_message(row['name'])}
────────────────────────────
""")


# ─────────────────────────────────────────────
# 5. RUN SYSTEM
# ─────────────────────────────────────────────

if __name__ == "__main__":
    show_followups()