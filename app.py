import streamlit as st
import sqlite3

# Connect to ONE database
conn = sqlite3.connect("database/Smartops.db", check_same_thread=False)
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    tag TEXT
)
""")

st.title("📊 Smartops - Customer Manager")

# ---------------- ADD CUSTOMER ----------------
st.subheader("➕ Add Customer")

col1, col2, col3 = st.columns(3)

with col1:
    name = st.text_input("Name")

with col2:
    phone = st.text_input("Phone")

with col3:
    tag = st.selectbox("Tag", ["New", "VIP", "Returning"])

if st.button("Add Customer"):
    if name:
        cursor.execute(
            "INSERT INTO customers (name, phone, tag) VALUES (?, ?, ?)",
            (name, phone, tag)
        )
        conn.commit()
        st.success("Customer added!")
    else:
        st.warning("Name is required")

# ---------------- VIEW CUSTOMERS ----------------
st.subheader("📋 Customer List")

cursor.execute("SELECT * FROM customers")
rows = cursor.fetchall()

if rows:
    for row in rows:
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

        with col1:
            st.write(f"**{row[1]}**")

        with col2:
            st.write(row[2])

        with col3:
            st.write(f"🔖 {row[3]}")

        with col4:
            if st.button("❌", key=row[0]):
                cursor.execute("DELETE FROM customers WHERE id=?", (row[0],))
                conn.commit()
                st.rerun()
else:
    st.info("No customers yet")