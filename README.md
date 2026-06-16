# SmartOps — AI-Powered Customer Follow-Up Intelligence System

## Overview
SmartOps is a web-based customer retention and follow-up management system designed for SMEs. It helps businesses track customer activity, detect inactive customers, and improve follow-up processes to reduce customer loss.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Open in Browser
Visit: `http://localhost:5000`

### Demo Account
- **Username:** `demo`
- **Password:** `demo1234`

---

## Features (MVP)
- **User Authentication** — Register, login, logout with bcrypt password hashing
- **Customer Management** — Add, view, edit, delete customer records
- **Follow-Up Engine** — Automatically detects inactive customers and assigns risk levels
- **Risk Classification** — HIGH (14+ days), MEDIUM (7–13 days), HEALTHY (<7 days)
- **AI-Generated Suggestions** — Context-aware follow-up message templates
- **Follow-Up Logging** — Track every follow-up with method, status, and notes
- **Dashboard** — Centralized view of all customers and action items

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3 + Flask |
| Database | SQLite (MVP) → PostgreSQL (Production) |
| ORM | SQLAlchemy |
| Frontend | HTML + CSS + Jinja2 Templates |
| Authentication | Flask-Login + Werkzeug (bcrypt) |
| Future AI | Claude API / OpenAI API |

---

## Project Structure
```
smartops/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── templates/
│   ├── base.html       # Base layout
│   ├── login.html      # Login page
│   ├── register.html   # Registration page
│   ├── dashboard.html  # Main dashboard
│   ├── customers.html  # Customer list
│   ├── add_customer.html
│   ├── edit_customer.html
│   ├── customer_detail.html
│   └── followups.html
└── smartops.db         # SQLite database (auto-created)
```

---

## Roadmap

| Version | Features |
|---------|---------|
| V1 (Current) | Flask MVP — auth, customers, follow-up engine |
| V2 | Claude API integration, email/SMS notifications |
| V3 | Multi-tenancy, PostgreSQL, payment integration |
| V4 | Full SaaS platform, automated workflows |
| V5 | West African SME intelligence infrastructure |

---

## Security Notes
- Passwords are hashed using Werkzeug (bcrypt-based) — **never stored in plain text**
- Session management via Flask-Login
- HTTPS/TLS should be enforced in production
- NDPR compliance measures required before public deployment

---

## Author
Monica — AI Accelerator Program Capstone Project, 2026
