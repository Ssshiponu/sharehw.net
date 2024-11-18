from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from models import db, User
from auth import auth
from admin import admin
from homework import homework
from main import main
from config import Config
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure upload directories exist
    os.makedirs(app.config['UPLOAD_FOLDER_HOMEWORK'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER_ID_CARDS'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    csrf = CSRFProtect(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'

    with app.app_context():
        # Create all database tables
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(homework)
    app.register_blueprint(main)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
