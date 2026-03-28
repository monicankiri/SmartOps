# SmartOps
## SmartOps is a simple AI-powered tool designed to help small businesses track customers, manage interactions, and improve follow-ups to increase sales and retention. It focuses on solving a common problem among small business owners: losing customers due to poor tracking and lack of follow-up systems.

### Current Features:
- Customer database management
- Basic customer tagging (New, VIP, Returning)
- Data storage using SQLite

### Upcoming Features:
- Interaction tracking
- Follow-up reminders
- AI-based customer insights

Built with Python, Streamlit, and SQLite.

# Evolution 🚀

This repository documents my journey from building simple tools to developing full AI systems for businesses.

## Stages
1. Tool (Customer Manager)
2. AI Tool (Insights)
3. AI System (Automation + Chatbot)
4. Future: Robotics Integration

## Vision
To build AI systems that help small businesses grow and make better decisions.

## Day 1: Project Setup & Database Design

### What I Did
- Installed Python and set up development environment
- Created GitHub repository: growsmart-v1
- Designed database schema for customer tracking

### Database Design
Customers table:
- id
- name
- phone
- email
- tag
- created_at

### What I Learned
- What a database is and how it stores structured data
- How to design a simple schema for real-world business use

### Next Step
- Create the actual database using SQLite

## Day 2: Database Implementation (SQLite)

### What I Did
- Created SQLite database file (growsmart.db)
- Created Customers table using Python
- Connected Python to SQLite database
- Inserted sample customer data for testing

### Tools Used
- Python (sqlite3)
- SQLite database

### What I Learned
- How to create a database using code
- How to connect Python to a database
- How data is stored and retrieved

### Next Step
- Build functions to add, view, and delete customers
