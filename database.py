import streamlit as st
import sqlite3

# Connect to database
conn = sqlite3.connect("growsmart.db")
cursor = conn.cursor()

st.title("GrowSmart - Customer Tracker")

# -------------------------------
# ADD CUSTOMER
# -------------------------------
st.header("Add New Customer")

name = st.text_input("Name")
phone = st.text_input("Phone")
email = st.text_input("Email")
tag = st.selectbox("Tag", ["New", "Returning", "VIP"])

if st.button("Add Customer"):
    cursor.execute("""
    INSERT INTO customers (name, phone, email, tag)
    VALUES (?, ?, ?, ?)
    """, (name, phone, email, tag))
    conn.commit()
    st.success("Customer added successfully!")

# -------------------------------
# VIEW CUSTOMERS
# -------------------------------
st.header("All Customers")

cursor.execute("SELECT * FROM customers")
customers = cursor.fetchall()

for customer in customers:
    st.write(customer)

conn.close()