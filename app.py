import os
from flask import Flask, render_template  # Removed unused imports from here
from flask_login import LoginManager
import datetime
from config import config_by_name
# Pokemon model not directly used here yet
from models import db, bcrypt, User, connect_db
from forms import SearchForm  # Global search form

# Initialize Flask extensions (globally if not app-specific config needed at init)
login_manager = LoginManager()
# bcrypt is initialized in models.py or can be initialized here too if preferred
# db is initialized in models.py


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions with app
    # connect_db(app) # Handled by db.init_app if using Flask-SQLAlchemy's preferred way
    db.init_app(app)
    # bcrypt needs the app context if used for hashing config
    bcrypt.init_app(app)
    login_manager.init_app(app)

    @app.context_processor
    def inject_current_year_and_search_form():
        return {
            'current_year': datetime.datetime.now(datetime.UTC).year,
            'search_form': SearchForm()  # Keep your existing search form injection
        }

    # Configure Flask-Login
    login_manager.login_view = 'auth.login'  # Blueprint.route_function_name
    login_manager.login_message_category = 'info'
    login_manager.login_message = "Please log in to access this page."

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import and register Blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    app.register_blueprint(main_bp)
    # Auth routes will be like /auth/login
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Context processor to make forms available to all templates
    @app.context_processor
    def inject_search_form():
        return dict(search_form=SearchForm())

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # --- CLI commands for DB ---
    @app.cli.command("init-db")
    def init_db_command():
        """Initializes the database and creates tables."""
        with app.app_context():  # Ensure app context for db operations
            db.create_all()
        print("Initialized the database and created tables.")

    @app.cli.command("seed-db")
    def seed_db_command():
        """Seeds the database with initial Pokemon data."""
        from seed import seed_pokemon_data
        print("Starting to seed Pokemon data. This may take a while...")
        with app.app_context():  # Ensure app context for db operations
            # Pass app if seed needs config or db directly
            count = seed_pokemon_data(app)
        print(f"Seeded {count} Pokemon into the database.")

    @app.cli.command("reset-db")
    def reset_db_command():
        """Drops all tables and re-initializes the database."""
        with app.app_context():
            db.drop_all()
            db.create_all()
        print("Dropped all tables and re-initialized the database.")
        # Optionally, re-seed
        from seed import seed_pokemon_data
        print("Starting to re-seed Pokemon data. This may take a while...")
        with app.app_context():
            count = seed_pokemon_data(app)
        print(f"Re-seeded {count} Pokemon into the database.")

    return app


# This part is generally for when you run `python app.py` directly
# If using `flask run`, it uses the app factory `create_app`
if __name__ == '__main__':
    flask_env = os.getenv('FLASK_CONFIG') or 'default'
    app = create_app(flask_env)
    # No need to call db.create_all() here if using CLI command 'init-db'
    app.run(debug=app.config['DEBUG'])
