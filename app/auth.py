from flask import Blueprint, request, jsonify
from app.extensions import db, bcrypt
from app.models import User
import re
from flask_jwt_extended import create_access_token, create_refresh_token
from app.models import User, TokenBlocklist
from app.extensions import db, bcrypt, limiter

auth_bp = Blueprint("auth", __name__)

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r"[0-9]", password):
        return "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character"
    return None

@auth_bp.route("/register", methods=["POST"])
@limiter.limit("3 per minute")
def register():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    email = data["email"].lower().strip()
    password = data["password"]

    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    password_error = is_valid_password(password)
    if password_error:
        return jsonify({"error": password_error}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(email=email, password_hash=password_hash)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Account created successfully"}), 201

from flask_jwt_extended import create_access_token, create_refresh_token
from flask import make_response

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    email = data["email"].lower().strip()
    password = data["password"]

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    additional_claims = {"role": user.role, "id": user.id}
    access_token = create_access_token(identity=user.email, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=user.email, additional_claims=additional_claims)

  
    response = make_response(jsonify({
        "access_token": access_token,
        "role": user.role
    }), 200)

    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,      
        secure=False,        
        samesite="Lax",      
        max_age=60 * 60 * 24 * 7  
    )

    return response

from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from flask import request as flask_request

@auth_bp.route("/refresh", methods=["POST"])
def refresh():
   
    refresh_token = flask_request.cookies.get("refresh_token")
    if not refresh_token:
        return jsonify({"error": "No refresh token found"}), 401

    try:
        from flask_jwt_extended import decode_token
        decoded = decode_token(refresh_token)
        identity = decoded["sub"]
        claims = {"role": decoded["role"], "id": decoded["id"]}
        new_access_token = create_access_token(identity=identity, additional_claims=claims)
        return jsonify({"access_token": new_access_token}), 200
    except Exception as e:
        return jsonify({"error": "Invalid or expired refresh token"}), 401
    
@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    blocked = TokenBlocklist(jti=jti)
    db.session.add(blocked)
    db.session.commit()

    response = make_response(jsonify({"message": "Successfully logged out"}), 200)
    response.delete_cookie("refresh_token")
    return response