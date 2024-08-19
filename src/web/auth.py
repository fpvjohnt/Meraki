from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from web.models import User
from web import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200
    return jsonify({"message": "Invalid email or password"}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing email or password"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_password = generate_password_hash(data['password'])
    new_user = User(email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "email": user.email} for user in users]), 200

@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    return jsonify({"message": f"Hello, User {current_user_id}!"}), 200

# Adding a mock API endpoint for health checks
@auth_bp.route('/health-check', methods=['GET'])
def health_check():
    try:
        mock_data = {
            "switchChecks": {
                "status": "healthy",
                "details": "All switches are operational."
            },
            "wirelessChecks": {
                "status": "degraded",
                "details": "Some wireless networks are experiencing issues."
            }
        }
        return jsonify(mock_data)
    except Exception as e:
        current_app.logger.error('Error in health check: %s', str(e))
        return jsonify(error=str(e)), 500
