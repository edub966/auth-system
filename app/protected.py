from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from functools import wraps

protected_bp = Blueprint("protected", __name__)

# regular protected route, any logged in user can access
@protected_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    current_email = get_jwt_identity()
    claims = get_jwt()
    return jsonify({
        "message": f"Welcome {current_email}",
        "role": claims["role"]
    }), 200


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims["role"] != "admin":
            return jsonify({"error": "Admins only"}), 403
        return fn(*args, **kwargs)
    return wrapper


# admin only route
@protected_bp.route("/admin/users", methods=["GET"])
@admin_required
def get_all_users():
    from app.models import User
    users = User.query.all()
    return jsonify([{
        "id": u.id,
        "email": u.email,
        "role": u.role,
        "created_at": u.created_at.isoformat()
    } for u in users]), 200