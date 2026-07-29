"""
SmartOps — AI-Powered Customer Follow-Up Intelligence System
Flask MVP Application
"""

from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'smartops-secret-key-change-in-production')
import os
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///smartops.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ─────────────────────────────────────────────
# DATABASE MODELS
# ─────────────────────────────────────────────

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    customers = db.relationship('Customer', backref='owner', lazy=True)


class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30))
    email = db.Column(db.String(120))
    request = db.Column(db.String(200))
    last_contacted = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followups = db.relationship('FollowUpActivity', backref='customer', lazy=True)

    @property
    def days_inactive(self):
        return (datetime.utcnow() - self.last_contacted).days

    @property
    def risk_level(self):
        days = self.days_inactive
        if days >= 14:
            return 'HIGH'
        elif days >= 7:
            return 'MEDIUM'
        return 'HEALTHY'

    @property
    def risk_color(self):
        return {'HIGH': '#ef4444', 'MEDIUM': '#f59e0b', 'HEALTHY': '#10b981'}[self.risk_level]

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'request': self.request,
            'last_contacted': self.last_contacted.isoformat(),
            'days_inactive': self.days_inactive,
            'risk_level': self.risk_level,
            'created_at': self.created_at.isoformat()
        }


class FollowUpActivity(db.Model):
    __tablename__ = 'followup_activity'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    follow_up_date = db.Column(db.DateTime, default=datetime.utcnow)
    follow_up_type = db.Column(db.String(50), default='call')  # call, SMS, email, WhatsApp
    status = db.Column(db.String(30), default='Pending')  # Pending, Completed, No Response
    notes = db.Column(db.Text)
    ai_suggested = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'user_id': self.user_id,
            'follow_up_date': self.follow_up_date.isoformat(),
            'follow_up_type': self.follow_up_type,
            'status': self.status,
            'notes': self.notes,
            'ai_suggested': self.ai_suggested
        }


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─────────────────────────────────────────────
# FOLLOW-UP ENGINE
# ─────────────────────────────────────────────

def get_ai_suggestion(customer):
    """Generate a follow-up message suggestion based on customer data."""
    days = customer.days_inactive
    name = customer.name
    service = customer.request or 'our services'

    if days >= 14:
        return (f"Hi {name}, we haven't heard from you in a while and truly value your business. "
                f"We'd love to catch up and see how we can support you with {service}. "
                f"Can we schedule a quick call this week?")
    elif days >= 7:
        return (f"Hi {name}, just checking in to see how things are going with {service}. "
                f"We're here if you need anything — feel free to reach out anytime!")
    else:
        return (f"Hi {name}, hope everything is going well! Let us know if there's anything "
                f"we can help you with regarding {service}.")


# ─────────────────────────────────────────────
# ROUTES — AUTH
# ─────────────────────────────────────────────

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register.html')

        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Account created successfully! Welcome to SmartOps.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ─────────────────────────────────────────────
# ROUTES — DASHBOARD
# ─────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    customers = Customer.query.filter_by(user_id=current_user.id).all()
    total = len(customers)
    high_risk = [c for c in customers if c.risk_level == 'HIGH']
    medium_risk = [c for c in customers if c.risk_level == 'MEDIUM']
    healthy = [c for c in customers if c.risk_level == 'HEALTHY']
    due_followups = [c for c in customers if c.risk_level in ('HIGH', 'MEDIUM')]

    return render_template('dashboard.html',
        customers=customers,
        total=total,
        high_risk=high_risk,
        medium_risk=medium_risk,
        healthy=healthy,
        due_followups=due_followups
    )


# ─────────────────────────────────────────────
# ROUTES — CUSTOMERS
# ─────────────────────────────────────────────

@app.route('/customers')
@login_required
def customers():
    all_customers = Customer.query.filter_by(user_id=current_user.id).order_by(Customer.last_contacted.asc()).all()
    return render_template('customers.html', customers=all_customers)


@app.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        service = request.form.get('request', '').strip()
        last_contacted_str = request.form.get('last_contacted', '')

        if not name:
            flash('Customer name is required.', 'error')
            return render_template('add_customer.html')

        last_contacted = datetime.utcnow()
        if last_contacted_str:
            try:
                last_contacted = datetime.strptime(last_contacted_str, '%Y-%m-%d')
            except ValueError:
                pass

        customer = Customer(
            name=name, phone=phone, email=email,
            request=service, last_contacted=last_contacted,
            user_id=current_user.id
        )
        db.session.add(customer)
        db.session.commit()
        flash(f'Customer "{name}" added successfully.', 'success')
        return redirect(url_for('customers'))

    return render_template('add_customer.html')


@app.route('/customers/<int:customer_id>')
@login_required
def customer_detail(customer_id):
    customer = Customer.query.filter_by(id=customer_id, user_id=current_user.id).first_or_404()
    followups = FollowUpActivity.query.filter_by(customer_id=customer_id).order_by(FollowUpActivity.follow_up_date.desc()).all()
    suggestion = get_ai_suggestion(customer)
    return render_template('customer_detail.html', customer=customer, followups=followups, suggestion=suggestion)


