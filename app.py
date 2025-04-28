from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta
import random
import string
import logging
from functools import wraps
import traceback

app = Flask(__name__)
# Update CORS configuration for local development
CORS(app, 
     resources={r"/api/*": {
         "origins": ["http://localhost:8080"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type"],
         "supports_credentials": True,
         "expose_headers": ["Content-Type", "X-CSRFToken"],
         "max_age": 120
     }},
     supports_credentials=True)

# Security configurations
app.config['SECRET_KEY'] = 'dev-key-123'  # Use a fixed key for development
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_DOMAIN'] = None

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///immunization.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,  # Change to DEBUG level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Error handler
@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"Error: {str(error)}")
    logger.error(traceback.format_exc())
    return jsonify({
        'success': False,
        'message': 'An error occurred on the server',
        'error': str(error)
    }), 500

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    identifier = db.Column(db.String(50))
    account = db.relationship('Account', backref='user', uselist=False)
    records = db.relationship('Record', backref='user', lazy=True)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    last_login = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    is_locked = db.Column(db.Boolean, default=False)
    lock_until = db.Column(db.DateTime)

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vaccine = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    dose = db.Column(db.Integer)
    filename = db.Column(db.String(255))
    uploader = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Create database tables
def init_db():
    with app.app_context():
        # Drop all tables first
        db.drop_all()
        # Create all tables
        db.create_all()
        # Initialize with sample data
        initialize_database()

# Helper function to generate random names
def generate_random_name():
    first_names = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 
                  'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica',
                  'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa',
                  'Matthew', 'Margaret', 'Anthony', 'Betty', 'Mark', 'Sandra', 'Donald', 'Ashley',
                  'Steven', 'Kimberly', 'Paul', 'Emily', 'Andrew', 'Donna', 'Joshua', 'Michelle']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
                 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
                 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker',
                 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores']
    return f"{random.choice(first_names)} {random.choice(last_names)}"

# Initialize database with random users
def initialize_database():
    with app.app_context():
        # Check if we already have users
        if User.query.count() == 0:
            # Create 25 random users
            for i in range(25):
                # Create user
                user = User(
                    name=generate_random_name(),
                    dob=datetime(1990 + random.randint(0, 30), random.randint(1, 12), random.randint(1, 28)),
                    identifier=f"ID{random.randint(1000, 9999)}"
                )
                db.session.add(user)
                db.session.flush()  # Get the user ID

                # Create account
                username = f"user{i+1}"
                account = Account(
                    username=username,
                    password_hash=generate_password_hash("password"),
                    role="User",
                    user_id=user.id
                )
                db.session.add(account)

            # Create admin accounts
            admin_roles = ['Admin', 'Sysadmin', 'Frontdesk']
            for role in admin_roles:
                account = Account(
                    username=role.lower(),
                    password_hash=generate_password_hash("password"),
                    role=role,
                    user_id=None
                )
                db.session.add(account)

            db.session.commit()

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Role-based access control decorator
def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'success': False, 'message': 'Authentication required'}), 401
            
            account = Account.query.filter_by(user_id=session['user_id']).first()
            if not account or account.role not in roles:
                return jsonify({'success': False, 'message': 'Permission denied'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Audit logging function
def log_audit(user_id, action, details, ip_address):
    log = AuditLog(
        user_id=user_id,
        action=action,
        details=details,
        ip_address=ip_address
    )
    db.session.add(log)
    db.session.commit()
    logger.info(f"Audit: {action} by user {user_id} - {details}")

# API Routes
@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    try:
        if request.method == 'OPTIONS':
            return '', 200
            
        logger.debug(f"Login attempt with data: {request.json}")
        
        data = request.json
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'success': False, 'message': 'Missing username or password'}), 400
            
        account = Account.query.filter_by(username=data['username']).first()
        
        # Check if account is locked
        if account and account.is_locked and account.lock_until and account.lock_until > datetime.utcnow():
            return jsonify({'success': False, 'message': 'Account is locked. Try again later.'}), 401
        
        if account and check_password_hash(account.password_hash, data['password']):
            # Reset failed login attempts
            account.failed_login_attempts = 0
            account.is_locked = False
            account.lock_until = None
            account.last_login = datetime.utcnow()
            db.session.commit()
            
            # Set session
            session.permanent = True
            session['user_id'] = account.user_id
            session['role'] = account.role
            
            # Log successful login
            log_audit(account.user_id, 'LOGIN', 'Successful login', request.remote_addr)
            
            response = jsonify({
                'success': True,
                'username': account.username,
                'role': account.role,
                'userId': account.user_id
            })
            return response
        
        # Increment failed login attempts
        if account:
            account.failed_login_attempts += 1
            if account.failed_login_attempts >= 5:
                account.is_locked = True
                account.lock_until = datetime.utcnow() + timedelta(minutes=15)
            db.session.commit()
        
        # Log failed login attempt
        if account:
            log_audit(account.user_id, 'LOGIN_FAILED', 'Failed login attempt', request.remote_addr)
        
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': 'An error occurred during login'}), 500

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    user_id = session.get('user_id')
    log_audit(user_id, 'LOGOUT', 'User logged out', request.remote_addr)
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    
    # Check if username already exists
    if Account.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
    
    # Create user
    user = User(
        name=data['name'],
        dob=datetime.strptime(data['dob'], '%Y-%m-%d'),
        identifier=data.get('identifier')
    )
    db.session.add(user)
    db.session.flush()
    
    # Create account
    account = Account(
        username=data['username'],
        password_hash=generate_password_hash(data['password']),
        role='User',
        user_id=user.id
    )
    db.session.add(account)
    db.session.commit()
    
    # Log registration
    log_audit(user.id, 'REGISTER', 'New user registration', request.remote_addr)
    
    return jsonify({'success': True, 'message': 'Registration successful'})

