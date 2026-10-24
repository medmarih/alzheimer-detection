# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_mail import Mail

mail = Mail()
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'

    # 👉 Importer le modèle APRÈS init_app
    from app.models import User

    # 👉 Définir le user_loader ici !
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 👉 Importer et enregistrer les blueprints APRÈS user_loader
    from app.routes.auth_routes import auth_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.medecin_routes import medecin_bp
    from app.routes.patient_routes import patient_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(medecin_bp)
    app.register_blueprint(patient_bp)

    return app