@app.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    customer = Customer.query.filter_by(id=customer_id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        customer.name = request.form.get('name', customer.name).strip()
        customer.phone = request.form.get('phone', '').strip()
        customer.email = request.form.get('email', '').strip()
        customer.request = request.form.get('request', '').strip()
        last_contacted_str = request.form.get('last_contacted', '')
        if last_contacted_str:
            try:
                customer.last_contacted = datetime.strptime(last_contacted_str, '%Y-%m-%d')
            except ValueError:
                pass
        db.session.commit()
        flash('Customer updated successfully.', 'success')
        return redirect(url_for('customer_detail', customer_id=customer_id))
    return render_template('edit_customer.html', customer=customer)


@app.route('/customers/<int:customer_id>/delete', methods=['POST'])
@login_required
def delete_customer(customer_id):
    customer = Customer.query.filter_by(id=customer_id, user_id=current_user.id).first_or_404()
    FollowUpActivity.query.filter_by(customer_id=customer_id).delete()
    db.session.delete(customer)
    db.session.commit()
    flash('Customer deleted.', 'success')
    return redirect(url_for('customers'))


# ─────────────────────────────────────────────
# ROUTES — FOLLOW-UPS
# ─────────────────────────────────────────────

@app.route('/followups')
@login_required
def followups():
    customer_ids = [c.id for c in Customer.query.filter_by(user_id=current_user.id).all()]
    all_followups = FollowUpActivity.query.filter(
        FollowUpActivity.customer_id.in_(customer_ids)
    ).order_by(FollowUpActivity.follow_up_date.desc()).all()
    return render_template('followups.html', followups=all_followups)


@app.route('/customers/<int:customer_id>/followup', methods=['POST'])
@login_required
def log_followup(customer_id):
    customer = Customer.query.filter_by(id=customer_id, user_id=current_user.id).first_or_404()
    followup = FollowUpActivity(
        customer_id=customer_id,
        user_id=current_user.id,
        follow_up_type=request.form.get('type', 'call'),
        status=request.form.get('status', 'Completed'),
        notes=request.form.get('notes', '').strip(),
        ai_suggested=request.form.get('ai_suggested', 'false') == 'true'
    )
    # Update last_contacted when a follow-up is completed
    if followup.status == 'Completed':
        customer.last_contacted = datetime.utcnow()
    db.session.add(followup)
    db.session.commit()
    flash('Follow-up logged successfully.', 'success')
    return redirect(url_for('customer_detail', customer_id=customer_id))


# ─────────────────────────────────────────────
# JSON API — for future frontend / mobile use
# Matches the API Endpoint Outline in the docs
# ─────────────────────────────────────────────

def login_required_json(f):
    """Like login_required, but returns JSON 401 instead of redirecting to login page."""
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return wrapper


# --- 4.1 Authentication ---

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''

    if not username or not email or not password:
        return jsonify({'error': 'username, email and password are required'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(username=username, email=email, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return jsonify({'message': 'User registered successfully', 'user': {'id': user.id, 'username': user.username}}), 201


@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid username or password'}), 401

    login_user(user)
    return jsonify({'message': 'Login successful', 'user': {'id': user.id, 'username': user.username}}), 200


@app.route('/api/auth/logout', methods=['POST'])
@login_required_json
def api_logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200


# --- 4.2 Customer Management ---

@app.route('/api/customers', methods=['GET'])
@login_required_json
def api_get_customers():
    customers = Customer.query.filter_by(user_id=current_user.id).all()
    return jsonify({'customers': [c.to_dict() for c in customers], 'total': len(customers)}), 200


@app.route('/api/customers', methods=['POST'])
@login_required_json
def api_create_customer():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'name is required'}), 400

    last_contacted = datetime.utcnow()
    if data.get('last_contacted'):
        try:
            last_contacted = datetime.strptime(data['last_contacted'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'last_contacted must be in YYYY-MM-DD format'}), 400

    customer = Customer(
        name=name,
        phone=data.get('phone', ''),
        email=data.get('email', ''),
        request=data.get('request', ''),
        last_contacted=last_contacted,
        user_id=current_user.id
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify({'message': 'Customer created', 'customer': customer.to_dict()}), 201


@app.route('/api/customers/<int:customer_id>', methods=['GET'])
@login_required_json
def api_get_customer(customer_id):
    customer = Customer.query.filter_by(id=customer_id, user_id=current_user.id).first()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    return jsonify({'customer': customer.to_dict()}), 200


@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
@login_required_json
def api_update_customer(customer_id):
    customer = Customer.query.filter_by(id=customer_id, user_id=current_user.id).first()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    data = request.get_json(silent=True) or {}
    customer.name = data.get('name', customer.name)
    customer.phone = data.get('phone', customer.phone)
    customer.email = data.get('email', customer.email)
    customer.request = data.get('request', customer.request)
    if data.get('last_contacted'):
        try:
            customer.last_contacted = datetime.strptime(data['last_contacted'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'last_contacted must be in YYYY-MM-DD format'}), 400

    db.session.commit()
    return jsonify({'message': 'Customer updated', 'customer': customer.to_dict()}), 200


@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
@login_required_json
def api_delete_customer(customer_id):
    customer = Customer.query.filter_by(id=customer_id, user_id=current_user.id).first()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    FollowUpActivity.query.filter_by(customer_id=customer_id).delete()
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted'}), 200


# --- 4.3 Follow-Up Management ---

@app.route('/api/followups', methods=['GET'])
@login_required_json
def api_get_followups():
    customer_ids = [c.id for c in Customer.query.filter_by(user_id=current_user.id).all()]
    followups = FollowUpActivity.query.filter(FollowUpActivity.customer_id.in_(customer_ids)).order_by(
        FollowUpActivity.follow_up_date.desc()
    ).all()
    return jsonify({'followups': [f.to_dict() for f in followups], 'total': len(followups)}), 200


@app.route('/api/followups/due', methods=['GET'])
@login_required_json
def api_get_followups_due():
    customers = Customer.query.filter_by(user_id=current_user.id).all()
    due = [c.to_dict() for c in customers if c.risk_level in ('HIGH', 'MEDIUM')]
    return jsonify({'due_followups': due, 'total': len(due)}), 200


@app.route('/api/followups', methods=['POST'])
@login_required_json
def api_create_followup():
    data = request.get_json(silent=True) or {}
    customer_id = data.get('customer_id')
    customer = Customer.query.filter_by(id=customer_id, user_id=current_user.id).first()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    followup = FollowUpActivity(
        customer_id=customer.id,
        user_id=current_user.id,
        follow_up_type=data.get('follow_up_type', 'call'),
        status=data.get('status', 'Completed'),
        notes=data.get('notes', ''),
        ai_suggested=bool(data.get('ai_suggested', False))
    )
    if followup.status == 'Completed':
        customer.last_contacted = datetime.utcnow()

    db.session.add(followup)
    db.session.commit()
    return jsonify({'message': 'Follow-up logged', 'followup': followup.to_dict()}), 201


@app.route('/api/followups/<int:followup_id>', methods=['PUT'])
@login_required_json
def api_update_followup(followup_id):
    followup = FollowUpActivity.query.get(followup_id)
    if not followup:
        return jsonify({'error': 'Follow-up not found'}), 404

    # Make sure this follow-up belongs to one of the current user's customers
    customer = Customer.query.filter_by(id=followup.customer_id, user_id=current_user.id).first()
    if not customer:
        return jsonify({'error': 'Follow-up not found'}), 404

    data = request.get_json(silent=True) or {}
    followup.status = data.get('status', followup.status)
    followup.notes = data.get('notes', followup.notes)
    db.session.commit()
    return jsonify({'message': 'Follow-up updated', 'followup': followup.to_dict()}), 200


# --- 4.4 Dashboard & Insights ---

@app.route('/api/dashboard/summary', methods=['GET'])
@login_required_json
def api_dashboard_summary():
    customers = Customer.query.filter_by(user_id=current_user.id).all()
    high = sum(1 for c in customers if c.risk_level == 'HIGH')
    medium = sum(1 for c in customers if c.risk_level == 'MEDIUM')
    healthy = sum(1 for c in customers if c.risk_level == 'HEALTHY')
    return jsonify({
        'total_customers': len(customers),
        'high_risk': high,
        'medium_risk': medium,
        'healthy': healthy,
        'followups_due': high + medium
    }), 200


@app.route('/api/dashboard/inactive', methods=['GET'])
@login_required_json
def api_dashboard_inactive():
    customers = Customer.query.filter_by(user_id=current_user.id).all()
    inactive = [c.to_dict() for c in customers if c.risk_level in ('HIGH', 'MEDIUM')]
    inactive.sort(key=lambda c: c['days_inactive'], reverse=True)
    return jsonify({'inactive_customers': inactive, 'total': len(inactive)}), 200


# ─────────────────────────────────────────────
# INIT DB
# ─────────────────────────────────────────────




def seed_demo_data(user):
    """Seed demo customers for testing."""
    demo_customers = [
        {'name': 'Emeka Okafor', 'phone': '+234 801 234 5678', 'request': 'Logistics delivery', 'days_ago': 20},
        {'name': 'Fatima Bello', 'phone': '+234 802 345 6789', 'request': 'Retail bulk order', 'days_ago': 9},
        {'name': 'Chidi Nwachukwu', 'phone': '+234 803 456 7890', 'request': 'Consulting services', 'days_ago': 3},
        {'name': 'Aisha Mohammed', 'phone': '+234 804 567 8901', 'request': 'Inventory management', 'days_ago': 15},
        {'name': 'Tunde Adeyemi', 'phone': '+234 805 678 9012', 'request': 'Product delivery', 'days_ago': 1},
    ]
    for c in demo_customers:
        customer = Customer(
            name=c['name'], phone=c['phone'], request=c['request'],
            last_contacted=datetime.utcnow() - timedelta(days=c['days_ago']),
            user_id=user.id
        )
        db.session.add(customer)
    db.session.commit()


with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='demo').first():
        demo = User(
            username='demo',
            email='demo@smartops.com',
            password=generate_password_hash('demo1234')
        )
        db.session.add(demo)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