@app.route('/api/users', methods=['GET'])
@login_required
@role_required(['Admin', 'Sysadmin'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'name': user.name,
        'dob': user.dob.strftime('%Y-%m-%d'),
        'identifier': user.identifier,
        'username': user.account.username if user.account else None
    } for user in users])

@app.route('/api/records', methods=['GET'])
@login_required
def get_records():
    current_user = Account.query.filter_by(user_id=session['user_id']).first()
    
    # Regular users can only see their own records
    if current_user.role == 'User':
        records = Record.query.filter_by(user_id=session['user_id']).all()
    else:
        records = Record.query.all()
    
    return jsonify([{
        'id': record.id,
        'userId': record.user_id,
        'vaccine': record.vaccine,
        'date': record.date.strftime('%Y-%m-%d'),
        'dose': record.dose,
        'filename': record.filename,
        'uploader': record.uploader,
        'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for record in records])

@app.route('/api/records', methods=['POST'])
@login_required
def add_record():
    data = request.json
    current_user = Account.query.filter_by(user_id=session['user_id']).first()
    
    # Check if user has permission to add records for this user
    if current_user.role == 'User' and data['userId'] != session['user_id']:
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    record = Record(
        user_id=data['userId'],
        vaccine=data['vaccine'],
        date=datetime.strptime(data['date'], '%Y-%m-%d'),
        dose=data.get('dose'),
        filename=data['filename'],
        uploader=current_user.username
    )
    db.session.add(record)
    db.session.commit()
    
    # Log record addition
    log_audit(session['user_id'], 'ADD_RECORD', f'Added record for user {data["userId"]}', request.remote_addr)
    
    return jsonify({'success': True, 'message': 'Record added successfully'})

@app.route('/api/audit-logs', methods=['GET'])
@login_required
@role_required(['Sysadmin'])
def get_audit_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return jsonify([{
        'id': log.id,
        'user_id': log.user_id,
        'action': log.action,
        'details': log.details,
        'ip_address': log.ip_address,
        'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for log in logs])

if __name__ == '__main__':
    try:
        init_db()  # Initialize database with tables and sample data
        app.run(host='127.0.0.1', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Server startup error: {str(e)}")
        logger.error(traceback.format_exc()) 
