from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from config.database import db
from models.models import User, AuditLog
from sqlalchemy import or_
from validators import validate_email, validate_password_strength, error

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'student')
        
        # Validation
        if not username or not email or not password:
            return jsonify({'error': 'Missing required fields'}), 400
        
        if role not in ['librarian', 'student']:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter(
            or_(User.username == username, User.email == email)
        ).first()
        
        if existing_user:
            return jsonify({'error': 'User already exists'}), 409
        
        # Validate email
        if not validate_email(data["email"]):
            return jsonify({"error": "Invalid email format"}), 400

        # Validate password strength
        if not validate_password_strength(data["password"]):
            return jsonify({"error": "Password is too weak"}), 400

        # At this point, both are valid — create user
        user = User(username, email, password, role)

        db.session.add(user)
        db.session.commit()

        # Log the registration
        audit_log = AuditLog(
            user_id=user.id,
            action='register',
            resource_type='user',
            details={'role': role}
        )
        db.session.add(audit_log)
        db.session.commit()

        return jsonify({
            "message": "User registered successfully",
            "user_id": user.id
        }), 201

        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Missing username or password'}), 400
        
        # Find user
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check password
        if not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Create access token (identity must be a string)
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role}
        )
        
        # Log the login
        audit_log = AuditLog(
            user_id=user.id,
            action='login',
            resource_type='system',
            details={'username': username}
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        # Convert string ID back to integer for database query
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500