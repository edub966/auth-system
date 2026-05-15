from flask import Flask
from app.extensions import db, bcrypt, jwt
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    from app.models import TokenBlocklist

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = TokenBlocklist.query.filter_by(jti=jti).first()
        return token is not None

    from app.auth import auth_bp
    from app.protected import protected_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(protected_bp, url_prefix="/api")

    # create db tables if they don't exist
    with app.app_context():
        db.create_all()

    from flask import send_from_directory

    @app.route("/")
    def index():
        return send_from_directory("../frontend", "index.html")
    
    return app